# Computational Biofluid Mechanics — Assignment Specification

**Academic year:** 2025–2026  
**Student:** Henri Van Overmeire

This file is the consolidated, text-accessible specification for the complete
course assignment. The original PDF documents remain the authoritative source.
Requirements from additional PDFs can be added to the placeholders below.

## Source documents

| ID | Source document | Extracted | Notes |
|---|---|---:|---|
| A1 | `Intermediate_Report_Assignment_1.pdf` | Yes | Structured critical analysis of a selected CFD paper |
| A2 | Ufora/Teams assignment instructions | Yes | Guest lecture and preparation/submission of two questions |
| A3 | `Intermediate_Report_Assignment_3.pdf` | Yes | Segmentation, measurements, qualitative flow behaviour, and resistance |
| A4 | `Intermediate_Report_Assignment_4.pdf` | Yes | Postoperative steady-state simulation |
| A5 | `Intermediate_Report_Assignment_5.pdf` | Yes | Postoperative mesh-sensitivity study |
| A6 | `Intermediate_Report_Assignment_6.pdf` | Yes | Postoperative transient simulation |
| TBD | Additional course PDF(s) | No | Backfill when available |

## General presentation requirements

The Assignment 3 source explicitly requires all figures and tables to be:

- High quality.
- Complete.
- Numbered.
- Accompanied by clear captions.

Any general course-wide requirements from other documents should be added here.

## Approved computational toolchain

The teaching staff has explicitly permitted use of the following alternatives
to the software named in the original assignment documents:

- 3D Slicer for segmentation and anatomical measurements.
- Gmsh for surface classification and volume meshing.
- OpenFOAM for steady and transient CFD.
- The student's own local and remote compute infrastructure.

This permission changes only the implementation tools and accepted equivalent
computational artifacts. It does **not** change the scientific questions,
required analyses, figures, formulas, word limits, grading allocation, or
submission intent of any assignment.

---

# Assignment 1A — CFD Paper

**Source:** `Intermediate_Report_Assignment_1.pdf`

Identify and critically evaluate the selected paper's main research question,
methods, results, limitations, and success in answering the research question.
Structure the submission under exactly these headings:

1. **Goal** — maximum 150 words.
2. **Methods** — maximum 150 words.
3. **Results** — maximum 150 words.
4. **Limitations** — maximum 150 words.
5. **Evaluation** — maximum 150 words.

A maximum of three figures may be included if relevant to the methods or
results. Every figure must have a number, caption, and reference.

## Selected paper

Taherian, S., Rahai, H., Gomez, B., Waddington, T., and Mazdisnian, F. (2017).
“Computational fluid dynamics evaluation of excessive dynamic airway
collapse.” *Clinical Biomechanics*, **50**, 145–153.
https://doi.org/10.1016/j.clinbiomech.2017.10.018

**Repository file:** `arcticle.pdf` (filename retained as provided).

## Initial extraction notes

- **Goal:** Evaluate patient-specific airflow in excessive dynamic airway
  collapse before and after airway stenting, including whether CFD reveals
  functional changes not captured sensitively by standard pulmonary function
  tests.
- **Methods:** Four CT-derived geometries represent pre-/post-stent inspiration
  and expiration. The authors used unsteady RANS with a low-Reynolds-number
  $k$–$\omega$ model, patient-specific outlet conditions derived from lobar
  volume changes, polyhedral/prism meshes, and mesh-independence checks.
- **Main results:** Post-stenting expiration showed lower pressure loss, velocity
  magnitude, and mean wall shear stress; inspiratory changes were comparatively
  small. CFD indicated improvement despite limited spirometric sensitivity.
- **Prominent limitations:** One patient, rigid endpoint geometries instead of
  moving walls, incomplete distal airway generations, uncertain structural
  properties, and modelling/boundary-condition assumptions.
- **Evaluation task:** Judge whether the methods and evidence adequately answer
  the stated clinical/flow question without overstating generalisability.

---

# Assignment 2 — Questions for the CFD Guest Lecture

## Instructions

1. Watch the guest lecture by Prof. Joris Degroote on the theoretical
   background of CFD. The recording and slides are available on Ufora under:
   `Assignments → Assignment 2 → Lecture for Assignment 2`.
