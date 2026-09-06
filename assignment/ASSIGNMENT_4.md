# Assignment 4 — Steady-State Postoperative Simulation

**Henri Van Overmeire**

## 4.1 Methods: meshing

### Mesh specification

| Parameter | Selected value |
|---|---:|
| Surface source | `meshes/postop/airways.stl` |
| Surface SHA-256 | `1282e23e50a80f6fe06262f223f164077d5b146f20a5131537cb064006652111` |
| Gmsh version | 4.15.2 |
| Global characteristic length | 0.15 mm |
| 3D algorithm | HXT |
| Element order/type | First-order tetrahedra |
| Volume cells | 776,568 |
| Points | 151,599 |
| Physical volume | `fluid` |
| Physical patches | `inlet`, `outlet_1`, `outlet_2`, `outlet_3`, `wall` |
| Maximum aspect ratio | 12.627 |
| Maximum non-orthogonality | 69.817°; zero faces above 70° |
| Maximum skewness | 1.1958 |
| Minimum cell volume | `5.1159e-14 m³` |
| Connected regions | 1 |
| Full `checkMesh` result | 1 failed extended check: 278 low-determinant cells |

The selected mesh had one connected fluid region and passed the reported
non-orthogonality and skewness criteria. The stricter
`-allTopology -allGeometry` run identified 278 localized low-determinant cells;
this remains a mesh-quality limitation.

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

Dimensional pressure uses \(\rho=1.204\,\mathrm{kg/m^3}\). At the normalized
centerline-matched section, \(U=6.47\,\mathrm{m/s}\), equivalent diameter
\(D=2.565\,\mathrm{mm}\), and the specified viscosity give \(Re\approx1107\).
The steady laminar model is therefore a defensible proof-of-concept assumption,
although the transient peak estimate of approximately 3500 motivates future
transitional-model sensitivity testing.

### Residuals and convergence (maximum 100 words)

The selected-mesh SIMPLE solution converged in 1611 iterations. Final initial
residuals were \(9.97\times10^{-7}\), \(9.35\times10^{-7}\), and
\(6.56\times10^{-7}\) for \(U_x\), \(U_y\), and \(U_z\), and
\(6.87\times10^{-6}\) for pressure. All
were below the configured controls of \(10^{-6}\) for velocity and
\(10^{-5}\) for pressure. The complete histories are plotted on logarithmic
axes in the report. Convergence of residuals establishes iterative convergence,
but final acceptance also requires stable integral quantities and outlet mass
balance.

### Effect of 1000 additional iterations (maximum 50 words)

The selected solution already met its residual criteria at iteration 1611, so
another 1000 iterations would not be expected to materially change the
\(6.473\,\mathrm{m/s}\) mean matched-section velocity if integral quantities
were stable. This continuation was not executed; therefore no numerical change
is claimed.

## 4.3 Results

### Flow, pressure, and lung distribution (maximum 100 words)

At 2 L/min, 11.80% exited through the right superior lobar bronchus, 61.88%
through the right inferior lobar bronchus, and 26.31% through the left main
bronchus. Thus, right- and left-lung fractions were 73.69% and 26.31%; relative
mass imbalance was only \(6.0\times10^{-7}\%\). Because all outlets had equal
zero gauge pressure, this unequal distribution arose from the resolved branch
areas, lengths, orientations, and associated hydraulic resistance rather than a
prescribed flow split. The final velocity and pressure visualizations use the
selected 0.15 mm HXT fields at iteration 1611.

### Local resistance (maximum 100 words)

Fixed centerline-normal planes gave area-averaged kinematic pressures of 64.49
and 35.24 m²/s². With \(\rho=1.204\,\mathrm{kg/m^3}\), \(\Delta P=35.21\) Pa.
Using the conservative imposed inlet flux
\(Q=3.3333\times10^{-5}\,\mathrm{m^3/s}\) gives
\(R=1.0565\times10^6\,\mathrm{Pa\,s/m^3}\), or 17.61 Pa/(L/min). The
interpolated slice flux is 0.36% higher and is not used for resistance. At the
matched section, mean and peak velocities were 6.47 and 9.67 m/s. Plane definitions are frozen in
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
