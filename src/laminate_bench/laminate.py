"""Classical laminate theory using engineering shear strain gamma_xy.

Angles are degrees from x toward y. Stack order is bottom to top, with
z=0 at the geometric midplane. Positive curvature produces positive strain
at positive z. Resultants are [Nx,Ny,Nxy,Mx,My,Mxy].
"""

from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class Material:
    e1_pa: float = 130e9
    e2_pa: float = 9e9
    g12_pa: float = 5e9
    nu12: float = 0.3
    density_kg_m3: float = 1580.0
    xt_pa: float = 1500e6
    xc_pa: float = 900e6
    yt_pa: float = 40e6
    yc_pa: float = 150e6
    shear_pa: float = 60e6

    def __post_init__(self):
        positive = (
            self.e1_pa,
            self.e2_pa,
            self.g12_pa,
            self.density_kg_m3,
            self.xt_pa,
            self.xc_pa,
            self.yt_pa,
            self.yc_pa,
            self.shear_pa,
        )
        if any(not math.isfinite(v) or v <= 0 for v in positive):
            raise ValueError(
                "Moduli, density and strengths must be positive and finite"
            )
        if (
            not math.isfinite(self.nu12)
            or 1 - self.nu12**2 * self.e2_pa / self.e1_pa <= 0
        ):
            raise ValueError("Poisson ratio gives non-positive strain energy")

    @property
    def q(self):
        factor = 1 - self.nu12**2 * self.e2_pa / self.e1_pa
        return (
            np.array(
                [
                    [self.e1_pa, self.nu12 * self.e2_pa, 0],
                    [self.nu12 * self.e2_pa, self.e2_pa, 0],
                    [0, 0, self.g12_pa * factor],
                ]
            )
            / factor
        )


def transformed_q(material, angle_deg):
    if not math.isfinite(angle_deg):
        raise ValueError("Ply angle must be finite")
    m, n = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    q = material.q
    q11, q22 = q[0, 0], q[1, 1]
    q12, q66 = q[0, 1], q[2, 2]
    a = q11 * m**4 + 2 * (q12 + 2 * q66) * m * m * n * n + q22 * n**4
    b = q11 * n**4 + 2 * (q12 + 2 * q66) * m * m * n * n + q22 * m**4
    c = (q11 + q22 - 4 * q66) * m * m * n * n + q12 * (m**4 + n**4)
    d = (q11 - q12 - 2 * q66) * m**3 * n - (q22 - q12 - 2 * q66) * m * n**3
    e = (q11 - q12 - 2 * q66) * m * n**3 - (q22 - q12 - 2 * q66) * m**3 * n
    f = (q11 + q22 - 2 * q12 - 2 * q66) * m * m * n * n + q66 * (m**4 + n**4)
    return np.array([[a, c, d], [c, b, e], [d, e, f]])


class Laminate:
    def __init__(self, angles_deg, ply_thickness_m=0.000125, material=None):
        angles = tuple(float(a) for a in angles_deg)
        if not angles or not all(math.isfinite(a) for a in angles):
            raise ValueError("Provide a nonempty finite ply sequence")
        if not math.isfinite(ply_thickness_m) or ply_thickness_m <= 0:
            raise ValueError("Ply thickness must be positive and finite")
        self.angles = angles
        self.ply_thickness_m = ply_thickness_m
        self.material = material or Material()
        self.z = np.linspace(
            -self.thickness_m / 2, self.thickness_m / 2, len(angles) + 1
        )
        self.qbars = [transformed_q(self.material, angle) for angle in angles]
        a, b, d = (np.zeros((3, 3)) for _ in range(3))
        for i, q in enumerate(self.qbars):
            lo, hi = self.z[i : i + 2]
            a += q * (hi - lo)
            b += q * (hi**2 - lo**2) / 2
            d += q * (hi**3 - lo**3) / 3
        self.a, self.b, self.d = a, b, d
        self.abd = np.block([[a, b], [b, d]])

    @property
    def thickness_m(self):
        return len(self.angles) * self.ply_thickness_m

    def response(self, resultants):
        loads = np.asarray(resultants, dtype=float)
        if loads.shape != (6,) or not np.all(np.isfinite(loads)):
            raise ValueError("Six finite force/moment resultants required")
        return np.linalg.solve(self.abd, loads)

    def beam_ei(self, width_m):
        if not math.isfinite(width_m) or width_m <= 0:
            raise ValueError("Width must be positive and finite")
        # Allow extension and transverse/twist curvature to relax. Using D11
        # alone silently constrains these degrees of freedom.
        compliance = self.response([0, 0, 0, 1, 0, 0])[3]
        return width_m / compliance

    def ply_stresses(self, resultants):
        response = self.response(resultants)
        rows = []
        for i, (angle, q) in enumerate(zip(self.angles, self.qbars)):
            m, n = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            transform = np.array(
                [
                    [m * m, n * n, 2 * m * n],
                    [n * n, m * m, -2 * m * n],
                    [-m * n, m * n, m * m - n * n],
                ]
            )
            for face, z in zip(("bottom", "top"), self.z[i : i + 2]):
                local = transform @ (q @ (response[:3] + z * response[3:]))
                s1, s2, shear = local
                mat = self.material
                ratios = [
                    abs(s1) / (mat.xt_pa if s1 >= 0 else mat.xc_pa),
                    abs(s2) / (mat.yt_pa if s2 >= 0 else mat.yc_pa),
                    abs(shear) / mat.shear_pa,
                ]
                rows.append(
                    {
                        "ply": i + 1,
                        "angle_deg": angle,
                        "face": face,
                        "z_m": z,
                        "s1_pa": s1,
                        "s2_pa": s2,
                        "t12_pa": shear,
                        "max_stress_index": max(ratios),
                    }
                )
        return rows
