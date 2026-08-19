import slicer
import vtk
from DICOMLib import DICOMUtils
import 

# ============================================================
# PARAMETERS
# ============================================================

source_folder = (
    "/home/hvoverme/tracheomalacia_cfd/"
    "segmentation/source/DICOM_postop"
)

# ------------------------------------------------------------
# Airways HU range
# ------------------------------------------------------------

airway_lower_HU = -1500
airway_upper_HU = -650

# ------------------------------------------------------------
# Lung HU range
# ------------------------------------------------------------

lung_lower_HU = -900
lung_upper_HU = -650


# ============================================================
# SEEDS
# ============================================================

# All coordinates are RAS coordinates.
#
# Original markup coordinates were LPS, so X and Y have been
# sign-flipped to obtain RAS.


# ------------------------------------------------------------
# Airways seed
# ------------------------------------------------------------

airway_seed_RAS = [
    5.870349611295694,
    108.31885395681064,
    1327.7000000000019
]

# ------------------------------------------------------------
# Left lung seed
# ------------------------------------------------------------

left_lung_seed_RAS = [
    -78.58658807491167,
    104.80917729611309,
    -387.4
]


# ------------------------------------------------------------
# Right lung seed
# ------------------------------------------------------------

right_lung_seed_RAS = [
    86.44522924240283,
    118.56182873922262,
    -387.4
]


# ============================================================
# LOAD DICOM
# ============================================================

print("")
print("======================================")
print("Loading DICOM")
print("======================================")

with DICOMUtils.TemporaryDICOMDatabase() as db:

    DICOMUtils.importDicom(
        source_folder,
        db
    )

    patientUIDs = db.patients()

    if not patientUIDs:
        raise RuntimeError(
            "No patients found in DICOM database."
        )

    patientUID = patientUIDs[0]

    DICOMUtils.loadPatientByUID(
        patientUID
    )


# ============================================================
# GET CT VOLUME
# ============================================================

print("")
print("======================================")
print("Getting CT volume")
print("======================================")

volume_node = slicer.util.getNode(
    "vtkMRMLScalarVolumeNode1"
)

if volume_node is None:
    raise RuntimeError(
        "vtkMRMLScalarVolumeNode1 was not found."
    )

image_data = volume_node.GetImageData()

if image_data is None:
    raise RuntimeError(
        "CT image data is not available."
    )

print("CT volume:", volume_node.GetName())
print("Volume ID:", volume_node.GetID())
print("Dimensions:", image_data.GetDimensions())
print("Extent:", image_data.GetExtent())
print("Spacing:", volume_node.GetSpacing())
print("Origin:", volume_node.GetOrigin())


# ============================================================
# CREATE SEGMENTATION
# ============================================================

print("")
print("======================================")
print("Creating segmentation")
print("======================================")

segmentation_node = (
    slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLSegmentationNode",
        "AirwayLungSegmentation"
    )
)

# ============================================================
# CREATE DISPLAY NODES
# ============================================================

segmentation_node.CreateDefaultDisplayNodes()

# Tell Slicer that the segmentation uses the CT geometry
segmentation_node.SetReferenceImageGeometryParameterFromVolumeNode(
    volume_node
)

segmentation = segmentation_node.GetSegmentation()


# ============================================================
# CREATE AIRWAYS SEGMENT
# ============================================================

airways_segment_id = segmentation.AddEmptySegment(
    "Airways",
    "Airways"
)

print("Airways ID:", airways_segment_id)


# ============================================================
# RAS -> IJK MATRIX
# ============================================================

ras_to_ijk = vtk.vtkMatrix4x4()

volume_node.GetRASToIJKMatrix(
    ras_to_ijk
)

extent = image_data.GetExtent()


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_seed_info(name, seed_RAS):

    # RAS -> homogeneous coordinate
    ras_h = [
        seed_RAS[0],
        seed_RAS[1],
        seed_RAS[2],
        1.0
    ]

    # RAS -> IJK
    ijk_h = [
        0.0,
        0.0,
        0.0,
        0.0
    ]

    ras_to_ijk.MultiplyPoint(
        ras_h,
        ijk_h
    )

    seed_IJK = [
        int(round(ijk_h[0])),
        int(round(ijk_h[1])),
        int(round(ijk_h[2]))
    ]

    # Check bounds
    if not (
        extent[0] <= seed_IJK[0] <= extent[1]
        and
        extent[2] <= seed_IJK[1] <= extent[3]
        and
        extent[4] <= seed_IJK[2] <= extent[5]
    ):

        raise RuntimeError(
            f"{name} is outside the CT volume.\n"
            f"RAS: {seed_RAS}\n"
            f"IJK: {seed_IJK}\n"
            f"CT extent: {extent}"
        )

    # Get HU
    hu = image_data.GetScalarComponentAsDouble(
        seed_IJK[0],
        seed_IJK[1],
        seed_IJK[2],
        0
    )

    print("")
    print(name)
    print("  RAS:", seed_RAS)
    print("  IJK:", seed_IJK)
    print("  HU :", hu)

    return seed_IJK, hu


# ============================================================
# CHECK AIRWAY SEED
# ============================================================

airway_seed_IJK, airway_seed_HU = get_seed_info(
    "Airway seed",
    airway_seed_RAS
)

if not (
    airway_lower_HU
    <= airway_seed_HU
    <= airway_upper_HU
):

    raise RuntimeError(
        f"Airway seed HU {airway_seed_HU} is outside "
        f"[{airway_lower_HU}, {airway_upper_HU}]"
    )


# ============================================================
# CREATE AIRWAY FIDUCIAL
# ============================================================

print("")
print("Creating airway seed markup")

airway_markup = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLMarkupsFiducialNode",
    "AirwaySeed"
)

