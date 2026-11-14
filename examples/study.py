"""Layup screening, finite-element evidence and a synthetic bend-data example."""

from pathlib import Path
import platform
import importlib.metadata
import csv
import hashlib
import json
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "laminate-bench-mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from laminate_bench.laminate import Laminate, Material
from laminate_bench.beam import beam_solve
from laminate_bench.reduction import reduce_bend


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def record_provenance():
    paths = []
    for directory in ('src', 'include', 'examples', 'tools', 'cad'):
        if (ROOT / directory).exists():
            paths.extend(p for p in (ROOT / directory).rglob('*')
                         if p.suffix in ('.py', '.hpp', '.cpp', '.json', '.scad')
                         and '__pycache__' not in p.parts)
    record = {
        'data_status': 'numerical or synthetic; no physical measurements',
        'python': platform.python_version(),
        'numpy': importlib.metadata.version('numpy'),
        'matplotlib': importlib.metadata.version('matplotlib'),
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(paths)},
    }
    (ROOT / 'results/provenance.json').write_text(json.dumps(record, indent=2) + '\n')


def main():
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    source = ROOT / "examples/design.json"
    config = json.loads(source.read_text())
    mat = Material(**config["material"])
    length, width, load = (config[key] for key in ("length_m", "width_m", "udl_n_m"))
    families = {"axial": [0, 0, 0, 0], "axial-shear": [0, 0, 45, -45],
                "quasi-isotropic": [0, 45, -45, 90]}
    rows, laminates = [], {}
    for family, block in families.items():
        for repeats in (2, 3, 4, 5, 6):
            half = block * repeats
            angles = half + half[::-1]
            lam = Laminate(angles, config["ply_thickness_m"], mat)
            ei = lam.beam_ei(width)
            beam = beam_solve(length, ei, 24, udl_n_m=-load)
            # Root moment per unit width. No artificial transverse clamp.
            stresses = lam.ply_stresses([0, 0, 0, -load * length ** 2 / (2 * width), 0, 0])
            index = max(r["max_stress_index"] for r in stresses)
            tip = abs(beam["deflection_m"][-1])
            linear_geometry = tip / length <= 0.05 and max(abs(beam['rotation_rad'])) <= 0.1
            key = f"{family}-{len(angles)}"
            laminates[key] = lam
            rows.append({"candidate": key, "plies": len(angles), "thickness_mm": lam.thickness_m * 1000,
                         "mass_kg": length * width * lam.thickness_m * mat.density_kg_m3,
                         "ei_nm2": ei, "tip_deflection_mm": tip * 1000,
                         "max_stress_index": index,
                         "within_small_deflection_screen": bool(linear_geometry),
                         "passes": bool(linear_geometry and tip <= config["deflection_limit_m"] and index <= config["ply_index_limit"])})
    write_csv(out / "layup_sweep.csv", rows)
    passing = sorted((r for r in rows if r["passes"]), key=lambda r: (r["mass_kg"], r["tip_deflection_mm"]))
    if not passing:
        raise RuntimeError("No candidate meets the declared screens")
    winner = passing[0]
    lam = laminates[winner["candidate"]]
    ei = winner["ei_nm2"]
    stresses = lam.ply_stresses([0, 0, 0, -load * length ** 2 / (2 * width), 0, 0])
    write_csv(out / "root_ply_stresses.csv", stresses)
    verification = []
    # With a consistent UDL vector, nodal values reproduce the closed form;
    # this is a patch/verification test rather than a convergence claim.
    for n in (2, 4, 8, 16, 32):
        result = beam_solve(length, ei, n, udl_n_m=-load)
        exact = -load * length ** 4 / (8 * ei)
        verification.append({"elements": n, "tip_deflection_m": result["deflection_m"][-1],
                             "closed_form_m": exact,
                             "absolute_error_m": abs(result["deflection_m"][-1] - exact),
                             "force_balance_residual_n": sum(result["reactions"][::2]) - load * length})
    write_csv(out / "beam_verification.csv", verification)
    # A 20 mm wide coupon from the same laminate at 120 mm support span.
    # All points are generated, not workshop measurements.
    span, coupon_ei, machine = 0.12, lam.beam_ei(0.02), 1.5e-7
    p = np.linspace(2, 50, 25)
    rng = np.random.default_rng(817)
    displacement = p * (span ** 3 / (48 * coupon_ei) + machine) + 20e-6 + rng.normal(0, 0.3e-6, p.size)
    write_csv(out / "synthetic_bend.csv", [{"source": "SYNTHETIC", "load_n": a, "crosshead_m": b}
                                          for a, b in zip(p, displacement)])
    reduced = reduce_bend(p, displacement, span, machine)
    (out / "bend_reduction.json").write_text(json.dumps({"source": "SYNTHETIC", "true_ei_nm2": coupon_ei,
                                                        "machine_compliance_m_n": machine, **reduced}, indent=2) + "\n")
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout="constrained")
    for family in families:
        subset = [r for r in rows if r["candidate"].rsplit("-", 1)[0] == family]
        axes[0, 0].plot([r["mass_kg"] * 1000 for r in subset], [r["tip_deflection_mm"] for r in subset], "o-", label=family)
    axes[0, 0].axhline(config["deflection_limit_m"] * 1000, color="#b66b36", ls="--", label="deflection limit")
    axes[0, 0].set(xlabel="Strip mass [g]", ylabel="Linear-model tip deflection [mm]", title="Large-deflection candidates are rejected")
    axes[0, 0].legend(fontsize=8)
    beam = beam_solve(length, ei, 32, udl_n_m=-load)
    exact = -load * beam["x_m"] ** 2 * (6*length**2 - 4*length*beam["x_m"] + beam["x_m"]**2) / (24*ei)
    axes[0, 1].plot(beam["x_m"], exact * 1000, color="#156b7a", label="closed form")
    axes[0, 1].plot(beam["x_m"][::4], beam["deflection_m"][::4] * 1000, "o", color="#b66b36", label="beam FE nodes")
    axes[0, 1].set(xlabel="Distance from root [m]", ylabel="Deflection [mm]", title=winner["candidate"])
    axes[0, 1].legend(fontsize=8)
    axes[1, 0].plot([r["s1_pa"] / 1e6 for r in stresses], [r["z_m"] * 1000 for r in stresses], color="#156b7a", label="fibre")
    axes[1, 0].plot([r["s2_pa"] / 1e6 for r in stresses], [r["z_m"] * 1000 for r in stresses], color="#b66b36", label="transverse")
    axes[1, 0].set(xlabel="Local ply stress [MPa]", ylabel="Thickness coordinate [mm]", title="Root stress recovery, both faces per ply")
    axes[1, 0].legend(fontsize=8)
    axes[1, 1].scatter(p, displacement * 1e6, s=15, color="#156b7a", label="synthetic data")
    axes[1, 1].plot(p, (reduced["measured_compliance_m_n"] * p + reduced["intercept_m"]) * 1e6, color="#b66b36", label="compliance fit")
    axes[1, 1].set(xlabel="Load [N]", ylabel="Crosshead travel [µm]", title="Bend-data pipeline demonstration · synthetic")
    axes[1, 1].legend(fontsize=8)
    fig.suptitle("Laminate Bench · assumed carbon/epoxy strip properties", fontsize=14)
    fig.savefig(out / "study.png", dpi=170)
    plt.close(fig)
    thickness_mm = lam.thickness_m * 1000
    (ROOT / 'cad/dimensions.scad').write_text(
        '// Generated by examples/study.py for the selected laminate. Units: mm.\n'
        f'span = 120;\nroller_d = 10;\ncoupon_width = 20;\ncoupon_t = {thickness_mm:g};\n'
        'base_l = 180;\nbase_w = 60;\nbase_t = 8;\nsupport_h = 22;\n')
    # Small dimensioned concept drawing: source dimensions match bend_fixture.scad.
    drawing = '''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400">
<rect width="960" height="400" fill="white"/>
<g font-family="sans-serif" fill="#24363c"><text x="40" y="35" font-size="23">Three-point-bend fixture · concept · dimensions in mm</text>
<text x="40" y="62" font-size="14">120 support span · 20 coupon width · Ø10 rollers · 180 × 60 × 8 base</text>
<rect x="120" y="275" width="720" height="32" fill="#b9c5c8"/>
<g fill="#788e96"><rect x="204" y="187" width="72" height="88"/><rect x="684" y="187" width="72" height="88"/></g>
<g fill="#156b7a"><circle cx="240" cy="187" r="20"/><circle cx="720" cy="187" r="20"/></g>
<rect x="180" y="COUPON_Y" width="600" height="COUPON_H" fill="#333"/>
<circle cx="480" cy="ROLLER_Y" r="20" fill="#b66b36"/>
<path d="M480 75 v28 m-7 -10 l7 10 7 -10" fill="none" stroke="#b66b36" stroke-width="3"/>
<text x="500" y="103" font-size="16">Load cell / crosshead interface</text>
<path d="M240 212 v38 M720 212 v38 M240 240 H720" fill="none" stroke="#24363c"/>
<text x="465" y="235" font-size="16">120</text>
<text x="40" y="350" font-size="14">Elevation scale: 4 px/mm. Supports at x = ±60 mm; coupon envelope 150 × 20 × COUPON_T mm.</text>
<text x="40" y="376" font-size="14">No crosshead design, alignment qualification or load rating has been established.</text></g></svg>'''
    for key, val in {'COUPON_Y': 167 - 4 * thickness_mm, 'COUPON_H': 4 * thickness_mm,
                     'ROLLER_Y': 147 - 4 * thickness_mm, 'COUPON_T': thickness_mm}.items():
        drawing = drawing.replace(key, f'{val:g}')
    (ROOT / 'cad/fixture.svg').write_text(drawing)
    report = f'''# Composite strip screening

Inputs: `examples/design.json` (SHA-256 `{hashlib.sha256(source.read_bytes()).hexdigest()}`).
All material values are illustrative assumptions, not measured allowables.

For a {length*1000:.0f} × {width*1000:.0f} mm cantilever strip under {load:.0f} N/m,
the lightest passing candidate in the enumerated set is **{winner['candidate']}**:
{winner['thickness_mm']:.2f} mm thick, {winner['mass_kg']*1000:.1f} g,
EI = {ei:.3f} N·m², tip deflection = {winner['tip_deflection_mm']:.3f} mm.
Its largest ply maximum-stress index is {winner['max_stress_index']:.3f}, against a
declared screen of {config['ply_index_limit']:.2f}. This is not a certified safety factor.

The axial stack wins this one-dimensional load case. It has no demonstrated
transverse, attachment or impact capability. Choosing it for a real wing spar
would require shear webs, joints, torsional loads, buckling and damage assessment.
The study therefore keeps the mixed-angle alternatives rather than declaring
one layup universally optimal. Full stacks appear in `selected_layup.json`.

Candidates with predicted tip travel above 5% of span or rotation above 0.1 rad
are flagged outside the declared small-deflection screen. Their linear-model
numbers are retained for traceability but cannot be taken as valid deformations.

The Euler–Bernoulli FE nodes match the consistent-load closed form to roundoff.
`beam_verification.csv` shows element count and equilibrium residuals. That
agreement verifies the implementation, not the material inputs or beam assumptions.

The 120 mm support-span, 20 mm wide synthetic coupon has true EI = {coupon_ei:.4f}
N·m²; the reduction recovers {reduced['ei_nm2']:.4f} N·m² after subtracting machine
compliance. A fitted intercept handles seating offset. The reported statistical
standard error excludes force calibration, support span, displacement calibration,
machine compliance and laminate thickness uncertainty.

The fixture source and schematic are concept CAD. Neither fixture manufacture nor
coupon testing has occurred. Next: fabricate witness coupons, measure thickness
at several points, verify support alignment, calibrate frame compliance and compare
measured stiffness and failure mode against these predictions.
'''
    (out / "selected_layup.json").write_text(json.dumps({"candidate": winner["candidate"],
        "bottom_to_top_angles_deg": lam.angles, "material_status": "assumed"}, indent=2) + "\n")
    (out / "report.md").write_text(report)
    record_provenance()
    print(report)


if __name__ == "__main__":
    main()
