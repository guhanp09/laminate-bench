"""Three-point-bend compliance reduction for an elastic loading window."""

import numpy as np


def reduce_bend(load_n, displacement_m, span_m, machine_compliance_m_n=0.0):
    p, d = np.asarray(load_n, dtype=float), np.asarray(displacement_m, dtype=float)
    if p.ndim != 1 or p.shape != d.shape or p.size < 5:
        raise ValueError("At least five paired one-dimensional samples required")
    if not np.all(np.isfinite(p)) or not np.all(np.isfinite(d)):
        raise ValueError("Measurements must be finite")
    if np.any(np.diff(p) <= 0) or p[0] < 0:
        raise ValueError("Provide an increasing, nonnegative elastic loading window")
    if not np.isfinite(span_m) or span_m <= 0:
        raise ValueError("Support span must be positive and finite")
    if not np.isfinite(machine_compliance_m_n) or machine_compliance_m_n < 0:
        raise ValueError("Machine compliance must be nonnegative and finite")
    design = np.column_stack((p, np.ones(p.size)))
    fit, _, _, _ = np.linalg.lstsq(design, d, rcond=None)
    residual = d - design @ fit
    measured = float(fit[0])
    specimen = measured - machine_compliance_m_n
    if specimen <= 0:
        raise ValueError("No positive specimen compliance after machine correction")
    slope_se = float(
        np.sqrt(
            np.dot(residual, residual) / (p.size - 2) / np.sum((p - np.mean(p)) ** 2)
        )
    )
    return {
        "measured_compliance_m_n": measured,
        "specimen_compliance_m_n": specimen,
        "intercept_m": float(fit[1]),
        "ei_nm2": span_m**3 / (48 * specimen),
        "compliance_standard_error_m_n": slope_se,
        "ei_relative_standard_error": slope_se / specimen,
        "rms_residual_m": float(np.sqrt(np.mean(residual**2))),
    }
