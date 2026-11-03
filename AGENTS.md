# Nested-Space Cosmology II — AI working guide and project index

This repository (`nested-space-cosmology-2`) is the home of **Paper II**:
**Nested-Space Cosmology: The Geometry of a Universe II — Force at Resolutions**.

It builds directly upon **Paper I** (`../nested-space-cosmology`, Foundation
Edition `v0.27.0`, archived at [Zenodo `10.5281/zenodo.23890258`](https://zenodo.org/records/23890258)).
Paper I remains locked around the cosmological hourglass geometry, the five
axioms (`A0–A4`), the seven parameter-free cosmological theorems, and the
stellar Planck-facet collapse threshold (`Proposition 9.2b`).

## Core Premise of Paper II: Force at Resolutions

In Paper I, we showed that every nested room sits between a floor wavelength
(the Absolute-Zero horizon $\lambda_{\max} = 2R$) and a ceiling resolution
cutoff (the Planck length $\ell_P = \sqrt{\hbar G/c^3}$). A sphere is a
finite-facet geometric creation of that frequency band, and a star collapses
into a black hole when its surface facets hit the room's Planck ceiling
($F_{\star} = (\lambda_{n}/\ell_{P})^2 = 1.688492\times 10^{38}$,
$\sqrt{R_{\star}\ell_{P}} = \lambda_{n}$).

In **Paper II**, the exact same geometric law is carried down to atomic and
subatomic resolutions:
- **There are no four separate fundamental forces ("strong", "weak", "electromagnetic", "gravitational").**
- **There is only ONE force — The Force:** the thermodynamic pressure and
  phase-flow gradient of energy across the room's resolution spectrum,
  $$\mathbf F = -\nabla E(\lambda_1,\lambda_2,\lambda_3;\chi),\qquad E = Q_{\mathrm{stretch}} + PV = \sum_{i=1}^3\frac{m_i}{\lambda_i} + PV_0\lambda_1\lambda_2\lambda_3.$$
- What standard textbook physics labels as four distinct forces (plus dark
  matter and dark energy) are simply **the same underlying pressure gradient
  observed at different geometric resolutions** of the room's band $[\ell_P, 2R]$:
  1. **Nuclear Scale ($\lambda_n$, "Strong Force"):** Undivided 1D generator
     stretch and $-2m_0/d$ shared-flow attraction inside the crystallized
     `(1,1,1)` baryon triad ($\chi_{\mathrm{freeze}} = 3$), bounded at short
     range by the `(2,2,2)` merger barrier $\Delta E_{\mathrm{core}} = 8(\sqrt{2}-1) \approx +3.3137$
     and at long range by the spaghettification string tension
     $\sigma_{\mathrm{string}} = PV_{0} e^{-2\chi}$ above $\chi_{\mathrm{spaghetti}} = \frac{1}{2}\ln 2$.
  2. **Macroscopic Scale ($r \ge R_\star$, "Gravity"):** The exact same
     nuclear pressure force diluted across all $F_{\star} = (\lambda_{n}/\ell_{P})^2 = 1.688492\times 10^{38}$
     Planck facets of the sphere:
     $$\alpha_G \equiv \frac{G m_n^2}{\hbar c} = \frac{1}{F_\star} = \left(\frac{\ell_P}{\lambda_n}\right)^2 = 5.922444\times 10^{-39} \quad\Longleftrightarrow\quad F_{\mathrm{grav}} = \frac{F_{\mathrm{nuclear}}}{F_\star}.$$
  3. **Sub-Nuclear Venting Scale ("Weak Force"):** Balloon-in-balloon pressure
     equilibration. Inside a multi-nucleon nucleus, neighboring `(1,1,1)`
     bubbles supply external confining pressure $\Delta P_{\mathrm{neighbors}}$
     that stabilizes the neutron. Removed into empty space, an isolated neutron
     lacks external counter-pressure and vents its excess 1D boundary winding
     across the neck barrier until the sphere reaches proton equilibrium.
  4. **Atomic Shell Scale ($a_{0} = \lambda_{e}/\alpha_{\mathrm{EM}}$, "Electromagnetism"):**
     Coupling between the 3D `(1,1,1)` baryonic core ($E^\star = 4$) and 1D
     closed azimuthal phase loops ($z(1)=z(0)\Rightarrow n\in\mathbb Z$) across
     the spherical-toroidal impedance $(4\pi^3 + \pi^2 + \pi)^{-1} \approx 1/137.036$,
     producing quantized Bohr shells $r_{n}^\star = n^2 a_{0}$ and periodic-table
     shell capacities $2n^2 = 2, 8, 18, 32, 50$ from $S^2$ spherical harmonics
     and **Axiom A1** helical handedness $\pm\omega^\star$.

## Mathematics, Calculation, and Epistemic Discipline

- Follow the same strict epistemic hygiene established in Paper I: distinguish
  exact algebraic identities derived from `A0–A4` (such as $\alpha_{G} = 1/F_{\star}$,
  $\Delta E_{\mathrm{core}} = 8(\sqrt{2}-1)$, $r_{n}^\star = n^2 a_{0}$, $N_{\mathrm{shell}} = 2n^2$,
  and the two-center nuclear fission neck) from geometric impedance evaluations
  and empirical comparisons.
- Keep all GitHub Markdown files 100% free of CommonMark/MathJax collisions:
  - Never use the disallowed `operatorname` macro (use `\mathrm{...}`).
  - Never use `*`, `%`, or `\,` inside `$ ... $` or `$$ ... $$` (use `^\star`/`_\star`, put `%` outside `$`, and use spaces).
  - Never place `_` immediately after punctuation (`}_`, `|_`, `)_`, `]_`, `'_`) inside math blocks.

## Project Owners

| Need | Owner |
| --- | --- |
| Overview and Manifesto | [README.md](README.md), [THEORY.md](THEORY.md) |
| Paper II Manuscript & PDF | [paper/nested-space-cosmology-2.md](paper/nested-space-cosmology-2.md), [paper/nested-space-cosmology-2.pdf](paper/nested-space-cosmology-2.pdf) |
| Core Calculation Engine | [src/nsc_force_resolutions/force_at_resolutions.py](src/nsc_force_resolutions/force_at_resolutions.py) |
| Unit Tests | [tests/test_force_at_resolutions.py](tests/test_force_at_resolutions.py) |
| Atlas Figure & Summary Builder | [scripts/plot_force_at_resolutions.py](scripts/plot_force_at_resolutions.py), [scripts/build_paper_2.py](scripts/build_paper_2.py) |
| Paper I Context (`v0.27.0`) | `../nested-space-cosmology/paper/nested-space-cosmology.md`, [Zenodo `10.5281/zenodo.23890258`](https://zenodo.org/records/23890258) |

## Working Environment

Use the isolated scientific Python runtime from `../nested-space-cosmology/.venv/science-runtime/python.exe` (via `python scripts/run_python.py`). Never alter Douglas's global Python 3.12 installation.
