# Assignment Completion Status

**Project:** Patient-specific airway CFD in tracheomalacia  
**Student:** Henri Van Overmeire  
**Specification:** [`ASSIGNMENT.md`](ASSIGNMENT.md)  
**Report source:** [`../report/report.tex`](../report/report.tex)  
**Workflow:** [`../WORKFLOW.md`](../WORKFLOW.md)

This file tracks whether the project has produced the evidence required by the
course assignment. A working processing script does not by itself constitute a
completed report answer: quantitative results, figures, interpretation, and
word-limit compliance must also be present in the final submission.

## Status legend

| Symbol | Meaning |
|---|---|
| ✅ | Complete and documented in the report |
| 🟡 | Partially complete or implemented, but report evidence is incomplete |
| ⬜ | Not started or no evidence available |
| ⚠️ | Blocked, uncertain, or requires verification |
| N/A | Not applicable |

## Overall status

| Area | Status | Summary |
|---|---:|---|
| Course specification extraction | ✅ | Assignments 1–6 are recorded, including manually supplied Assignment 2 |
| Assignment 1 response | ✅ | Five reviewed sections are within 150 words, integrated into LaTeX, and properly cited; optional figures were not used |
| Assignment 2 response | 🟡 | Two questions prepared; lecture review and Teams submission require confirmation |
| Reproducible processing workflow | ✅ | Slicer-to-Gmsh-to-OpenFOAM workflow documented and scripted |
| Preoperative anatomy | 🟡 | Case-specific assets exist, but final report figures and measurements are not documented |
| Postoperative anatomy | 🟡 | Segmentation/CFD pipeline has been exercised; final report evidence remains incomplete |
| Baseline CFD simulation | 🟡 | Simulation and result-fetch workflow work; quantitative findings are not yet entered in the report |
| Fine-mesh CFD simulation | 🟡 | Automated workflow exists; final mesh-independence results are not yet documented |
| Assignment 3 response | 🟡 | Methods infrastructure exists; required concise text, figures, measurements, and calculations remain |
| Assignment 4 response | 🟡 | Steady postoperative OpenFOAM result exists; required post-processing, figures, resistance, and text remain |
| Assignment 5 response | 🟡 | Baseline/fine OpenFOAM workflow exists; plots, quantitative comparison, discussion, and accepted artifact submission remain |
| Assignment 6 response | ⬜ | No transient breathing-cycle simulation or required transient analyses implemented yet |
| Final LaTeX report | 🟡 | Template builds successfully; most result placeholders remain |

---

# Assignment 1 status

**Selected paper:** Taherian et al. (2017), “Computational fluid dynamics
evaluation of excessive dynamic airway collapse,” *Clinical Biomechanics* 50,
145–153, https://doi.org/10.1016/j.clinbiomech.2017.10.018.

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Select a scientific paper | ✅ | `assignment/arcticle.pdf` | None |
| Record complete paper citation | ✅ | Citation and DOI recorded in `ASSIGNMENT.md` | None |
| Extract Assignment 1 requirements | ✅ | Five required headings and limits recorded | None |
| Goal, max. 150 words | ✅ | Final 97-word section in `ASSIGNMENT_1.md` and `report/report.tex` | None |
| Methods, max. 150 words | ✅ | Final 129-word section includes geometry, boundary conditions, solver, extensions, and mesh study | None |
| Results, max. 150 words | ✅ | Final 119-word section includes pressure, velocity, wall shear stress, turbulence, and spirometry findings | None |
| Limitations, max. 150 words | ✅ | Final 127-word section distinguishes key model and generalisability limitations | None |
| Evaluation, max. 150 words | ✅ | Final 132-word critical judgement answers the research question with appropriate scope | None |
| Select no more than three figures | N/A | No optional paper figures were used | None |
| Number, caption, and reference figures | N/A | No paper figures were reproduced | None |
| Cite selected paper | ✅ | Full citation and DOI included in Markdown and LaTeX bibliography | None |

---

# Assignment 2 status

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Watch Prof. Joris Degroote's CFD guest lecture | ⚠️ | No confirmation recorded | Watch the recording and/or review the slides on Ufora |
| Prepare question about incompressibility in stenotic bronchi | ✅ | Submission-ready question recorded in `ASSIGNMENT.md` | None unless revised after watching the lecture |
| Prepare question about hyperbolic/elliptic PDE terminology | ✅ | Submission-ready question recorded in `ASSIGNMENT.md` | None unless revised after watching the lecture |
| Submit both questions in the designated Teams file | ⬜ | No submission confirmation recorded | Add both questions to `Assignment2_add_your_questions_here` |

