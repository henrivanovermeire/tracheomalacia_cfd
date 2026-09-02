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

## Work sequence

### 1.1 Create a structured evidence sheet

- [ ] Read the complete paper once without drafting.
- [ ] On the second reading, extract page/figure/table references for:
  - research question;
  - four CT-derived geometries;
  - segmentation and geometry extent;
  - inlet and outlet boundary conditions;
  - unsteady RANS and low-Reynolds-number `k–ω` model;
  - temporal and spatial discretisation;
  - mesh sensitivity;
  - inspiration and expiration findings;
  - wall shear stress and pressure results;
  - author-stated limitations; and
  - conclusions about stent effectiveness.
- [ ] Save these notes in `assignment/assignment_1_notes.md`.
- [ ] Distinguish direct statements from personal criticism.

### 1.2 Verify key numerical details

- [ ] Record the three mesh sizes/cell counts and reported percentage changes.
- [ ] Record inspiration/expiration duration and waveform description.
- [ ] Record inlet/outlet strategy and extension lengths.
- [ ] Record the reported pressure, velocity, wall shear stress, and turbulence
      findings used in the final Results section.
- [ ] Record sample size and model assumptions used in Limitations.

### 1.3 Select figures

Use at most three. A strong initial choice is:

- [ ] Geometry comparison showing pre-/post-stent inspiration/expiration.
- [ ] Velocity comparison at peak inspiration/expiration.
- [ ] Pressure/velocity axial comparison or expiratory wall shear stress.

For every selected figure:

- [ ] Verify readability at report scale.
- [ ] Record the original figure number and page.
- [ ] Write a caption that states it is reproduced/adapted from Taherian et al.
- [ ] Add the full paper citation to the LaTeX bibliography.

### 1.4 Draft the five required sections

- [ ] **Goal:** one explicit research question and clinical motivation.
- [ ] **Methods:** geometry, boundary conditions, solver/model, and comparison
      design; omit low-value implementation detail.
- [ ] **Results:** quantitative, separated into inspiration and expiration.
- [ ] **Limitations:** include both author-stated and critical limitations.
- [ ] **Evaluation:** directly answer whether the study answered its question;
      separate internal evidence from generalisability.
- [ ] Count each section independently and keep each at or below 150 words.

## Definition of done

- Five correctly headed sections, each ≤150 words.
- No more than three numbered, captioned, and cited figures.
- Every quantitative claim traceable to the paper.
- Evaluation gives a defensible yes/partly/no judgement.

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

Run the Slicer scripts with `CASE = "preop"`:

1. `segment_airway.py`
2. `calculate_centerline.py`
3. `load_cutting_points.py`
4. Adjust `AirwayCutEndpoints` in the UI.
5. `cut_airways_centerline.py`
6. `export_segmentation.py`

Then:

- [ ] Confirm the stenosis is retained and lung leaks are excluded.
- [ ] Match the anatomical extent to the postoperative geometry.
- [ ] Verify extensions and planar caps.
- [ ] Capture a 3D reconstruction using the postoperative camera orientation.
- [ ] Preserve the final preoperative STL separately.

## 3.3 Improve case-specific file organisation

Before repeated exports, prevent `meshes/airways.stl` from being overwritten:

- [ ] Create `meshes/preop/` and `meshes/postop/`.
- [ ] Make STL and Gmsh paths case-specific.
- [ ] Keep separately verified physical-surface mappings for both anatomies.

## 3.4 Measure the preoperative constriction

- [ ] Mark proximal and distal constriction limits on the centerline.
- [ ] Measure constriction length along the centerline.
- [ ] Sample cross-sections perpendicular to the centerline through the stenosis.
- [ ] Identify the minimum cross-sectional area.
- [ ] Calculate equivalent diameter:

```text
D_eq = 2 sqrt(A / π)
```

- [ ] Save section position, orientation, area, equivalent diameter, and—if
      useful—minimum/maximum Feret diameters.

## 3.5 Measure the matched postoperative section

- [ ] Identify the same anatomical location using bifurcation-relative landmarks.
- [ ] Use the same centerline-normal cross-section method.
- [ ] Record matched postoperative area and equivalent diameter.
- [ ] Document how correspondence was established.

## 3.6 Calculate constriction

Calculate and retain both:

```text
Area constriction = (1 - A_pre,min / A_post,matched) × 100%
Diameter reduction = (1 - D_pre,min / D_post,matched) × 100%
```

Use area constriction as the primary result unless a course clarification says
otherwise.

## Required outputs

- [ ] `assignment/data/anatomical_measurements.csv`
- [ ] Preoperative annotated reconstruction.
- [ ] Postoperative annotated reconstruction.
- [ ] Clear figure captions and measurement methodology.
- [ ] Final Methods/Measurements response ≤200 words.
- [ ] Qualitative pressure/velocity graph for the separate flow-behaviour task.
- [ ] Resistance-method answer ≤50 words.

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

- [ ] STL identity/checksum.
- [ ] Gmsh characteristic length.
- [ ] Classification angle and meshing algorithm.
- [ ] Node and cell counts.
- [ ] Element order and type.
- [ ] Maximum aspect ratio.
- [ ] Maximum non-orthogonality and number above 70°.
- [ ] Maximum skewness and minimum volume.
- [ ] Statement that the current mesh has tetrahedra but no dedicated prism
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

- [ ] Area-averaged kinematic pressure on both resistance planes.
- [ ] Dimensional pressure difference using a documented air density.
- [ ] Volumetric flow through the section.
- [ ] Local resistance `R = ΔP / Q`.
- [ ] Area-averaged axial velocity on the selected section.
- [ ] Flow rate through each outlet.
- [ ] Combined left- and right-lung flow fractions.
- [ ] Peak velocity in a defined region, if selected for mesh sensitivity.

