# Assignment 1A — CFD Paper

**Henri Van Overmeire**

**Selected paper:** Taherian, S., Rahai, H., Gomez, B., Waddington, T., and
Mazdisnian, F. (2017). “Computational fluid dynamics evaluation of excessive
dynamic airway collapse.” *Clinical Biomechanics*, 50, 145–153.
https://doi.org/10.1016/j.clinbiomech.2017.10.018

## Goal

The study investigated whether patient-specific computational fluid dynamics
could quantify the functional consequences of excessive dynamic airway collapse
and assess improvement after tracheal stenting. The authors specifically
compared inspiratory and expiratory airflow before and after intervention using
CT-derived airway geometries. They aimed to determine how stenting affected
pressure loss, velocity, wall shear stress, and turbulence, and whether these
CFD quantities revealed clinically relevant changes that conventional pulmonary
function tests might miss. The underlying question was therefore not merely
whether the airway lumen became larger, but whether the anatomical intervention
produced a meaningful improvement in respiratory flow behaviour.

## Methods

Four patient-specific airway models represented inspiration and expiration
before and after stenting. CT images were segmented in Mimics and simulated in
STAR-CCM+. Each rigid model included the trachea and approximately six to eight
airway generations. The authors simulated 2.5 s inspiration and 2.5 s expiration
with sinusoidal resting-breathing flow. Patient-specific outlet pressure
functions were derived in a preliminary step from lobar volume changes, while
the inlet was atmospheric with 10% turbulence intensity. Unsteady RANS with a
low-Reynolds-number k–ω model and second-order spatial and temporal schemes was
used. Inlet and outlet extensions measured one and four hydraulic diameters,
respectively. Polyhedral meshes with prism layers were tested at 0.9, 1.7, and
3.2 million cells; 1.7 million cells was selected from pressure, velocity, and
wall-shear-stress sensitivity.

## Results

Stenting produced the clearest improvement during expiration. The severe
pre-stent narrowing generated a high-velocity jet, recirculation, substantial
pressure loss, and elevated wall shear stress. The reported pre-/post-stent
expiratory pressure difference was approximately 26 cmH₂O, while mean tracheal
wall shear stress decreased from 3.98 to 0.793 Pa, an approximately 80%
reduction. Velocity variations also became smaller after stenting. Inspiratory
changes were comparatively minor; mean wall shear stress increased from 0.0354
to 0.0813 Pa, and the stent introduced some local flow disturbance. Turbulence
intensity increased in parts of both phases after intervention. Spirometry
changed only modestly—FEV₁ increased by 290 mL—whereas CFD exposed pronounced
expiratory functional improvement that pulmonary function testing did not
clearly reflect.

## Limitations

The study considered only one patient, so its quantitative findings cannot be
generalised to all patients with excessive dynamic airway collapse. The airway
walls were rigid even though wall deformation is the defining feature of the
disease. Separate end-inspiration and end-expiration geometries represented the
extremes of breathing rather than continuously moving anatomy; fluid–structure
interaction was omitted because patient-specific tissue properties were
unavailable. The upper airway and deeper peripheral generations were truncated,
although both may influence tracheal flow and outlet impedance. Outlet pressures
were inferred indirectly from lobar volume changes, and local CFD predictions
were not validated against invasive pressure or velocity measurements. The
RANS turbulence model and selected boundary conditions add model-form
uncertainty. Finally, mesh sensitivity was demonstrated primarily for selected
quantities in one pre-stent expiratory geometry.

## Evaluation

For this patient, the authors largely answered their research question. The
paired pre-/post-stent and inspiration/expiration design isolated the phase in
which airway collapse mattered most, and pressure, velocity, and wall shear
stress changed coherently after intervention. The contrast with relatively
insensitive spirometry supports the claim that CFD can provide additional
functional information. The mesh test and patient-informed outlet conditions
strengthen the internal comparison. However, the study establishes a
patient-specific proof of concept rather than a validated diagnostic or
prognostic method. Rigid endpoint geometries cannot reproduce dynamic coupling
between airflow and collapse, and a single case cannot establish clinical
accuracy or treatment thresholds. Thus, the conclusion that stenting improved
this patient’s expiratory airflow is supported, whereas broader claims about
CFD-guided management require validation in more patients with dynamic or
fluid–structure-interaction models.
