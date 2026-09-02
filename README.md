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
```

For a new case without `CenterlineEndpoints.json`, run
`prepare_centerline_endpoints.py`, place one proximal and three distal points,
and export the markup to the case asset directory. Then continue:

```python
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/calculate_centerline.py").read())

exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/load_cutting_points.py").read())
```

For a new case without `refined_endpoints.json`, run
`prepare_cutting_points.py` after centerline calculation, place/export the four
cut points, and skip `load_cutting_points.py` for that first run.
At this point, review/adjust the loaded `AirwayCutEndpoints` points in the
Markups module, then run:
```
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/cut_airways_centerline.py").read())

exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/export_segmentation.py").read())
```

The export script writes the capped and extended CFD surface to
`meshes/<case>/airways.stl`. `create_volume_mesh.sh` reads both
`meshes/<case>/airways.stl` and `meshes/<case>/airways.geo`.

## Meshing and CFD

The meshing and solver stages are deliberately separate:

```bash
# Generate a verified Gmsh volume mesh locally (default: 0.25 mm)
./create_volume_mesh.sh postop

# Run the existing mesh with OpenFOAM in Docker
NPROCS=8 ./run_cfd.sh postop
```

`run_cfd.sh` validates that `inlet`, `outlet_1`, `outlet_2`, `outlet_3`, and
`wall` exist before starting the solver. The `NPROCS` value must match
`numberOfSubdomains` in the case's `system/decomposeParDict`.

Fetch reconstructed results from a remote host with:

```bash
./fetch_cfd_results.sh <DROPLET_IP> postop
paraview results/postop/postop.foam
```

Run the complete remote fine-mesh experiment, using defaults of `0.15 mm` and
60 MPI ranks, with:

```bash
./run_fine_cfd.sh <DROPLET_IP>
```

Override those defaults when needed:

```bash
MESH_SIZE=0.12 NPROCS=60 ./run_fine_cfd.sh <DROPLET_IP> --visualize
```

See [`WORKFLOW.md`](WORKFLOW.md) for installation instructions, the complete
Slicer-to-ParaView procedure, physical-boundary verification, remote execution,
and mesh-independence guidance.