2. Prepare two good questions to ask.
3. Add the questions to the shared Microsoft Teams file under:
   `Teams → UF25 E092923A - Computational Bio-Fluid Mechanics → Files →
   Assignment2_add_your_questions_here`.

No word limit or grading allocation has been provided for this assignment.

## Selected questions

1. **Validity of incompressibility in stenotic bronchi**  
   How should the validity of the incompressible-flow assumption for air be
   assessed in stenotic bronchi? In particular, should it be evaluated from the
   expected local Mach number, and why do different sources use Mach-number
   limits of approximately 0.1 versus 0.3?

2. **Origin of hyperbolic and elliptic terminology**  
   What is the mathematical origin of the terms *hyperbolic* and *elliptic*
   when classifying partial differential equations, and how is this
   classification related to the corresponding conic sections?

## Deliverables

- [ ] Watch the lecture recording and/or review the slides.
- [x] Prepare two questions.
- [ ] Add both questions to the designated Microsoft Teams file.

---

# Assignment 3 — Segmentation and Measurements

**Source:** `Intermediate_Report_Assignment_3.pdf`  
**Total:** 10 points

## 3.1 Methods: segmentation and measurements

**Maximum length:** 200 words  
**Weight:** 4 points

### Requirements

1. **Segmentation and reconstruction — 2 points**
   - Describe the segmentation process.
   - Include a clear image of the 3D reconstruction of the preoperative case.
   - Include a clear image of the 3D reconstruction of the postoperative case.

2. **Anatomical measurements — 1 point**
   - Measure the length of the constricted region in the preoperative case.
   - Measure the minimum diameter of the constricted region in the
     preoperative case.
   - Measure the diameter in the postoperative case at the same anatomical
     location as in the preoperative case.
   - Clearly indicate these measurements on the 3D reconstructions.

3. **Degree of constriction — 1 point**
   - Calculate the degree of constriction as a percentage.
   - Select the definition/formula thoughtfully.
   - State the formula explicitly.
   - Explain the reasoning behind the selected formula.

4. Ensure that all figures are numbered and have clear captions.

### Candidate constriction definitions

The assignment asks the student to choose and justify the formula. An area-based
measure is physically relevant to flow:

```text
area constriction (%) = (1 - A_pre,min / A_reference) × 100
```

If only diameters are measured and circular cross-sections are assumed:

```text
area constriction (%) = [1 - (D_pre,min / D_reference)²] × 100
```

A diameter-based measure is an alternative, but it describes diameter reduction
rather than lumen-area reduction:

```text
diameter constriction (%) = (1 - D_pre,min / D_reference) × 100
```

The final submission must identify the reference diameter/area unambiguously.
For the requested pre-/postoperative comparison, the postoperative section at
the same anatomical location is a possible reference, provided this choice is
justified.

## 3.2 Flow behaviour

**Maximum length:** 100 words  
**Weight:** 4 points

The source document provides a sketch of an approximately constant-diameter
tube with an incoming flow jet followed by a constricted region resembling the
preoperative case.

### Requirements

1. **Velocity — 1 point**
   - Draw the qualitative velocity before, throughout, and after the
     constriction on the provided graphs.
   - Identify the simple physical law on which this behaviour is based.

2. **Pressure before the constriction — 1 point**
   - Explain what happens to pressure in the approximately constant-diameter
     section before the constriction.
   - Give an equation that explains the behaviour.
   - Identify the force responsible for the behaviour.

3. **Pressure through the constriction — 1 point**
   - Explain what happens to pressure through the constriction in relation to
     the velocity change.
   - Identify the physical principles and/or mathematical equations governing
     the pressure–velocity behaviour.

4. **Pressure after the constriction — 1 point**
   - Explain what happens to pressure downstream, given the expected velocity
     behaviour.

### Relevant theory to address

- Conservation of mass/continuity: `Q = A U` for incompressible flow.
- Viscous pressure loss in a constant-diameter section.
- Bernoulli conversion between static pressure and kinetic energy.
- Irreversible losses caused by viscosity, separation, mixing, and potentially
  transitional or turbulent flow.
- Partial rather than complete pressure recovery downstream of an expansion.

## 3.3 Resistance

**Maximum length:** 50 words  
**Weight:** 2 points

