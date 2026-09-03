# Chronological Assignment Work Plan

**Course:** Computational Biofluid Mechanics, 2025–2026  
**Student:** Henri Van Overmeire  
**Assignments covered:** 1–6  
**Approved toolchain:** 3D Slicer/SlicerVMTK, Gmsh, OpenFOAM, Docker,
independent local/remote compute, and ParaView

This plan proceeds in assignment order. It prioritises concrete work products:
verified data, measurements, simulations, plots, tables, and figures. Generic
theoretical prose will be finalised only after the computational evidence is
available.

## General working rules

1. Do not overwrite accepted geometries, meshes, or results.
2. Use a unique name for every anatomy, mesh level, and transient run.
3. Validate boundary patches and mesh quality before starting a solver.
4. Store raw quantitative outputs in CSV/JSON before making report figures.
5. Reuse identical measurement sections across Assignments 4–6.
6. Record the Git commit, software versions, mesh settings, cell count, solver
   settings, and runtime for every simulation.
7. OpenFOAM incompressible pressure is kinematic pressure. Convert pressure
   differences to pascals with `ΔP = ρ Δp` before reporting dimensional
   resistance.
8. Update `STATUS.md` immediately when an item is completed.

---

# Assignment 1A — CFD paper

## Goal

Produce five concise, evidence-based sections on the selected article, each no
longer than 150 words, with no more than three correctly referenced figures.

## Selected article

Taherian, S., Rahai, H., Gomez, B., Waddington, T., and Mazdisnian, F. (2017).
“Computational fluid dynamics evaluation of excessive dynamic airway
collapse.” *Clinical Biomechanics*, 50, 145–153.
https://doi.org/10.1016/j.clinbiomech.2017.10.018

Repository copy: `assignment/arcticle.pdf`.

## Completion record

**Status: complete.** The final standalone response is in
`assignment/ASSIGNMENT_1.md` and the same content is integrated into
`report/report.tex` under “Critical review of a selected CFD paper.”

- [x] Extracted the research question, methods, quantitative results,
      limitations, and conclusions from the full paper.
- [x] Verified the four-geometry design, boundary-condition method, unsteady
      RANS model, mesh study, respiratory timing, and key outcome values.
- [x] Distinguished patient-specific evidence from broader clinical
      generalisability.
- [x] Added the full citation and DOI to the LaTeX bibliography.
- [x] Completed **Goal** in 97 words.
- [x] Completed **Methods** in 129 words.
- [x] Completed **Results** in 119 words.
- [x] Completed **Limitations** in 127 words.
- [x] Completed **Evaluation** in 132 words.
- [x] Chose not to use optional reproduced figures, remaining below the maximum
      of three and avoiding unnecessary page use.
- [x] Rebuilt `report/report.pdf` successfully.

---

# Assignment 2 — Guest lecture questions

## Goal

Complete the lecture activity and submit the two prepared questions.

## Work sequence

- [ ] Watch Prof. Joris Degroote’s lecture or review the recording and slides.
- [ ] Check whether the lecture already answers either selected question.
- [ ] If needed, sharpen the incompressibility question using local Mach number,
      density variation, and the practical meaning of 0.1 versus 0.3 cutoffs.
- [ ] If needed, sharpen the PDE-classification question using discriminants,
      characteristics, and conic-section terminology.
- [ ] Submit both questions to the designated Microsoft Teams file.
- [ ] Record submission completion in `STATUS.md`.

## Definition of done

The lecture has been reviewed and both questions are present in the specified
Teams document.

---

# Assignment 3 — Segmentation and anatomical measurements

## Goal

Produce equivalent preoperative and postoperative airway reconstructions,
measure the constriction, and generate the annotated figures and raw values
required by Assignment 3.

## 3.1 Freeze the accepted postoperative geometry

- [ ] Confirm `AirwayCutEndpoints`, centerline-directed extensions, and flat caps.
- [ ] Confirm four openings: one tracheal inlet and three distal outlets.
- [ ] Capture a high-resolution 3D reconstruction with a saved/reproducible
      camera orientation.
- [ ] Preserve the final postoperative STL under a case-specific path.

## 3.2 Complete the preoperative geometry

Set `CASE = "preop"` only in `segment_airway.py`; all later scripts read the
`AirwayCase` scene tag. Then run:

