# Assignment Completion Status

**Project:** Patient-specific airway CFD in tracheomalacia  
**Student:** Henri Van Overmeire  
**Specification:** [`ASSIGNMENT.md`](ASSIGNMENT.md)  
**Report source:** [`../report/report/report.tex`](../report/report/report.tex)
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
| Preoperative anatomy | ✅ | Segmentation, measurements, and annotated report figures are complete |
| Postoperative anatomy | ✅ | Segmentation, selected-mesh steady CFD, and report figures are complete |
| Baseline CFD simulation | ✅ | Converged 2 L/min result, residuals, pressure, velocity, resistance, and outlet distribution are documented |
| Fine-mesh CFD simulation | ✅ | Four-level HXT sensitivity study completed; 0.15 mm selected as the accuracy/cost compromise |
| Assignment 3 response | ✅ | Numerical, written, and illustrated requirements are integrated in the report |
| Assignment 4 response | ✅ | Selected 0.15 mm HXT results and resistance-plane visualization are complete; the unexecuted extra-iteration test is reported transparently |
| Assignment 5 response | 🟡 | Numerical analysis, plots, discussion, limitations, and mesh selection are complete; submission packaging remains |
| Assignment 6 response | ✅ | One-cycle postoperative coarse-grid transient proof of concept and required analyses are complete |
| Final LaTeX report | ✅ | Report content is populated and builds; remaining limitations and unavailable provenance are stated explicitly |

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
| Goal, max. 150 words | ✅ | Final 97-word section in `ASSIGNMENT_1.md` and `report/report/report.tex` | None |
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
| Describe segmentation process | ✅ | Final assignment-specific methods draft in `ASSIGNMENT_3.md` describes both case workflows and manual preop lung removal | None |
| Preoperative 3D reconstruction | ✅ | Consistently oriented, annotated reconstruction is included in the report | None |
| Postoperative 3D reconstruction | ✅ | Consistently oriented postoperative comparison is included in the report | None |
| Measure preoperative constriction length | ✅ | Accepted centerline path; `preop_stenosis_summary.json`: 12.157 mm | None |
| Measure preoperative minimum diameter | ✅ | Accepted centerline-normal section: minimum Feret 0.798 mm, equivalent diameter 1.519 mm, area 1.813 mm² | None |
| Measure postoperative diameter at normalized centerline-matched location | ✅ | Section at 76.53% inlet-to-carina: area 5.169 mm², minimum Feret 2.292 mm, equivalent diameter 2.565 mm | None |
| Calculate cross-scan deficit | ✅ | Preoperative area deficit 64.9%; minimum-Feret deficit 65.2%; recorded in `stenosis_comparison.json` | None |
| Explain comparison formula | ✅ | Report uses area because continuity depends on area, while explicitly distinguishing this cross-scan deficit from conventional within-scan stenosis severity | None |
| Number and caption all figures | ✅ | Final images, numbering, labels, and captions are integrated | None |
| Respect 200-word limit | ✅ | Final methods/measurements response is 194 words | None |

### Measurements to record

| Quantity | Symbol | Value | Units | Measurement method/location |
|---|---|---:|---|---|
| Preoperative constriction length | `L_pre` | 12.157 | mm | Centerline arc length between accepted stenosis endpoints |
| Preoperative minimum Feret diameter | `D_pre,min` | 0.798 | mm | Minimum centerline-normal section |
| Preoperative equivalent diameter | `D_pre,eq` | 1.519 | mm | `2 sqrt(A/pi)` at minimum section |
| Postoperative minimum Feret diameter | `D_post,matched` | 2.292 | mm | Centerline-normal section at 76.53% inlet-to-carina position |
| Postoperative equivalent diameter | `D_post,eq` | 2.565 | mm | `2 sqrt(A/pi)` at matched section |
| Preoperative minimum area | `A_pre,min` | 1.813 | mm² | Minimum sampled centerline-normal area |
| Postoperative matched area | `A_post,matched` | 5.169 | mm² | Same normalized anatomical position |
| Cross-scan preoperative area deficit | `C_A` | 64.9 | % | `(1 - A_pre,min/A_post,matched) × 100`; not conventional stenosis severity |
| Cross-scan minimum-Feret deficit | `C_D,Feret` | 65.2 | % | `(1 - D_pre,Feret/D_post,Feret) × 100` |