### Requirement

Explain how the local resistance of the preoperative constriction can be
estimated using CFD results and how the calculation would be performed.

A suitable method is to calculate area-averaged pressure immediately upstream
and downstream of the constriction and divide the local pressure drop by the
volumetric flow rate:

```text
R_constriction = (p̄_upstream - p̄_downstream) / Q
```

The exact cross-section locations and pressure definition must be stated. If a
dimensionless local-loss coefficient is reported, define the reference velocity
and use:

```text
K = Δp / (0.5 ρ U_ref²)
```

---

# Assignment 4 — Steady-State Simulation of Postoperative Case

**Source:** `Intermediate_Report_Assignment_4.pdf`  
**Total:** 10 points

All figures and tables must be high quality and complete, have numbers and clear
captions, and be referred to in the text.

## 4.1 Methods: meshing

**Weight:** 2 points

1. **Mesh table — 1 point**
   - Provide a table with relevant mesh parameters.
   - Include element size, number, and type.
   - Include enough information for another researcher to replicate the mesh.

2. **Near-boundary elements — max. 100 words, 1 point**
   - Explain why different elements are used near boundaries.

> **Toolchain interpretation:** The current Gmsh mesh uses first-order
> tetrahedra and does not yet include dedicated prism/inflation layers. The
> report must describe the actual mesh rather than imply otherwise, discuss the
> purpose of boundary-layer elements, and treat their absence as a modelling
> limitation or add them before the final study.

## 4.2 Methods: simulation setup

**Weight:** 4 points

1. **Fluid and boundary conditions — max. 100 words, 2.5 points**
   - Describe relevant material properties of the fluid — 0.5 points.
   - Describe boundary conditions — 2 points.
   - Use references where needed.

2. **Residuals and convergence — max. 100 words, 1 point**
   - Include a residual figure.
   - Explain how convergence was assessed.
   - State whether the simulation is considered converged.

3. **Additional iterations — max. 50 words, 0.5 points**
   - If axial velocity is calculated as a parameter of interest from the
     current solution, explain how adding 1000 iterations would affect it.

## 4.3 Results

**Weight:** 3 points

1. **Flow, pressure, and lung distribution — max. 100 words, 2 points**
   - Visualise flow behaviour.
   - Visualise pressure behaviour.
   - Calculate flow distribution between the left and right lungs — 1 point.
   - Explain why the distribution is equal or unequal — 1 point.

2. **Local resistance — max. 100 words, 1 point**
   - Use CFD results to calculate local resistance across a section before the
     bifurcation, corresponding approximately to the preoperative constriction
     location.
   - Indicate this section visually.
   - State the formula clearly.

## 4.4 Future work

**Maximum length:** 100 words  
**Weight:** 1 point

Select and justify the parameters of interest for the mesh-sensitivity analysis
in Assignment 5.

## OpenFOAM-equivalent deliverables

Under the approved toolchain, the steady solution, logs, reconstructed fields,
Gmsh mesh, OpenFOAM dictionaries, and reproducible scripts serve as equivalents
to proprietary solver project files. All requested physical quantities and
figures remain mandatory.

---

# Assignment 5 — Mesh Sensitivity Study of Postoperative Case

**Source:** `Intermediate_Report_Assignment_5.pdf`  
**Total:** 10 points

## Submission requirement

Individually submit the Fluent `.cas` and `.dat` files of the steady simulation
with the final mesh to Assignment 5 on Ufora.

> **Approved alternative:** The teaching staff has permitted 3D Slicer, Gmsh,
> OpenFOAM, and independent compute infrastructure. Therefore, submit the
> accepted OpenFOAM/Gmsh equivalents of the requested Fluent `.cas`/`.dat`
> artifacts while preserving the same steady-simulation content and scientific
> requirements. Confirm the exact packaging/naming expected on Ufora if it is
> not specified separately.

All figures and tables must be high quality and complete, have numbers and clear
captions, and be referred to in the text.

## 5.1 Results

**Maximum length:** 150 words  
**Weight:** 4 points

1. **Parameter-versus-mesh-size plots — 2 points**
   - Plot the mesh-sensitivity results using X–Y plots.
   - Put the number of mesh elements on the x-axis.
   - Put a parameter of interest on the y-axis.
   - Produce a plot for every selected parameter of interest.

