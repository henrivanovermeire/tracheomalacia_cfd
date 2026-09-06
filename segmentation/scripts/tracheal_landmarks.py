"""Identify the preoperative tracheal inlet and carina from the airway network.

Run inside 3D Slicer after calculate_centerline.py. The script finds the
superior-most terminal of AirwayNetworkModel and then identifies the first
bifurcation reached along the network as the carina. Both landmarks and the
selected tracheal centerline path are added to the scene for visual review.
"""

import heapq
import json
import math
from pathlib import Path

import slicer
import vtk


PROJECT_PATH = Path("/home/hvoverme/tracheomalacia_cfd")
CASE = "preop"
SEGMENTATION_NODE_NAME = "AirwayLungSegmentation"
NETWORK_MODEL_NAME = "AirwayNetworkModel"
LANDMARKS_NODE_NAME = "PreopTrachealLandmarks"
PATH_MODEL_NAME = "PreopTrachealCenterline"
LANDMARKS_PATH = (
    PROJECT_PATH / "segmentation" / "assets" / CASE / "TrachealLandmarks.json"
)
SUMMARY_PATH = (
    PROJECT_PATH / "assignment" / "data" / "preop_tracheal_landmarks.json"
)
STENOSIS_SUMMARY_PATH = (
    PROJECT_PATH / "assignment" / "data" / "preop_stenosis_summary.json"
)
NETWORK_MERGE_TOLERANCE_MM = 1e-3


def distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def remove_node_if_present(name):
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if node is not None:
        slicer.mrmlScene.RemoveNode(node)


def clean_network_polydata(poly_data):
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(poly_data)
    cleaner.PointMergingOn()
    cleaner.ToleranceIsAbsoluteOn()
    cleaner.SetAbsoluteTolerance(NETWORK_MERGE_TOLERANCE_MM)
    cleaner.Update()

    result = vtk.vtkPolyData()
    result.DeepCopy(cleaner.GetOutput())
    return result


def build_network_graph(poly_data):
    adjacency = {point_id: {} for point_id in range(poly_data.GetNumberOfPoints())}
    for cell_id in range(poly_data.GetNumberOfCells()):
        point_ids = poly_data.GetCell(cell_id).GetPointIds()
        for local_index in range(point_ids.GetNumberOfIds() - 1):
            first = point_ids.GetId(local_index)
            second = point_ids.GetId(local_index + 1)
            weight = distance(poly_data.GetPoint(first), poly_data.GetPoint(second))
            if weight <= 1e-12:
                continue
            previous = adjacency[first].get(second)
            if previous is None or weight < previous:
                adjacency[first][second] = weight
                adjacency[second][first] = weight
    return adjacency


def dijkstra(adjacency, start):
    distances = {start: 0.0}
    previous = {}
    queue = [(0.0, start)]
    while queue:
        current_distance, current = heapq.heappop(queue)
        if current_distance != distances.get(current):
            continue
        for neighbor, weight in adjacency[current].items():
            candidate = current_distance + weight
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                previous[neighbor] = current
                heapq.heappush(queue, (candidate, neighbor))
    return distances, previous


def reconstruct_path(previous, start, end):
    if end != start and end not in previous:
        raise RuntimeError("Selected carina is not connected to the tracheal inlet.")
    path = [end]
    while path[-1] != start:
        path.append(previous[path[-1]])
    path.reverse()
    return path


def create_path_model(poly_data, path_ids):
    points = vtk.vtkPoints()
    line = vtk.vtkPolyLine()
    line.GetPointIds().SetNumberOfIds(len(path_ids))
    for index, point_id in enumerate(path_ids):
        points.InsertNextPoint(poly_data.GetPoint(point_id))
        line.GetPointIds().SetId(index, index)

    cells = vtk.vtkCellArray()
    cells.InsertNextCell(line)
    path_poly_data = vtk.vtkPolyData()
    path_poly_data.SetPoints(points)
    path_poly_data.SetLines(cells)

    remove_node_if_present(PATH_MODEL_NAME)
    model = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", PATH_MODEL_NAME)
    model.SetAndObserveMesh(path_poly_data)
    model.CreateDefaultDisplayNodes()
    model.GetDisplayNode().SetColor(1.0, 0.5, 0.0)
    model.GetDisplayNode().SetLineWidth(6)
    model.SetDisplayVisibility(True)
    return model


def create_landmarks(inlet_ras, carina_ras):
    remove_node_if_present(LANDMARKS_NODE_NAME)
    node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLMarkupsFiducialNode", LANDMARKS_NODE_NAME
    )
    for label, position in (("TrachealInlet", inlet_ras), ("Carina", carina_ras)):
        index = node.AddControlPoint(*position)
        node.SetNthControlPointLabel(index, label)
        node.SetNthControlPointLocked(index, True)

    node.CreateDefaultDisplayNodes()
    display = node.GetDisplayNode()
    display.SetSelectedColor(1.0, 0.2, 0.2)
    display.SetColor(1.0, 0.8, 0.0)
    display.SetGlyphScale(3.0)
    display.SetPointLabelsVisibility(True)
    node.SetDisplayVisibility(True)
    return node