## Selected questions

1. How should the validity of the incompressible-flow assumption for air be
   assessed in stenotic bronchi? In particular, should it be evaluated from the
   expected local Mach number, and why do different sources use Mach-number
   limits of approximately 0.1 versus 0.3?
2. What is the mathematical origin of the terms *hyperbolic* and *elliptic*
   when classifying partial differential equations, and how is this
   classification related to the corresponding conic sections?

---

# Assignment 3 status

## 3.1 Methods: segmentation and measurements — 4 points, max. 200 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Describe segmentation process | 🟡 | `WORKFLOW.md`; segmentation scripts; methods text in `report/report.tex` | Produce a ≤200-word assignment-specific version |
| Preoperative 3D reconstruction | ⬜ | Pipeline and preoperative assets exist | Generate and export a high-quality, consistently oriented figure |
| Postoperative 3D reconstruction | 🟡 | Postoperative CFD surface and STL exist | Export a publication-quality reconstruction figure |
| Measure preoperative constriction length | ⬜ | No final measurement recorded | Measure in Slicer and annotate the figure |
| Measure preoperative minimum diameter | ⬜ | No final measurement recorded | Define measurement plane, measure, and annotate |
| Measure postoperative diameter at matching location | ⬜ | No final measurement recorded | Register/identify corresponding location, measure, and annotate |
| Calculate percentage constriction | ⬜ | Candidate formulas documented in `ASSIGNMENT.md` | Select reference and formula; insert measurements and result |
| Explain constriction formula | ⬜ | Area- and diameter-based options identified | Write concise justification within the word limit |
| Number and caption all figures | ⬜ | LaTeX figure placeholders exist | Add final images, numbers, labels, and complete captions |
| Respect 200-word limit | ⬜ | No final Assignment 3 response yet | Count final prose and revise |

### Measurements to record

| Quantity | Symbol | Value | Units | Measurement method/location |
|---|---|---:|---|---|
| Preoperative constriction length | `L_pre` | TBD | mm | TBD |
| Preoperative minimum diameter | `D_pre,min` | TBD | mm | TBD |
| Postoperative matched diameter | `D_post,matched` | TBD | mm | TBD |
| Preoperative minimum area, if used | `A_pre,min` | TBD | mm² | TBD |
| Postoperative matched area, if used | `A_post,matched` | TBD | mm² | TBD |
| Degree of constriction | `C` | TBD | % | Formula TBD |

## 3.2 Flow behaviour — 4 points, max. 100 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Draw qualitative velocity behaviour | ⬜ | Governing theory included in report template | Annotate the supplied graph/sketch |
| State physical law for velocity | 🟡 | Continuity equation documented | Include in ≤100-word answer |
| Explain pressure before constriction | 🟡 | Viscous-loss discussion outlined | State trend, governing equation, and viscous force clearly |
| Explain pressure through constriction | 🟡 | Bernoulli and continuity principles identified | Write concise explanation including irreversible loss |
| Explain pressure after constriction | 🟡 | Partial pressure recovery identified | Add downstream trend to graph and answer |
| Respect 100-word limit | ⬜ | No final response yet | Draft, count, and revise |

### Required figure annotations

- [ ] Velocity trend before the constriction.
- [ ] Velocity increase through the constriction.
- [ ] Velocity decrease downstream.
- [ ] Pressure decline before the constriction due to viscous resistance.
- [ ] Additional pressure reduction through the constriction.
- [ ] Partial pressure recovery after the constriction.
- [ ] Clear flow direction and axial-position axis.
- [ ] Figure number and complete caption.

## 3.3 Resistance — 2 points, max. 50 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Explain CFD-based local resistance estimate | 🟡 | `R = Δp/Q` documented in assignment and report template | Write final ≤50-word answer |
| Define upstream pressure section | ⬜ | Not selected | Create a plane outside the acceleration region |
| Define downstream pressure section | ⬜ | Not selected | Create a plane after the constriction; document rationale |
| Calculate area-averaged pressures | ⬜ | CFD results can be loaded in ParaView | Integrate pressure over both planes |
| Calculate local resistance | ⬜ | Formula available | Insert `Δp`, `Q`, resistance, and units |
| Respect 50-word limit | ⬜ | No final response yet | Draft, count, and revise |

---

# Assignment 4 status

