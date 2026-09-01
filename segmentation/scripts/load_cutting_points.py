import json
import pathlib

import slicer

# ============================================================
# CONFIGURATION
# ============================================================

project_path = pathlib.Path("/home/hvoverme/tracheomalacia_cfd/")

# Which patient case to process. Keep this in sync with segment_airway.py.
CASE = "postop"

CUT_ENDPOINTS_NODE_NAME = "AirwayCutEndpoints"

cut_endpoints_path = (
    project_path / "segmentation" / "assets" / CASE / "refined_endpoints.json"
)


# ============================================================
# HELPERS
# ============================================================

def remove_node_if_present(node_name):

    try:
        existing_node = slicer.util.getNode(node_name)
    except Exception:
        existing_node = None

    if existing_node is not None:
        slicer.mrmlScene.RemoveNode(existing_node)


def control_point_to_ras(control_point, coordinate_system):

    position = control_point["position"]

    if coordinate_system == "LPS":
        x, y, z = position
        return [-x, -y, z]
    if coordinate_system == "RAS":
        return list(position)

    raise ValueError(
        f"Unsupported coordinate system '{coordinate_system}' "
        f"in markups file: {cut_endpoints_path}"
    )


# ============================================================
# LOAD REFINED CUT POINTS INTO THE SCENE
# ============================================================

print("")
print("======================================")
print("Loading airway cut points")
print("======================================")

with open(cut_endpoints_path, "r") as endpoints_file:
    endpoints_data = json.load(endpoints_file)

endpoints_markup_data = endpoints_data["markups"][0]
coordinate_system = endpoints_markup_data.get("coordinateSystem", "LPS")
control_points = endpoints_markup_data["controlPoints"]

if not control_points:
    raise RuntimeError(
        f"No control points found in {cut_endpoints_path}."
    )

# Always reload fresh from disk here (unlike cut_airways_centerline.py,
# which reuses an existing node if present so it doesn't clobber
# adjustments made afterwards in the UI).
remove_node_if_present(CUT_ENDPOINTS_NODE_NAME)

cut_endpoints_node = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLMarkupsFiducialNode",
    CUT_ENDPOINTS_NODE_NAME
)

for control_point in control_points:
    point_ras = control_point_to_ras(control_point, coordinate_system)
    point_label = control_point.get("label", "AirwayCutEndpoint")
    point_selected = control_point.get("selected", True)

    point_index = cut_endpoints_node.AddControlPoint(
        point_ras[0],
        point_ras[1],
        point_ras[2]
    )

    cut_endpoints_node.SetNthControlPointLabel(point_index, point_label)
    cut_endpoints_node.SetNthControlPointSelected(point_index, point_selected)

cut_endpoints_node.SetDisplayVisibility(True)


# ============================================================
# FINAL REPORT
# ============================================================

print("Loaded", CUT_ENDPOINTS_NODE_NAME, "from:", cut_endpoints_path)
print(
    f"{CUT_ENDPOINTS_NODE_NAME} control points:",
    cut_endpoints_node.GetNumberOfControlPoints()
)
print("")
print("Adjust the points in the Markups module as needed.")
print("cut_airways_centerline.py will reuse this node as-is when you run it.")
