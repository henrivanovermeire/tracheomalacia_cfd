# Assignment 5 — Postoperative Mesh-Sensitivity Study

**Henri Van Overmeire**

## 5.1 Results (maximum 150 words)

Four HXT tetrahedral meshes contained 180,163 (0.25 mm), 339,886 (0.20 mm),
776,568 (0.15 mm), and 1,493,440 cells (0.12 mm). Fixed anatomical sections and
identical 2 L/min boundary conditions were used. Selected metrics were local
resistance, right-lung flow fraction, right-superior share of right flow, and
matched-section peak velocity. Relative difference from the densest mesh was
calculated as
\(\delta_i=|\phi_i-\phi_{0.12}|/|\phi_{0.12}|\times100\%\).
For the 0.15 mm mesh, differences were 2.02%, 0.39%, 1.43%, and 1.54%,
respectively. Corresponding 0.20 mm differences were 8.62%, 0.30%, 4.02%, and
2.53%. The 0.12 mm solution reached 2000 iterations without satisfying residual
control, so densest-mesh differences are interpreted cautiously. Plots use
actual volume-cell count.

## 5.2 Discussion (maximum 100 words)

Resistance and the small right-superior branch split were more mesh-sensitive
than total right-lung fraction. Refinement from 0.15 to 0.12 mm changed all
selected metrics by at most 2.02%, but increased cells by 92% and solver time by 157%. The 0.12 mm case did not reach residual control, whereas the 0.15 mm case
converged in 1611 iterations. Using a 2.5% threshold, the 0.15 mm mesh is therefore optimal: it is the
finest converged solution, satisfies the threshold against the denser result,
and avoids substantial computational cost for limited apparent improvement.

## 5.3 Limitations

### Current modelling approach (maximum 150 words)

The model assumes steady, incompressible, laminar flow through rigid,
patient-specific postoperative airways. A constant 2 L/min inlet and identical
zero-gauge-pressure outlets omit breathing-cycle acceleration, lung compliance,
and patient-specific distal impedance. Segmentation, smoothing, clipping, and
flow extensions introduce geometric uncertainty. The tetrahedral meshes contain
no prism boundary layers; bulk pressure, velocity, and flow division are more
defensible than wall shear or near-wall gradients. The 0.12 mm run remained
iteratively unconverged, so it is not an independent truth solution. Greater
realism would require transient breathing waveforms, compliant walls or
fluid--structure interaction, resistance/compliance outlet models, uncertainty
analysis of segmentation and boundary conditions, and validation against
measured pressure or flow. Near-wall studies should add consistently generated
prism layers and quantify wall-normal resolution.

### Expanded mesh-sensitivity study (maximum 100 words)

With additional resources, the study should add refinement levels around the
observed asymptotic range, repeat all cases with improved solver stabilization,
and require convergence of both residuals and monitored integrals. Local
refinement should target the matched tracheal region, carina, and small right
superior branch instead of reducing global size uniformly. A consistent
prismatic boundary layer could then support wall-shear analysis. Formal
Richardson extrapolation and a grid-convergence index should be used where the
solutions show monotonic asymptotic behavior. Runtime, memory, mesh quality,
and geometric section-area variation should be tracked alongside each physical
metric.

## 5.4 Interpretation (maximum 100 words)

For fully developed laminar flow in a rigid constant-diameter tube,
Poiseuille's law gives \(\Delta P=128\mu LQ/(\pi D^4)=RQ\). Geometry and fluid
properties are constant, so increasing inspiratory flow produces a proportional
pressure drop while \(R=\Delta P/Q\) remains constant. Resistance is therefore horizontal during increasing inspiration.
In the patient-specific airway, developing flow, curvature, bifurcation,
separation, and inertial losses can make pressure drop nonlinear in flow and
cause apparent resistance to increase. Transient inertia can produce phase differences between pressure drop and flow,
so instantaneous
\(\Delta P/Q\) need not remain constant.
