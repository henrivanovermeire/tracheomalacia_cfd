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

in the Slicer Python console, run the following command:
```
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/segment_airway.py").read())

exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/calculate_centerline.py").read())
```
