"""Measure preoperative or postoperative airway stenosis in 3D Slicer.

Run after remove_lungs.py and calculate_centerline.py. The case is read from
AirwayLungSegmentation's ``AirwayCase`` attribute and must be ``preop`` or
``postop``. Preop uses the authored stenosis endpoints and reports the sampled
minimum. Postop uses ``postop_matched_location.json``: it profiles the mapped
stenosis interval and separately measures the exact matched comparison section.

Both workflows use the live Airways surface and the robustly cleaned
AirwayNetworkModel, create case-specific scene nodes, and write a profile CSV,
a summary JSON, and a section fiducial markup.
"""

import csv
import heapq
import json
import math
from pathlib import Path

import slicer
import vtk


PROJECT_PATH = Path("/home/hvoverme/tracheomalacia_cfd")
SEGMENTATION_NODE_NAME = "AirwayLungSegmentation"
SEGMENT_NAME = "Airways"
NETWORK_MODEL_NAME = "AirwayNetworkModel"
PREOP_ENDPOINTS_PATH = (
    PROJECT_PATH / "segmentation" / "assets" / "preop" / "StenosisEndpoints.json"
)
POSTOP_MATCHED_LOCATION_PATH = (
    PROJECT_PATH / "assignment" / "data" / "postop_matched_location.json"
)

SAMPLE_SPACING_MM = 0.25
MIN_CONTOUR_POINTS = 6


def remove_node_if_present(name):
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if node is not None:
        slicer.mrmlScene.RemoveNode(node)


def control_point_to_ras(control_point, coordinate_system):
    position = list(control_point["position"])
    if coordinate_system == "RAS":
        return position
    if coordinate_system == "LPS":
        return [-position[0], -position[1], position[2]]
    raise ValueError(f"Unsupported coordinate system: {coordinate_system}")


def distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def subtract(a, b):
    return [a[i] - b[i] for i in range(3)]


def cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def normalize(vector):
    magnitude = math.sqrt(dot(vector, vector))
    if magnitude <= 1e-12:
        raise ValueError("Cannot normalize a zero-length vector.")
    return [component / magnitude for component in vector]


def get_segmentation_node_and_case():
    segmentation_node = slicer.mrmlScene.GetFirstNodeByName(SEGMENTATION_NODE_NAME)
    if segmentation_node is None:
        raise RuntimeError(f"Scene node '{SEGMENTATION_NODE_NAME}' was not found.")

    case = segmentation_node.GetAttribute("AirwayCase")
    if case not in ("preop", "postop"):
        raise RuntimeError(
            f"'{SEGMENTATION_NODE_NAME}' AirwayCase must be 'preop' or 'postop'; "
            f"found {case!r}."
        )
    return segmentation_node, case


def get_live_airway_surface(segmentation_node):
    segmentation = segmentation_node.GetSegmentation()
    segment_id = segmentation.GetSegmentIdBySegmentName(SEGMENT_NAME)
    if not segment_id:
        raise RuntimeError(
            f"Segment '{SEGMENT_NAME}' was not found in "
            f"'{SEGMENTATION_NODE_NAME}'."
        )

    segmentation_node.CreateClosedSurfaceRepresentation()
    surface = vtk.vtkPolyData()
    segmentation_node.GetClosedSurfaceRepresentation(segment_id, surface)
    if surface.GetNumberOfPoints() == 0:
        raise RuntimeError("The live Airways closed surface is empty.")

    result = vtk.vtkPolyData()
    result.DeepCopy(surface)
    return result


def clean_network_polydata(poly_data):
    """Merge duplicate polyline junction points before graph traversal."""
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(poly_data)
    cleaner.PointMergingOn()
    cleaner.ToleranceIsAbsoluteOn()
    cleaner.SetAbsoluteTolerance(1e-3)  # mm; joins coincident IDs, not anatomy
    cleaner.Update()

    result = vtk.vtkPolyData()
    result.DeepCopy(cleaner.GetOutput())
    return result