## 3.2 Flow behaviour — 4 points, max. 100 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Draw qualitative velocity behaviour | ✅ | Reproducible vector figure `report/report/figures/assignment3_flow_behavior.pdf` | None |
| State physical law for velocity | ✅ | Continuity equation included in final 97-word response | None |
| Explain pressure before constriction | ✅ | Viscous pressure gradient and Hagen–Poiseuille relation included | None |
| Explain pressure through constriction | ✅ | Bernoulli conversion and irreversible loss included | None |
| Explain pressure after constriction | ✅ | Partial recovery and dissipation included | None |
| Respect 100-word limit | ✅ | Final response is 97 words in `ASSIGNMENT_3.md` | None |

### Required figure annotations

- [x] Velocity trend before the constriction.
- [x] Velocity increase through the constriction.
- [x] Velocity decrease downstream.
- [x] Pressure decline before the constriction due to viscous resistance.
- [x] Additional pressure reduction through the constriction.
- [x] Partial pressure recovery after the constriction.
- [x] Clear flow direction and axial-position axis.
- [x] Figure number and complete caption.

## 3.3 Resistance — 2 points, max. 50 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Explain CFD-based local resistance estimate | ✅ | Final 47-word method in `ASSIGNMENT_3.md` defines planes, averages, flow integration, and `R = ΔP/Q` | None for Assignment 3 |
| Define upstream pressure section | 🟡 | Method specifies an immediate upstream centerline-normal plane | Exact plane is selected computationally in Assignment 4 |
| Define downstream pressure section | 🟡 | Method specifies an immediate downstream centerline-normal plane | Exact plane is selected computationally in Assignment 4 |
| Calculate area-averaged pressures | N/A | Assignment 3 asks how resistance would be estimated | Actual calculation belongs to Assignment 4 |
| Calculate local resistance | N/A | Assignment 3 asks for the method, not a numerical result | Actual calculation belongs to Assignment 4 |
| Respect 50-word limit | ✅ | Final response is 47 words | None |

---

# Assignment 4 status

## 4.1 Methods: meshing — 2 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Replicable table of element size, number, and type | ✅ | `ASSIGNMENT_4.md` records the 0.25 mm mesh: Gmsh version, hashes, 44,383 nodes, 209,652 tetrahedra, quality metrics, patches, and region count | None |
| Explain use of different near-boundary elements, max. 100 words | ✅ | Final 82-word response in `ASSIGNMENT_4.md` explains prism-layer purpose and honestly states their absence | None |

## 4.2 Methods: simulation setup — 4 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Fluid properties, max. 100 words section | ✅ | `nu=1.5e-5 m²/s`, `rho=1.204 kg/m³`, Newtonian incompressible laminar model, and Reynolds-number justification documented | None |
| Boundary conditions | ✅ | Selected case uses 2 L/min inlet, no-slip wall, and equal zero-pressure outlets | None |
| Residual figure and convergence, max. 100 words | ✅ | Selected 0.15 mm HXT run converged at iteration 1611; residual history and mass balance are documented | None |
| Effect of 1000 additional iterations, max. 50 words | ✅ | Expected negligible effect is explained; continuation was not executed and no unsupported numerical change is claimed | None |

## 4.3 Results — 3 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Visualise flow | ✅ | Reproducible selected-mesh full-lumen velocity-vector render at iteration 1611 with fixed 0–10 m/s scale | None |
| Visualise pressure | ✅ | Selected-mesh frontal dimensional-pressure map and centerline pressure profile generated in Pa | None |
| Calculate left/right lung flow distribution | ✅ | Right 73.686%, left 26.314%; exact patch flows and mass balance saved in `postop_hxt_015_flow_distribution.json` | None |
| Explain equal/unequal distribution | ✅ | Final response attributes split under equal outlet pressure to resolved branch geometry and resistance | None |
| Define pre-bifurcation resistance section | ✅ | Superior, matched, and inferior centerline-normal planes frozen in `resistance_sections.json` | None |
| Calculate and visualise local resistance, max. 100 words | ✅ | Selected-mesh ΔP 35.21 Pa and conservative-flux resistance 1.0565e6 Pa·s/m³ are documented and visualized | None |

## 4.4 Future work — 1 point, max. 100 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Select mesh-sensitivity parameters | ✅ | `ASSIGNMENT_4.md` selects outlet fractions, local pressure drop/resistance, mean axial velocity, and peak velocity with justification | None |

