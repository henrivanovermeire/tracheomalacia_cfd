# Airway CFD workflow

This document describes the complete path from a CT scan to an OpenFOAM result:

```text
DICOM
  → 3D Slicer airway segmentation
  → centerline and refined cutting points
  → clipped airway with flow extensions and flat caps
  → STL export
  → Gmsh tetrahedral volume mesh
  → OpenFOAM simpleFoam simulation
  → reconstructed results
  → ParaView
```

The repository currently supports two anatomical cases, `postop` and `preop`. The postoperative OpenFOAM case is the configured baseline used in the commands below.

## 1. Requirements

### Local workstation

- 3D Slicer 5.12.2
- SlicerVMTK extension
- Gmsh
- Git
- OpenSSH client
- `rsync`
- ParaView

On an Arch Linux workstation, install the command-line dependencies using the appropriate system packages. Confirm that these commands are available:

```bash
gmsh --version
ssh -V
rsync --version
paraview --version
```

### Remote CFD host

The remote host needs:

- Docker
- Git
- `rsync`
- The cloned repository
- The Docker image `opencfd/openfoam-default:latest`

Example Ubuntu setup:

```bash
sudo apt update
sudo apt install -y docker.io git rsync
sudo systemctl enable --now docker
docker pull opencfd/openfoam-default:latest
```

The scripts assume the remote repository is located at:

```text
/root/tracheomalacia_cfd
```

Override this with `REMOTE_REPO` if necessary.

## 2. Select the anatomical case in Slicer

The segmentation scripts contain a `CASE` variable near the top. Set it consistently to either:

```python
CASE = "postop"
```

or:

```python
CASE = "preop"
```

Start from a fresh Slicer scene when changing cases. Case-specific inputs are stored under:

```text
segmentation/assets/<case>/
```

The expected markup and configuration files include:

- `AirwaySeed.json`
- `CenterlineEndpoints.json`
- `refined_endpoints.json`
- `segmentation_settings.json`

## 3. Segment the airway

Run the segmentation script from the Slicer Python console:

```python
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/segment_airway.py").read())
```

Inspect the segmentation in 2D and 3D. Confirm that:

- The trachea is connected through any stenosis.
- The required bronchi are present.
- Lung parenchyma and exterior air have not become part of the intended final airway model.

Segmentation thresholds and seed coordinates are case-specific.

For the preoperative case, the permissive HU range intentionally preserves the
narrow stenosis but may also include the lungs. After manually cleaning the
`Airways` segment and exporting it as
`segmentation/assets/preop/AirwayLungSegmentation.seg.nrrd`, replace the live
scene node with that file by running:

```python
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/remove_lungs.py").read())
```

This is a data substitution only. It keeps the node name
`AirwayLungSegmentation` and segment name `Airways`, so all downstream scripts
continue from the loaded scene node without another save/reload cycle.

## 4. Prepare centerline endpoints for a new case

If `segmentation/assets/<case>/CenterlineEndpoints.json` does not exist, run:

```python
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/prepare_centerline_endpoints.py").read())
```

Place four anatomy-specific points: one proximal tracheal endpoint and one at
each of the three retained distal branch ends. Export the completed markup as
`segmentation/assets/<case>/CenterlineEndpoints.json`. Never copy endpoint
coordinates from the other anatomy.

## 5. Calculate the centerline

Run:

```python
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/calculate_centerline.py").read())
```

This creates the centerline/network used to orient clipping and flow extensions. The clipping workflow expects the model node:

```text
AirwayNetworkModel
```

## 6. Prepare or load refined cutting points

For a new case without `refined_endpoints.json`, run
`prepare_cutting_points.py`, place the four desired CFD cut points, and export
the node to `segmentation/assets/<case>/refined_endpoints.json`. In that same
scene, proceed directly to clipping because the clipping script reuses the
adjusted node.

For an existing exported markup, run:

```python
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/load_cutting_points.py").read())
```

This creates or replaces the markup node:

```text
AirwayCutEndpoints
```

