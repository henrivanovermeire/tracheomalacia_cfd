import json
import pathlib

import slicer
import vtk
from vtk.util.numpy_support import vtk_to_numpy

# ============================================================
# CONFIGURATION
# ============================================================

project_path = pathlib.Path("/home/hvoverme/tracheomalacia_cfd/")

# Which patient case to process. Keep this in sync with segment_airway.py.
CASE = "preop"

setting_path = (
    project_path / "segmentation" / "assets" / CASE / "segmentation_settings.json"
)
airway_seed_path = (
    project_path / "segmentation" / "assets" / CASE / "AirwaySeed.json"
)

with open(setting_path, "r") as seg_setting_file:
    seg_setting = json.load(seg_setting_file)


def hu_range(name):
    for entry in seg_setting["HU_RANGES"]:
        if entry.get("name") == name:
            return entry["min"], entry["max"]
    raise RuntimeError(f"No HU range named '{name}' found in {setting_path}.")


AIRWAY_MIN, AIRWAY_MAX = hu_range("airway")

# Global (non-seeded) threshold used only to find "any plausible lung
# tissue" candidate voxels, before filtering down to the two largest
# connected components (the two lungs). This is independent from the
# "lung" entry in segmentation_settings.json (that entry was designed
# for the old seeded-grow approach and is no longer used here) -- tune
# these two constants directly if needed. Keep the ceiling moderate:
# it must stay below whatever ceiling would bridge the trachea into
# the lung parenchyma (we know from experience that happens somewhere
# around -400/-300 for this dataset), so -500 leaves a safe margin.
LUNG_GLOBAL_MIN = -1000.0
LUNG_GLOBAL_MAX = -500.0


# ============================================================
# HELPERS
# ============================================================

def load_seed_positions_ras(json_path):
    """Load every control point position from a markups fiducial JSON
    file, converted to RAS coordinates (see segment_airway.py for the
    LPS -> RAS conversion rationale)."""

    with open(json_path, "r") as seed_file:
        data = json.load(seed_file)

    markup = data["markups"][0]
    coordinate_system = markup.get("coordinateSystem", "LPS")
    control_points = markup["controlPoints"]

    if not control_points:
        raise RuntimeError(f"No control points found in {json_path}.")

    positions_ras = []

    for control_point in control_points:
        position = control_point["position"]

        if coordinate_system == "LPS":
            x, y, z = position
            ras = [-x, -y, z]
        elif coordinate_system == "RAS":
            ras = list(position)
        else:
            raise ValueError(
                f"Unsupported coordinate system '{coordinate_system}' "
                f"in markups file: {json_path}"
            )

        positions_ras.append([float(v) for v in ras])

    return positions_ras


def count_nonzero(image_data_binary):
    array = vtk_to_numpy(image_data_binary.GetPointData().GetScalars())
    return int((array > 0).sum())


def largest_region(binary_image):
    """Extract only the single largest connected component (value 1)
    from a binary (0/1) vtkImageData, returned as a new binary
    vtkImageData."""

    connectivity = vtk.vtkImageConnectivityFilter()
    connectivity.SetInputData(binary_image)
    connectivity.SetScalarRange(1, 1)
    connectivity.SetExtractionModeToLargestRegion()
    connectivity.SetLabelModeToConstantValue()
    connectivity.SetLabelConstantValue(1)
    connectivity.Update()

    result = vtk.vtkImageData()
    result.DeepCopy(connectivity.GetOutput())
    return result


def logical_not(binary_image):
    op = vtk.vtkImageLogic()
    op.SetOperationToNot()
    op.SetOutputTrueValue(1)
    op.SetInput1Data(binary_image)
    op.Update()

    result = vtk.vtkImageData()
    result.DeepCopy(op.GetOutput())
    return result


