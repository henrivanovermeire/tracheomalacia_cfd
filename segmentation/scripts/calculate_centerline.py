import slicer
import json
import pathlib
import ExtractCenterline

# ============================================================
# LOAD PARAMETERS
# ============================================================

project_path = pathlib.Path("/home/hvoverme/tracheomalacia_cfd/")

# Which patient case to process. Keep this in sync with segment_airway.py.
CASE = "postop"

endpoints_path = (
    project_path / "segmentation" / "assets" / CASE / "CenterlineEndpoints.json"
)

if not endpoints_path.is_file():
    raise FileNotFoundError(
        f"Centerline endpoint markup not found: {endpoints_path}\n"
        "Run prepare_centerline_endpoints.py in Slicer, place the four "
        "case-specific points, and export the node to this path first."
    )

with open(endpoints_path, "r") as endpoints_file:
    endpoints_data = json.load(endpoints_file)

endpoints_markup_data = endpoints_data["markups"][0]
endpoints_coordinate_system = endpoints_markup_data.get("coordinateSystem", "LPS")
endpoints_control_points = endpoints_markup_data["controlPoints"]

if not endpoints_control_points:
    raise RuntimeError(
        f"No control points found in {endpoints_path}."
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def control_point_to_RAS(control_point):

    position = control_point["position"]

    if endpoints_coordinate_system == "LPS":
        x, y, z = position
        return [-x, -y, z]
    elif endpoints_coordinate_system == "RAS":
        return list(position)
    else:
        raise ValueError(
            f"Unsupported coordinate system '{endpoints_coordinate_system}' "
            f"in markups file: {endpoints_path}"
        )


def remove_node_if_present(node_name):

    try:
        existing_node = slicer.util.getNode(node_name)
    except Exception:
        existing_node = None

    if existing_node is not None:
        slicer.mrmlScene.RemoveNode(existing_node)


# ============================================================
# ADD CENTERLINE ENDPOINTS TO SCENE
# ============================================================

print("")
print("======================================")
print("Loading centerline endpoints")
print("======================================")

remove_node_if_present("CenterlineEndpoints")

centerline_endpoints_markup = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLMarkupsFiducialNode",
    "CenterlineEndpoints"
)

for control_point in endpoints_control_points:
    point_ras = control_point_to_RAS(control_point)
    point_label = control_point.get("label", "CenterlineEndpoint")
    point_selected = control_point.get("selected", True)

    point_index = centerline_endpoints_markup.AddControlPoint(
        point_ras[0],
        point_ras[1],
        point_ras[2]
    )

    centerline_endpoints_markup.SetNthControlPointLabel(
        point_index,
        point_label
    )

    centerline_endpoints_markup.SetNthControlPointSelected(
        point_index,
        point_selected
    )

centerline_endpoints_markup.SetDisplayVisibility(True)

print("Loaded CenterlineEndpoints from:", endpoints_path)
print(
    "CenterlineEndpoints control points:",
    centerline_endpoints_markup.GetNumberOfControlPoints()
)


# ============================================================
# GET AIRWAYS SEGMENTATION
# ============================================================

print("")
print("======================================")
print("Getting Airways surface")
print("======================================")

segmentation_node = slicer.util.getNode("AirwayLungSegmentation")

if segmentation_node is None:
    raise RuntimeError(
        "AirwayLungSegmentation node was not found. Run segment_airway.py first."
    )

segmentation = segmentation_node.GetSegmentation()
airways_segment_id = segmentation.GetSegmentIdBySegmentName("Airways")

if not airways_segment_id:
    raise RuntimeError(
        "Airways segment was not found in AirwayLungSegmentation."
    )

extract_centerline_logic = ExtractCenterline.ExtractCenterlineLogic()

input_surface_poly_data = extract_centerline_logic.polyDataFromNode(
    segmentation_node,
    airways_segment_id
)

if (
    input_surface_poly_data is None
    or input_surface_poly_data.GetNumberOfPoints() == 0
):
    raise RuntimeError(
        "Failed to obtain a valid input surface from the Airways segment."
    )

print("Airways segment ID:", airways_segment_id)
print(
    "Input surface points:",
    input_surface_poly_data.GetNumberOfPoints()
)


# ============================================================
# PREPROCESS SURFACE
# ============================================================

print("")
print("======================================")
print("Preprocessing surface")
print("======================================")

preprocessed_surface_poly_data = extract_centerline_logic.preprocess(
    input_surface_poly_data,
    targetNumberOfPoints=5000.0,
    decimationAggressiveness=4.0,
    subdivide=False
)

remove_node_if_present("AirwayPreprocessedSurface")

preprocessed_surface_model_node = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLModelNode",
    "AirwayPreprocessedSurface"
)

preprocessed_surface_model_node.SetAndObserveMesh(
    preprocessed_surface_poly_data
)
preprocessed_surface_model_node.CreateDefaultDisplayNodes()
preprocessed_surface_model_node.GetDisplayNode().SetColor(1.0, 1.0, 0.0)
preprocessed_surface_model_node.GetDisplayNode().SetOpacity(0.4)
preprocessed_surface_model_node.GetDisplayNode().SetLineWidth(2)

print(
    "Preprocessed surface points:",
    preprocessed_surface_poly_data.GetNumberOfPoints()
)


# ============================================================
# EXTRACT NETWORK
# ============================================================

print("")
print("======================================")
print("Extracting airway network")
print("======================================")

network_poly_data = extract_centerline_logic.extractNetwork(
    preprocessed_surface_poly_data,
    centerline_endpoints_markup,
    computeGeometry=True
)

remove_node_if_present("AirwayNetworkModel")

network_model_node = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLModelNode",
    "AirwayNetworkModel"
)

network_model_node.SetAndObserveMesh(
    network_poly_data
)
network_model_node.CreateDefaultDisplayNodes()
network_model_node.GetDisplayNode().SetColor(0.0, 0.0, 1.0)
network_model_node.GetDisplayNode().SetLineWidth(3)

network_model_node.SetDisplayVisibility(True)

segmentation_display_node = segmentation_node.GetDisplayNode()
if segmentation_display_node is not None:
    segmentation_display_node.SetOpacity3D(0.4)

print("Network points:", network_poly_data.GetNumberOfPoints())
print("Network cells:", network_poly_data.GetNumberOfCells())


# ============================================================
# FINAL REPORT
# ============================================================

print("")
print("======================================")
print("AIRWAY NETWORK EXTRACTION COMPLETE")
print("======================================")
print("")
print("Endpoints node:", centerline_endpoints_markup.GetName())
print("Preprocessed surface model:", preprocessed_surface_model_node.GetName())
print("Network model:", network_model_node.GetName())
print("")
print("======================================")