def build_network_graph(poly_data):
    adjacency = {point_id: {} for point_id in range(poly_data.GetNumberOfPoints())}

    for cell_id in range(poly_data.GetNumberOfCells()):
        cell = poly_data.GetCell(cell_id)
        point_ids = cell.GetPointIds()
        for local_index in range(point_ids.GetNumberOfIds() - 1):
            first = point_ids.GetId(local_index)
            second = point_ids.GetId(local_index + 1)
            weight = distance(poly_data.GetPoint(first), poly_data.GetPoint(second))
            previous = adjacency[first].get(second)
            if previous is None or weight < previous:
                adjacency[first][second] = weight
                adjacency[second][first] = weight

    return adjacency


def shortest_path(adjacency, start, end):
    distances = {start: 0.0}
    previous = {}
    queue = [(0.0, start)]

    while queue:
        current_distance, current = heapq.heappop(queue)
        if current_distance != distances.get(current):
            continue
        if current == end:
            break

        for neighbor, weight in adjacency[current].items():
            candidate = current_distance + weight
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                previous[neighbor] = current
                heapq.heappush(queue, (candidate, neighbor))

    if end not in distances:
        raise RuntimeError(
            "The superior and inferior stenosis landmarks projected onto "
            "disconnected parts of AirwayNetworkModel."
        )

    path = [end]
    while path[-1] != start:
        path.append(previous[path[-1]])
    path.reverse()
    return path, distances[end]


def cumulative_distances(points):
    result = [0.0]
    for index in range(1, len(points)):
        result.append(result[-1] + distance(points[index - 1], points[index]))
    return result


def interpolate_polyline(points, cumulative, position):
    if position <= 0.0:
        return list(points[0])
    if position >= cumulative[-1]:
        return list(points[-1])

    for index in range(1, len(cumulative)):
        if cumulative[index] >= position:
            interval = cumulative[index] - cumulative[index - 1]
            fraction = (position - cumulative[index - 1]) / interval
            return [
                points[index - 1][axis]
                + fraction * (points[index][axis] - points[index - 1][axis])
                for axis in range(3)
            ]

    return list(points[-1])


def plane_basis(normal):
    reference = [1.0, 0.0, 0.0]
    if abs(dot(normal, reference)) > 0.9:
        reference = [0.0, 1.0, 0.0]
    first = normalize(cross(normal, reference))
    second = normalize(cross(normal, first))
    return first, second


