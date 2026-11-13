"""Unit tests for Nested-Space Cosmology II: Force at Resolutions."""

from __future__ import annotations

import math

from nsc_force_resolutions import (
    atomic_shell_and_em_impedance,
    helium_absolute_zero_wave_particle_bridge,
    magnetic_vorticity_and_moments,
    nuclear_binding_and_fission_neck,
    single_force_facet_dilution_bridge,
    strong_nuclear_triad_confinement,
    unified_resolution_hierarchy_readout,
    weak_balloon_in_balloon_venting,
)


def test_proposition_2_1_helium_absolute_zero_wave_particle_bridge() -> None:
    res = helium_absolute_zero_wave_particle_bridge()
    # Doubly closed He-4 core + n=1 (+/- omega*) shell
    assert res["alpha_vent_margin_mev"] > 19.0
    assert math.isclose(res["z_eff_he_screened"], 27.0 / 16.0, rel_tol=1e-15)
    assert -78.0 <= res["e_he_ground_nsc_ev"] <= -77.0
    # Zero-point stretch exceeds van der Waals well -> never freezes at 1 atm
    assert res["never_freezes_at_1atm"] is True
    assert res["q_zpe_cell_k"] > res["eps_vdw_k"]
    assert res["q_zpe_k"] > 2.2 * res["eps_vdw_k"]
    assert res["de_boer_lambda_star"] > 2.55
    assert 24.0 <= res["p_solid_nsc_atm"] <= 26.0
    # Paper I Theorem 3 added mass (3/2 M_He) shifts BEC 3.14 K -> 2.09-2.16 K (exp 2.172 K)
    assert math.isclose(res["added_mass_factor_3_over_2"], 1.5, rel_tol=1e-15)
    assert res["rel_diff_t_lambda"] < 0.01
    # Unfreezing e^3 expansion at T_lambda matches chi_freeze = 3 within 2.5%
    assert 2.90 <= res["chi_unfreeze_at_t_lambda"] <= 3.05
    # Exponential cloud slope explosion near Absolute Zero
    ladder = {row["temperature_k"]: row for row in res["de_broglie_ladder"]}
    assert ladder[1.0e-3]["dlambda_dt_pm_per_k"] > 1e7 * ladder[300.0]["dlambda_dt_pm_per_k"]
    assert ladder[1.0e-9]["superfluid_zero_friction_fraction"] > 0.999999


def test_theorem_1_single_force_facet_dilution_bridge() -> None:
    res = single_force_facet_dilution_bridge()
    assert math.isclose(res["baryon_compton_wavelength_m"], 2.10019415e-16, rel_tol=1e-6)
    assert math.isclose(res["proton_compton_wavelength_m"], 2.10308910e-16, rel_tol=1e-6)
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
    prof = {row["d_over_r_star"]: row["delta_e_norm"] for row in res["potential_profile"]}
    assert math.isclose(prof[0.0], res["hard_core_barrier_delta_e"], rel_tol=1e-15)
    assert math.isclose(prof[2.0], -1.0, rel_tol=1e-15)


def test_theorem_3_atomic_shell_and_em_impedance() -> None:
    res = atomic_shell_and_em_impedance()
    expected_inv = 4.0 * (math.pi ** 3) + (math.pi ** 2) + math.pi
    assert math.isclose(res["alpha_geom_inv"], expected_inv, rel_tol=1e-15)
    assert abs(res["relative_diff_ppm"]) < 2.5
    assert math.isclose(res["bohr_radius_geom_m"], 5.29178e-11, rel_tol=1e-5)
    capacities = [s["shell_capacity_2n2"] for s in res["shells"]]
    assert capacities == [2, 8, 18, 32, 50, 72]
    radii_ratios = [s["r_n_over_a0"] for s in res["shells"]]
    assert radii_ratios == [1, 4, 9, 16, 25, 36]