## 4.1 Methods: meshing — 2 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Replicable table of element size, number, and type | 🟡 | Gmsh settings and `checkMesh` output exist | Consolidate exact final values and software version in a table |
| Explain use of different near-boundary elements, max. 100 words | ⬜ | Current mesh is tetrahedral without dedicated prism layers | Explain boundary-layer purpose honestly and discuss current limitation or add layers |

## 4.2 Methods: simulation setup — 4 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Fluid properties, max. 100 words section | 🟡 | Kinematic viscosity is configured and documented | Verify density/pressure interpretation, cite source, and write final text |
| Boundary conditions | 🟡 | OpenFOAM `0/U` and `0/p` are configured | Summarise and justify each patch condition |
| Residual figure and convergence, max. 100 words | 🟡 | Solver logs have been generated | Parse residuals, plot them, and assess convergence quantitatively |
| Effect of 1000 additional iterations, max. 50 words | ⬜ | No axial-velocity convergence comparison | Evaluate expected/observed change after convergence and draft response |

## 4.3 Results — 3 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Visualise flow | 🟡 | Reconstructed fields fetched for ParaView | Create final velocity figure with defined plane/scale |
| Visualise pressure | 🟡 | Reconstructed pressure field available | Create final pressure figure and state kinematic/dimensional units |
| Calculate left/right lung flow distribution | ⬜ | Three outlet patches available | Integrate outlet fluxes and combine anatomically by lung |
| Explain equal/unequal distribution | ⬜ | No quantitative split recorded | Relate result to geometry and outlet assumptions |
| Define pre-bifurcation resistance section | ⬜ | Assignment specifies approximate pre-op constriction location | Create and save fixed upstream/downstream planes for reuse in Assignment 6 |
| Calculate and visualise local resistance, max. 100 words | ⬜ | Formula documented; fields available | Integrate section pressures/flow, calculate resistance, and annotate location |

## 4.4 Future work — 1 point, max. 100 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Select mesh-sensitivity parameters | 🟡 | Candidate quantities identified in report template | Finalise parameters based on Assignment 4 outputs and justify them |

---

# Assignment 5 status

## Submission

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Individually submit accepted final steady solver artifacts to Ufora | ⬜ | Teaching staff approved 3D Slicer, Gmsh, OpenFOAM, and own infrastructure | Package final mesh, case dictionaries, reconstructed solution, logs, and reproducibility metadata as instructed |

## 5.1 Results — 4 points, max. 150 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Run multiple postoperative mesh resolutions | 🟡 | Baseline and automated fine-mesh workflows exist | Confirm successful final runs and add enough resolutions for a defensible trend |
| Record number of elements for every mesh | ⬜ | Counts may exist in logs | Extract and tabulate final counts |
| Select parameters of interest | ⬜ | Candidate quantities are mentioned in report template | Select final quantities, e.g. pressure drop, peak velocity, resistance, and outlet flow split |
| Plot each parameter against element count | ⬜ | No plots documented | Generate one X–Y plot per parameter |
| Calculate differences relative to densest mesh | ⬜ | Formula documented in `ASSIGNMENT.md` | Calculate values for every non-reference mesh |
| Plot percentage differences | ⬜ | No plots documented | Generate and label percentage-difference plots |
| State exact percentage-difference formula | 🟡 | Candidate formula archived | Include chosen formula in final response |
| Respect 150-word limit | ⬜ | No final response drafted | Draft, count, and revise |

## 5.2 Discussion — 2 points, max. 100 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Interpret mesh-sensitivity results | ⬜ | Fine workflow exists, but no quantitative comparison documented | Interpret convergence trends and anomalous values |
| Identify and justify optimal mesh | ⬜ | No criterion selected | Balance parameter convergence against cell count/runtime |
| Respect 100-word limit | ⬜ | No final response drafted | Draft, count, and revise |

## 5.3 Limitations — 2 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Discuss current-model limitations, max. 150 words | 🟡 | Limitations listed in `report/report.tex` | Tailor discussion to actual model and word limit |
| Explain how to make model more realistic | 🟡 | Candidate improvements identified in report template | Prioritise and justify specific improvements |
| Explain expanded mesh study, max. 100 words | ⬜ | No final response | Discuss additional levels, local refinement, formal convergence metrics, and computational cost |

