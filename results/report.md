# Strip sizing result

Inputs: `examples/design.json` (SHA-256 `22488c83ad7191c4c61554518b5482af2fc38e9a1e11f87c0b2694b5f91b160f`).
All material values are illustrative assumptions, not measured allowables.

For a 350 × 40 mm cantilever strip under 120 N/m,
the lightest passing candidate in the enumerated set is **axial-40**:
5.00 mm thick, 110.6 g,
EI = 54.2 N·m², tip deflection = 4.16 mm.
Its largest ply maximum-stress index is 0.049, against a
declared screen of 0.50.

There are 15 candidates; 3 pass both the displacement and
ply-stress screens. The comparison applies to longitudinal bending only. Shear
webs, attachments, torsion, buckling and impact could change the preferred layup.
The selected stack, bottom to top, is in `selected_layup.json`.

7 candidates exceed 5% tip/span or 0.1 rad rotation. They are
excluded; their raw linear-model values remain in `layup_sweep.csv` for diagnosis.

The FE tip-displacement errors in `beam_verification.csv` range from
5.2e-18 to
1.3e-14 m. Consistent nodal loads
make this a closed-form verification rather than a mesh-convergence study.

The 120 mm support-span, 20 mm wide synthetic coupon has true EI = 27.0833
N·m²; the reduction recovers 27.1494 N·m² after subtracting machine
compliance. A fitted intercept handles seating offset. The reported statistical
standard error excludes force calibration, support span, displacement calibration,
machine compliance and laminate thickness uncertainty.

The fixture and synthetic data share a 120 mm support span, 20 mm coupon width
and 5 mm coupon thickness. Physical test planning is in
`docs/test-plan.md`; the current evidence consists of calculations and generated data.
