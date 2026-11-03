#!/usr/bin/env python3
"""Build paper/nested-space-cosmology-2.pdf from paper/nested-space-cosmology-2.md."""

from __future__ import annotations

import hashlib
import re
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "paper" / "nested-space-cosmology-2.md"
PDF_PATH = ROOT / "paper" / "nested-space-cosmology-2.pdf"


def latex_to_readable(s: str) -> str:
    """Convert inline/display LaTeX tokens into clean Unicode for wrapped text."""
    rep = {
        r"\mathbf F": "F",
        r"\mathbf x": "x",
        r"\mathbf e_z": "e_z",
        r"\nabla": "∇",
        r"\lambda_{\max}": "λ_max",
        r"\lambda_{\min}": "λ_min",
        r"\lambda_n": "λ_n",
        r"\lambda_e": "λ_e",
        r"\lambda_1": "λ_1",
        r"\lambda_2": "λ_2",
        r"\lambda_3": "λ_3",
        r"\lambda_\perp": "λ_⊥",
        r"\lambda_{\mathrm{crit}}": "λ_crit",
        r"\ell_P": "l_P",
        r"\hbar": "ℏ",
        r"\times": "×",
        r"\cdot": "·",
        r"\ge": "≥",
        r"\le": "≤",
        r"\approx": "≈",
        r"\equiv": "≡",
        r"\propto": "∝",
        r"\infty": "∞",
        r"\Rightarrow": "⇒",
        r"\Longleftrightarrow": "⟺",
        r"\to": "→",
        r"\pm": "±",
        r"\mp": "∓",
        r"\odot": "⊙",
        r"\star": "⋆",
        r"\chi_{\mathrm{freeze}}": "χ_freeze",
        r"\chi_{\mathrm{spaghetti}}": "χ_spaghetti",
        r"\chi": "χ",
        r"\theta^\star": "θ⋆",
        r"\theta": "θ",
        r"\omega^\star": "ω⋆",
        r"\omega": "ω",
        r"\varphi": "φ",
        r"\phi": "ϕ",
        r"\pi": "π",
        r"\alpha_G": "α_G",
        r"\alpha_S": "α_S",
        r"\alpha_W": "α_W",
        r"\alpha_{\mathrm{EM}}": "α_EM",
        r"\alpha_{\mathrm{geom}}": "α_geom",
        r"\gamma_{\mathrm{core}}": "γ_core",
        r"\sigma_{\mathrm{eff}}": "σ_eff",
        r"\sigma_{\mathrm{phys}}": "σ_phys",
        r"\Delta": "Δ",
        r"\Omega_{\mathrm{DM}}": "Ω_DM",
        r"\Omega_{\mathrm{DE}}": "Ω_DE",
        r"\rho_{\mathrm{DE}}": "ρ_DE",
        r"\tau_n": "τ_n",
        r"\tau_{\mathrm{nuc}}": "τ_nuc",
        r"\tau_{\mathrm{vent}}": "τ_vent",
        r"\tau": "τ",
        r"\lambda": "λ",
        r"\ell": "l",
        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\sigma": "σ",
        r"\rho": "ρ",
        r"\Omega": "Ω",
        r"\Phi": "Φ",
        r"\perp": "⊥",
        r"\max": "max",
        r"\min": "min",
        r"\sum": "∑",
        r"\mathcal N_{1\mathrm{D}}": "N_1D",
        r"\mathcal R": "R",
        r"\mathcal B": "B",
        r"\mathbb Z_{\ge 0}^3": "Z_≥0^3",
        r"\mathbb Z_{\ge 1}": "Z_≥1",
        r"\mathbb Z": "Z",
        r"\boxed": "",
        r"\left": "",
        r"\right": "",
        r"\quad": "  ",
        r"\qquad": "    ",
        r"\ ": " ",
    }
    out = re.sub(r"_\{([A-Za-z0-9]|\\[A-Za-z]+)\}", r"_\1", s)
    for k, v in rep.items():
        out = out.replace(k, v)
    out = re.sub(r"\\mathrm\{([^}]+)\}", r"\1", out)
    out = re.sub(r"\\text\{([^}]+)\}", r"\1", out)
    out = re.sub(r"\\sqrt\{([^}]+)\}", r"√(\1)", out)
    out = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1)/(\2)", out)
    out = re.sub(r"_\{([^}]+)\}", r"_\1", out)
    out = re.sub(r"\^\{([^}]+)\}", r"^\1", out)
    out = out.replace("$", "")
    return out


