# Assignment 6 — Transient postoperative simulation

## Objective

Simulate one complete postoperative breathing cycle on the mesh selected by the Assignment 5 sensitivity study, assess time-step convergence, visualize representative phases, and calculate local resistance over the cycle using the same anatomical section as Assignment 4.

## Frozen inputs

- Geometry: postoperative airway.
- Mesh: 0.15 mm HXT, 776,568 tetrahedral cells.
- Resistance planes: `assignment/data/resistance_sections.json`.
- Fluid: incompressible Newtonian air.
- Kinematic viscosity: `1.5e-5 m²/s`.
- Density for converting kinematic pressure to Pa: `1.204 kg/m³`.
- Walls: rigid, no slip.
- Outlets: zero fixed kinematic pressure with `pressureInletOutletVelocity` for reversal.

The mesh has no prism boundary layers. Conclusions are therefore restricted to bulk flow, pressure, resistance, and fixed-section quantities; wall-shear claims are excluded.

## Breathing waveform

The prescribed inlet flow is

```text
Q(t) = Qmax sin(2πt/T)
```

with:

| Parameter | Value |
|---|---:|
| Period | 2.0 s |
| Respiratory rate | 30/min |
| Minute ventilation | 2.0 L/min |
| Tidal volume | 66.7 mL |
| Peak flow magnitude | 6.283 L/min |
| Peak flow magnitude | 1.0472e-4 m³/s |
| Inspiration | 0–1 s (positive) |
| Expiration | 1–2 s (negative) |

Versioned artifacts:

- `assignment/data/breathing_waveform.csv`
- `openFOAM/postop_transient/constant/breathingFlowRate.table`
- `report/figures/assignment6_breathing_waveform.tex`

## Numerical setup

- Solver: `pimpleFoam`.
- Temporal scheme: second-order backward.
- Initial time step: `1e-5 s`.
- Maximum adaptive time step: `5e-5 s`.
- Maximum Courant number: 2.0 after the original `maxCo=1` timing test proved prohibitively restrictive.
- Field write interval: 0.02 s.
- PIMPLE: up to 3 outer correctors, 2 pressure correctors, 1 non-orthogonal corrector.
- Outer-loop stopping targets: `2e-3` for velocity and `1e-2` for pressure.
- Linear-equation absolute tolerances remain `1e-8` for velocity and pressure.
- Decomposition: Scotch, 48 MPI ranks by default (approximately 16,200 cells per rank).

## Physical-model checks

The estimated peak mean speed at the matched section is approximately 20.3 m/s. This gives Mach ≈ 0.06, supporting incompressibility for the simplified waveform. Reynolds number is approximately 3500, so transition or turbulence is an acknowledged limitation of the laminar model.

For the same tidal volume, a shorter mechanically ventilated inspiratory phase would require a higher peak flow. Such a waveform could approach or exceed Mach 0.1 and would require the incompressibility assumption to be reassessed.

## Execution

Run the short timing diagnostic first:

```bash
./run_transient_workflow.sh 159.203.184.188 --timing
```

The original `maxCo=1` test reached only 0.0099 s in approximately 239 s and
forced `deltaT` below `1e-5 s`, despite a mean Courant number below 0.08. The
revised test uses `maxCo=2`; an early excerpt showed mean Co 0.156, maximum Co
2.02, tight final linear residuals, and final continuity errors around `1e-12`.
The timing run must complete before extrapolating peak-flow cost.

If accepted, run the 0.55 s pilot and then the complete cycle:

```bash
./run_transient_workflow.sh 159.203.184.188 --pilot
./run_transient_workflow.sh 159.203.184.188 --full
```

```bash
./run_transient_workflow.sh 159.203.184.188 --full
```

A one-cycle solution initialized from rest is not assumed periodic. Compare corresponding flow and pressure quantities at cycle boundaries or between consecutive cycles; extend the simulation if startup dependence remains material.

## Planned analysis

1. Parse transient residuals and flag unconverged time steps.
2. Evaluate inlet/outlet mass conservation over time.
3. At each written time, sample the frozen superior and inferior resistance planes.
4. Convert OpenFOAM kinematic pressure using `ΔP = ρ Δp`.
5. Calculate `R(t) = ΔP(t)/Q(t)` and mark resistance undefined when `|Q|` is near zero.
6. Plot aligned `Q(t)`, `ΔP(t)`, and `R(t)` series using Gnuplot/cairolatex.
7. Render velocity vectors at approximately 0.25 s, 0.50 s, and 1.50 s with one frontal camera and common scale.
8. Discuss nonlinear pressure loss, phase lag, hysteresis, and the expected higher preoperative resistance.

## Current status

The waveform generator, case preparation, three-mode remote runner, report methods, and breathing-waveform figure are implemented. The `maxCo=1` test was rejected as too restrictive. The revised `maxCo=2` timing run is in progress; its completed log must be assessed before the 0–0.55 s pilot.