def test_theorem_4_magnetic_vorticity_and_moments() -> None:
    res = magnetic_vorticity_and_moments()
    # Exact transverse Lorentz / Magnus zero-work identity and paired Cooper flux quantum
    assert res["lorentz_work_rate_residual"] < 1e-16
    assert math.isclose(res["flux_quantum_single_wb"], 2.0 * res["flux_quantum_cooper_wb"], rel_tol=1e-15)
    assert res["g_orbital_exact"] == 1.0
    assert res["g_helix_bare_exact"] == 2.0
    # Electron anomalous moment from alpha_geom = (4 pi^3 + pi^2 + pi)^-1
    assert abs(res["rel_diff_g_e_1loop_ppm"]) < 2.0
    assert abs(res["rel_diff_g_e_2loop_ppm"]) < 0.05
    # Proton RMS charge radius r_p = 4 * lambda_p and negative neutron <r_E^2>_n
    assert res["rel_diff_r_proton"] < 0.001  # within 0.06% of CODATA 0.84075 fm
    assert res["r2_neutron_nsc_fm2"] < 0.0
    assert res["rel_diff_r2_neutron"] < 0.02  # within 1.6% of PDG -0.1161 fm^2
    # Proton and neutron magnetic moments & -0.684975 ratio (within 7 ppm of CODATA!)
    assert math.isclose(res["exterior_shell_area_fraction_15_16"], 15.0 / 16.0, rel_tol=1e-15)
    assert math.isclose(res["mu_neutron_nsc_mun"], -(0.5 + math.sqrt(2.0)), rel_tol=1e-15)
    assert res["rel_diff_mu_neutron"] < 0.001
    assert res["rel_diff_mu_proton"] < 0.001
    assert abs(res["rel_diff_ratio_ppm"]) < 10.0
    assert abs(res["su6_quark_error_ppm"]) > 25000.0
    # Deuteron magnetic moment and 21-cm hydrogen hyperfine line
    assert res["rel_diff_mu_deuteron"] < 0.002
    assert res["rel_diff_21cm"] < 0.001


def test_theorem_5_weak_balloon_in_balloon_venting() -> None:
    res = weak_balloon_in_balloon_venting()
    assert res["is_stable_in_deuteron"] is True
    assert res["is_unstable_in_vacuum"] is True
    assert res["net_deuteron_stability_margin_mev"] > 0.9
    assert math.isclose(res["bare_valve_conductance_e_minus_12"], math.exp(-12.0), rel_tol=1e-15)
    assert res["rel_diff_g_fermi"] < 0.02  # within 1.7% of experimental G_F * m_p^2
    assert res["rel_diff_g_axial"] < 0.001  # g_A = 1.2761 within 0.06% of experimental 1.2754
    assert 870.0 <= res["tau_vent_estimate_s"] <= 920.0
    assert 875.0 <= res["tau_vent_with_exp_gf_s"] <= 882.0


def test_theorem_6_nuclear_binding_and_fission_neck() -> None:
    res = nuclear_binding_and_fission_neck()
    assert 47.0 <= res["fissility_crit_z2_over_a"] <= 49.0
    assert math.isclose(res["fissility_crit_upper_z2_over_a"], 48.51, rel_tol=2e-3)
    assert math.isclose(res["a_pair_mev"], 0.75 * res["a_vol_mev"], rel_tol=1e-15)
    assert math.isclose(res["neck_cubic_root_p_plus"], 2.1038034027, rel_tol=1e-9)
    by_name = {row["nucleus"]: row for row in res["sample_nuclei"]}
    # Iron/Nickel peak > Uranium binding per nucleon
    assert by_name["Fe-56"]["B_per_A_mev"] > by_name["U-235"]["B_per_A_mev"]
    assert 8.4 <= by_name["Fe-56"]["B_per_A_mev"] <= 9.0
    assert 7.4 <= by_name["U-235"]["B_per_A_mev"] <= 7.8
    # Beta-stability valley Z*(A) matches stable nuclei closely
    assert abs(by_name["He-4"]["Z_star_beta_valley"] - 2.0) < 0.1
    assert abs(by_name["Fe-56"]["Z_star_beta_valley"] - 26.0) < 1.0
    assert abs(by_name["Pb-208"]["Z_star_beta_valley"] - 82.0) < 1.0


def test_theorem_7_unified_resolution_hierarchy() -> None:
    res = unified_resolution_hierarchy_readout()
    assert len(res["resolution_tiers"]) == 8
    assert res["room_dynamic_range_b"] > 1e61
    assert 46.5 <= res["room_3axis_cascade_cycles"] <= 47.5
    assert "proposition_2_1_helium_bridge" in res
    assert "theorem_4_magnetism_moments" in res
