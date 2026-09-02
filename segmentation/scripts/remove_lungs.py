"""Replace the live preoperative segmentation with the manually cleaned file.

Run in 3D Slicer after segment_airway.py and before centerline calculation:

    exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/remove_lungs.py").read())

This script performs only a data substitution. It does not threshold, grow,
erode, clip, or otherwise modify the saved segmentation. The loaded node and
segment retain the exact names expected by all downstream scripts.
"""

from pathlib import Path

import slicer


CASE = "preop"
SEGMENTATION_NODE_NAME = "AirwayLungSegmentation"
AIRWAYS_SEGMENT_NAME = "Airways"
PROJECT_PATH = Path("/home/hvoverme/tracheomalacia_cfd")
SEGMENTATION_PATH = (
    PROJECT_PATH
    / "segmentation"
    / "assets"
    / CASE
    / "AirwayLungSegmentation.seg.nrrd"
)


if CASE != "preop":
    raise RuntimeError(
        "remove_lungs.py is intentionally restricted to the preoperative case."
    )

if not SEGMENTATION_PATH.is_file():
    raise FileNotFoundError(
        f"Cleaned preoperative segmentation not found: {SEGMENTATION_PATH}"
    )

print("")
print("======================================")
print("Loading cleaned preoperative airway")
print("======================================")
print("Input:", SEGMENTATION_PATH)

# Keep the current scene node until the file has loaded and passed validation.
# A bad or incompatible file therefore cannot destroy the live segmentation.
existing_node = slicer.mrmlScene.GetFirstNodeByName(SEGMENTATION_NODE_NAME)

loaded_node = slicer.util.loadSegmentation(str(SEGMENTATION_PATH))
if loaded_node is None:
    raise RuntimeError(
        f"Slicer failed to load the segmentation: {SEGMENTATION_PATH}"
    )

loaded_segmentation = loaded_node.GetSegmentation()
airways_segment_id = loaded_segmentation.GetSegmentIdBySegmentName(
    AIRWAYS_SEGMENT_NAME
)

if not airways_segment_id:
    slicer.mrmlScene.RemoveNode(loaded_node)
    raise RuntimeError(
        f"Loaded segmentation does not contain a segment named "
        f"'{AIRWAYS_SEGMENT_NAME}'. The existing scene segmentation was kept."
    )

if existing_node is not None and existing_node is not loaded_node:
    slicer.mrmlScene.RemoveNode(existing_node)

# Restore the stable node name used by calculate_centerline.py and
# cut_airways_centerline.py. Loading while the original node still existed may
# have caused Slicer to append a numeric suffix.
loaded_node.SetName(SEGMENTATION_NODE_NAME)
loaded_node.CreateDefaultDisplayNodes()
loaded_node.CreateClosedSurfaceRepresentation()

closed_surface = loaded_segmentation.GetSegment(
    airways_segment_id
).GetRepresentation("Closed surface")
if closed_surface is None or closed_surface.GetNumberOfPoints() == 0:
    raise RuntimeError(
        "The cleaned Airways segment was loaded, but its closed surface is empty."
    )

display_node = loaded_node.GetDisplayNode()
if display_node is not None:
    display_node.SetSegmentVisibility(airways_segment_id, True)
    display_node.SetVisibility2DFill(True)
    display_node.SetVisibility2DOutline(True)
    display_node.SetVisibility3D(True)

print("Case:", CASE)
print("Scene node:", loaded_node.GetName())
print("Segment name:", AIRWAYS_SEGMENT_NAME)
print("Segment ID:", airways_segment_id)
print("Closed-surface points:", closed_surface.GetNumberOfPoints())
print("")
print("CLEANED PREOPERATIVE SEGMENTATION LOADED")
print("Downstream scripts can now use the live AirwayLungSegmentation node.")
print("No saving or reloading is required in this Slicer session.")
print("======================================")