1. `segment_airway.py`
2. `remove_lungs.py` to substitute the manually cleaned preoperative
   `AirwayLungSegmentation.seg.nrrd` into the live scene.
3. `prepare_centerline_endpoints.py`
4. Place one proximal and three distal points; export
   `segmentation/assets/preop/CenterlineEndpoints.json`.
5. `calculate_centerline.py`
6. `prepare_cutting_points.py`
7. Place/adjust `AirwayCutEndpoints` and export
   `segmentation/assets/preop/refined_endpoints.json`.
8. `cut_airways_centerline.py` (it reuses the adjusted scene node).
9. `export_segmentation.py`

On later runs, use `load_cutting_points.py` instead of steps 5–6 to restore the
saved refined points.

Then:

- [ ] Confirm the stenosis is retained and lung leaks are excluded.
- [ ] Match the anatomical extent to the postoperative geometry.
- [ ] Verify extensions and planar caps.
- [ ] Capture a 3D reconstruction using the postoperative camera orientation.
- [ ] Preserve the final preoperative STL separately.

## 3.3 Improve case-specific file organisation

Case-specific export organisation is now implemented:

- [x] Created `meshes/preop/` and `meshes/postop/`.
- [x] Made STL and Gmsh input paths case-specific.
- [x] Preserved the verified postoperative STL and Gmsh definition.
- [ ] Export the final preoperative STL to `meshes/preop/airways.stl`.
- [ ] Create and verify `meshes/preop/airways.geo` after inspecting its cap IDs.

## 3.4 Measure the preoperative constriction

- [x] Marked proximal and distal limits in
      `segmentation/assets/preop/StenosisEndpoints.json`.
- [x] Ran `segmentation/scripts/measure_stenosis.py` in the preoperative Slicer
      scene.
- [x] Inspected and accepted the generated centerline segment and minimum
      cross-section.
- [x] Accepted the stenosis endpoints after visual review.
- [x] Recorded centerline length (12.157 mm) and minimum cross-sectional area
      (1.813 mm²).
- [ ] Calculate equivalent diameter:

```text
D_eq = 2 sqrt(A / π)
```

- [x] Saved section position, orientation, area, equivalent diameter (1.519 mm),
      and minimum/maximum Feret diameters (0.798/2.859 mm).

## 3.5 Measure the matched postoperative section

- [x] Identified the corresponding location at 76.53% of inlet-to-carina
      centerline length; postoperative carina is the network bifurcation nearest
      `AirwaySeed`.
- [x] Generalized `measure_stenosis.py` to use the same centerline-normal method
      in both scene cases and to distinguish the matched section from the local
      interval minimum.
- [x] Ran `measure_stenosis.py` in the postoperative scene and recorded matched
      area (5.169 mm²), minimum Feret diameter (2.292 mm), and equivalent
      diameter (2.565 mm).
- [x] Documented the normalized centerline correspondence and mapped both
      stenosis endpoints for visual verification.

## 3.6 Calculate constriction

Calculated and retained both:

```text
Area constriction = (1 - A_pre,min / A_post,matched) × 100%
Diameter reduction = (1 - D_pre,min / D_post,matched) × 100%
```

The resulting area constriction is 64.9%; minimum-Feret-diameter reduction is
65.2%. Area constriction is the primary result because it directly represents
loss of flow area in the non-circular lumen.

## Required outputs

- [x] `assignment/data/anatomical_measurements.csv`
- [ ] Preoperative annotated reconstruction.
- [ ] Postoperative annotated reconstruction.
- [ ] Clear figure captions and measurement methodology.
- [x] Final Methods/Measurements response is 194 words.
- [x] Qualitative pressure/velocity graph for the separate flow-behaviour task.
- [x] Resistance-method answer ≤50 words.

## Definition of done

Both reconstructions are comparable, every value is reproducible, the measured
locations are visible, and all three Assignment 3 word limits are satisfied.

---

# Assignment 4 — Steady postoperative simulation

## Goal

Convert the existing postoperative steady result into complete quantitative
Assignment 4 evidence. This stage defines the planes and monitored quantities
that must remain unchanged for Assignments 5 and 6.

## 4.1 Freeze run provenance

