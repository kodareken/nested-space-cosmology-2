#!/usr/bin/env python3
"""Generate the 6-panel Force at Resolutions atlas figure and summary JSON."""

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
    nuclear_binding_and_fission_neck,
    single_force_facet_dilution_bridge,
    strong_nuclear_triad_confinement,
    unified_resolution_hierarchy_readout,
    weak_balloon_in_balloon_venting,
)

ROOT = Path(__file__).resolve().parents[1]
FIG_PATH = ROOT / "paper" / "figures" / "nsc-force-at-resolutions-atlas.png"
JSON_PATH = ROOT / "results" / "nsc-force-at-resolutions-v1.json"


def main() -> None:
    FIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    t1 = single_force_facet_dilution_bridge()
    t2 = strong_nuclear_triad_confinement()
    t3 = atomic_shell_and_em_impedance()
    t4 = weak_balloon_in_balloon_venting()
    t5 = nuclear_binding_and_fission_neck()
    t6 = unified_resolution_hierarchy_readout()

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

    # Panel B: Theorem 2 — (1,1,1) Nuclear Potential (Hard Core + Shared Flow + Linear String)
    ax = axes[0, 1]
    d_vals = np.linspace(0.45, 5.0, 300)
    # Effective interaction potential relative to 2 E*(1,1,1) = 8.0:
    # Hard core +3.3137 * exp(-(d/1.0)^2) - 2/(d) + 0.5*(d - 2.0)*H(d-2.0)
    v_core = t2["hard_core_barrier_delta_e"] * np.exp(-((d_vals / 0.95) ** 4))
    v_flow = -2.0 / np.maximum(d_vals, 0.8)
    v_string = np.where(d_vals > 2.0, t2["sigma_spaghetti_normalized"] * (d_vals - 2.0), 0.0)
    v_tot = v_core + v_flow + v_string
    ax.plot(d_vals, v_tot, color="#922b21", lw=2.5, label=r"Total $\Delta E(d)$ between $(1,1,1)$ triads")
    ax.axhline(0.0, color="#555555", ls="--", lw=1.0)
    ax.axhline(t2["hard_core_barrier_delta_e"], color="#c0392b", ls=":", lw=1.2, label=r"$(2,2,2)$ hard core $+8(\sqrt{2}-1)=+3.314$")
    ax.axvline(2.0, color="#2e86c1", ls=":", lw=1.2, label=r"Equilibrium contact $d=2R^\star$ ($\Delta E=-1.0$)")
    ax.set_ylim(-1.6, 4.2)
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
    # Net free-energy change upon venting a neutron into p + e + nu:
    # Delta G(N_coord) = -Q_beta + N_coord * (deuteron_binding_mev)
    delta_g_vent = -t4["q_beta_free_mev"] + coord_numbers * t4["deuteron_binding_mev"]
    colors = ["#c0392b" if val < 0 else "#1e8449" for val in delta_g_vent]
    ax.bar(coord_numbers, delta_g_vent, color=colors, width=0.55, alpha=0.85)
    ax.axhline(0.0, color="#222222", lw=1.3)
    ax.text(0.15, delta_g_vent[0] - 0.25, "Unconfined\n(Vents: $\\beta^-$)", ha="center", va="top", fontsize=7.5, color="#922b21", fontweight="bold")
    ax.text(2.4, 8.8, "Balloon-in-Balloon Confined\n($\\Delta P_{\\mathrm{neighbors}}$ locks neutron)", ha="center", va="center", fontsize=8.3, color="#1e8449", fontweight="bold")
    ax.set_ylim(-2.6, 14.2)
    ax.set_xlabel(r"Neighboring $(1,1,1)$ Coordination Count $N_{\mathrm{coord}}$", fontsize=9.5)
    ax.set_ylabel(r"Venting Cost $\Delta E_{\mathrm{vent}}(N_{\mathrm{coord}})$ [MeV]", fontsize=9.5)
    ax.set_title("D. Theorem 4: Weak Decay as Balloon-in-Balloon Pressure Venting", fontsize=10, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)

    # Panel E: Theorem 5 — Multi-Nucleon Packing Curve B/A and Fission Threshold
    ax = axes[1, 1]
    a_grid = np.linspace(4, 260, 250)
    z_grid = a_grid / (2.0 + 0.015 * (a_grid ** (2.0 / 3.0)))
    b_per_a_curve = (
        t5["a_vol_mev"]
        - t5["a_surf_mev"] / (a_grid ** (1.0 / 3.0))
        - t5["a_coul_mev"] * z_grid * (z_grid - 1.0) / (a_grid ** (4.0 / 3.0))
        - t5["a_asym_mev"] * ((a_grid - 2.0 * z_grid) ** 2) / (a_grid ** 2)
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

    # Panel F: Theorem 6 — Unified 7-Tier Resolution Spectrum [ell_P, 2 R_H]
    ax = axes[1, 2]
    tiers = t6["resolution_tiers"]
    log_scales = [math.log10(row["scale_m"]) for row in tiers]
    tier_nums = [row["tier"] for row in tiers]
    labels = [
        "1. Planck Pen Tip ($\\ell_P$)",
        "2. Two-Valve Neck ($e^{-3}\\lambda_n$)",
        "3. Baryon $(1,1,1)$ Core ($\\lambda_n$)",
        "4. Atomic 1D Loop ($a_0$)",
        "5. Neutron Star ($R_{\\mathrm{NS}}$)",
        "6. Galactic Halo ($10\\ \\mathrm{kpc}$)",
        "7. Room Floor ($2R_H$)",
    ]
    ax.plot(log_scales, tier_nums, "o-", color="#117864", lw=2.4, markersize=8)
    for x_val, y_val, lbl in zip(log_scales, tier_nums, labels):
        offset_x = 1.5 if y_val < 6 else -26.0
        ax.text(x_val + offset_x, y_val - 0.12, lbl, fontsize=7.8, fontweight="bold")
    ax.set_xlim(-38, 30)
    ax.set_ylim(0.4, 7.6)
    ax.set_xlabel(r"Log Wavelength / Resolution Scale $\log_{10}(\lambda / \mathrm{m})$", fontsize=9.5)
    ax.set_ylabel("Resolution Tier in Room Band $[\\ell_P, 2R_H]$", fontsize=9.5)
    ax.set_title("F. Theorem 6: One Force Across 141 e-Folds ($47\\times\\chi_{\\mathrm{freeze}}$)", fontsize=10, fontweight="bold")
    ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.955])
    fig.savefig(FIG_PATH, dpi=220)
    plt.close(fig)

    JSON_PATH.write_text(json.dumps(t6, indent=2), encoding="utf-8", newline="\n")
    print(f"Wrote {FIG_PATH}")
    print(f"Wrote {JSON_PATH}")


if __name__ == "__main__":
    main()
