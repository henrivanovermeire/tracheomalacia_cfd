# Assignment 3 — Segmentation and Measurements

**Henri Van Overmeire**

## Methods: segmentation and measurements

The pre- and postoperative CT scans were segmented in 3D Slicer using seeded,
connected thresholding. The postoperative airway range was −1500 to −650 HU.
For the tighter preoperative stenosis, the upper threshold was increased to
−300 HU to maintain luminal connectivity. This also selected lung air, which
was removed manually with the Segment Editor before centerline extraction. VMTK
centerlines guided four anatomically corresponding cuts and adaptive,
centerline-directed flow extensions; planar caps produced CFD-ready surfaces.
The preoperative constriction measured **12.16 mm** along the centerline. Its
minimum centerline-normal section had area **1.813 mm²**, minimum Feret diameter
**0.798 mm**, and area-equivalent diameter **1.519 mm**, where
\(D_{eq}=2\sqrt{A/\pi}\). The matched postoperative section was placed at the
same normalized inlet-to-carina centerline position (76.53% from the inlet);
its area, minimum Feret diameter, and equivalent diameter were **5.169 mm²**,
**2.292 mm**, and **2.565 mm**, respectively. Area constriction was calculated
as \(C_A=(1-A_{pre}/A_{post})\times100=64.9\%\). Area reduction
was selected because continuity depends directly on lumen area and the strongly
non-circular preoperative section is poorly represented by one diameter.

**Figures still required:** annotated preoperative and postoperative 3D
reconstructions showing constriction length and both measurement sections.

## Flow behaviour

For incompressible flow, continuity \(Q=AU\) requires velocity to rise as the
area narrows and fall after expansion. Before the stenosis, pressure decreases
gradually because viscous wall shear opposes motion; for laminar circular flow,
\(\Delta p=128\mu LQ/(\pi D^4)\). Through the stenosis, acceleration converts
static pressure into kinetic energy according to Bernoulli’s principle, while
viscosity and separation add irreversible loss. Downstream, deceleration causes
partial pressure recovery, but pressure remains below the upstream trend because
separation, mixing, and wall friction dissipate mechanical energy.

![Qualitative velocity and pressure behaviour through a
constriction](../report/figures/assignment3_flow_behavior.pdf)

## Resistance

Place centerline-normal planes immediately upstream and downstream of the
constriction. From the CFD solution, area-average dimensional pressure on both
planes and integrate normal velocity to obtain flow rate. The local resistance
is \(R=(\bar P_{up}-\bar P_{down})/Q\); plane locations must exclude unrelated
branch losses.

## Remaining measured inputs

| Placeholder | Required value |
|---|---|
| `L_pre` | 12.157 mm preoperative constriction centerline length |
| `A_pre,min` | 1.813 mm² preoperative minimum cross-sectional area |
| `D_pre,Feret` | 0.798 mm preoperative minimum Feret diameter |
| `D_pre,eq` | 1.519 mm preoperative area-equivalent diameter |
| `A_post,matched` | 5.169 mm² matched postoperative area |
| `D_post,Feret` | 2.292 mm matched postoperative minimum Feret diameter |
| `D_post,eq` | 2.565 mm matched postoperative equivalent diameter |
| `C_A` | 64.9% area constriction |
| `C_D,Feret` | 65.2% minimum Feret diameter reduction |