- [ ] Record Git commit.
- [ ] Record Slicer/SlicerVMTK, Gmsh, ParaView, and OpenFOAM versions.
- [ ] Record Docker image ID, `NPROCS`, runtime, and host configuration.
- [ ] Archive the verified `airways.msh`, case dictionaries, solver log, and
      `checkMesh` output.
- [ ] Confirm five patches and one connected fluid region.

## 4.2 Build the replicable mesh table

Record:

- [x] STL identity/checksum.
- [x] Gmsh characteristic length (0.5 mm).
- [x] Classification angle (40°) and 3D algorithm (Gmsh Delaunay).
- [x] Node and cell counts for the committed mesh (8,424 nodes; 32,298 cells).
- [x] Element order and type (first-order tetrahedra).
- [ ] Maximum aspect ratio.
- [ ] Maximum non-orthogonality and number above 70°.
- [ ] Maximum skewness and minimum volume.
- [x] Statement that the current mesh has tetrahedra but no dedicated prism
      boundary layer.

## 4.3 Residual and convergence analysis

- [ ] Parse `Ux`, `Uy`, `Uz`, and `p` residuals from the solver log.
- [ ] Write a reusable parser that outputs CSV.
- [ ] Plot residual versus iteration using a logarithmic y-axis.
- [ ] Mark configured convergence thresholds.
- [ ] Check stability of resistance, flow split, and selected axial velocity.
- [ ] Quantify final mass imbalance from patch flows.

## 4.4 Define reusable resistance planes

Before any mesh comparison:

- [ ] Define upstream and downstream planes around the pre-bifurcation section
      corresponding to the preoperative constriction location.
- [ ] Orient both planes normal to the centerline.
- [ ] Avoid bifurcations, caps, and ambiguous section intersections.
- [ ] Save origins and normals in `assignment/data/resistance_sections.json`.
- [ ] Create a geometry figure showing both planes.

These definitions are frozen for Assignments 4, 5, and 6.

## 4.5 Extract steady integral quantities

Automate extraction to CSV for:

- [x] Area-averaged kinematic pressure on both resistance planes.
- [x] Dimensional pressure difference using air density 1.204 kg/m³.
- [x] Volumetric flow through the section.
- [x] Local resistance `R = ΔP / Q`.
- [x] Area-averaged axial velocity on the selected section.
- [x] Flow rate through each outlet.
- [x] Combined left- and right-lung flow fractions.
- [x] Peak velocity on the fixed matched section, selected for mesh sensitivity.

Prefer an OpenFOAM function object or scripted ParaView/Python workflow over
manual GUI readings.

## 4.6 Test 1000 additional iterations

- [ ] Record the selected axial-velocity value at iteration 2000.
- [ ] Continue from the converged field for 1000 iterations.
- [ ] Record the same value at iteration 3000.
- [ ] Calculate absolute and percentage change.
- [ ] Confirm no reinitialisation occurred.

## 4.7 Produce final steady figures

- [x] Full-lumen velocity-vector field with fixed scale and anatomical frontal view.
- [x] Dimensional pressure field and centerline pressure profile in Pa.
- [x] Residual history.
- [ ] Resistance-plane locations.
- [ ] Outlet/lung flow distribution table or chart.

## Definition of done

Every Assignment 4 number can be regenerated from scripts and archived fields;
all figures use clear scales and the resistance sections are frozen for later
assignments.

---

# Assignment 5 — Postoperative mesh-sensitivity study

## Goal

Run a defensible multi-level postoperative mesh study and choose the least
expensive mesh that preserves the selected integral quantities.

## 5.1 Select mesh levels

Use at least three systematically refined meshes. Initial proposal:

| Label | Target size | Purpose |
|---|---:|---|
| HXT baseline | 0.25 mm | Quality-consistent replacement for the Assignment 4 Delaunay mesh |
| HXT fine 1 | 0.20 mm | First refinement |
| HXT fine 2 | 0.15 mm | Second refinement |
| HXT reference | 0.12 mm | Densest reference |

Adjust sizes if cell counts or memory use become impractical, but preserve a
clear refinement sequence.

## 5.2 Generate and validate every mesh locally

For every level:

- [x] Generated all levels with `run_mesh_sensitivity.sh` and the HXT algorithm.
- [x] Used the same postoperative STL and physical-surface definition.
- [x] Preserved and verified the named physical groups.
- [x] Confirmed `inlet`, `outlet_1`, `outlet_2`, `outlet_3`, `wall`, and `fluid`.
- [x] Recorded element count and mesh-quality metrics.
- [x] Rejected the original sliver-prone Delaunay refinement and replaced the
      entire series consistently with HXT.