def build_pdf() -> None:
    raw = MD_PATH.read_text(encoding="utf-8").replace("\r\n", "\n")
    lines = raw.splitlines()

    blocks: list[tuple[str, str]] = []
    in_math = False
    math_buf: list[str] = []

    for line in lines:
        s = line.strip()
        if s == "$$":
            if in_math:
                blocks.append(("math", " ".join(math_buf)))
                math_buf = []
                in_math = False
            else:
                in_math = True
            continue
        if in_math:
            math_buf.append(s)
            continue
        if not s or s == "---":
            blocks.append(("spacer", ""))
        elif s.startswith("# "):
            blocks.append(("h1", s[2:]))
        elif s.startswith("## "):
            blocks.append(("h2", s[3:]))
        elif s.startswith("!["):
            m = re.search(r"\(([^)]+)\)", s)
            if m:
                blocks.append(("image", m.group(1)))
        elif s.startswith("|"):
            blocks.append(("table", s))
        else:
            blocks.append(("para", s))

    page_w, page_h = 8.27, 11.69  # A4 inches
    top_y, bottom_y = 0.93, 0.06

    with PdfPages(PDF_PATH) as pdf:
        fig = plt.figure(figsize=(page_w, page_h))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        y = top_y
        page_num = 1

        def new_page() -> None:
            nonlocal fig, ax, y, page_num
            ax.text(
                0.5,
                0.028,
                f"Nested-Space Cosmology II: Force at Resolutions (`v0.1.0`) — Page {page_num}",
                ha="center",
                va="bottom",
                fontsize=8,
                color="#555555",
            )
            pdf.savefig(fig)
            plt.close(fig)
            page_num += 1
            fig = plt.figure(figsize=(page_w, page_h))
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis("off")
            y = top_y

        for kind, content in blocks:
            if kind == "spacer":
                y -= 0.010
                if y < bottom_y:
                    new_page()
            elif kind == "h1":
                if y < bottom_y + 0.08:
                    new_page()
                ax.text(0.07, y, latex_to_readable(content), fontsize=15.5, fontweight="bold", color="#112233", va="top")
                y -= 0.036
            elif kind == "h2":
                if y < bottom_y + 0.06:
                    new_page()
                y -= 0.008
                ax.text(0.07, y, latex_to_readable(content), fontsize=11.5, fontweight="bold", color="#1b4f72", va="top")
                y -= 0.028
            elif kind == "math":
                txt = latex_to_readable(content)
                wrapped = textwrap.wrap(txt, width=92) or [txt]
                needed = 0.018 * len(wrapped) + 0.012
                if y - needed < bottom_y:
                    new_page()
                for wline in wrapped:
                    ax.text(0.10, y, wline, fontsize=9.2, family="monospace", color="#111111", va="top")
                    y -= 0.017
                y -= 0.006
            elif kind == "table":
                if re.match(r"^\|\s*[-:]+\s*\|", content):
                    continue
                txt = latex_to_readable(content.replace("**", ""))
                wrapped = textwrap.wrap(txt, width=106) or [txt]
                needed = 0.015 * len(wrapped) + 0.004
                if y - needed < bottom_y:
                    new_page()
                for wline in wrapped:
                    ax.text(0.07, y, wline, fontsize=7.6, family="monospace", color="#222222", va="top")
                    y -= 0.0145
                y -= 0.002
            elif kind == "image":
                img_file = (MD_PATH.parent / content).resolve()
                if img_file.exists():
                    img_h = 0.42
                    if y - img_h < bottom_y:
                        new_page()
                    img_ax = fig.add_axes([0.06, y - img_h, 0.88, img_h - 0.02])
                    img_ax.imshow(mpimg.imread(img_file))
                    img_ax.axis("off")
                    y -= img_h + 0.01
            else:
                clean = latex_to_readable(content.replace("**", "").replace("*", ""))
                wrapped = textwrap.wrap(clean, width=98) or [clean]
                needed = 0.0165 * len(wrapped) + 0.004
                if y - needed < bottom_y:
                    new_page()
                is_bold = content.strip().startswith("**Theorem") or content.strip().startswith("**Epistemic")
                for wline in wrapped:
                    ax.text(
                        0.07,
                        y,
                        wline,
                        fontsize=9.1,
                        fontweight="bold" if is_bold else "normal",
                        color="#111111",
                        va="top",
                    )
                    y -= 0.0162
                y -= 0.003

        ax.text(
            0.5,
            0.028,
            f"Nested-Space Cosmology II: Force at Resolutions (`v0.1.0`) — Page {page_num}",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#555555",
        )
        pdf.savefig(fig)
        plt.close(fig)

    digest = hashlib.sha256(PDF_PATH.read_bytes()).hexdigest()
    print(f"Wrote {PDF_PATH}")
    print(f"pages: {page_num}")
    print(f"bytes: {PDF_PATH.stat().st_size}")
    print(f"sha256: {digest}")


if __name__ == "__main__":
    build_pdf()