def logical_and(image_a, image_b):
    op = vtk.vtkImageLogic()
    op.SetOperationToAnd()
    op.SetOutputTrueValue(1)
    op.SetInput1Data(image_a)
    op.SetInput2Data(image_b)
    op.Update()

    result = vtk.vtkImageData()
    result.DeepCopy(op.GetOutput())
    return result


def logical_or(image_a, image_b):
    op = vtk.vtkImageLogic()
    op.SetOperationToOr()
    op.SetOutputTrueValue(1)
    op.SetInput1Data(image_a)
    op.SetInput2Data(image_b)
    op.Update()

    result = vtk.vtkImageData()
    result.DeepCopy(op.GetOutput())
    return result


# ============================================================
# LOAD EXISTING SCENE NODES
# ============================================================

print("")
print("======================================")
print("Loading existing airway segmentation")
print("======================================")

segmentation_node = slicer.util.getNode("AirwayLungSegmentation")
segmentation = segmentation_node.GetSegmentation()

airways_segment_id = segmentation.GetSegmentIdBySegmentName("Airways")

if not airways_segment_id:
    raise RuntimeError(
        "Airways segment was not found. Run segment_airway.py first."
    )

volume_node = slicer.util.getNode("vtkMRMLScalarVolumeNode1")
image_data = volume_node.GetImageData()

if image_data is None:
    raise RuntimeError("CT image data is not available.")

extent = image_data.GetExtent()

ras_to_ijk = vtk.vtkMatrix4x4()
volume_node.GetRASToIJKMatrix(ras_to_ijk)

ijk_to_ras = vtk.vtkMatrix4x4()
volume_node.GetIJKToRASMatrix(ijk_to_ras)

segmentation_logic = slicer.modules.segmentations.logic()


# ============================================================
# SEED -> IJK / HU HELPER
# ============================================================

def get_seed_info(name, seed_ras):

    ras_h = [seed_ras[0], seed_ras[1], seed_ras[2], 1.0]
    ijk_h = [0.0, 0.0, 0.0, 0.0]

    ras_to_ijk.MultiplyPoint(ras_h, ijk_h)

    seed_ijk = [
        int(round(ijk_h[0])),
        int(round(ijk_h[1])),
        int(round(ijk_h[2]))
    ]

    if not (
        extent[0] <= seed_ijk[0] <= extent[1]
        and extent[2] <= seed_ijk[1] <= extent[3]
        and extent[4] <= seed_ijk[2] <= extent[5]
    ):
        raise RuntimeError(
            f"{name} is outside the CT volume.\n"
            f"RAS: {seed_ras}\n"
            f"IJK: {seed_ijk}\n"
            f"CT extent: {extent}"
        )

    hu = image_data.GetScalarComponentAsDouble(
        seed_ijk[0], seed_ijk[1], seed_ijk[2], 0
    )

    print("")
    print(name)
    print("  RAS:", seed_ras)
    print("  IJK:", seed_ijk)
    print("  HU :", hu)

    return seed_ijk, hu


# ============================================================
# RE-GROW AIRWAYS (same seed/threshold as segment_airway.py)
#
# Regrown here (rather than reusing the existing segment's stored
# labelmap) so it shares the exact same image geometry/extent as the
# lung mask below, guaranteeing the two masks can be combined
# voxel-for-voxel without any resampling.
# ============================================================

print("")
print("======================================")
print("Re-growing Airways")
print("======================================")

airway_seed_ras = load_seed_positions_ras(airway_seed_path)[0]
airway_seed_ijk, airway_seed_hu = get_seed_info("Airway seed", airway_seed_ras)

airway_grow = vtk.vtkImageThresholdConnectivity()
airway_grow.SetInputData(image_data)
airway_grow.ThresholdBetween(AIRWAY_MIN, AIRWAY_MAX)

airway_seed_points = vtk.vtkPoints()
airway_seed_points.InsertNextPoint(*airway_seed_ijk)
airway_grow.SetSeedPoints(airway_seed_points)