Review every point in the Slicer UI. Move points as needed so each cut is made at a suitable airway cross-section. These refined points are deliberately separate from the original `CenterlineEndpoints` used during centerline extraction.

## 7. Clip, extend, and cap the airway

Run:

```python
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/cut_airways_centerline.py").read())
```

The script uses SlicerVMTK `ClipVesselLogic`, matching the interactive Clip Vessel workflow:

- Surface: airway segmentation surface
- Centerline: `AirwayNetworkModel`
- Clipping points: `AirwayCutEndpoints`
- Flow extensions: enabled
- Extension direction: centerline direction
- Extension radius: adaptive to the local cross-section
- Final CFD caps: flat

The final combined model is:

```text
AirwayExtendedSurfaceCapped
```

Inspect the model before export. In particular, verify that all four ends have straight, natural extensions and planar caps.

## 8. Export the CFD surface

Run in the Slicer Python console:

```python
exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/export_segmentation.py").read())
```

This triangulates and cleans a copy of `AirwayExtendedSurfaceCapped` and writes:

```text
meshes/<case>/airways.stl
```

The STL coordinates are in millimetres. `run_cfd.sh` scales the converted OpenFOAM mesh to metres.

## 9. Verify Gmsh physical surfaces

`meshes/<case>/airways.geo` imports the case-specific `airways.stl`, classifies its surfaces, creates a volume, and assigns physical groups.

The required physical surfaces are:

```text
inlet
outlet_1
outlet_2
outlet_3
wall
```

The required volume is:

```text
fluid
```

For the currently inspected postoperative geometry, the elementary-surface mapping is documented in `meshes/postop/airways.geo` as:

```geo
inlet[]   = {25}; // tracheal inlet
outlet1[] = {23}; // upper-right outlet
outlet2[] = {24}; // lower-right outlet
outlet3[] = {22}; // left outlet
```

These elementary IDs are not affected by changing only `MESH_SIZE`. They can change when:

- A new STL is exported.
- Cutting points or flow extensions change.
- STL topology changes.
- `ClassifySurfaces` settings change.
- A different Gmsh version classifies the surface differently.

Open the geometry on the same machine that creates the volume mesh:

```bash
gmsh meshes/postop/airways.geo
```

Use Gmsh's elementary-entity visibility controls to verify all four cap IDs. Do not run CFD if any cap is assigned to `wall`.

## 10. Create a volume mesh

Make the scripts executable once after cloning:

```bash
chmod +x create_volume_mesh.sh run_cfd.sh fetch_cfd_results.sh run_fine_cfd.sh
```

Create the baseline postoperative mesh with the default `0.25 mm` target size:

```bash
./create_volume_mesh.sh postop
```

Specify another target size through `MESH_SIZE`:

```bash
MESH_SIZE=0.15 ./create_volume_mesh.sh postop
```

The output is:

```text
openFOAM/postop/airways.msh
```

The script uses MSH 2.2 for `gmshToFoam` compatibility.

A smaller characteristic length produces many more tetrahedra. For a geometrically similar 3D domain, reducing `0.25 mm` to `0.15 mm` may increase the cell count by approximately:

```text
(0.25 / 0.15)^3 ≈ 4.6
```

Inspect the generated mesh in Gmsh before transferring it:

```bash
gmsh openFOAM/postop/airways.msh
```

## 10. Run OpenFOAM

`run_cfd.sh` does not generate a Gmsh mesh. It requires an existing, verified:

```text
openFOAM/<case>/airways.msh
```

Run locally with Docker:

```bash
NPROCS=8 ./run_cfd.sh postop
```

The `NPROCS` value must match `numberOfSubdomains` in:

```text
openFOAM/<case>/system/decomposeParDict
```

The script performs:

1. `gmshToFoam airways.msh`
2. Scaling from millimetres to metres
3. Validation of all five required boundary patches
4. `checkMesh`
5. Removal of stale nonzero time directories and old processor partitions
6. `decomposePar -force`
7. Parallel `simpleFoam`
8. `reconstructPar`
9. Final `checkMesh`

MPI is invoked with:

