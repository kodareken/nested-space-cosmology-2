"""Unit tests for Nested-Space Cosmology II: Force at Resolutions."""

from __future__ import annotations

import math

from nsc_force_resolutions import (
    atomic_shell_and_em_impedance,
    nuclear_binding_and_fission_neck,
    single_force_facet_dilution_bridge,
    strong_nuclear_triad_confinement,
    unified_resolution_hierarchy_readout,
    weak_balloon_in_balloon_venting,
)


def test_theorem_1_single_force_facet_dilution_bridge() -> None:
    res = single_force_facet_dilution_bridge()
    assert math.isclose(res["n_1d_resolution_ratio"], 1.29942005e19, rel_tol=1e-6)
    assert math.isclose(res["f_star_facet_capacity"], 1.68849246e38, rel_tol=1e-6)
    # Exact algebraic bridge: F_grav = F_nuclear / F_star and alpha_G = 1 / F_star
    assert res["relative_bridge_residual"] < 1e-15
    assert res["alpha_grav_bridge_residual"] < 1e-15
    assert res["geometric_mean_residual"] < 1e-15
    assert math.isclose(res["alpha_grav_dimensionless"], 5.9224428e-39, rel_tol=1e-6)
    assert math.isclose(res["r_ns_km"], 10.916137, rel_tol=1e-5)


def test_theorem_2_strong_nuclear_triad_confinement() -> None:
    res = strong_nuclear_triad_confinement()
    assert res["v_star_100"] == 0.0
    assert res["v_star_110"] == 0.0
    assert res["e_star_111"] == 4.0
    assert math.isclose(res["hard_core_barrier_delta_e"], 8.0 * (math.sqrt(2.0) - 1.0), rel_tol=1e-15)
    assert math.isclose(res["gamma_core_per_axis"], 8.0 * (math.sqrt(2.0) - 1.0) / 3.0, rel_tol=1e-15)
    assert res["contact_energy_at_2r"] == 7.0
    assert res["bare_binding_fraction"] == 0.125
    # Nuclear binding band (7.80 - 8.61 MeV/nucleon) matches empirical 7.7 - 8.8 MeV/nucleon
    assert 7.75 <= res["nuclear_binding_base_mev"] <= 7.85
    assert 8.55 <= res["nuclear_binding_barrier_mev"] <= 8.65
    assert math.isclose(res["chi_spaghetti"], 0.5 * math.log(2.0), rel_tol=1e-15)
    assert res["theta_spaghetti"] == 0.5
    assert res["lambda_3_snap_normalized"] == 8.0


def test_theorem_3_atomic_shell_and_em_impedance() -> None:
    res = atomic_shell_and_em_impedance()
    expected_inv = 4.0 * (math.pi ** 3) + (math.pi ** 2) + math.pi
    assert math.isclose(res["alpha_geom_inv"], expected_inv, rel_tol=1e-15)
    assert abs(res["relative_diff_ppm"]) < 2.5
    assert math.isclose(res["bohr_radius_geom_m"], 5.29177e-11, rel_tol=1e-5)
    capacities = [s["shell_capacity_2n2"] for s in res["shells"]]
    assert capacities == [2, 8, 18, 32, 50, 72]
    radii_ratios = [s["r_n_over_a0"] for s in res["shells"]]
    assert radii_ratios == [1, 4, 9, 16, 25, 36]


def test_theorem_4_weak_balloon_in_balloon_venting() -> None:
    res = weak_balloon_in_balloon_venting()
    assert res["is_stable_in_deuteron"] is True
    assert res["is_unstable_in_vacuum"] is True
    assert res["net_deuteron_stability_margin_mev"] > 0.9
    assert math.isclose(res["bare_valve_conductance_e_minus_12"], math.exp(-12.0), rel_tol=1e-15)
    assert res["rel_diff_g_fermi"] < 0.02  # within 1.7% of experimental G_F * m_p^2


def test_theorem_5_nuclear_binding_and_fission_neck() -> None:
    res = nuclear_binding_and_fission_neck()
    assert 47.0 <= res["fissility_crit_z2_over_a"] <= 49.0
    assert math.isclose(res["neck_cubic_root_p_plus"], 2.1038034027, rel_tol=1e-9)
    by_name = {row["nucleus"]: row for row in res["sample_nuclei"]}
    # Iron/Nickel peak > Uranium binding per nucleon
    assert by_name["Fe-56"]["B_per_A_mev"] > by_name["U-235"]["B_per_A_mev"]
    assert 8.4 <= by_name["Fe-56"]["B_per_A_mev"] <= 9.0
    assert 7.4 <= by_name["U-235"]["B_per_A_mev"] <= 7.8


def test_theorem_6_unified_resolution_hierarchy() -> None:
    res = unified_resolution_hierarchy_readout()
    assert len(res["resolution_tiers"]) == 7
    assert res["room_dynamic_range_b"] > 1e61
    assert 46.5 <= res["room_3axis_cascade_cycles"] <= 47.5