Prefer an OpenFOAM function object or scripted ParaView/Python workflow over
manual GUI readings.

## 4.6 Test 1000 additional iterations

- [ ] Record the selected axial-velocity value at iteration 2000.
- [ ] Continue from the converged field for 1000 iterations.
- [ ] Record the same value at iteration 3000.
- [ ] Calculate absolute and percentage change.
- [ ] Confirm no reinitialisation occurred.

## 4.7 Produce final steady figures

- [ ] Velocity field on a defined plane or centre surface.
- [ ] Pressure field with clear kinematic or dimensional units.
- [ ] Residual history.
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
| Coarse | 0.35 mm | Establish low-resolution trend |
| Baseline | 0.25 mm | Existing comparison point |
| Fine | 0.15 mm | Dense reference |

Adjust sizes if cell counts or memory use become impractical, but preserve a
clear refinement sequence.

## 5.2 Generate and validate every mesh locally

For every level:

- [ ] Generate with `create_volume_mesh.sh` or a generalised multi-mesh runner.
- [ ] Use the same postoperative STL and physical-surface definition.
- [ ] Inspect physical groups in Gmsh.
- [ ] Confirm `inlet`, `outlet_1`, `outlet_2`, `outlet_3`, `wall`, and `fluid`.
- [ ] Record element count and complete mesh-quality metrics.
- [ ] Reject meshes with invalid topology or unacceptable quality.

Changing only `MESH_SIZE` should not alter physical groups, but verification is
still mandatory.

## 5.3 Run every mesh with identical physics

- [ ] Use identical material properties and boundary conditions.
- [ ] Use identical solver schemes, convergence criteria, and maximum iterations.
- [ ] Set `numberOfSubdomains` equal to `NPROCS`.
- [ ] Run remotely using unique case names.
- [ ] Reconstruct and fetch every result.
- [ ] Record runtime and memory use.

Suggested names:

```text
postop_coarse
postop_baseline
postop_fine
```

## 5.4 Extract identical parameters

Use the frozen Assignment 4 sections and scripts. Recommended primary
parameters:

- [ ] Pre-bifurcation local resistance.
- [ ] Left/right lung flow split.
- [ ] Area-averaged axial velocity at the fixed section.

Optional secondary parameters:

- [ ] Peak velocity in a defined region.
- [ ] Pressure drop across the fixed section.
- [ ] Wall shear stress only if near-wall mesh treatment is adequate.

## 5.5 Create sensitivity data and plots

- [ ] Create `assignment/data/mesh_sensitivity.csv` with one row per mesh.
- [ ] Plot every parameter versus number of volume elements.
- [ ] Calculate percentage difference from the densest mesh:

```text
δ_i = |φ_i - φ_dense| / |φ_dense| × 100%
```

- [ ] Plot percentage difference versus element count for every parameter.
- [ ] Use consistent units, labels, and significant figures.
- [ ] Select an acceptance threshold before declaring an optimal mesh.

## 5.6 Choose the optimal mesh

- [ ] Select the coarsest mesh satisfying the acceptance criterion for all
      primary parameters.
- [ ] Compare accuracy gain with runtime and memory increase.
- [ ] Explain any non-monotonic convergence.
- [ ] Package the accepted Gmsh/OpenFOAM equivalents requested for submission.

## 5.7 Optional mesh-quality improvement gate

The current mesh has no prism layers. Before finalising the study, decide:

- [ ] Whether Assignment 5 parameters are sufficiently integral/bulk quantities
      for the tetrahedral approach.
- [ ] Whether boundary-layer elements are needed for wall shear stress claims.
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

- [ ] Obtain the prescribed course waveform or document the source of a chosen
      physiological waveform.
- [ ] Store time and volumetric flow rate in a versioned table.
- [ ] Plot the exact waveform before implementing it.
- [ ] Confirm sign convention for inspiration and expiration.
- [ ] Confirm total cycle duration and tidal volume.

Suggested artifact:

```text
openFOAM/postop_transient/constant/boundaryData/
assignment/data/breathing_waveform.csv
```

## 6.2 Configure the transient OpenFOAM case

- [ ] Copy the selected optimal steady case to `postop_transient`.
- [ ] Select and document the transient incompressible solver.
- [ ] Implement the time-varying inlet flow boundary condition.
- [ ] Review outlet conditions for flow reversal during expiration.
- [ ] Retain no-slip rigid walls unless an approved extension is undertaken.
- [ ] Initialise from a suitable converged steady field where physically valid.
- [ ] Configure residual/function-object output for every time step.

## 6.3 Select time step and run temporal checks

- [ ] Estimate time step from mesh scale, peak velocity, and target Courant
      number.
- [ ] Run a short pilot around peak flow.
- [ ] Monitor maximum Courant number.
- [ ] Check convergence within every time step.
- [ ] Adjust time step, inner correctors, relaxation, or linear solvers as needed.
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

1. [ ] Create `assignment/assignment_1_notes.md` and complete the structured
       second reading of Taherian et al.
2. [ ] Draft the five Assignment 1 sections and select no more than three
       figures.
3. [ ] Review the Assignment 2 lecture and submit the prepared questions.
4. [ ] Freeze the postoperative geometry and complete/freeze the preoperative
       geometry.
5. [ ] Perform Assignment 3 cross-sectional measurements and annotated figures.
6. [ ] Build automated Assignment 4 residual, patch-flow, and resistance
       extraction before launching more meshes.
7. [ ] Run at least three Assignment 5 mesh levels with identical physics.
8. [ ] Select the optimal mesh.
9. [ ] Configure and validate the Assignment 6 transient breathing-cycle case.

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