Changing only `MESH_SIZE` should not alter physical groups, but verification is
still mandatory.

## 5.3 Run every mesh with identical physics

- [x] Used identical material properties and 2 L/min boundary conditions.
- [x] Used identical solver schemes, convergence criteria, and iteration limit.
- [x] Set `numberOfSubdomains` equal to `NPROCS`.
- [x] Ran remotely using unique HXT case names.
- [x] Reconstructed and fetched every result.
- [x] Recorded reported solver runtime; memory use was not available.

Suggested names:

```text
postop_coarse
postop_baseline
postop_fine
```

## 5.4 Extract identical parameters

Use the frozen Assignment 4 sections and scripts. Recommended primary
parameters:

- [x] Selected pre-bifurcation local resistance.
- [x] Selected right-lung flow fraction.
- [x] Selected right-superior share of right-lung flow.

Optional secondary parameters:

- [x] Selected peak velocity on the fixed matched section.
- [x] Retain pressure drop and area-averaged axial velocity as secondary tabulated metrics.
- [ ] Wall shear stress only if near-wall mesh treatment is adequate.

## 5.5 Create sensitivity data and plots

- [x] Created `assignment/data/mesh_sensitivity.csv` with one row per mesh.
- [x] Plotted every selected parameter versus number of volume elements.
- [ ] Calculate percentage difference from the densest mesh:

```text
δ_i = |φ_i - φ_dense| / |φ_dense| × 100%
```

- [x] Plotted percentage difference versus element count for every parameter.
- [x] Used consistent units, labels, and significant figures.
- [x] Applied a practical 2.5% acceptance threshold.

## 5.6 Choose the optimal mesh

- [x] Selected the 0.15 mm mesh: all selected differences are ≤2.02% relative
      to the denser result.
- [x] Compared gain with the 92% cell-count and 157% runtime increase at 0.12 mm.
- [x] Documented that the densest case was not residually converged and therefore
      is not treated as a truth solution.
- [ ] Package the accepted Gmsh/OpenFOAM equivalents requested for submission.

## 5.7 Optional mesh-quality improvement gate

The current mesh has no prism layers. Before finalising the study, decide:

- [x] Restricted conclusions to integral/bulk and fixed-section quantities
      suitable for the tetrahedral approach.
- [x] Excluded wall-shear claims because no dedicated boundary layers exist.
- [ ] If the mesh method changes, regenerate every level consistently; do not
      compare mixed meshing strategies as one refinement sequence.

## Definition of done

At least three validated meshes have converged results; all parameter and
percentage-difference plots exist; the optimal mesh is justified quantitatively;
and accepted solver artifacts are packaged for Ufora.

---

# Assignment 6 — Transient postoperative simulation

## Goal

Run a validated complete breathing-cycle simulation on the selected Assignment 5
mesh and quantify time-varying local resistance on the frozen Assignment 4
section.

## 6.1 Define the breathing waveform

- [x] Define and document a simplified physiological sinusoid based on the
      assumed infant minute ventilation.
- [x] Store time and volumetric flow rate in a versioned table.
- [x] Plot the exact waveform before implementing it.
- [x] Confirm sign convention: positive inspiration, negative expiration.
- [x] Confirm the 2.0 s cycle and 66.7 mL tidal volume.

Suggested artifact:

```text
openFOAM/postop_transient/constant/boundaryData/
assignment/data/breathing_waveform.csv
```

## 6.2 Configure the transient OpenFOAM case

- [x] Copy the selected 0.15 mm HXT mesh to `postop_transient` reproducibly.
- [x] Select and document the transient incompressible `pimpleFoam` solver.
- [x] Implement the tabulated time-varying `flowRateInletVelocity` condition.
- [x] Use `pressureInletOutletVelocity` to permit outlet flow reversal.
- [x] Retain no-slip rigid walls.
- [x] Initialise the first cycle from rest; assess startup dependence before
      treating a cycle as periodic.
- [x] Configure solver logging and fields every 0.02 s.

## 6.3 Select time step and run temporal checks