## 5.4 Interpretation — 2 points, max. 100 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Draw/explain resistance during increasing inspiratory flow | ⬜ | Resistance and viscous pressure-loss equations documented | Produce the requested sketch and concise derivation |
| Connect `R = Δp/Q` with constant-diameter pressure–flow relation | 🟡 | Theory documented in Assignment 3 materials | State expected constant resistance for linear laminar Poiseuille behaviour and relevant caveats |
| Respect 100-word limit | ⬜ | No final response drafted | Draft, count, and revise |

---

# Assignment 6 status

## 6.1 Methods — 3.5 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Configure transient postoperative simulation | ⬜ | Current case is steady `simpleFoam` | Select transient solver and configure the case |
| Define material properties | 🟡 | Steady case uses `ν = 1.5e-5 m²/s` | Verify transient properties and report density if dimensional pressure is used |
| Apply time-varying breathing inlet profile | ⬜ | Current inlet is a constant volumetric flow rate | Obtain/define waveform and implement time-dependent boundary condition |
| Document all boundary conditions | ⬜ | Steady conditions exist only | Define and justify transient inlet/outlet/wall conditions |
| Select and document time-step size | ⬜ | No transient setup | Perform temporal-resolution/Courant-number assessment |
| Discuss residual evolution | ⬜ | No transient run | Export residual history by time step |
| Define convergence assessment | ⬜ | No transient convergence criterion | Specify residual and iteration criteria plus mass conservation checks |
| Identify unconverged time steps | ⬜ | No transient run | Analyse every time step after simulation |

## 6.2 Results — 5.5 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Velocity vectors coloured by magnitude at three time points | ⬜ | No transient fields | Select three relevant phases and create consistent ParaView figures |
| Explain time-point selection | ⬜ | No phases selected | Relate choices to acceleration, peak flow, and deceleration/reversal |
| Plot postoperative local resistance over a complete cycle | ⬜ | No transient simulation or section analysis | Compute section-averaged pressure difference and flow over time |
| Use same section as Assignment 4 | ⚠️ | Assignment 4 has not yet been extracted and section is not documented | Extract Assignment 4 and define reusable section locations |
| Compare with constant-diameter expectation | ⬜ | Assignment 5 theory not yet answered | Explain effects of geometry, inertia, separation, and phase lag |
| Plot applied inlet flow waveform | ⬜ | No waveform selected | Plot exact boundary-condition data |
| Sketch qualitative pre-/postoperative resistance | ⬜ | No sketch | Produce panel B requested by assignment |
| Explain pre-/postoperative resistance difference | ⬜ | No final interpretation | Link stenosis and unsteady losses to expected behaviour |

## 6.3 Discussion — 1 point

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Explain how unconverged time steps would be addressed | ⬜ | No transient convergence study | Discuss smaller time steps, more inner iterations, solver controls, mesh quality, and resources |

---

# Technical workflow status

## Segmentation and geometry

| Item | Status | Evidence/notes |
|---|---:|---|
| Case-specific DICOM loading | ✅ | `segmentation/scripts/segment_airway.py` |
| Case-specific airway seeds/settings | ✅ | `segmentation/assets/preop/` and `segmentation/assets/postop/` |
| Airway segmentation | ✅ | Scripted Slicer workflow |
| Centerline/network calculation | ✅ | `segmentation/scripts/calculate_centerline.py` |
| Refined clipping-point loading | ✅ | `segmentation/scripts/load_cutting_points.py` |
| Clip Vessel-equivalent clipping | ✅ | `segmentation/scripts/cut_airways_centerline.py` |
| Centerline-directed adaptive extensions | ✅ | Implemented through SlicerVMTK logic |
| Flat CFD caps | ✅ | `AirwayExtendedSurfaceCapped` model |
| STL export | ✅ | `segmentation/scripts/export_segmentation.py` → `meshes/airways.stl` |
| Preoperative final surface verification | ⚠️ | Must be visually verified and documented separately |
| Postoperative final surface verification | 🟡 | Workflow validated interactively; report image still needed |

## Meshing

| Item | Status | Evidence/notes |
|---|---:|---|
| Gmsh geometry definition | ✅ | `meshes/airways.geo` |
| Physical inlet/outlet/wall groups | 🟡 | IDs identified for current postoperative STL; must be rechecked after geometry/Gmsh changes |
| Separate mesh-generation script | ✅ | `create_volume_mesh.sh` |
| Baseline mesh preserved for reproducibility | ✅ | `openFOAM/postop/airways.msh` intended for version control |
| Baseline `checkMesh` metrics recorded in report | ⬜ | Add final values to `report/report.tex` |
| Fine mesh generated | 🟡 | Automated in `run_fine_cfd.sh`; confirm final run and archive parameters |
| Fine `checkMesh` metrics recorded in report | ⬜ | Add final values |

