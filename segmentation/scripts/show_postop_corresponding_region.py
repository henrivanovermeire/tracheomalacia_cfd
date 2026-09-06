"""Show the postoperative section corresponding to the preoperative stenosis.

Run inside 3D Slicer after calculating the postoperative AirwayNetworkModel.
The preoperative minimum is transferred using its normalized centerline distance
from the tracheal inlet to the carina. The matched postoperative point, tracheal
path, and centerline-normal lumen contour are displayed for inspection.
"""

import heapq
import json
import math
from pathlib import Path

import slicer
import vtk

PROJECT_PATH = Path("/home/hvoverme/tracheomalacia_cfd")
CASE = "postop"
SEGMENTATION_NODE_NAME = "AirwayLungSegmentation"
SEGMENT_NAME = "Airways"
NETWORK_MODEL_NAME = "AirwayNetworkModel"
PREOP_SUMMARY_PATH = PROJECT_PATH / "assignment" / "data" / "preop_tracheal_landmarks.json"
OUTPUT_MARKUP_PATH = PROJECT_PATH / "segmentation" / "assets" / CASE / "PostopMatchedSection.json"
OUTPUT_SUMMARY_PATH = PROJECT_PATH / "assignment" / "data" / "postop_matched_location.json"
LANDMARKS_NODE_NAME = "PostopTrachealLandmarks"
PATH_MODEL_NAME = "PostopTrachealCenterline"
SECTION_MODEL_NAME = "PostopMatchedCrossSection"
NETWORK_MERGE_TOLERANCE_MM = 1e-3


def distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def normalize(vector):
    magnitude = math.sqrt(sum(component * component for component in vector))
    if magnitude <= 1e-12:
        raise RuntimeError("Cannot normalize a zero-length centerline tangent.")
    return [component / magnitude for component in vector]


def remove_node_if_present(name):
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if node is not None:
        slicer.mrmlScene.RemoveNode(node)


def clean_network(poly_data):
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(poly_data)
    cleaner.PointMergingOn()
    cleaner.ToleranceIsAbsoluteOn()
    cleaner.SetAbsoluteTolerance(NETWORK_MERGE_TOLERANCE_MM)
    cleaner.Update()
    result = vtk.vtkPolyData()
    result.DeepCopy(cleaner.GetOutput())
    return result


def build_graph(poly_data):
    adjacency = {point_id: {} for point_id in range(poly_data.GetNumberOfPoints())}
    for cell_id in range(poly_data.GetNumberOfCells()):
        ids = poly_data.GetCell(cell_id).GetPointIds()
        for index in range(ids.GetNumberOfIds() - 1):
            first, second = ids.GetId(index), ids.GetId(index + 1)
            weight = distance(poly_data.GetPoint(first), poly_data.GetPoint(second))
            if weight > 1e-12:
                adjacency[first][second] = min(weight, adjacency[first].get(second, weight))
                adjacency[second][first] = min(weight, adjacency[second].get(first, weight))
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
    path = [end]
    while path[-1] != start:
        if path[-1] not in previous:
            raise RuntimeError("The selected postoperative carina is disconnected from the inlet.")
        path.append(previous[path[-1]])
    path.reverse()
    return path


def cumulative_distances(points):
    cumulative = [0.0]
    for index in range(1, len(points)):
        cumulative.append(cumulative[-1] + distance(points[index - 1], points[index]))
    return cumulative


def interpolate(points, cumulative, target):
    target = max(0.0, min(target, cumulative[-1]))
    for index in range(1, len(cumulative)):
        if cumulative[index] >= target:
            length = cumulative[index] - cumulative[index - 1]
            fraction = 0.0 if length <= 1e-12 else (target - cumulative[index - 1]) / length
            return [
                points[index - 1][axis] + fraction * (points[index][axis] - points[index - 1][axis])
                for axis in range(3)
            ]
    return list(points[-1])


def create_polyline_model(name, points, color, width):
    vtk_points = vtk.vtkPoints()
    line = vtk.vtkPolyLine()
    line.GetPointIds().SetNumberOfIds(len(points))
    for index, point in enumerate(points):
        vtk_points.InsertNextPoint(point)
        line.GetPointIds().SetId(index, index)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(line)
    data = vtk.vtkPolyData()
    data.SetPoints(vtk_points)
    data.SetLines(cells)
    remove_node_if_present(name)
    node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", name)
    node.SetAndObserveMesh(data)
    node.CreateDefaultDisplayNodes()
    node.GetDisplayNode().SetColor(*color)
    node.GetDisplayNode().SetLineWidth(width)
    node.SetDisplayVisibility(True)
    return node


