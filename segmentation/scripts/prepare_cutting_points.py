"""Create an empty AirwayCutEndpoints markup for case-specific manual placement.

Run in 3D Slicer after calculate_centerline.py when refined_endpoints.json does
not yet exist for the selected case. Place four cutting points at the desired
cross-sections, export the markup, and then run cut_airways_centerline.py in the
same scene. On later runs, load_cutting_points.py restores the saved points.
"""

from pathlib import Path

import slicer


CASE = "preop"
NODE_NAME = "AirwayCutEndpoints"
PROJECT_PATH = Path("/home/hvoverme/tracheomalacia_cfd")
OUTPUT_PATH = (
    PROJECT_PATH
    / "segmentation"
    / "assets"
    / CASE
    / "refined_endpoints.json"
)


if CASE not in {"preop", "postop"}:
    raise ValueError("CASE must be either 'preop' or 'postop'.")

existing_node = slicer.mrmlScene.GetFirstNodeByName(NODE_NAME)
if existing_node is not None:
    slicer.mrmlScene.RemoveNode(existing_node)

cut_points_node = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLMarkupsFiducialNode",
    NODE_NAME,
)
cut_points_node.SetControlPointLabelFormat("AirwayCutEndpoint-%d")
cut_points_node.CreateDefaultDisplayNodes()
cut_points_node.SetDisplayVisibility(True)

display_node = cut_points_node.GetDisplayNode()
if display_node is not None:
    display_node.SetPointLabelsVisibility(True)
    display_node.SetTextScale(3.0)
    display_node.SetGlyphScale(3.0)

print("")
print("======================================")
print("AIRWAY CUTTING-POINT PLACEMENT READY")
print("======================================")
print("Case:", CASE)
print("Markup node:", NODE_NAME)
print("")
print("Place four points at the desired CFD cut cross-sections:")
print("  1. Proximal tracheal cut")
print("  2. Upper-right distal branch cut")
print("  3. Lower-right distal branch cut")
print("  4. Left distal branch cut")
print("")
print("Use the airway surface and AirwayNetworkModel to inspect each location.")
print("Export the completed markup as:")
print(" ", OUTPUT_PATH)
print("")
print("Then run cut_airways_centerline.py in this scene. It will reuse the")
print("adjusted AirwayCutEndpoints node rather than replacing it.")
print("======================================")