airway_grow.ReplaceInOn()
airway_grow.ReplaceOutOn()
airway_grow.SetInValue(1)
airway_grow.SetOutValue(0)
airway_grow.Update()

airway_cast = vtk.vtkImageCast()
airway_cast.SetInputData(airway_grow.GetOutput())
airway_cast.SetOutputScalarTypeToUnsignedChar()
airway_cast.Update()

airway_output = vtk.vtkImageData()
airway_output.DeepCopy(airway_cast.GetOutput())

print("Airway voxels (before lung removal):", airway_grow.GetNumberOfInVoxels())


# ============================================================
# BUILD LUNGS MASK: global threshold + two largest components
#
# Region-growing from a single seed is fragile for parenchyma (noisy,
# foam-like tissue at the voxel scale). Instead: threshold the WHOLE
# volume for plausible lung-density tissue (no seed, no connectivity
# requirement), then keep only the two largest connected components.
# Anatomically each lung is far larger than the trachea/bronchi air
# column or any noise speckle, so this reliably isolates just the
# lungs while discarding both speckle noise and the airway tree.
# ============================================================

print("")
print("======================================")
print("Building Lungs mask (global threshold + 2 largest components)")
print("======================================")

lung_candidate_filter = vtk.vtkImageThreshold()
lung_candidate_filter.SetInputData(image_data)
lung_candidate_filter.ThresholdBetween(LUNG_GLOBAL_MIN, LUNG_GLOBAL_MAX)
lung_candidate_filter.SetInValue(1)
lung_candidate_filter.SetOutValue(0)
lung_candidate_filter.ReplaceInOn()
lung_candidate_filter.ReplaceOutOn()
lung_candidate_filter.SetOutputScalarTypeToUnsignedChar()
lung_candidate_filter.Update()

candidate_output = vtk.vtkImageData()
candidate_output.DeepCopy(lung_candidate_filter.GetOutput())

print("Lung candidate voxels (pre-filtering):", count_nonzero(candidate_output))

# Exclude exterior/background air (outside the patient, couch/bore air,
# etc.) before picking the largest components. Room air often reads at
# the same HU as lung air, so it can only be told apart by connectivity
# to the image border rather than by density alone: any air-density
# region touching the outer boundary of the CT volume is, by
# definition, not inside the patient's body.
border_seed_points = vtk.vtkPoints()

for i in (extent[0], extent[1]):
    for j in (extent[2], extent[3]):
        for k in (extent[4], extent[5]):
            border_seed_points.InsertNextPoint(i, j, k)

border_seed_data = vtk.vtkPolyData()
border_seed_data.SetPoints(border_seed_points)

exterior_filter = vtk.vtkImageConnectivityFilter()
exterior_filter.SetInputData(candidate_output)
exterior_filter.SetScalarRange(1, 1)
exterior_filter.SetSeedData(border_seed_data)
exterior_filter.SetExtractionModeToSeededRegions()
exterior_filter.SetLabelModeToConstantValue()
exterior_filter.SetLabelConstantValue(1)
exterior_filter.Update()

exterior_air = vtk.vtkImageData()
exterior_air.DeepCopy(exterior_filter.GetOutput())

print("Exterior/background air voxels (excluded):", count_nonzero(exterior_air))

interior_candidate = logical_and(candidate_output, logical_not(exterior_air))
print(
    "Interior lung candidate voxels (after excluding exterior air):",
    count_nonzero(interior_candidate)
)

lung_a = largest_region(interior_candidate)
print("Largest component voxels (lung A):", count_nonzero(lung_a))

remainder = logical_and(interior_candidate, logical_not(lung_a))
lung_b = largest_region(remainder)
print("Second largest component voxels (lung B):", count_nonzero(lung_b))

lung_output = logical_or(lung_a, lung_b)
print("Total Lungs mask voxels:", count_nonzero(lung_output))