## OpenFOAM

| Item | Status | Evidence/notes |
|---|---:|---|
| Docker execution | ✅ | `opencfd/openfoam-default:latest` via `run_cfd.sh` |
| Boundary patch validation | ✅ | Solver refuses to start unless all five expected patches exist |
| Millimetre-to-metre conversion | ✅ | `transformPoints -scale '(0.001 0.001 0.001)'` |
| Parallel decomposition | ✅ | Scotch decomposition; `NPROCS` must match `numberOfSubdomains` |
| Root-capable MPI invocation | ✅ | `--allow-run-as-root --use-hwthread-cpus` |
| `simpleFoam` run | ✅ | Parallel solver workflow validated |
| Result reconstruction | ✅ | `reconstructPar` included |
| Stale-time cleanup | ✅ | Nonzero old times removed while preserving `0/` |
| Result retrieval | ✅ | `fetch_cfd_results.sh` excludes `processor*/` and mirrors deletions |
| Baseline result interpretation | ⬜ | Add ParaView-derived quantitative results and figures |
| Fine result interpretation | ⬜ | Add mesh-independence comparison |

## Numerical-model checks

| Item | Status | Remaining work |
|---|---:|---|
| Inlet flow rate documented | ✅ | Verify physiological scenario and cite source/assumption |
| No-slip wall documented | ✅ | None unless wall-motion limitations are expanded |
| Outlet pressure model documented | ✅ | Discuss equal-pressure outlet assumption |
| Laminar model documented | ✅ | Calculate Reynolds numbers and justify or revise model |
| Solver convergence documented | 🟡 | Logs exist; prepare residual plot and state final residuals |
| Mass conservation verified | ⬜ | Integrate inlet and outlet fluxes |
| Mesh independence verified | ⬜ | Compare integral quantities between baseline and fine cases |

---

# Report and evidence checklist

## Figures

- [ ] Preoperative 3D reconstruction with constriction length and minimum diameter.
- [ ] Postoperative 3D reconstruction with matched-location diameter.
- [ ] Qualitative velocity and pressure sketch required by Assignment 3.
- [ ] Baseline and fine volume-mesh comparison.
- [ ] Preoperative and postoperative velocity magnitude with identical scale.
- [ ] Preoperative and postoperative pressure with identical scale.
- [ ] Centerline or section-based pressure plot.
- [ ] Solver residual/convergence plot.

## Tables

- [ ] Imaging metadata.
- [ ] Segmentation thresholds and voxel counts.
- [ ] Anatomical measurements and constriction percentage.
- [ ] Mesh cell counts and quality metrics.
- [ ] Boundary conditions.
- [ ] Outlet flow rates and fractions.
- [ ] Baseline-versus-fine mesh comparison.

## Reproducibility metadata

- [ ] Final Git commit recorded.
- [ ] Slicer version recorded.
- [ ] SlicerVMTK version recorded.
- [ ] Gmsh version recorded.
- [ ] OpenFOAM image tag and immutable image ID recorded.
- [ ] Baseline and fine `MESH_SIZE` recorded.
- [ ] Baseline and fine cell counts recorded.
- [ ] `NPROCS` recorded.
- [ ] DICOM series identifiers recorded without patient-identifying information.
- [ ] Final boundary mapping verified for each anatomical case.

---

# Additional course assignments

Assignments 2, 3, 5, and 6 are now recorded. PDFs for Assignments 1 and 4 are
present but have not yet been fully extracted into the specification. For every
new or newly extracted source document:

1. Add its requirements to `ASSIGNMENT.md`.
2. Add one status row per independently gradable requirement here.
3. Link each completed requirement to a report section, figure, table, script,
   or result file.
4. Do not mark an item complete solely because code exists; verify that the
   requested deliverable appears in the submitted report.

## Change log

| Date | Change |
|---|---|
| 2026-09-02 | Extracted Assignment 1 and recorded the selected Taherian et al. (2017) paper |
| 2026-09-02 | Recorded approved 3D Slicer/Gmsh/OpenFOAM toolchain and extracted Assignment 4 |
| 2026-09-02 | Extracted Assignments 5 and 6 and added requirement-level status tracking |
| 2026-09-02 | Added Assignment 2 instructions and selected questions; recorded Assignment 1 paper-selection milestone |
| 2026-09-02 | Created tracker and populated Assignment 3 requirements/status |