---

# Assignment 5 status

## Submission

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Individually submit accepted final steady solver artifacts to Ufora | ⬜ | Teaching staff approved 3D Slicer, Gmsh, OpenFOAM, and own infrastructure | Package final mesh, case dictionaries, reconstructed solution, logs, and reproducibility metadata as instructed |

## 5.1 Results — 4 points, max. 150 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Run multiple postoperative mesh resolutions | ✅ | HXT cases completed at 0.25, 0.20, 0.15, and 0.12 mm; all reconstructed and fetched | None |
| Record number of elements for every mesh | ✅ | 180,163; 339,886; 776,568; and 1,493,440 cells recorded | None |
| Select parameters of interest | ✅ | Fixed metrics: local resistance, right-lung fraction, right-superior share of right flow, and matched-section peak velocity | None |
| Plot each parameter against element count | ✅ | Gnuplot/cairolatex 2×2 metric figure generated and integrated | None |
| Calculate differences relative to densest mesh | ✅ | All four metrics compared with 0.12 mm; densest non-convergence explicitly qualified | None |
| Plot percentage differences | ✅ | Gnuplot/cairolatex difference figure generated and integrated | None |
| State exact percentage-difference formula | ✅ | `|phi_i-phi_dense|/|phi_dense| × 100%` stated | None |
| Respect 150-word limit | ✅ | Final results response in `ASSIGNMENT_5.md` is within limit | None |

## 5.2 Discussion — 2 points, max. 100 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Interpret mesh-sensitivity results | ✅ | Resistance and small-branch split identified as most sensitive; densest non-convergence discussed | None |
| Identify and justify optimal mesh | ✅ | 0.15 mm selected using 2.5% criterion and efficiency trade-off | None |
| Respect 100-word limit | ✅ | Final discussion response in `ASSIGNMENT_5.md` is within limit | None |

## 5.3 Limitations — 2 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Discuss current-model limitations, max. 150 words | ✅ | Final case-specific 130-word limitations response | None |
| Explain how to make model more realistic | ✅ | Transient flow, compliant walls, distal impedance, uncertainty and validation addressed | None |
| Explain expanded mesh study, max. 100 words | ✅ | Final 95-word expansion response covers local refinement, convergence, layers and GCI | None |

## 5.4 Interpretation — 2 points, max. 100 words

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Draw/explain resistance during increasing inspiratory flow | ✅ | Final explanation predicts constant resistance for ideal Poiseuille flow | None |
| Connect `R = Δp/Q` with constant-diameter pressure–flow relation | ✅ | Derivation and patient-specific deviations documented | None |
| Respect 100-word limit | ✅ | Final interpretation response is within limit | None |

---

# Assignment 6 status

## 6.1 Methods — 3.5 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Configure transient postoperative simulation | ✅ | Complete 2 s `pimpleFoam` PoC on the 0.25 mm HXT mesh; exact fallback controls documented | None; production-mesh run remains future work |
| Define material properties | ✅ | Incompressible Newtonian air; `ν = 1.5e-5 m²/s`, `ρ = 1.204 kg/m³` for dimensional pressure | Add final citation for density |
| Apply time-varying breathing inlet profile | ✅ | Versioned sinusoidal table and generator; ±6.283 L/min peak | None |
| Document all boundary conditions | ✅ | Flow-rate inlet, reversal-capable pressure outlets, no-slip wall documented in report | None |
| Select and document time-step size | ✅ | Final PoC: initial 1e-5 s, adaptive maximum 2e-4 s, `maxCo=5`; observed 3.287e-6–2.019e-4 s | Temporal-independence study remains a limitation |
| Discuss residual evolution | ✅ | Full 904 MB log parsed; Courant/timestep figure and quantitative convergence discussion integrated | None |
| Define convergence assessment | ✅ | Outer and linear criteria, continuity, Courant control, and timestep status assessed over complete cycle | None |
| Identify unconverged time steps | ✅ | 617/355,016 did not meet the outer criterion; localized at startup and zero-flow transitions | None |

