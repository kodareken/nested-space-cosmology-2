# Nested-Space Cosmology II — Force at Resolutions (`THEORY.md`)

**Foundation Edition II (`v0.1.0`)** · [Paper II Manuscript](paper/nested-space-cosmology-2.md) · [Paper II PDF](paper/nested-space-cosmology-2.pdf) · [Paper I (`v0.27.0`, Zenodo `10.5281/zenodo.23890258`)](https://zenodo.org/records/23890258)

## 1. From Cosmological Hourglass to Subatomic Resolutions

In **Nested-Space Cosmology I (`v0.27.0`)**, the five geometric axioms (`A0–A4`)
established that every nested room $k$ is bounded between its **Absolute-Zero
floor** ($\lambda_{\max,k} = 2R_{k}$) and its **Planck-length ceiling**
($\lambda_{\min,k} = \ell_{P,k} = \sqrt{\hbar G/c^3}$). Because a sphere inside
that room has a finite number of Planck facets ($F < \infty$, with excess
isoperimetric ratio $A_{F}^3/(36\pi V_{F}^2) = 1 + \pi\sqrt{3}/F + O(F^{-2}) > 1$),
a star compressed by enclosing pressure exhausts its surface facet capacity at
$$
\mathcal N_{1\mathrm{D}} = \frac{\lambda_n}{\ell_P} = \frac{M_P}{m_n} = 1.299420\times 10^{19},\qquad
F_\star = \mathcal N_{1\mathrm{D}}^2 = \left(\frac{\lambda_n}{\ell_P}\right)^2 = 1.688492\times 10^{38},
$$
where $\sqrt{R_{\star}\ell_{P}} = \lambda_{n}$, $R_{\mathrm{NS}} = 4\lambda_{n}^2/\ell_{P} = 10.916\ \mathrm{km}$,
and $M_{\mathrm{TOV}} \in [2.0414, 2.1454]\ M_{\odot}$ (**Proposition 9.2b** of Paper I).

In **Paper II**, we prove that this exact same finite-facet resolution geometry
governs **atomic and subatomic physics**. Standard physics invents four separate
fundamental forces — the strong nuclear force, the weak nuclear force,
electromagnetism, and gravity — plus dark matter and dark energy, because it
treats space as a featureless infinite continuum ($F \to \infty$, $\ell_P \to 0$)
and therefore must assign a separate coupling constant and exchange particle to
every resolution tier.

Under **Axiom A0 (Path of Least Resistance)**, there is only **one energy
functional** and therefore only **one force** in nature:
$$
\mathbf F = -\nabla E(\lambda_1,\lambda_2,\lambda_3;\chi),\qquad
E = Q_{\mathrm{stretch}} + PV = \sum_{i=1}^3\frac{m_i}{\lambda_i} + PV_0\lambda_1\lambda_2\lambda_3.
$$

## 2. The Six Core Theorems of Paper II

1. **Theorem 1 — The $1/F_\star$ Facet Dilution Bridge Between Nuclear Pressure and Gravity (`single_force_facet_dilution_bridge`):**
   At the baryon Compton wavelength $\lambda_{n} = \hbar/(m_{n} c)$, the undivided
   1D generator stretch force is $F_{\mathrm{nuclear}}(\lambda_{n}) = \hbar c/\lambda_{n}^2$.
   When transmitted outward across the room, the force is distributed over all
   $F_{\star} = (\lambda_{n}/\ell_{P})^2 = 1.688492\times 10^{38}$ Planck facets of
   the sphere:
   $$
   F_{\mathrm{grav}}(r) = \frac{F_{\mathrm{nuclear}}(r)}{F_\star} = \frac{\hbar c / r^2}{(\lambda_n/\ell_P)^2} = \frac{G m_n^2}{r^2},\qquad
   \alpha_G \equiv \frac{G m_n^2}{\hbar c} = \frac{1}{F_\star} = 5.922444\times 10^{-39}.
   $$
2. **Theorem 2 — Nuclear Confinement, Hard-Core Repulsion, and Spaghettification String Tension (`strong_nuclear_triad_confinement`):**
   Inside the crystallized `(1,1,1)` baryon triad ($E^\star(1,1,1) = 4.0$ at
   $\chi_{\mathrm{freeze}} = 3$), short-range compression hits the `(2,2,2)`
   merger barrier $\Delta E_{\mathrm{core}} = 8(\sqrt{2}-1) = +3.3137$, medium-range
   contact shares the $75$% exterior Virial flow ($\Delta E_{\mathrm{flow}} = -2m_{0}/d = -1.0$,
   giving $7.80\text{--}8.61\ \mathrm{MeV/nucleon}$ binding across the $e^{-3}$
   cascade floor), and long-range pulling above $\chi_{\mathrm{spaghetti}} = \frac{1}{2}\ln 2$
   creates a linear 1D filament cost $\sigma_{\mathrm{eff}}\lambda_{3}$ that snaps
   into a new `(1,1,1)` pair (`1 -> 2` fission) because a single 1D axis `(1,0,0)`
   has zero 3D volume ($V^\star(1,0,0) = 0$).
3. **Theorem 3 — Atomic Bohr Shells, Periodic Capacities $2n^2$, and 3D-to-1D Impedance (`atomic_shell_and_em_impedance`):**
   Coupling a 3D `(1,1,1)` core ($E^\star = 4$, volume factor $4\pi^3$) to a 1D
   closed azimuthal phase loop ($\pi$, $e^{i\pi}=-1$) across the 2D surface
   ($\pi^2$) yields the geometric impedance
   $\alpha_{\mathrm{geom}}^{-1} = 4\pi^3 + \pi^2 + \pi = 137.036304$ ($+2.22\ \mathrm{ppm}$
   from CODATA $137.035999$), quantized shell radii $r_{n}^\star = n^2 a_{0}$, and
   periodic-table shell capacities $N_{\mathrm{shell}}(n) = 2\sum_{l=0}^{n-1}(2l+1) = 2n^2 = 2, 8, 18, 32, 50, 72$
   where the factor of $2$ is the right/left helical buckling handedness
   $\pm\omega^\star$ of **Axiom A1**.
4. **Theorem 4 — Balloon-in-Balloon Pressure Venting as Beta Decay (`weak_balloon_in_balloon_venting`):**
   Inside a nucleus, neighboring `(1,1,1)` bubbles supply confining counter-pressure
   work $W_{\mathrm{confine}} > \Delta E_{np} = 1.2933\ \mathrm{MeV}$, keeping
   neutrons stable. In empty space, external counter-pressure vanishes and the
   un-confined neutron vents its excess 1D boundary winding across the two-valve
   cascade barrier ($\gamma_{\mathrm{core}}^5 e^{-4\chi_{\mathrm{freeze}}} = \gamma_{\mathrm{core}}^5 e^{-12} = 1.0102\times 10^{-5}$
   vs. experimental $G_{F} m_{p}^2 c/\hbar^3 = 1.0268\times 10^{-5}$).
5. **Theorem 5 — Nuclear Binding Curve and Heavy-Nucleus Fission (`nuclear_binding_and_fission_neck`):**
   Packing $A$ `(1,1,1)` triads reproduces the semi-empirical binding curve
   peaking at $^{56}\mathrm{Fe}\text{--}^{62}\mathrm{Ni}$ and proves that
   heavy-nucleus fission above $(Z^2/A)_{\mathrm{crit}} = 2a_{S}/a_{C} = 48.51$
   follows the Paper I two-center equipotential neck equation and Cardano cubic
   $p^3 - 3p - 3 = 0$ ($p_+ = \varphi^{2/3}+\varphi^{-2/3} = 2.1038034$).
6. **Theorem 6 — The Unified Seven-Tier Resolution Hierarchy (`unified_resolution_hierarchy_readout`):**
   Connects all seven resolution regimes across the $141.0$ e-folds
   ($\approx 47\times\chi_{\mathrm{freeze}}$) between $\ell_P$ and $2R_H$.