print("")
print("Sanity check: lung A and lung B voxel counts should be roughly")
print("comparable in magnitude (both real lungs). If one is much")
print("smaller than the other, the fissure may have split a single")
print("lung into two 'largest' pieces while missing the other lung")
print("entirely -- inspect the 'Lungs' segment visually either way.")


# ============================================================
# SUBTRACT: Airways_clean = Airways AND NOT Lungs
# ============================================================

print("")
print("======================================")
print("Removing lung leak from Airways")
print("======================================")

cleaned_output = logical_and(airway_output, logical_not(lung_output))
cleaned_voxel_count = count_nonzero(cleaned_output)

print("Airway voxels (after lung removal):", cleaned_voxel_count)
print(
    "Voxels removed:",
    airway_grow.GetNumberOfInVoxels() - cleaned_voxel_count
)


# ============================================================
# INSERT LUNGS SEGMENT (for visual reference)
# ============================================================

lung_segment_id = segmentation.GetSegmentIdBySegmentName("Lungs")

if not lung_segment_id:
    lung_segment_id = segmentation.AddEmptySegment("Lungs", "Lungs")

lung_image = slicer.vtkOrientedImageData()
lung_image.DeepCopy(lung_output)
lung_image.SetGeometryFromImageToWorldMatrix(ijk_to_ras)

segmentation_logic.SetBinaryLabelmapToSegment(
    lung_image,
    segmentation_node,
    lung_segment_id,
    segmentation_logic.MODE_REPLACE
)

segmentation.GetSegment(lung_segment_id).SetColor(0.0, 1.0, 0.0)


# ============================================================
# INSERT CLEANED AIRWAYS
# ============================================================

cleaned_image = slicer.vtkOrientedImageData()
cleaned_image.DeepCopy(cleaned_output)
cleaned_image.SetGeometryFromImageToWorldMatrix(ijk_to_ras)

success = segmentation_logic.SetBinaryLabelmapToSegment(
    cleaned_image,
    segmentation_node,
    airways_segment_id,
    segmentation_logic.MODE_REPLACE
)

if not success:
    raise RuntimeError("Failed to insert cleaned Airways mask.")

print("Cleaned Airways mask inserted successfully.")


# ============================================================
# RECOMPUTE 3D SURFACES
# ============================================================

print("")
print("======================================")
print("Recomputing 3D surfaces")
print("======================================")

segmentation_node.CreateClosedSurfaceRepresentation()

airways_surface = segmentation.GetSegment(airways_segment_id).GetRepresentation(
    "Closed surface"
)

if airways_surface is None:
    raise RuntimeError("Failed to create cleaned Airways closed surface.")

print("Cleaned Airways closed surface created.")


# ============================================================
# DISPLAY
# ============================================================

display_node = segmentation_node.GetDisplayNode()
if display_node is not None:
    display_node.SetSegmentOpacity3D(lung_segment_id, 0.25)
    display_node.SetSegmentVisibility3D(lung_segment_id, True)


# ============================================================
# FINAL REPORT
# ============================================================

print("")
print("======================================")
print("LUNG LEAK REMOVAL COMPLETE")
print("======================================")
print("")
print("Airway HU range:", (AIRWAY_MIN, AIRWAY_MAX))
print("Lung candidate HU range:", (LUNG_GLOBAL_MIN, LUNG_GLOBAL_MAX))
print("")
print("Airway voxels before:", airway_grow.GetNumberOfInVoxels())
print("Lungs mask voxels:", count_nonzero(lung_output))
print("Airway voxels after:", cleaned_voxel_count)
print(
    "Voxels removed:",
    airway_grow.GetNumberOfInVoxels() - cleaned_voxel_count
)
print("")
print("Inspect the semi-transparent green 'Lungs' segment to confirm it")
print("covers both lungs (and only the lungs), then re-run")
print("calculate_centerline.py.")