def save_landmarks(node):
    LANDMARKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not slicer.util.saveNode(node, str(LANDMARKS_PATH)):
        raise RuntimeError(f"Failed to save landmarks to {LANDMARKS_PATH}")


print("")
print("======================================")
print("Identifying preoperative tracheal landmarks")
print("======================================")

segmentation_node = slicer.mrmlScene.GetFirstNodeByName(SEGMENTATION_NODE_NAME)
if segmentation_node is None:
    raise RuntimeError(f"Scene node '{SEGMENTATION_NODE_NAME}' was not found.")
scene_case = segmentation_node.GetAttribute("AirwayCase")
if scene_case is not None and scene_case != CASE:
    raise RuntimeError(
        f"This script identifies '{CASE}' landmarks, but the live segmentation "
        f"is tagged '{scene_case}'."
    )

network_node = slicer.mrmlScene.GetFirstNodeByName(NETWORK_MODEL_NAME)
if network_node is None or network_node.GetPolyData() is None:
    raise RuntimeError(
        f"Network model '{NETWORK_MODEL_NAME}' was not found. Run "
        "calculate_centerline.py first."
    )
raw_network = network_node.GetPolyData()
if raw_network.GetNumberOfPoints() == 0:
    raise RuntimeError(f"Network model '{NETWORK_MODEL_NAME}' is empty.")

network = clean_network_polydata(raw_network)
adjacency = build_network_graph(network)
terminals = [point_id for point_id, neighbors in adjacency.items() if len(neighbors) == 1]
branch_candidates = [
    point_id for point_id, neighbors in adjacency.items() if len(neighbors) >= 3
]

print(
    "Network points before/after junction merging:",
    raw_network.GetNumberOfPoints(),
    "/",
    network.GetNumberOfPoints(),
)
if len(terminals) < 2:
    raise RuntimeError(f"Expected at least two network terminals, found {len(terminals)}.")
if not branch_candidates:
    raise RuntimeError("No network bifurcation (degree >= 3) was found.")

# In RAS coordinates, increasing z is superior. The superior-most terminal is
# therefore the most anatomically plausible tracheal inlet.
inlet_id = max(terminals, key=lambda point_id: network.GetPoint(point_id)[2])
distances, previous = dijkstra(adjacency, inlet_id)
reachable_branches = [
    point_id for point_id in branch_candidates if point_id in distances
]
if not reachable_branches:
    raise RuntimeError("No bifurcation is connected to the selected tracheal inlet.")
ordered_branches = sorted(reachable_branches, key=lambda point_id: distances[point_id])
if len(ordered_branches) < 3:
    raise RuntimeError(
        "The preoperative carina rule requires three reachable bifurcations, "
        f"but only {len(ordered_branches)} was found."
    )
# The first two preoperative bifurcations belong to the double-pseudolumen
# region within the stenotic trachea. The anatomical carina is the third
# branching node reached from the superior inlet.
carina_id = ordered_branches[2]
path_ids = reconstruct_path(previous, inlet_id, carina_id)

print("")
print("Terminal candidates (superior-most is selected as inlet):")
for point_id in sorted(terminals, key=lambda item: network.GetPoint(item)[2], reverse=True):
    point = network.GetPoint(point_id)
    marker = " <-- selected inlet" if point_id == inlet_id else ""
    print(f"  ID {point_id}: RAS {list(point)}, degree 1{marker}")

print("")
print("Bifurcation candidates (ordered by network distance from inlet):")
for point_id in ordered_branches:
    point = network.GetPoint(point_id)
    marker = " <-- selected carina" if point_id == carina_id else ""
    print(
        f"  ID {point_id}: RAS {list(point)}, degree {len(adjacency[point_id])}, "
        f"distance {distances[point_id]:.3f} mm{marker}"
    )

inlet_ras = list(network.GetPoint(inlet_id))
carina_ras = list(network.GetPoint(carina_id))
tracheal_length = distances[carina_id]
landmarks_node = create_landmarks(inlet_ras, carina_ras)
create_path_model(network, path_ids)
save_landmarks(landmarks_node)

SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
stenosis_location = None
if STENOSIS_SUMMARY_PATH.is_file():
    with open(STENOSIS_SUMMARY_PATH, "r") as stenosis_file:
        stenosis_summary = json.load(stenosis_file)
    minimum = stenosis_summary["minimum_section"]
    minimum_ras = [
        minimum["center_x_ras_mm"],
        minimum["center_y_ras_mm"],
        minimum["center_z_ras_mm"],
    ]
    locator = vtk.vtkPointLocator()
    locator.SetDataSet(network)
    locator.BuildLocator()
    minimum_id = locator.FindClosestPoint(minimum_ras)
    minimum_distances, _ = dijkstra(adjacency, minimum_id)
    if inlet_id not in minimum_distances or carina_id not in minimum_distances:
        raise RuntimeError("The minimum stenosis section is disconnected from the tracheal path.")
    distance_from_inlet = minimum_distances[inlet_id]
    distance_to_carina = minimum_distances[carina_id]
    mapped_endpoints = []
    endpoint_labels = stenosis_summary.get("endpoint_labels", [])
    endpoint_positions = stenosis_summary.get("endpoint_positions_ras_mm", [])
    for index, endpoint_ras in enumerate(endpoint_positions):
        endpoint_id = locator.FindClosestPoint(endpoint_ras)
        endpoint_distances, _ = dijkstra(adjacency, endpoint_id)
        if inlet_id not in endpoint_distances or carina_id not in endpoint_distances:
            raise RuntimeError("A stenosis endpoint is disconnected from the tracheal path.")
        endpoint_from_inlet = endpoint_distances[inlet_id]
        endpoint_to_carina = endpoint_distances[carina_id]
        mapped_endpoints.append(
            {
                "label": endpoint_labels[index] if index < len(endpoint_labels) else f"StenosisEndpoint-{index + 1}",
                "source_ras_mm": endpoint_ras,
                "nearest_network_point_id": endpoint_id,
                "network_snap_distance_mm": distance(endpoint_ras, network.GetPoint(endpoint_id)),
                "distance_from_inlet_mm": endpoint_from_inlet,
                "distance_to_carina_mm": endpoint_to_carina,
                "relative_distance_from_inlet": endpoint_from_inlet / tracheal_length,
                "relative_distance_to_carina": endpoint_to_carina / tracheal_length,
            }
        )

    stenosis_location = {
        "minimum_section_ras_mm": minimum_ras,
        "nearest_network_point_id": minimum_id,
        "network_snap_distance_mm": distance(minimum_ras, network.GetPoint(minimum_id)),
        "distance_from_inlet_mm": distance_from_inlet,
        "distance_to_carina_mm": distance_to_carina,
        "relative_distance_from_inlet": distance_from_inlet / tracheal_length,
        "relative_distance_to_carina": distance_to_carina / tracheal_length,
        "endpoints": mapped_endpoints,
    }

summary = {
    "schema_version": 1,
    "case": CASE,
    "method": (
        "Superior-most degree-1 network terminal to third degree>=3 "
        "bifurcation by centerline graph distance; first two bifurcations "
        "skipped because they represent the preoperative double pseudolumen"
    ),
    "network_merge_tolerance_mm": NETWORK_MERGE_TOLERANCE_MM,
    "source_network_node": NETWORK_MODEL_NAME,
    "terminal_count": len(terminals),
    "branch_candidate_count": len(branch_candidates),
    "tracheal_inlet": {"network_point_id": inlet_id, "ras_mm": inlet_ras},
    "carina": {"network_point_id": carina_id, "ras_mm": carina_ras},
    "tracheal_centerline_length_mm": tracheal_length,
    "stenosis_location": stenosis_location,
}
with open(SUMMARY_PATH, "w") as summary_file:
    json.dump(summary, summary_file, indent=2)
    summary_file.write("\n")

print("")
print("Selected tracheal inlet RAS:", inlet_ras)
print("Selected carina RAS:", carina_ras)
print(f"Tracheal centerline length: {tracheal_length:.3f} mm")
if stenosis_location is not None:
    print(
        "Minimum stenosis relative distance from inlet:",
        f"{stenosis_location['relative_distance_from_inlet']:.6f}",
    )
    print(
        "Minimum stenosis relative distance to carina:",
        f"{stenosis_location['relative_distance_to_carina']:.6f}",
    )
    for endpoint in stenosis_location["endpoints"]:
        print(
            f"{endpoint['label']} relative distance from inlet:",
            f"{endpoint['relative_distance_from_inlet']:.6f}",
        )
else:
    print("WARNING: preop stenosis summary unavailable; normalized location not saved.")
print("Landmarks saved to:", LANDMARKS_PATH)
print("Summary saved to:", SUMMARY_PATH)
print("")
print("Inspect the orange PreopTrachealCenterline and the Carina markup.")
print("The first two branches are intentionally skipped because they represent")
print("the preoperative double-pseudolumen region. Confirm that the selected")
print("third branch is the primary carina rather than a distal bifurcation.")
print("======================================")
