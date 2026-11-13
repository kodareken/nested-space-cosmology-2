#!/usr/bin/env python3
"""Generate the Force at Resolutions atlas figures and summary JSON."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from nsc_force_resolutions import (
    atomic_shell_and_em_impedance,
    helium_absolute_zero_wave_particle_bridge,
    nuclear_binding_and_fission_neck,
    single_force_facet_dilution_bridge,
    strong_nuclear_triad_confinement,
    unified_resolution_hierarchy_readout,
    weak_balloon_in_balloon_venting,
)

ROOT = Path(__file__).resolve().parents[1]
FIG_ATLAS_PATH = ROOT / "paper" / "figures" / "nsc-force-at-resolutions-atlas.png"
FIG_HELIUM_PATH = ROOT / "paper" / "figures" / "nsc-helium-floor-and-fission-neck.png"
JSON_PATH = ROOT / "results" / "nsc-force-at-resolutions-v1.json"


def build_helium_figure(p2_1: dict, t5: dict) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13.6, 9.2), dpi=220)
    fig.patch.set_facecolor("#ffffff")
    fig.suptitle(
        "Proposition 2.1 & Theorems 4–5: Helium at the Absolute-Zero Floor, Exponential Cloud Widening & Room-Weaving Zero Friction",
        fontsize=11.5,
        fontweight="bold",
        y=0.98,
    )

    # Panel A: Exponential widening of the outer phase/electron cloud as T -> 0 (d lambda / dT ~ T^{-3/2})
    ax = axes[0, 0]
    t_grid = np.logspace(-4, 2.5, 300)
    m_eff = (1.5 - math.exp(-3.0)) * 6.6464731e-27
    h_planck = 6.62607015e-34
    k_b = 1.380649e-23
    lam_angstrom = (h_planck / np.sqrt(2.0 * np.pi * m_eff * k_b * t_grid)) * 1e10
    d_he_a = p2_1["d_he_interatomic_m"] * 1e10
    r_he_a = p2_1["r_he_cloud_m"] * 1e10
    lam_e3_a = p2_1["lambda_weave_e3_m"] * 1e10

    ax.loglog(t_grid, lam_angstrom, color="#1b4f72", lw=2.5, label=r"Outer phase/cloud span $\lambda_{\mathrm{cloud}}(T) \propto T^{-1/2} = R_{\mathrm{He}}e^{+\Delta\chi}$")
    ax.axhline(r_he_a, color="#7f8c8d", ls=":", lw=1.3, label=f"Internal $n=1$ He shell $R_{{\\mathrm{{He}}}} = (16/27)a_0 = {r_he_a:.3f}$ Å")
    ax.axhline(d_he_a, color="#d35400", ls="--", lw=1.4, label=f"Inter-atomic spacing $d_{{\\mathrm{{He}}}} = {d_he_a:.2f}$ Å")
    ax.axhline(lam_e3_a, color="#1e8449", ls="-.", lw=1.5, label=f"Unfreezing span $e^{{+\\chi_{{\\mathrm{{freeze}}}}}}R_{{\\mathrm{{He}}}} = e^3 R_{{\\mathrm{{He}}}} = {lam_e3_a:.2f}$ Å")
    ax.axvline(p2_1["t_lambda_exp_k"], color="#8e44ad", ls=":", lw=1.5, label=f"Superfluid $\\lambda$-point $T_\\lambda = {p2_1['t_lambda_exp_k']:.3f}$ K")
    ax.invert_xaxis()
    ax.set_xlabel("Temperature $T$ [K] (Cooling rightward toward Absolute-Zero Floor)", fontsize=9.2)
    ax.set_ylabel(r"Wavelength / Cloud Span $\lambda$ [Å]", fontsize=9.2)
    ax.set_title("A. Exponential Cloud Widening Toward the Absolute-Zero Floor", fontsize=9.8, fontweight="bold")
    ax.grid(True, which="both", alpha=0.28)
    ax.legend(fontsize=7.3, loc="upper left")

    # Panel B: Room-Weaving Overlap & Friction Vanishing Below T_lambda
    ax = axes[0, 1]
    t_lin = np.linspace(0.05, 5.0, 300)
    lam_lin = (h_planck / np.sqrt(2.0 * np.pi * m_eff * k_b * t_lin)) * 1e10
    w_weave = np.exp(-np.pi * ((d_he_a / lam_lin) ** 2))
    rho_s_frac = np.where(t_lin < p2_1["t_lambda_exp_k"], 1.0 - (t_lin / p2_1["t_lambda_exp_k"]) ** 1.5, 0.0)
    friction_frac = 1.0 - rho_s_frac

    ax.plot(t_lin, w_weave, color="#2874a6", lw=2.2, ls="--", label=r"Inter-atomic wave overlap $\mathcal{W}_{\mathrm{weave}}(T) = \exp(-\pi d_{\mathrm{He}}^2/\lambda^2)$")
    ax.plot(t_lin, rho_s_frac, color="#1e8449", lw=2.6, label=r"Room-woven superfluid fraction $\rho_s/\rho$ ($\eta_{\mathrm{friction}} = 0$)")
    ax.plot(t_lin, friction_frac, color="#c0392b", lw=2.0, label=r"Normal viscous shear fraction $\rho_n/\rho$ ($Q_{\mathrm{shear}} > 0$)")
    ax.axvline(p2_1["t_lambda_dressed_k"], color="#8e44ad", ls=":", lw=1.5, label=f"NSC $3:1$ added-mass $T_\\lambda = {p2_1['t_lambda_dressed_k']:.3f}$ K")
    ax.set_xlim(5.0, 0.0)
    ax.set_ylim(-0.04, 1.06)
    ax.set_xlabel("Temperature $T$ [K] (Cooling rightward to $0$ K)", fontsize=9.2)
    ax.set_ylabel("Order Parameter / Fraction", fontsize=9.2)
    ax.set_title("B. Room-Weaving Zero-Friction Transition ($F_{\\mathrm{friction}} = -\\nabla Q_{\\mathrm{shear}} \\to 0$)", fontsize=9.8, fontweight="bold")
    ax.grid(True, alpha=0.28)
    ax.legend(fontsize=7.3, loc="center left")

    # Panel C: Why Helium Never Freezes at 1 atm vs. 25.07 atm Pressure-Chamber Threshold
    ax = axes[1, 0]
    p_atm_grid = np.linspace(0.0, 40.0, 250)
    # Net crystallization barrier Delta G_solid(P) = Q_ZPE,cell - eps_vdW - P * (1/3 gamma_core V_cell) in K
    delta_v_virial_m3 = (1.0 / 3.0) * ((8.0 * (math.sqrt(2.0) - 1.0)) / 3.0) * (p2_1["d_he_interatomic_m"] ** 3)
    delta_g_solid_k = (p2_1["q_zpe_cell_k"] - p2_1["eps_vdw_k"]) - (p_atm_grid * 101325.0 * delta_v_virial_m3) / k_b

    ax.plot(p_atm_grid, delta_g_solid_k, color="#1f618d", lw=2.5, label=r"$\Delta G_{\mathrm{solid}}(P) = Q_{\mathrm{ZPE,cell}} - \varepsilon_{\mathrm{vdW}} - P\Delta V_{\mathrm{virial}}$")
    ax.axhline(0.0, color="#222222", lw=1.2)
    ax.axvline(p2_1["p_solid_nsc_atm"], color="#c0392b", ls="--", lw=1.6, label=f"NSC solidification threshold $P_{{\\mathrm{{solid}}}} = {p2_1['p_solid_nsc_atm']:.2f}$ atm (exp $25.0$ atm)")
    ax.fill_between(p_atm_grid, 0, delta_g_solid_k, where=(delta_g_solid_k > 0), color="#d4efdf", alpha=0.55, label="Unfrozen superfluid wave ($Q_{\\mathrm{stretch}} > |\\Delta E_{\\mathrm{bind}}|$)")
    ax.fill_between(p_atm_grid, delta_g_solid_k, 0, where=(delta_g_solid_k <= 0), color="#fadbd8", alpha=0.55, label="Pressure-locked hcp crystal ($PV$ overcomes $Q_{\\mathrm{ZPE}}$)")
    ax.set_xlim(0.0, 40.0)
    ax.set_xlabel("Enclosing Chamber Pressure $P$ [atm]", fontsize=9.2)
    ax.set_ylabel(r"Lattice Freezing Barrier $\Delta G_{\mathrm{solid}} / k_B$ [K]", fontsize=9.2)
    ax.set_title("C. Why $^4\\mathrm{He}$ Never Freezes at $1$ atm ($Q_{\\mathrm{ZPE}}=14.01\\,\\mathrm{K} > \\varepsilon_{\\mathrm{vdW}}=10.90\\,\\mathrm{K}$)", fontsize=9.8, fontweight="bold")
    ax.grid(True, alpha=0.28)
    ax.legend(fontsize=7.3, loc="upper right")

    # Panel D: Nuclear Beta-Stability Valley Z*(A) and Two-Center Fission Threshold
    ax = axes[1, 1]
    a_vals = np.linspace(2, 260, 260)
    a_c = t5["a_coul_mev"]
    a_a = t5["a_asym_mev"]
    dm_np = 1.29333
    z_star_curve = (a_vals * (1.0 + (dm_np + a_c * (a_vals ** (-1.0 / 3.0))) / (4.0 * a_a))) / (
        2.0 + (a_c / (2.0 * a_a)) * (a_vals ** (2.0 / 3.0))
    )
    ax.plot(a_vals, a_vals / 2.0, color="#7f8c8d", ls=":", lw=1.4, label=r"Symmetric $Z = N = A/2$ line")
    ax.plot(a_vals, z_star_curve, color="#117864", lw=2.5, label=r"NSC balloon-in-balloon $\beta$-stability valley $Z^\star(A)$")
    valley_offsets = {
        "He-4": (4, -4.5),
        "C-12": (-2, 4.5),
        "O-16": (5, -3.5),
        "Fe-56": (-26, 3.8),
        "Ni-62": (5, -4.2),
        "Pb-208": (4, -6.0),
        "U-235": (-32, 4.2),
        "U-238": (4, -5.5),
        "Cf-252": (-28, 4.5),
    }
    for row in t5["sample_nuclei"]:
        ax.scatter([row["A"]], [row["Z"]], color="#b03a2e", s=38, zorder=5)
        dx, dy = valley_offsets.get(row["nucleus"], (3, -2.5))
        ax.text(row["A"] + dx, row["Z"] + dy, row["nucleus"], fontsize=7.4, fontweight="bold")
    ax.set_xlim(0, 270)
    ax.set_ylim(0, 125)
    ax.set_xlabel("Baryon Triad Count $A = Z + N$", fontsize=9.2)
    ax.set_ylabel("Equilibrium Proton Loop Count $Z$", fontsize=9.2)
    ax.set_title("D. Balloon-in-Balloon Beta-Stability Valley $Z^\\star(A)$ Across the Nuclide Chart", fontsize=9.8, fontweight="bold")
    ax.grid(True, alpha=0.28)
    ax.legend(fontsize=7.6, loc="upper left")

    plt.tight_layout(rect=[0, 0, 1, 0.955])
    fig.savefig(FIG_HELIUM_PATH, dpi=220)
    plt.close(fig)


def main() -> None:
    FIG_ATLAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    p2_1 = helium_absolute_zero_wave_particle_bridge()
    t1 = single_force_facet_dilution_bridge()
    t2 = strong_nuclear_triad_confinement()
    t3 = atomic_shell_and_em_impedance()
    t4 = weak_balloon_in_balloon_venting()
    t5 = nuclear_binding_and_fission_neck()
    t6 = unified_resolution_hierarchy_readout()

    build_helium_figure(p2_1, t5)

    fig, axes = plt.subplots(2, 3, figsize=(16.5, 10.2), dpi=220)
    fig.patch.set_facecolor("#ffffff")
    fig.suptitle(
        "Nested-Space Cosmology II: Force at Resolutions — One Thermodynamic Pressure Gradient Across [Planck Ceiling, Absolute-Zero Floor]",
        fontsize=12.5,
        fontweight="bold",
        y=0.98,
    )

    # Panel A: Theorem 1 — 1/F_star Facet Dilution Bridge
    ax = axes[0, 0]
    log_f = np.linspace(0, 38.2275, 200)
    log_coupling = -log_f
    ax.plot(log_f, log_coupling, color="#1b4f72", lw=2.5, label=r"$\alpha(F) = 1/F$ facet dilution")
    ax.scatter([0.0], [0.0], color="#c0392b", s=70, zorder=5, label=r"Nuclear $(1,1,1)$ core ($F=1, \alpha_S=1$)")
    ax.scatter(
        [math.log10(t3["alpha_geom_inv"])],
        [-math.log10(t3["alpha_geom_inv"])],
        color="#d35400",
        s=70,
        zorder=5,
        label=r"Atomic 1D loop ($\alpha_{\mathrm{EM}}^{-1}=137.036$)",
    )
    ax.scatter(
        [math.log10(1.0 / t4["barrier_dressed_conductance"])],
        [math.log10(t4["barrier_dressed_conductance"])],
        color="#8e44ad",
        s=70,
        zorder=5,
        label=r"Two-valve neck venting ($\gamma_{\mathrm{core}}^5 e^{-12}=1.01\times 10^{-5}$)",
    )
    ax.scatter(
        [math.log10(t1["f_star_facet_capacity"])],
        [math.log10(t1["alpha_grav_dimensionless"])],
        color="#27ae60",
        s=80,
        zorder=5,
        label=r"Planck facet ceiling ($F_\star=1.688\times 10^{38}, \alpha_G=1/F_\star$)",
    )
    ax.set_xlabel(r"Effective Facet / Impedance Count $\log_{10}(F_{\mathrm{eff}})$", fontsize=9.5)
    ax.set_ylabel(r"Log Effective Strength $\log_{10}(\alpha_{\mathrm{eff}})$", fontsize=9.5)
    ax.set_title("A. Theorem 1: Gravity = Nuclear Force / $F_\\star$ ($10^{38}$ Bridge)", fontsize=10, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7.5, loc="lower left")

    # Panel B: Theorem 2 — Variational Two-Center (1,1,1) Nuclear Potential
    ax = axes[0, 1]
    d_vals = np.linspace(0.0, 5.5, 350)
    u_vals = np.minimum(d_vals / 2.0, 1.0)
    f_ov = ((1.0 - u_vals) ** 2) * (1.0 + 0.5 * u_vals)
    v_short = t2["hard_core_barrier_delta_e"] * f_ov - 1.0 * (1.0 - f_ov)
    v_long = (-2.0 / np.maximum(d_vals, 2.0)) + t2["sigma_spaghetti_normalized"] * np.maximum(d_vals - 2.0, 0.0)
    v_tot = np.where(d_vals <= 2.0, v_short, v_long)
    ax.plot(d_vals, v_tot, color="#922b21", lw=2.5, label=r"Variational $\Delta E_{\mathrm{NSC}}(d)$ between $(1,1,1)$ triads")
    ax.axhline(0.0, color="#555555", ls="--", lw=1.0)
    ax.axhline(t2["hard_core_barrier_delta_e"], color="#c0392b", ls=":", lw=1.2, label=r"$(2,2,2)$ hard core $+8(\sqrt{2}-1)=+3.314$")
    ax.axvline(2.0, color="#2e86c1", ls=":", lw=1.2, label=r"Equilibrium contact $d=2R^\star$ ($\Delta E=-1.0$)")
    ax.set_ylim(-1.5, 3.8)
    ax.set_xlabel(r"Separation / Stretch Distance $d / R^\star$", fontsize=9.5)
    ax.set_ylabel(r"Interaction Cost $\Delta E = E(d) - 2E^\star(1,1,1)$", fontsize=9.5)
    ax.set_title("B. Theorem 2: Hard Core, Shared-Flow Binding & String Tension", fontsize=10, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7.5, loc="upper right")

    # Panel C: Theorem 3 — Atomic Bohr Shells r_n = n^2 a_0 and Capacities 2n^2
    ax = axes[0, 2]
    n_vals = [s["n"] for s in t3["shells"]]
    caps = [s["shell_capacity_2n2"] for s in t3["shells"]]
    radii = [s["r_n_over_a0"] for s in t3["shells"]]
    bars = ax.bar(n_vals, caps, color="#2874a6", alpha=0.82, width=0.55, label=r"Shell capacity $N_{\mathrm{shell}}(n)=2n^2$")
    for bar, cap, r_val in zip(bars, caps, radii):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            cap + 1.5,
            f"{cap}\n({r_val}$a_0$)",
            ha="center",
            va="bottom",
            fontsize=7.5,
            fontweight="bold",
        )
    ax.set_ylim(0, 86)
    ax.set_xticks(n_vals)
    ax.set_xlabel(r"Principal Loop Winding Integer $n\in\mathbb{Z}_{\geq 1}$", fontsize=9.5)
    ax.set_ylabel(r"Allowed States $2\sum_{l=0}^{n-1}(2l+1) = 2n^2$", fontsize=9.5)
    ax.set_title(r"C. Theorem 3: Atomic Shells & $\alpha_{\mathrm{geom}}^{-1}=4\pi^3+\pi^2+\pi=137.036$", fontsize=10, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")

    # Panel D: Theorem 4 — Balloon-in-Balloon Pressure Stabilization vs. Free Venting
    ax = axes[1, 0]
    coord_numbers = np.arange(0, 7)
    delta_g_vent = -t4["q_beta_free_mev"] + coord_numbers * t4["deuteron_binding_mev"]
    colors = ["#c0392b" if val < 0 else "#1e8449" for val in delta_g_vent]
    ax.bar(coord_numbers, delta_g_vent, color=colors, width=0.55, alpha=0.85)
    ax.axhline(0.0, color="#222222", lw=1.3)
    ax.text(0.15, delta_g_vent[0] - 0.25, "Unconfined\n(Vents: $\\beta^-$)", ha="center", va="top", fontsize=7.5, color="#922b21", fontweight="bold")
    ax.text(2.4, 8.8, "Balloon-in-Balloon Confined\n($\\Delta P_{\\mathrm{neighbors}}$ locks neutron)", ha="center", va="center", fontsize=8.3, color="#1e8449", fontweight="bold")
    ax.set_ylim(-2.6, 14.2)
    ax.set_xlabel(r"Neighboring $(1,1,1)$ Coordination Count $N_{\mathrm{coord}}$", fontsize=9.5)
    ax.set_ylabel(r"Venting Cost $\Delta G_{\mathrm{vent}}(N_{\mathrm{coord}})$ [MeV]", fontsize=9.5)
    ax.set_title("D. Theorem 4: Weak Decay as Balloon-in-Balloon Pressure Venting", fontsize=10, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)

    # Panel E: Theorem 5 — Multi-Nucleon Packing Curve B/A and Fission Threshold
    ax = axes[1, 1]
    a_grid = np.linspace(4, 260, 250)
    z_grid = a_grid / (2.0 + 0.0155 * (a_grid ** (2.0 / 3.0)))
    b_per_a_curve = (
        t5["a_vol_mev"]
        - t5["a_surf_mev"] / (a_grid ** (1.0 / 3.0))
        - t5["a_coul_mev"] * z_grid * (z_grid - 1.0) / (a_grid ** (4.0 / 3.0))
        - t5["a_asym_mev"] * ((a_grid - 2.0 * z_grid) ** 2) / (a_grid ** 2)
        + t5["a_pair_mev"] / (a_grid ** 1.5)
    )
    ax.plot(a_grid, b_per_a_curve, color="#1f618d", lw=2.3, label=r"NSC $(1,1,1)$ packing curve $B(A,Z)/A$")
    label_offsets = {
        "He-4": (5, -0.08),
        "C-12": (6, -0.12),
        "O-16": (6, -0.05),
        "Fe-56": (-26, 0.14),
        "Ni-62": (6, 0.12),
        "Pb-208": (-36, -0.15),
        "U-235": (-34, -0.22),
        "U-238": (5, 0.08),
        "Cf-252": (-18, -0.26),
    }
    for row in t5["sample_nuclei"]:
        ax.scatter([row["A"]], [row["B_per_A_mev"]], color="#b03a2e", s=38, zorder=5)
        dx, dy = label_offsets.get(row["nucleus"], (4, -0.12))
        ax.text(row["A"] + dx, row["B_per_A_mev"] + dy, row["nucleus"], fontsize=7.5, fontweight="bold")
    ax.set_xlim(0, 272)
    ax.set_ylim(5.5, 9.3)
    ax.set_xlabel(r"Baryon Triad Count $A$", fontsize=9.5)
    ax.set_ylabel(r"Binding Energy per Nucleon $B/A$ [MeV]", fontsize=9.5)
    ax.set_title(r"E. Theorem 5: Nuclear Packing & Fission Neck ($p_+=\varphi^{2/3}+\varphi^{-2/3}$)", fontsize=10, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")

    # Panel F: Theorem 6 — Unified 8-Tier Resolution Spectrum [ell_P, 2 R_H]
    ax = axes[1, 2]
    tiers = t6["resolution_tiers"]
    log_scales = [math.log10(row["scale_m"]) for row in tiers]
    tier_nums = [row["tier"] for row in tiers]
    labels = [
        "1. Planck Pen Tip ($\\ell_P$)",
        "2. Two-Valve Neck ($e^{-3}\\lambda_n$)",
        "3. Baryon $(1,1,1)$ Core ($\\lambda_n$)",
        "4. Atomic 1D Loop ($a_0$)",
        "5. $^4\\mathrm{He}$ Floor Weave ($\\lambda_{\\mathrm{dB}}$)",
        "6. Neutron Star ($R_{\\mathrm{NS}}$)",
        "7. Galactic Halo ($10\\ \\mathrm{kpc}$)",
        "8. Room Floor ($2R_H$)",
    ]
    ax.plot(log_scales, tier_nums, "o-", color="#117864", lw=2.4, markersize=7.5)
    for x_val, y_val, lbl in zip(log_scales, tier_nums, labels):
        offset_x = 1.5 if y_val < 7 else -26.5
        ax.text(x_val + offset_x, y_val - 0.12, lbl, fontsize=7.5, fontweight="bold")
    ax.set_xlim(-38, 30)
    ax.set_ylim(0.4, 8.6)
    ax.set_xlabel(r"Log Wavelength / Resolution Scale $\log_{10}(\lambda / \mathrm{m})$", fontsize=9.5)
    ax.set_ylabel("Resolution Tier in Room Band $[\\ell_P, 2R_H]$", fontsize=9.5)
    ax.set_title("F. Theorem 6: One Force Across 8 Tiers & 141 e-Folds ($47\\times\\chi_{\\mathrm{freeze}}$)", fontsize=10, fontweight="bold")
    ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.955])
    fig.savefig(FIG_ATLAS_PATH, dpi=220)
    plt.close(fig)

    JSON_PATH.write_text(json.dumps(t6, indent=2), encoding="utf-8", newline="\n")
    print(f"Wrote {FIG_ATLAS_PATH}")
    print(f"Wrote {FIG_HELIUM_PATH}")
    print(f"Wrote {JSON_PATH}")


if __name__ == "__main__":
    main()