- [x] Reject the original `maxCo=1` setup after it forced `deltaT` below 1e-5 s
      by t=0.0099 s while the mean Courant number remained below 0.08.
- [x] Configure a 0--0.05 s timing mode with `maxCo=2`, maximum `deltaT=5e-5 s`,
      and transient outer-loop criteria distinct from the tight linear tolerances.
- [ ] Complete and analyse the timing diagnostic.
- [ ] Run the 0--0.55 s pilot through peak inspiratory flow.
- [x] Monitor early maximum Courant behavior; revised run holds max Co near 2.02.
- [ ] Check convergence within every time step over the completed timing run.
- [x] Adjust outer stopping criteria to p=1e-2 and U=2e-3 while retaining
      1e-8 linear-equation tolerances.
- [ ] Compare at least two time steps for one key transient quantity.

## 6.4 Establish periodicity

- [ ] Run enough cycles to remove dependence on initial conditions.
- [ ] Compare inlet pressure drop/resistance between consecutive cycles.
- [ ] Define a periodicity tolerance.
- [ ] Analyse one complete final periodic cycle.

## 6.5 Select three reporting times

Choose from the actual waveform, likely:

- [ ] Inspiratory acceleration.
- [ ] Peak inspiratory flow.
- [ ] Deceleration, expiration, or flow reversal.

For each time:

- [ ] Record exact time and inlet flow rate.
- [ ] Create velocity vectors coloured by velocity magnitude.
- [ ] Use the same plane, camera, glyph scaling, and colour range.

## 6.6 Calculate time-varying local resistance

At every saved time in the final cycle:

- [ ] Area-average pressure on the same frozen upstream/downstream planes.
- [ ] Convert kinematic pressure difference to pascals.
- [ ] Calculate section flow rate.
- [ ] Calculate `R(t) = ΔP(t) / Q(t)`.
- [ ] Mask or treat points near `Q = 0` explicitly to avoid numerical blow-up.
- [ ] Save `time`, `Q`, `ΔP`, and `R` to CSV.
- [ ] Plot `Q(t)`, `ΔP(t)`, and `R(t)` with aligned time axes.
- [ ] Assess phase lag and hysteresis rather than assuming a single-valued
      pressure–flow relation.

## 6.7 Produce Assignment 6 figures

- [ ] Residual/convergence status by time step.
- [ ] Three velocity-vector panels.
- [ ] Applied inlet breathing waveform.
- [ ] Computed postoperative local resistance over one complete cycle.
- [ ] Qualitative pre-/postoperative resistance comparison.

## 6.8 Handle unconverged steps

If needed, test in this order:

1. Reduce time step and maximum Courant number.
2. Increase inner correctors/iterations.
3. Improve linear-solver tolerances and preconditioning.
4. Improve problematic mesh cells.
5. Use a better periodic initial condition.
6. Add compute resources only after numerical settings are justified.

## Definition of done

A final periodic breathing cycle is reconstructed; convergence is known for
every time step; three vector figures and all resistance/waveform plots exist;
and every quantity uses the same Assignment 4 section definition.

---

# Immediate next actions

Work strictly in this order:

1. [x] Complete the structured review of Taherian et al. and verify key
       numerical details.
2. [x] Complete all five Assignment 1 sections; optional figures were not used.
3. [ ] Review the Assignment 2 lecture and submit the prepared questions.
4. [x] Freeze the postoperative and preoperative computational geometries.
5. [x] Perform Assignment 3 cross-sectional measurements; anatomical screenshots
       remain deferred.
6. [x] Automate Assignment 4 residual, patch-flow, and resistance extraction.
7. [x] Run the consistent HXT mesh-sensitivity series for Assignment 5.
8. [x] Select the 0.15 mm HXT mesh.
9. [x] Configure the Assignment 6 waveform and transient case.
10. [ ] **Next:** run and assess the 0--0.55 s transient pilot before launching
        the full cycle.

## Data directory to create as work begins

```text
assignment/data/
├── anatomical_measurements.csv
├── breathing_waveform.csv
├── mesh_sensitivity.csv
├── resistance_sections.json
├── steady_integrals.csv
└── transient_resistance.csv
```

## Report integration rule

Only move a checkbox to complete when the corresponding value, figure, table,
or explanation is present in `report/report.tex` or linked reproducible data.
Implementation alone is not completion of an assignment deliverable.