def get_airway_surface(segmentation_node):
    segmentation = segmentation_node.GetSegmentation()
    segment_id = segmentation.GetSegmentIdBySegmentName(SEGMENT_NAME)
    if not segment_id:
        raise RuntimeError(f"Segment '{SEGMENT_NAME}' was not found.")
    segmentation_node.CreateClosedSurfaceRepresentation()
    surface = vtk.vtkPolyData()
    segmentation_node.GetClosedSurfaceRepresentation(segment_id, surface)
    if surface.GetNumberOfPoints() == 0:
        raise RuntimeError("The postoperative airway surface is empty.")
    return surface


def closest_cut_contour(surface, origin, normal):
    plane = vtk.vtkPlane()
    plane.SetOrigin(origin)
    plane.SetNormal(normal)
    cutter = vtk.vtkCutter()
    cutter.SetInputData(surface)
    cutter.SetCutFunction(plane)
    cutter.Update()
    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(cutter.GetOutputPort())
    stripper.JoinContiguousSegmentsOn()
    stripper.Update()
    output = stripper.GetOutput()
    if output.GetNumberOfCells() == 0:
        raise RuntimeError("No postoperative lumen contour intersects the matched plane.")
    best_points = None
    best_distance = float("inf")
    for cell_id in range(output.GetNumberOfCells()):
        cell = output.GetCell(cell_id)
        points = [list(output.GetPoint(cell.GetPointId(i))) for i in range(cell.GetNumberOfPoints())]
        if len(points) < 3:
            continue
        centroid = [sum(point[axis] for point in points) / len(points) for axis in range(3)]
        candidate_distance = distance(centroid, origin)
        if candidate_distance < best_distance:
            best_distance = candidate_distance
            best_points = points
    if best_points is None:
        raise RuntimeError("The matched plane produced no usable lumen contour.")
    return best_points


print("\n======================================")
print("Mapping preoperative stenosis to postoperative airway")
print("======================================")
if not PREOP_SUMMARY_PATH.is_file():
    raise FileNotFoundError(
        f"Missing {PREOP_SUMMARY_PATH}. Re-run tracheal_landmarks.py in the preoperative scene."
    )
with open(PREOP_SUMMARY_PATH, "r") as source_file:
    preop_summary = json.load(source_file)
stenosis_location = preop_summary.get("stenosis_location")
if not stenosis_location:
    raise RuntimeError(
        "The preoperative summary lacks normalized stenosis data. Re-run "
        "tracheal_landmarks.py in the preoperative scene first."
    )
relative_from_inlet = stenosis_location["relative_distance_from_inlet"]
if not 0.0 <= relative_from_inlet <= 1.0:
    raise RuntimeError(f"Invalid normalized preoperative location: {relative_from_inlet}")

segmentation_node = slicer.mrmlScene.GetFirstNodeByName(SEGMENTATION_NODE_NAME)
if segmentation_node is None:
    raise RuntimeError(f"Scene node '{SEGMENTATION_NODE_NAME}' was not found.")
scene_case = segmentation_node.GetAttribute("AirwayCase")
if scene_case is not None and scene_case != CASE:
    raise RuntimeError(f"The live segmentation is tagged '{scene_case}', not '{CASE}'.")
network_node = slicer.mrmlScene.GetFirstNodeByName(NETWORK_MODEL_NAME)
if network_node is None or network_node.GetPolyData() is None:
    raise RuntimeError(f"Run calculate_centerline.py to create '{NETWORK_MODEL_NAME}'.")
network = clean_network(network_node.GetPolyData())
adjacency = build_graph(network)
terminals = [point_id for point_id, neighbors in adjacency.items() if len(neighbors) == 1]
branches = [point_id for point_id, neighbors in adjacency.items() if len(neighbors) >= 3]
if len(terminals) < 2 or not branches:
    raise RuntimeError("The postoperative network lacks usable terminals or bifurcations.")

inlet_id = max(terminals, key=lambda point_id: network.GetPoint(point_id)[2])
distances, previous = dijkstra(adjacency, inlet_id)
reachable_branches = [point_id for point_id in branches if point_id in distances]

airway_seed_node = slicer.mrmlScene.GetFirstNodeByName("AirwaySeed")
if airway_seed_node is None or airway_seed_node.GetNumberOfControlPoints() < 1:
    raise RuntimeError(
        "The AirwaySeed markup is missing from the postoperative scene. "
        "Run segment_airway.py first."
    )
