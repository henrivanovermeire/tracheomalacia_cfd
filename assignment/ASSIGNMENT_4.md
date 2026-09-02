# Assignment 4 — Steady-State Postoperative Simulation

**Henri Van Overmeire**

## 4.1 Methods: meshing

### Mesh specification

| Parameter | Baseline value |
|---|---:|
| Surface source | `meshes/postop/airways.stl` |
| Surface SHA-256 | `1282e23e50a80f6fe06262f223f164077d5b146f20a5131537cb064006652111` |
| Gmsh version | 4.15.2 |
| Global characteristic length | 0.25 mm |
| Surface classification angle | 40° |
| 3D algorithm | Gmsh algorithm 1 (Delaunay) |
| Optimization | Enabled |
| Element order/type | First-order tetrahedra |
| Volume cells | 209,652 |
| Boundary faces | 40,874 |
| Nodes | 44,383 |
| Physical volume | `fluid` |
| Physical patches | `inlet`, `outlet_1`, `outlet_2`, `outlet_3`, `wall` |
| Volume-mesh SHA-256 | `ed49b8ab9dc0047ea6285903457fca5dce7b4067f5286b34f17eaa4b6a3add35` |
| Maximum aspect ratio | 35.675 |
| Non-orthogonality | Mean 21.931°; maximum 87.064°; 7 faces >70° |
| Maximum skewness | 1.654 |
| Minimum cell volume | `3.2403e-14 m³` |
| Connected regions | 1 |
| Full `checkMesh` result | 2 failed extended checks: 242 low-determinant cells and 33 low-weight faces |

The mesh passed the standard geometry checks and had one connected fluid region.
The stricter `-allTopology -allGeometry` run identified localized low determinant
and interpolation-weight cells; these are retained as quality limitations for
the sensitivity study.

### Near-boundary elements (maximum 100 words)

Boundary-layer prism elements align cells with the airway wall and provide
controlled wall-normal spacing. They resolve steep near-wall velocity gradients
and wall shear more efficiently and accurately than isotropic tetrahedra,
particularly when the first-cell height and layer growth are selected for the
target wall treatment. The present baseline instead uses first-order tetrahedra
throughout and has no dedicated inflation layers. It can represent bulk flow
and pressure trends, but near-wall gradients and wall-derived quantities are
more mesh-sensitive. This absence is therefore treated as a limitation and must
be considered when selecting quantities for the mesh-sensitivity study.

## 4.2 Methods: simulation setup

### Fluid and boundary conditions (maximum 100 words)

Air was modelled as incompressible, Newtonian, and laminar with kinematic
viscosity \(\nu=1.5\times10^{-5}\,\mathrm{m^2\,s^{-1}}\). The rigid airway wall
used no slip. A constant volumetric flow of
\(3.3333\times10^{-5}\,\mathrm{m^3\,s^{-1}}\) (2.0 L/min) was prescribed at
the tracheal inlet. All three distal outlets used zero kinematic gauge pressure
and pressure-compatible velocity conditions, allowing the anatomical geometry
to determine the outlet flow split. Inlet pressure used zero gradient. The
steady incompressible equations were solved with `simpleFoam`; pressure is
reported as kinematic pressure and converted to Pa using \(P=\rho p\) where
required.

**Pending:** insert the selected air density and literature citation, and verify
that the laminar assumption is consistent with calculated Reynolds numbers.

### Residuals and convergence (maximum 100 words)

The SIMPLE solution converged in 589 iterations. Final initial residuals were
\(9.93\times10^{-7}\), \(7.57\times10^{-7}\), and \(6.48\times10^{-7}\) for
\(U_x\), \(U_y\), and \(U_z\), and \(4.92\times10^{-6}\) for pressure. All
were below the configured controls of \(10^{-6}\) for velocity and
\(10^{-5}\) for pressure. The complete histories are plotted on logarithmic
axes in the report. Convergence of residuals establishes iterative convergence,
but final acceptance also requires stable integral quantities and outlet mass
balance.

### Effect of 1000 additional iterations (maximum 50 words)

Once the residuals and monitored axial velocity have stabilized, another 1000
iterations should not materially change the result; it should only reduce the
remaining iterative error. This must be verified by continuing from iteration
2000 and reporting the absolute and percentage change in the same axial-velocity
measurement at iteration 3000.

## 4.3 Results

### Flow, pressure, and lung distribution (maximum 100 words)

At 2 L/min, 11.23% exited through the right superior lobar bronchus, 61.94%
through the right inferior lobar bronchus, and 26.83% through the left main
bronchus. Thus, right- and left-lung fractions were 73.17% and 26.83%; relative
mass imbalance was only \(6.0\times10^{-7}\%\). Because all outlets had equal
zero gauge pressure, this unequal distribution arose from the resolved branch
areas, lengths, orientations, and associated hydraulic resistance rather than a
prescribed flow split. Final velocity and pressure visualizations will use the
converged iteration-589 fields.

### Local resistance (maximum 100 words)

Fixed centerline-normal planes at the mapped superior and inferior stenosis
limits gave area-averaged kinematic pressures of 53.70 and 27.99 m²/s². With
\(\rho=1.204\,\mathrm{kg/m^3}\), \(\Delta P=30.95\) Pa. Mean section flow was
\(3.347\times10^{-5}\,\mathrm{m^3/s}\), yielding
\(R=\Delta P/Q=9.25\times10^5\,\mathrm{Pa\,s/m^3}\), or 15.41 Pa/(L/min).
At the matched minimum section, area-averaged axial velocity was 6.53 m/s and
sectional peak velocity was 9.25 m/s. Plane definitions are frozen in
`resistance_sections.json` for subsequent mesh comparisons.

## 4.4 Future work (maximum 100 words)

Mesh sensitivity will monitor outlet flow fractions, local pressure drop and
resistance across the matched tracheal region, area-averaged axial velocity, and
peak velocity in a fixed anatomical region. Outlet fractions assess whether
branch-flow predictions are stable; pressure drop and resistance are especially
sensitive to stenosis resolution; mean velocity is a robust conservation-based
quantity; peak velocity probes local discretization error. At least three
systematically refined meshes will use unchanged geometry, boundary conditions,
solver settings, and sampling definitions. Percentage changes relative to the
finest mesh will determine whether further refinement materially affects the
reported conclusions.
