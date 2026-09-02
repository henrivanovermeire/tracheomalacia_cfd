"""Create an empty case-specific CenterlineEndpoints markup for manual placement.

Run in a fresh 3D Slicer scene after segment_airway.py and before
calculate_centerline.py. Place four points in the airway lumen:

1. One proximal point at the tracheal end.
2. One point at each of the three distal branch ends retained for CFD.

Then export the markup from Slicer's Markups module to:

    segmentation/assets/<case>/CenterlineEndpoints.json

The points are anatomy-specific; this script intentionally does not copy
coordinates from the other case.
"""

from pathlib import Path

import slicer


CASE = "preop"
NODE_NAME = "CenterlineEndpoints"
PROJECT_PATH = Path("/home/hvoverme/tracheomalacia_cfd")
OUTPUT_PATH = (
    PROJECT_PATH
    / "segmentation"
    / "assets"
    / CASE
    / "CenterlineEndpoints.json"
)


if CASE not in {"preop", "postop"}:
    raise ValueError("CASE must be either 'preop' or 'postop'.")

existing_node = slicer.mrmlScene.GetFirstNodeByName(NODE_NAME)
if existing_node is not None:
    slicer.mrmlScene.RemoveNode(existing_node)

endpoints_node = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLMarkupsFiducialNode",
    NODE_NAME,
)
endpoints_node.SetControlPointLabelFormat("CenterlineEndpoint-%d")
endpoints_node.CreateDefaultDisplayNodes()
endpoints_node.SetDisplayVisibility(True)

display_node = endpoints_node.GetDisplayNode()
if display_node is not None:
    display_node.SetPointLabelsVisibility(True)
    display_node.SetTextScale(3.0)
    display_node.SetGlyphScale(3.0)
    # Restrict interactive placement to a visible model/segmentation surface
    # when Slicer supports this snap-mode value.
    if hasattr(display_node, "SetSnapMode") and hasattr(
        display_node, "SnapModeToVisibleSurface"
    ):
        display_node.SetSnapMode(display_node.SnapModeToVisibleSurface)

print("")
print("======================================")
print("CENTERLINE ENDPOINT PLACEMENT READY")
print("======================================")
print("Case:", CASE)
print("Markup node:", NODE_NAME)
print("")
print("Place four control points:")
print("  1. Proximal tracheal endpoint")
print("  2. Upper-right distal branch endpoint")
print("  3. Lower-right distal branch endpoint")
print("  4. Left distal branch endpoint")
print("")
print("Keep every point inside the segmented airway lumen near its end.")
print("Export the completed markup as:")
print(" ", OUTPUT_PATH)
print("")
print("Then set CASE consistently and run calculate_centerline.py.")
print("======================================")