def convex_hull(points):
    unique = sorted(set((round(p[0], 10), round(p[1], 10)) for p in points))
    if len(unique) <= 1:
        return unique

    def orientation(origin, first, second):
        return (
            (first[0] - origin[0]) * (second[1] - origin[1])
            - (first[1] - origin[1]) * (second[0] - origin[0])
        )

    lower = []
    for point in unique:
        while len(lower) >= 2 and orientation(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper = []
    for point in reversed(unique):
        while len(upper) >= 2 and orientation(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    return lower[:-1] + upper[:-1]


def contour_metrics(points_3d, origin, normal):
    axis_u, axis_v = plane_basis(normal)
    points_2d = [
        (
            dot(subtract(point, origin), axis_u),
            dot(subtract(point, origin), axis_v),
        )
        for point in points_3d
    ]

    area_twice = 0.0
    perimeter = 0.0
    for index, point in enumerate(points_2d):
        following = points_2d[(index + 1) % len(points_2d)]
        area_twice += point[0] * following[1] - following[0] * point[1]
        perimeter += math.hypot(
            following[0] - point[0], following[1] - point[1]
        )
    area = abs(area_twice) * 0.5

    hull = convex_hull(points_2d)
    if len(hull) < 3:
        raise ValueError("Cross-section contour has no valid convex hull.")

    minimum_feret = float("inf")
    for index, first in enumerate(hull):
        second = hull[(index + 1) % len(hull)]
        edge = (second[0] - first[0], second[1] - first[1])
        edge_length = math.hypot(edge[0], edge[1])
        if edge_length <= 1e-12:
            continue
        normal_2d = (-edge[1] / edge_length, edge[0] / edge_length)
        projections = [p[0] * normal_2d[0] + p[1] * normal_2d[1] for p in hull]
        minimum_feret = min(minimum_feret, max(projections) - min(projections))

    maximum_feret = max(
        math.hypot(a[0] - b[0], a[1] - b[1])
        for index, a in enumerate(hull)
        for b in hull[index + 1 :]
    )

    equivalent_diameter = 2.0 * math.sqrt(area / math.pi)
    return area, perimeter, minimum_feret, maximum_feret, equivalent_diameter


def cut_contours(surface, origin, normal):
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
    contours = []
    for cell_id in range(output.GetNumberOfCells()):
        cell = output.GetCell(cell_id)
        if cell.GetNumberOfPoints() < MIN_CONTOUR_POINTS:
            continue
        points = [list(cell.GetPoints().GetPoint(i)) for i in range(cell.GetNumberOfPoints())]
        if distance(points[0], points[-1]) < 1e-5:
            points = points[:-1]
        if len(points) >= MIN_CONTOUR_POINTS:
            contours.append(points)
    return contours


def contour_centroid(points):
    return [sum(point[axis] for point in points) / len(points) for axis in range(3)]


def project_point_to_polyline(point, points, cumulative):
    """Return the closest point and continuous arc distance on a polyline."""
    best = None
    for index in range(1, len(points)):
        start = points[index - 1]
        segment = subtract(points[index], start)
        length_squared = dot(segment, segment)
        if length_squared <= 1e-12:
            continue
        fraction = max(0.0, min(1.0, dot(subtract(point, start), segment) / length_squared))
        projected = [start[axis] + fraction * segment[axis] for axis in range(3)]
        snap_distance = distance(point, projected)
        arc_distance = cumulative[index - 1] + fraction * math.sqrt(length_squared)
        candidate = (snap_distance, arc_distance, projected)
        if best is None or candidate[0] < best[0]:
            best = candidate
    if best is None:
        raise RuntimeError("Cannot project onto a centerline path with no valid segments.")
    return best[2], best[1], best[0]


def measure_section(surface, path_points, path_cumulative, arc_distance):
    """Measure one lumen section using the centerline-normal contour routine."""
    centerline_length = path_cumulative[-1]
    origin = interpolate_polyline(path_points, path_cumulative, arc_distance)
    tangent_offset = min(0.5, max(centerline_length * 0.02, SAMPLE_SPACING_MM))
    before = interpolate_polyline(
        path_points, path_cumulative, max(0.0, arc_distance - tangent_offset)
    )
    after = interpolate_polyline(
        path_points,
        path_cumulative,
        min(centerline_length, arc_distance + tangent_offset),
    )
    normal = normalize(subtract(after, before))
    contours = cut_contours(surface, origin, normal)
    if not contours:
        raise ValueError("no closed contour")
    contour = min(contours, key=lambda points: distance(contour_centroid(points), origin))
    area, perimeter, min_feret, max_feret, equivalent = contour_metrics(
        contour, origin, normal
    )
    return {
        "distance_from_superior_mm": arc_distance,
        "center_x_ras_mm": origin[0],
        "center_y_ras_mm": origin[1],
        "center_z_ras_mm": origin[2],
        "normal_x": normal[0],
        "normal_y": normal[1],
        "normal_z": normal[2],
        "area_mm2": area,
        "perimeter_mm": perimeter,
        "minimum_feret_diameter_mm": min_feret,
        "maximum_feret_diameter_mm": max_feret,
        "equivalent_diameter_mm": equivalent,
        "contour": contour,
    }


def create_path_model(points, case_title):
    vtk_points = vtk.vtkPoints()
    line = vtk.vtkPolyLine()
    line.GetPointIds().SetNumberOfIds(len(points))
    for index, point in enumerate(points):
        vtk_points.InsertNextPoint(point)
        line.GetPointIds().SetId(index, index)

    cells = vtk.vtkCellArray()
    cells.InsertNextCell(line)
    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(vtk_points)
    poly_data.SetLines(cells)

    node_name = f"{case_title}StenosisCenterlineSegment"
    remove_node_if_present(node_name)
    node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", node_name)
    node.SetAndObserveMesh(poly_data)
    node.CreateDefaultDisplayNodes()
    node.GetDisplayNode().SetColor(1.0, 0.6, 0.0)
    node.GetDisplayNode().SetLineWidth(6)
    return node


def create_contour_model(points, node_name, color=(1.0, 0.0, 1.0)):
    vtk_points = vtk.vtkPoints()
    line = vtk.vtkPolyLine()
    line.GetPointIds().SetNumberOfIds(len(points) + 1)
    for index, point in enumerate(points):
        vtk_points.InsertNextPoint(point)
        line.GetPointIds().SetId(index, index)
    line.GetPointIds().SetId(len(points), 0)

    cells = vtk.vtkCellArray()
    cells.InsertNextCell(line)
    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(vtk_points)
    poly_data.SetLines(cells)

    remove_node_if_present(node_name)
    node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", node_name)
    node.SetAndObserveMesh(poly_data)
    node.CreateDefaultDisplayNodes()
    node.GetDisplayNode().SetColor(*color)
    node.GetDisplayNode().SetLineWidth(6)
    return node


def load_measurement_inputs(case):
    if case == "preop":
        source_path = PREOP_ENDPOINTS_PATH
        if not source_path.is_file():
            raise FileNotFoundError(f"Stenosis endpoint markup not found: {source_path}")
        with open(source_path, "r") as source_file:
            source_data = json.load(source_file)
        markup = source_data["markups"][0]
        coordinate_system = markup.get("coordinateSystem", "LPS")
        control_points = markup["controlPoints"]
        if len(control_points) != 2:
            raise RuntimeError(
                f"Expected exactly two stenosis endpoints, found {len(control_points)}."
            )
        landmarks = [
            control_point_to_ras(point, coordinate_system) for point in control_points
        ]
        labels = [
            point.get("label", f"Endpoint-{index + 1}")
            for index, point in enumerate(control_points)
        ]
        return source_path, source_data, landmarks, labels, None

    source_path = POSTOP_MATCHED_LOCATION_PATH
    if not source_path.is_file():
        raise FileNotFoundError(f"Postop matched-location file not found: {source_path}")
    with open(source_path, "r") as source_file:
        source_data = json.load(source_file)
    mapped = source_data.get("mapped_stenosis_endpoints", [])
    if len(mapped) != 2:
        raise RuntimeError("Expected exactly two mapped postop stenosis endpoints.")
    by_role = {}
    for endpoint in mapped:
        label = endpoint.get("label", "")
        if "superior" in label.lower():
            by_role["superior"] = endpoint
        elif "inferior" in label.lower():
            by_role["inferior"] = endpoint
    if set(by_role) != {"superior", "inferior"}:
        raise RuntimeError("Mapped endpoints must be labeled superior and inferior.")
    ordered = [by_role["superior"], by_role["inferior"]]
    landmarks = [list(endpoint["ras_mm"]) for endpoint in ordered]
    labels = [endpoint["label"] for endpoint in ordered]
    matched_position = source_data.get("matched_section_ras_mm")
    if not isinstance(matched_position, list) or len(matched_position) != 3:
        raise RuntimeError("No valid matched_section_ras_mm was found.")
    return source_path, source_data, landmarks, labels, matched_position


def public_measurement(row, profile_fields, role):
    result = {key: row[key] for key in profile_fields if key in row}
    result["measurement_role"] = role
    return result


def main():
    segmentation_node, case = get_segmentation_node_and_case()
    case_title = case.capitalize()
    profile_path = PROJECT_PATH / "assignment" / "data" / f"{case}_stenosis_profile.csv"
    summary_path = PROJECT_PATH / "assignment" / "data" / f"{case}_stenosis_summary.json"
    section_name = "PreopMinimumSection" if case == "preop" else "PostopMeasuredSection"
    section_markup_path = (
        PROJECT_PATH / "segmentation" / "assets" / case / f"{section_name}.json"
    )

    print("")
    print("======================================")
    print(f"Measuring {case} stenosis")
    print("======================================")
    source_path, source_data, landmarks_ras, landmark_labels, matched_ras = (
        load_measurement_inputs(case)
    )
    straight_length = distance(landmarks_ras[0], landmarks_ras[1])

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
    print(
        "Network points before/after junction merging:",
        raw_network.GetNumberOfPoints(),
        "/",
        network.GetNumberOfPoints(),
    )

    locator = vtk.vtkPointLocator()
    locator.SetDataSet(network)
    locator.BuildLocator()
    nearest_ids = [locator.FindClosestPoint(point) for point in landmarks_ras]
    nearest_points = [list(network.GetPoint(point_id)) for point_id in nearest_ids]
    snap_distances = [
        distance(landmarks_ras[index], nearest_points[index]) for index in range(2)
    ]
    adjacency = build_network_graph(network)
    path_ids, centerline_length = shortest_path(adjacency, nearest_ids[0], nearest_ids[1])
    path_points = [list(network.GetPoint(point_id)) for point_id in path_ids]
    path_cumulative = cumulative_distances(path_points)
    create_path_model(path_points, case_title)
    surface = get_live_airway_surface(segmentation_node)

    sample_count = max(2, int(math.ceil(centerline_length / SAMPLE_SPACING_MM)) + 1)
    sample_distances = [
        centerline_length * index / (sample_count - 1) for index in range(sample_count)
    ]
    profile = []
    for sample_index, arc_distance in enumerate(sample_distances):
        try:
            row = measure_section(surface, path_points, path_cumulative, arc_distance)
        except ValueError as error:
            print(
                f"WARNING: sample {sample_index} at {arc_distance:.3f} mm "
                f"skipped: {error}"
            )
            continue
        row["sample_index"] = sample_index
        profile.append(row)
    if not profile:
        raise RuntimeError("No valid cross-sections were measured.")
    local_minimum = min(profile, key=lambda row: row["area_mm2"])

    matched_projection = None
    if case == "postop":
        projected_ras, matched_arc_distance, matched_snap_distance = (
            project_point_to_polyline(matched_ras, path_points, path_cumulative)
        )
        try:
            primary_section = measure_section(
                surface, path_points, path_cumulative, matched_arc_distance
            )
        except ValueError as error:
            raise RuntimeError(
                f"Could not measure the exact postop matched section: {error}"
            ) from error
        primary_section["sample_index"] = None
        matched_projection = {
            "requested_position_ras_mm": matched_ras,
            "projected_position_ras_mm": projected_ras,
            "projection_distance_mm": matched_snap_distance,
            "distance_from_superior_mm": matched_arc_distance,
            "source_matching_method": source_data.get("matching_method"),
            "source_preop_relative_distance_from_inlet": source_data.get(
                "preop_relative_distance_from_inlet"
            ),
            "source_postop_distance_from_inlet_mm": source_data.get(
                "postop_distance_from_inlet_mm"
            ),
            "source_matched_section_normal_ras": source_data.get(
                "matched_section_normal_ras"
            ),
        }
        contour_name = "PostopMatchedCrossSection"
    else:
        primary_section = local_minimum
        contour_name = "PreopMinimumCrossSection"

    create_contour_model(primary_section["contour"], contour_name)
    remove_node_if_present(section_name)
    section_node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLMarkupsFiducialNode", section_name
    )
    section_node.AddControlPoint(
        primary_section["center_x_ras_mm"],
        primary_section["center_y_ras_mm"],
        primary_section["center_z_ras_mm"],
    )
    section_node.SetNthControlPointLabel(0, section_name)
    section_node.CreateDefaultDisplayNodes()
    section_node.GetDisplayNode().SetSelectedColor(1.0, 0.0, 1.0)
    section_node.GetDisplayNode().SetColor(1.0, 0.0, 1.0)
    section_node.SetDisplayVisibility(True)

    profile_fields = [
        "sample_index",
        "distance_from_superior_mm",
        "center_x_ras_mm",
        "center_y_ras_mm",
        "center_z_ras_mm",
        "normal_x",
        "normal_y",
        "normal_z",
        "area_mm2",
        "perimeter_mm",
        "minimum_feret_diameter_mm",
        "maximum_feret_diameter_mm",
        "equivalent_diameter_mm",
    ]
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    section_markup_path.parent.mkdir(parents=True, exist_ok=True)
    with open(profile_path, "w", newline="") as profile_file:
        writer = csv.DictWriter(profile_file, fieldnames=profile_fields)
        writer.writeheader()
        for row in profile:
            writer.writerow({field: row[field] for field in profile_fields})
    if not slicer.util.saveNode(section_node, str(section_markup_path)):
        raise RuntimeError(f"Failed to save section markup: {section_markup_path}")

    summary = {
        "schema_version": 2,
        "case": case,
        "source_endpoints": str(source_path),
        "endpoint_labels": landmark_labels,
        "endpoint_positions_ras_mm": landmarks_ras,
        "nearest_network_point_ids": nearest_ids,
        "nearest_network_positions_ras_mm": nearest_points,
        "endpoint_to_network_snap_distances_mm": snap_distances,
        "straight_line_length_mm": straight_length,
        "centerline_length_mm": centerline_length,
        "sample_spacing_mm": SAMPLE_SPACING_MM,
        "valid_cross_section_count": len(profile),
        "minimum_section": public_measurement(
            primary_section,
            profile_fields,
            "sampled_interval_minimum" if case == "preop" else "matched_comparison",
        ),
    }
    if case == "postop":
        summary.update(
            {
                "source_matched_location": str(source_path),
                "matched_section": public_measurement(
                    primary_section, profile_fields, "matched_comparison"
                ),
                "matched_section_projection": matched_projection,
                "local_minimum_in_mapped_interval": public_measurement(
                    local_minimum, profile_fields, "sampled_interval_local_minimum"
                ),
            }
        )
    with open(summary_path, "w") as summary_file:
        json.dump(summary, summary_file, indent=2)

    print("Endpoint labels:", landmark_labels)
    print("Straight-line length (mm):", round(straight_length, 4))
    print("Centerline length (mm):", round(centerline_length, 4))
    print("Endpoint snap distances (mm):", [round(value, 4) for value in snap_distances])
    print("Valid cross-sections:", len(profile))
    role = "Matched" if case == "postop" else "Minimum"
    print(
        f"{role} section distance (mm):",
        round(primary_section["distance_from_superior_mm"], 4),
    )
    print(f"{role} area (mm^2):", round(primary_section["area_mm2"], 4))
    if case == "postop":
        print(
            "Local minimum area in mapped interval (mm^2):",
            round(local_minimum["area_mm2"], 4),
        )
    print(
        "Minimum Feret diameter (mm):",
        round(primary_section["minimum_feret_diameter_mm"], 4),
    )
    print(
        "Maximum Feret diameter (mm):",
        round(primary_section["maximum_feret_diameter_mm"], 4),
    )
    print("Equivalent diameter (mm):", round(primary_section["equivalent_diameter_mm"], 4))
    print("Profile CSV:", profile_path)
    print("Summary JSON:", summary_path)
    print("Measured-section markup:", section_markup_path)
    print("")
    print(f"Inspect {case_title}StenosisCenterlineSegment and {contour_name}")
    print("in the 3D and slice views before accepting the measurements.")
    print("======================================")


main()