## 6.2 Results — 5.5 points

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Velocity vectors coloured by magnitude at three time points | ✅ | Common-scale frontal panels at 0.24, 0.50, and 1.50 s integrated into report | None |
| Explain time-point selection | ✅ | Accelerating inspiration, peak inspiration, and peak expiration tied to exact waveform states | None |
| Plot postoperative local resistance over a complete cycle | ✅ | 100 saved states extracted; near-zero-flow values masked at 5% of peak | None |
| Use same section as Assignment 4 | ✅ | `assignment/data/resistance_sections.json` | Reuse unchanged in transient extractor |
| Compare with constant-diameter expectation | ✅ | Computed curve compared with steady reference and ideal constant-resistance reasoning | None |
| Plot applied inlet flow waveform | ✅ | `assignment6_breathing_waveform.tex/.pdf` generated from exact boundary table | None |
| Sketch qualitative pre-/postoperative resistance | ✅ | Explicitly non-computational arbitrary-unit comparison included in cycle-response figure | None |
| Explain pre-/postoperative resistance difference | ✅ | Discussion links the 64.9% cross-scan preoperative area deficit to qualitatively higher expected resistance without presenting it as conventional stenosis severity | None |

## 6.3 Discussion — 1 point

| Requirement | Status | Existing evidence | Remaining work |
|---|---:|---|---|
| Explain how unconverged time steps would be addressed | ✅ | Targeted remedies prioritize lower Courant limit, correctors, periodic initialization, and mesh repair | None |

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
| STL export | ✅ | `segmentation/scripts/export_segmentation.py` → `meshes/<case>/airways.stl` |
| Preoperative final surface verification | ✅ | Cleaned segmentation, refined points, boundary map, measurements, STL, and annotated report figure exist |
| Postoperative final surface verification | ✅ | Workflow and normalized centerline comparison figure are documented |

## Meshing

| Item | Status | Evidence/notes |
|---|---:|---|
| Gmsh geometry definition | 🟡 | Verified postoperative definition in `meshes/postop/airways.geo`; preoperative definition pending |
| Physical inlet/outlet/wall groups | 🟡 | Postoperative IDs verified; preoperative Gmsh cap IDs still require inspection |
| Separate mesh-generation script | ✅ | `create_volume_mesh.sh` |
| Baseline mesh preserved for reproducibility | ✅ | `openFOAM/postop/airways.msh` intended for version control |
| Baseline `checkMesh` metrics recorded in report | ✅ | 0.25 mm HXT metrics are tabulated with limitations |
| Refined meshes generated | ✅ | Four HXT levels from 0.25 to 0.12 mm are archived in results/data |
| Refined `checkMesh` metrics recorded in report | ✅ | All levels are tabulated; poor local quality of the densest mesh is explicit |

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
| Selected steady result interpretation | ✅ | Selected 0.15 mm HXT quantitative results and figures are integrated |
| Refined result interpretation | ✅ | Four-level mesh-sensitivity comparison is integrated |

## Numerical-model checks

| Item | Status | Remaining work |
|---|---:|---|
| Inlet flow rate documented | ✅ | Physiological interpretation and idealized-boundary limitation are stated |
| No-slip wall documented | ✅ | Rigid-wall limitation is explicit |
| Outlet pressure model documented | ✅ | Equal-pressure, geometry-driven split and its limitation are discussed |
| Laminar model documented | ✅ | Steady and transient Reynolds estimates and transitional limitation are stated |
| Solver convergence documented | ✅ | Residual plots, criteria, iteration counts, and transient outer convergence are reported |
| Mass conservation verified | ✅ | Conservative inlet/outlet patch fluxes and imbalance are reported |
| Mesh sensitivity assessed | ✅ | Four integral quantities are compared; mesh independence is not claimed |

---

# Report and evidence checklist

## Figures

- [x] Preoperative 3D reconstruction with constriction length and minimum diameter.
- [x] Postoperative 3D reconstruction with normalized centerline comparison section.
- [x] Qualitative velocity and pressure sketch required by Assignment 3.
- [x] Four-level volume-mesh comparison.
- [x] Selected steady velocity vectors and dimensional pressure distribution.
- [x] Three transient velocity-vector phases with a common scale.
- [x] Centerline and section-based pressure plots.
- [x] Steady and transient solver convergence plots.

## Tables

- [x] Imaging geometry metadata and explicit unknown respiratory phase.
- [x] Segmentation thresholds; unarchived final segmented voxel counts stated transparently.
- [x] Anatomical measurements and cross-scan deficits.
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