```text
--allow-run-as-root --use-hwthread-cpus
```

This supports root execution inside Docker on a remote server.

To open a locally completed case automatically:

```bash
./run_cfd.sh postop --visualize
```

## 11. Run a verified mesh on a remote host

Transfer a locally generated and inspected mesh:

```bash
scp openFOAM/postop/airways.msh \
    root@<DROPLET_IP>:/root/tracheomalacia_cfd/openFOAM/postop/
```

On the remote host:

```bash
cd /root/tracheomalacia_cfd
NPROCS=60 ./run_cfd.sh postop
```

Before starting `simpleFoam`, the script refuses to proceed unless all five patches are present. The first `checkMesh` should report five boundary patches.

## 12. Fetch remote results

Fetch reconstructed results while excluding bulky `processor*/` directories:

```bash
./fetch_cfd_results.sh <DROPLET_IP> postop
```

A bare IP uses `root` by default. An explicit user can also be supplied:

```bash
./fetch_cfd_results.sh ubuntu@<DROPLET_IP> postop
```

For a non-default remote repository path:

```bash
REMOTE_REPO=/opt/tracheomalacia_cfd \
    ./fetch_cfd_results.sh <DROPLET_IP> postop
```

The local result is written to:

```text
results/postop/
```

Open it with:

```bash
paraview results/postop/postop.foam
```

The fetch uses `rsync --delete`, so stale local time directories from older boundary configurations are removed.

## 13. Automated fine-mesh experiment

`run_fine_cfd.sh` performs the entire fine-mesh comparison workflow:

1. Recreates local `openFOAM/postop_fine` from the baseline `postop` dictionaries.
2. Removes the inherited OpenFOAM mesh.
3. Sets `numberOfSubdomains` to `NPROCS`.
4. Generates a fine Gmsh mesh locally.
5. Transfers the current `run_cfd.sh` and fine case to the remote host.
6. Runs the fine simulation remotely.
7. Fetches reconstructed results into `results/postop_fine`.
8. Optionally opens ParaView.

Default run:

```bash
./run_fine_cfd.sh <DROPLET_IP>
```

Defaults:

```text
BASE_CASE=postop
FINE_CASE=postop_fine
MESH_SIZE=0.15 mm
NPROCS=60
REMOTE_USER=root
REMOTE_REPO=/root/tracheomalacia_cfd
```

Override settings as needed:

```bash
MESH_SIZE=0.12 NPROCS=60 \
    ./run_fine_cfd.sh <DROPLET_IP>
```

Run and open the downloaded result automatically:

```bash
./run_fine_cfd.sh <DROPLET_IP> --visualize
```

The script intentionally deletes and recreates the generated `openFOAM/postop_fine` case locally and remotely. It does not modify the baseline `openFOAM/postop` case or `results/postop`.

## 14. Mesh-independence comparison

Compare the baseline and fine cases in ParaView:

```bash
paraview \
    results/postop/postop.foam \
    results/postop_fine/postop_fine.foam
```

Useful comparison quantities include:

- Pressure drop from inlet to outlets
- Peak velocity, especially through stenotic regions
- Outlet flow split
- Cross-sectional velocity profiles
- Wall-adjacent velocity gradients
- Integrated inlet and outlet flow rates

Visual similarity is not sufficient for a mesh-independence claim. Compare integral quantities and report their relative changes between mesh levels.

## 15. Reproducibility and generated files

The verified baseline mesh can be committed at:

```text
openFOAM/postop/airways.msh
```

Downloaded results and the generated fine-case workspace are ignored:

```text
results/
openFOAM/postop_fine/
```

If committed mesh files exceed the hosting provider's file-size limit, use Git LFS:

```bash
git lfs install
git lfs track "openFOAM/*/airways.msh"
git add .gitattributes
```

Record the following for every reported simulation:

- Git commit
- Anatomical case
- STL version
- Gmsh version
- OpenFOAM Docker image/version
- `MESH_SIZE`
- Cell count and `checkMesh` summary
- `NPROCS`
- Boundary-condition settings
- Solver convergence criteria
