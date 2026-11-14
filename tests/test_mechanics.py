import numpy as np
import pytest
from laminate_bench.laminate import Laminate, Material, transformed_q
from laminate_bench.beam import beam_solve
from laminate_bench.reduction import reduce_bend


def test_isotropic_rotation_and_beam_limit():
    e, nu, width = 70e9, 0.3, 0.04
    mat = Material(e1_pa=e, e2_pa=e, g12_pa=e / (2 * (1 + nu)), nu12=nu)
    for angle in (0, 17, 45, 90, -73):
        assert transformed_q(mat, angle) == pytest.approx(mat.q, abs=1e-4)
    lam = Laminate([0] * 16, material=mat)
    assert lam.beam_ei(width) == pytest.approx(e * width * lam.thickness_m ** 3 / 12)


def test_symmetric_balanced_and_unsymmetric_coupling():
    lam = Laminate([0, 45, -45, 90, 90, -45, 45, 0])
    assert np.max(abs(lam.b)) < 1e-10
    assert abs(lam.a[0, 2]) < 1e-7
    assert abs(lam.a[1, 2]) < 1e-7
    unsym = Laminate([0, 90])
    assert np.linalg.norm(unsym.b) > 100
    assert abs(unsym.response([100, 0, 0, 0, 0, 0])[3]) > 0.1
    assert unsym.beam_ei(0.04) < 0.04 * unsym.d[0, 0]


def test_ninety_degree_and_signed_ply_strengths():
    mat = Material()
    q90 = transformed_q(mat, 90)
    assert q90[0, 0] == pytest.approx(mat.q[1, 1])
    lam = Laminate([0] * 8)
    tension = lam.ply_stresses([100000, 0, 0, 0, 0, 0])
    compression = lam.ply_stresses([-100000, 0, 0, 0, 0, 0])
    assert max(x['max_stress_index'] for x in compression) > max(x['max_stress_index'] for x in tension)


def test_off_axis_local_stresses_against_direct_stress_rotation():
    lam = Laminate([45] * 8)
    nx = 10000
    sigma_x = nx / lam.thickness_m
    for row in lam.ply_stresses([nx, 0, 0, 0, 0, 0]):
        assert row['s1_pa'] == pytest.approx(sigma_x / 2)
        assert row['s2_pa'] == pytest.approx(sigma_x / 2)
        assert row['t12_pa'] == pytest.approx(-sigma_x / 2)


@pytest.mark.parametrize("elements", [2, 8, 32])
def test_cantilever_udl_matches_closed_form_and_equilibrium(elements):
    length, ei, load = 0.4, 15.0, -20.0
    r = beam_solve(length, ei, elements, udl_n_m=load)
    exact = load * length ** 4 / (8 * ei)
    assert r['deflection_m'][-1] == pytest.approx(exact, rel=1e-7)
    assert sum(r['reactions'][::2]) == pytest.approx(-load * length, rel=1e-7)
    assert r['reactions'][1] == pytest.approx(-load * length ** 2 / 2, rel=1e-7)
    assert r['strain_energy_j'] > 0


def test_three_point_bend_and_inside_element_load():
    r = beam_solve(0.3, 8, 20, point_load_n=-10, point_position_m=0.15, support='simple')
    assert r['deflection_m'][10] == pytest.approx(-10 * 0.3 ** 3 / (48 * 8), rel=1e-8)
    r = beam_solve(1, 10, 6, point_load_n=-3, point_position_m=0.37)
    # Tip deflection due to a point load at a: P a^2 (3L-a)/(6EI).
    assert r['deflection_m'][-1] == pytest.approx(-3 * 0.37 ** 2 * (3 - 0.37) / 60)


def test_synthetic_measurement_identification_with_machine_correction():
    p = np.linspace(1, 20, 30)
    compliance = 0.3 ** 3 / (48 * 8)
    d = (compliance + 2e-6) * p + 0.0001
    r = reduce_bend(p, d, 0.3, 2e-6)
    assert r['ei_nm2'] == pytest.approx(8, rel=1e-10)
    assert r['intercept_m'] == pytest.approx(0.0001)
    with pytest.raises(ValueError):
        reduce_bend(p, d, 0.3, 1.0)
    with pytest.raises(ValueError):
        reduce_bend([1, 2, 2, 4, 5], [1, 2, 3, 4, 5], 0.3)


def test_strain_energy_and_face_stress_reconstruct_loads():
    lam = Laminate([0, 45, -45, 90, 0, 0, 90, -45, 45, 0])
    loads = np.array([1000, -200, 100, 2, -1, 0.5])
    response = lam.response(loads)
    assert lam.abd @ response == pytest.approx(loads)
    assert response @ lam.abd @ response > 0
    # Integrate face-linear global stresses independently over each ply.
    n, m = np.zeros(3), np.zeros(3)
    for i, q in enumerate(lam.qbars):
        lo, hi = lam.z[i:i + 2]
        s_lo, s_hi = (q @ (response[:3] + z * response[3:]) for z in (lo, hi))
        n += (s_lo + s_hi) * (hi - lo) / 2
        slope = (s_hi - s_lo) / (hi - lo)
        intercept = s_lo - slope * lo
        m += intercept * (hi ** 2 - lo ** 2) / 2 + slope * (hi ** 3 - lo ** 3) / 3
    assert np.r_[n, m] == pytest.approx(loads, abs=1e-9)