airway_seed_ras = [0.0, 0.0, 0.0]
airway_seed_node.GetNthControlPointPositionWorld(0, airway_seed_ras)
carina_id = min(
    reachable_branches,
    key=lambda point_id: distance(network.GetPoint(point_id), airway_seed_ras),
)
path_ids = reconstruct_path(previous, inlet_id, carina_id)
path_points = [list(network.GetPoint(point_id)) for point_id in path_ids]
cumulative = cumulative_distances(path_points)
tracheal_length = cumulative[-1]
target_distance = relative_from_inlet * tracheal_length
matched_ras = interpolate(path_points, cumulative, target_distance)
mapped_endpoint_points = []
for endpoint in stenosis_location.get("endpoints", []):
    relative_position = endpoint["relative_distance_from_inlet"]
    if not 0.0 <= relative_position <= 1.0:
        raise RuntimeError(
            f"Invalid normalized position for {endpoint['label']}: {relative_position}"
        )
    mapped_endpoint_points.append(
        {
            "label": endpoint["label"],
            "relative_distance_from_inlet": relative_position,
            "distance_from_inlet_mm": relative_position * tracheal_length,
            "ras_mm": interpolate(
                path_points, cumulative, relative_position * tracheal_length
            ),
        }
    )
offset = min(0.5, max(0.1, tracheal_length * 0.01))
before = interpolate(path_points, cumulative, target_distance - offset)
after = interpolate(path_points, cumulative, target_distance + offset)
normal = normalize([after[i] - before[i] for i in range(3)])

remove_node_if_present(LANDMARKS_NODE_NAME)
landmarks = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", LANDMARKS_NODE_NAME)
landmark_points = [
    ("TrachealInlet", path_points[0]),
    ("PostopMatchedSection", matched_ras),
]
landmark_points.extend(
    (f"Mapped{endpoint['label']}", endpoint["ras_mm"])
    for endpoint in mapped_endpoint_points
)
landmark_points.append(("Carina", path_points[-1]))
for label, point in landmark_points:
    index = landmarks.AddControlPoint(*point)
    landmarks.SetNthControlPointLabel(index, label)
landmarks.CreateDefaultDisplayNodes()
landmarks.GetDisplayNode().SetColor(1.0, 0.8, 0.0)
landmarks.GetDisplayNode().SetSelectedColor(1.0, 0.2, 0.8)
landmarks.GetDisplayNode().SetGlyphScale(3.0)
landmarks.SetDisplayVisibility(True)
create_polyline_model(PATH_MODEL_NAME, path_points, (1.0, 0.5, 0.0), 6)

surface = get_airway_surface(segmentation_node)
contour = closest_cut_contour(surface, matched_ras, normal)
if distance(contour[0], contour[-1]) > 1e-6:
    contour.append(contour[0])
create_polyline_model(SECTION_MODEL_NAME, contour, (1.0, 0.0, 1.0), 6)

OUTPUT_MARKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
if not slicer.util.saveNode(landmarks, str(OUTPUT_MARKUP_PATH)):
    raise RuntimeError(f"Failed to save {OUTPUT_MARKUP_PATH}")
OUTPUT_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
summary = {
    "schema_version": 1,
    "case": CASE,
    "matching_method": "preoperative normalized centerline distance from tracheal inlet to carina",
    "preop_relative_distance_from_inlet": relative_from_inlet,
    "preop_relative_distance_to_carina": stenosis_location["relative_distance_to_carina"],
    "postop_tracheal_centerline_length_mm": tracheal_length,
    "postop_distance_from_inlet_mm": target_distance,
    "postop_distance_to_carina_mm": tracheal_length - target_distance,
    "matched_section_ras_mm": matched_ras,
    "matched_section_normal_ras": normal,
    "mapped_stenosis_endpoints": mapped_endpoint_points,
    "postop_inlet_ras_mm": path_points[0],
    "postop_carina_ras_mm": path_points[-1],
    "postop_carina_rule": "degree>=3 network branch spatially closest to AirwaySeed",
    "airway_seed_ras_mm": airway_seed_ras,
    "airway_seed_to_carina_distance_mm": distance(airway_seed_ras, path_points[-1]),
}
with open(OUTPUT_SUMMARY_PATH, "w") as output_file:
    json.dump(summary, output_file, indent=2)
    output_file.write("\n")

print(f"Preoperative normalized distance from inlet: {relative_from_inlet:.6f}")
print(f"Postoperative tracheal length: {tracheal_length:.3f} mm")
print(f"Matched postoperative distance from inlet: {target_distance:.3f} mm")
print("Matched postoperative RAS:", matched_ras)
for endpoint in mapped_endpoint_points:
    print(f"Mapped {endpoint['label']} RAS:", endpoint["ras_mm"])
print("Saved markup:", OUTPUT_MARKUP_PATH)
print("Saved summary:", OUTPUT_SUMMARY_PATH)
print("Inspect the magenta PostopMatchedCrossSection and labeled landmarks.")
print("======================================")
