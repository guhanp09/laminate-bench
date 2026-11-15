"""Two-node Euler-Bernoulli finite elements, displacement and rotation per node."""

import math
import numpy as np


def beam_solve(
    length_m,
    ei_nm2,
    elements=20,
    udl_n_m=0.0,
    point_load_n=0.0,
    point_position_m=None,
    support="cantilever",
):
    values = (length_m, ei_nm2, udl_n_m, point_load_n)
    if not all(math.isfinite(v) for v in values) or length_m <= 0 or ei_nm2 <= 0:
        raise ValueError("Finite loads and positive length/EI required")
    if not isinstance(elements, int) or not 2 <= elements <= 400:
        raise ValueError("Use 2 to 400 beam elements")
    if support not in ("cantilever", "simple"):
        raise ValueError("Support must be cantilever or simple")
    n = elements + 1
    x = np.linspace(0, length_m, n)
    le = length_m / elements
    stiffness = np.zeros((2 * n, 2 * n))
    force = np.zeros(2 * n)
    ke = (
        ei_nm2
        / le**3
        * np.array(
            [
                [12, 6 * le, -12, 6 * le],
                [6 * le, 4 * le**2, -6 * le, 2 * le**2],
                [-12, -6 * le, 12, -6 * le],
                [6 * le, 2 * le**2, -6 * le, 4 * le**2],
            ]
        )
    )
    fe = udl_n_m * le / 12 * np.array([6, le, 6, -le])
    for i in range(elements):
        dofs = np.arange(2 * i, 2 * i + 4)
        stiffness[np.ix_(dofs, dofs)] += ke
        force[dofs] += fe
    if point_load_n:
        position = length_m if point_position_m is None else point_position_m
        if not math.isfinite(position) or not 0 <= position <= length_m:
            raise ValueError("Point load must be on the beam")
        # Consistent Hermite interpolation also supports loads inside elements.
        el = min(int(position / le), elements - 1)
        r = (position - x[el]) / le
        shape = np.array(
            [
                1 - 3 * r * r + 2 * r**3,
                le * (r - 2 * r * r + r**3),
                3 * r * r - 2 * r**3,
                le * (-r * r + r**3),
            ]
        )
        force[2 * el : 2 * el + 4] += point_load_n * shape
    constrained = [0, 1] if support == "cantilever" else [0, 2 * (n - 1)]
    free = np.setdiff1d(np.arange(2 * n), constrained)
    u = np.zeros(2 * n)
    u[free] = np.linalg.solve(stiffness[np.ix_(free, free)], force[free])
    reactions = stiffness @ u - force
    return {
        "x_m": x,
        "deflection_m": u[::2],
        "rotation_rad": u[1::2],
        "reactions": reactions,
        "force_vector": force,
        "strain_energy_j": 0.5 * float(u @ stiffness @ u),
    }