2. **Percentage-difference plots — 2 points**
   - Compare each mesh's parameter value with the value from the densest mesh.
   - Calculate and plot the percentage difference for every parameter of
     interest.
   - State the formula used to calculate the percentage difference.

A suitable signed or absolute relative difference must be explicitly defined.
For example, the absolute difference relative to the densest mesh is:

```text
percentage difference = |φ_i - φ_dense| / |φ_dense| × 100
```

## 5.2 Discussion

**Maximum length:** 100 words  
**Weight:** 2 points

- Interpret the mesh-sensitivity results.
- Identify the optimal mesh.
- Justify the trade-off between accuracy/mesh independence and computational
  cost.

## 5.3 Limitations

**Weight:** 2 points

1. **Current modelling approach — max. 150 words, 1 point**
   - Discuss limitations of the current model.
   - Explain how the model could be made more realistic.

2. **Expanded mesh-sensitivity study — max. 100 words, 1 point**
   - Explain how the study could be expanded with more time and computational
     resources.

## 5.4 Interpretation

**Maximum length:** 100 words  
**Weight:** 2 points

Assume that a time-varying inlet velocity is applied to the postoperative
geometry and increases during inspiration. Restrict the interpretation to the
postoperative airway before the bifurcation and simplify it as a
constant-diameter tube.

Using the definition of resistance from Assignment 3 and the relationship
between pressure drop and flow rate in a constant-diameter tube:

- Draw and/or explain the expected time-dependent resistance during this period
  of inspiration.

---

# Assignment 6 — Transient Simulation of Postoperative Case

**Source:** `Intermediate_Report_Assignment_6.pdf`  
**Total:** 10 points

All figures and tables must be high quality and complete, and have numbers and
clear captions.

## 6.1 Methods

**Weight:** 3.5 points

1. **Simulation setup — 1.5 points**
   - Describe material properties.
   - Describe boundary conditions.
   - Describe other relevant simulation setup choices.
   - Describe solver settings, including time-step size.

2. **Residuals and transient convergence — 2 points**
   - Discuss residual evolution for the transient postoperative simulation.
   - Explain how convergence was assessed.
   - State whether convergence was reached in every time step.
   - If not, identify the time steps that did not converge.

## 6.2 Results

**Weight:** 5.5 points

1. **Velocity-vector visualisation — 1.5 points**
   - Visualise flow patterns using velocity vectors coloured by velocity
     magnitude.
   - Show three relevant time points.
   - Explain why those time points were selected.

2. **Time-varying local resistance — 2 points**
   - Use CFD results to plot local resistance through a complete breathing
     cycle.
   - Use the same anatomical section as in the steady case from Assignment 4.
   - Compare the result with the expected resistance of a constant-diameter
     tube from Assignment 5.
   - Explain why the simulated behaviour is or is not the same.

3. **Breathing profile and qualitative comparison — 2 points**
   - Create a figure showing the time-varying inlet flow rate used as the
     boundary condition.
   - Sketch the corresponding qualitative time-varying local resistance for
     both the preoperative and postoperative cases.
   - Explain the difference in resistance behaviour between the two cases.

## 6.3 Discussion

**Weight:** 1 point

If convergence was not reached in every time step, explain how the problem
would be addressed with additional time and computational resources.

---

# Final report requirements — To be extracted

> Consolidate requirements that apply to the final course report, including
> page limits, required sections, expected comparisons, grading criteria,
> deadline, submission format, and naming conventions.

## Deliverables

- [ ] To be added.

---

# Administrative requirements — To be extracted

- Submission deadline: **TBD**
- Submission platform: **TBD**
- Required file format: **TBD**
- File naming convention: **TBD**
- Individual/group assignment: **TBD**
- Permitted software and external resources: **TBD**
- Data privacy requirements: **TBD**

## Backfilling procedure

For each additional PDF:

1. Add it to the source-document table.
2. Preserve its assignment number and exact section names.
3. Transcribe every requested deliverable.
4. Record all word/page limits and point allocations.
5. Separate explicit requirements from suggested solution methods.
6. Add corresponding rows to `STATUS.md`.
7. Keep the original PDF as the authoritative reference.