airway_markup.AddControlPoint(
    airway_seed_RAS[0],
    airway_seed_RAS[1],
    airway_seed_RAS[2]
)

airway_markup.SetNthControlPointLabel(
    0,
    f"Airway ({airway_seed_HU:.0f} HU)"
)

airway_markup.SetDisplayVisibility(True)


# ============================================================
# SEGMENTATION LOGIC
# ============================================================

segmentation_logic = slicer.modules.segmentations.logic()


# ============================================================
# AIRWAY REGION GROWING
# ============================================================

print("")
print("======================================")
print("Growing Airways")
print("======================================")

airway_grow = vtk.vtkImageThresholdConnectivity()

airway_grow.SetInputData(
    image_data
)

airway_grow.ThresholdBetween(
    airway_lower_HU,
    airway_upper_HU
)


# ------------------------------------------------------------
# Airway seed
# ------------------------------------------------------------

airway_seed_points = vtk.vtkPoints()

airway_seed_points.InsertNextPoint(
    airway_seed_IJK[0],
    airway_seed_IJK[1],
    airway_seed_IJK[2]
)

airway_grow.SetSeedPoints(
    airway_seed_points
)

airway_grow.ReplaceInOn()
airway_grow.ReplaceOutOn()

airway_grow.SetInValue(1)
airway_grow.SetOutValue(0)

airway_grow.Update()


# ============================================================
# GET AIRWAY RESULT
# ============================================================

airway_output = airway_grow.GetOutput()

airway_voxels = airway_grow.GetNumberOfInVoxels()

print(
    "Airway dimensions:",
    airway_output.GetDimensions()
)

print(
    "Airway extent:",
    airway_output.GetExtent()
)

print(
    "Airway scalar range:",
    airway_output.GetScalarRange()
)

print(
    "Airway voxels:",
    airway_voxels
)


# ============================================================
# VERIFY AIRWAY SEED
# ============================================================

airway_seed_value = (
    airway_output.GetScalarComponentAsDouble(
        airway_seed_IJK[0],
        airway_seed_IJK[1],
        airway_seed_IJK[2],
        0
    )
)

print(
    "Airway seed value:",
    airway_seed_value
)

if airway_seed_value != 1:

    raise RuntimeError(
        "Airway region growing does not contain the seed."
    )


# ============================================================
# CONVERT AIRWAY RESULT TO ORIENTED IMAGE
# ============================================================

airway_image = slicer.vtkOrientedImageData()

airway_image.DeepCopy(
    airway_output
)

ijk_to_ras = vtk.vtkMatrix4x4()

volume_node.GetIJKToRASMatrix(
    ijk_to_ras
)

airway_image.SetGeometryFromImageToWorldMatrix(
    ijk_to_ras
)


# ============================================================
# INSERT AIRWAYS INTO SEGMENT
# ============================================================

success = segmentation_logic.SetBinaryLabelmapToSegment(
    airway_image,
    segmentation_node,
    airways_segment_id,
    segmentation_logic.MODE_REPLACE
)

if not success:

    raise RuntimeError(
        "Failed to insert Airways mask."
    )

print("Airways mask inserted successfully.")


# ============================================================
# GET AIRWAYS SEGMENT
# ============================================================

airways_segment = segmentation.GetSegment(
    airways_segment_id
)

if airways_segment is None:

    raise RuntimeError(
        "Airways segment could not be retrieved."
    )


# ============================================================
# CREATE 3D AIRWAY SURFACE
# ============================================================

print("")
print("======================================")
print("Creating Airways 3D surface")
print("======================================")

segmentation_node.CreateClosedSurfaceRepresentation()

airways_surface = airways_segment.GetRepresentation(
    "Closed surface"
)

if airways_surface is None:

    raise RuntimeError(
        "Failed to create Airways closed surface."
    )

print("Airways closed surface created.")


# ============================================================
# AIRWAY COLOR
# ============================================================

airways_segment.SetColor(
    1.0,
    0.0,
    0.0
)


# ============================================================
# DISPLAY
# ============================================================

segmentation_node.SetDisplayVisibility(True)

display_node = segmentation_node.GetDisplayNode()

if display_node is None:

    raise RuntimeError(
        "Segmentation display node is missing."
    )

display_node.SetVisibility2DFill(True)
display_node.SetVisibility2DOutline(True)
display_node.SetVisibility3D(True)

volume_node.SetDisplayVisibility(True)


# ============================================================
# FINAL REPORT
# ============================================================

print("")
print("======================================")
print("AIRWAY SEGMENTATION COMPLETE")
print("======================================")

print("")
print("CT:")
print("  Name:", volume_node.GetName())
print("  Dimensions:", image_data.GetDimensions())
print("  Spacing:", volume_node.GetSpacing())

print("")
print("AIRWAYS:")
print("  Seed RAS:", airway_seed_RAS)
print("  Seed IJK:", airway_seed_IJK)
print("  Seed HU:", airway_seed_HU)
print(
    "  HU range:",
    airway_lower_HU,
    "to",
    airway_upper_HU
)
print("  Voxels:", airway_voxels)

print("")
print("3D:")
print("  Airways surface: created")

print("")
print("Display:")
print("  2D fill: enabled")
print("  2D outline: enabled")
print("  3D: enabled")

print("")
print("======================================")

# ============================================================
# CENTER CAMERA ON AIRWAYS
# ============================================================

print("")
print("======================================")
print("Recentering camera on airway seed")
print("======================================")

node = slicer.util.getNode("AirwaySeed")
pos = [0, 0, 0]
node.GetNthControlPointPositionWorld(0, pos)

slicer.app.layoutManager().threeDWidget(0).threeDView().cameraNode().SetFocalPoint(pos)

