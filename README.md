# tracheomalacia_cfd
This repository serves as a code and results repository for the computational biofluidmechanics assignment. 

## Assignment


## Segmentation

### 3DSlicer installation

There are a lot of installation possibilities for 3DSlicer. What is important is that we will be requiring extension modules to calculate the centerline of our segmented airways.
Make sure to either install from source or extract the Linux archive in a place where non-root users have write access. 


I used [3DSlicer](https://www.slicer.org) version 5.12.2 for this assignment.  

### Approach to segmentation

Broadly, the following steps were taken to segment the airways:
    1. Load the DICOM data
    2. Define seed points
    3. Check suitable Hounsfield unit range
    4. Use the grow algorithm to segment the airways
    5. calculate the centerline of the airways using VMTK
    6. cut along the calculated centerlines to restrict the model to the larger airways only

### Physical Boundaries

During the segmentation process, the caps of the airways were defined as physical boundary surfaces.

### Running the segmentation scripts

Two patient cases are analysed with the exact same flow: `postop` and
`preop`. Each script has a `CASE` variable near the top (defaulting to
`"postop"`) that selects which DICOM series and which case-specific asset
files (seeds, endpoints, boundary ids, ...) under `segmentation/assets/`
are used. Set `CASE = "preop"` in every script below before switching to
the other case, and start from a fresh Slicer scene when doing so.

Note that case-specific markup files (`AirwaySeed.json`,
`CenterlineEndpoints.json`, `refined_endpoints.json`) must exist under
`segmentation/assets/<case>/` before running that case; they are created
by placing/adjusting points visually in Slicer and exporting them from
the Markups module, since seed/endpoint locations are specific to each
patient's anatomy.

In the Slicer Python console, run the following commands in order:
```
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/segment_airway.py").read())

exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/calculate_centerline.py").read())

exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/load_cutting_points.py").read())
```
At this point, review/adjust the loaded `AirwayCutEndpoints` points in the
Markups module, then run:
```
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/cut_airways_centerline.py").read())
```
