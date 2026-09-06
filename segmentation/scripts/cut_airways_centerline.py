import json
import pathlib
import re

import slicer
import vtk

import ClipVessel

# ============================================================
# OPTIONAL VMTK IMPORTS
# ============================================================

vtkvmtk = None
vtkvmtkComputationalGeometry = None
vtkvmtkMisc = None

try:
    from vmtk import vtkvmtk
except ImportError:
    vtkvmtk = None

try:
    import vtkvmtkComputationalGeometryPython as vtkvmtkComputationalGeometry
except ImportError:
    vtkvmtkComputationalGeometry = None

try:
    import vtkvmtkMiscPython as vtkvmtkMisc
except ImportError:
    vtkvmtkMisc = None


# ============================================================
# CONFIGURATION
# ============================================================

project_path = pathlib.Path("/home/hvoverme/tracheomalacia_cfd/")

scene_segmentation_node = slicer.mrmlScene.GetFirstNodeByName(
    "AirwayLungSegmentation"
)
if scene_segmentation_node is None:
    raise RuntimeError(
        "AirwayLungSegmentation node was not found. Run segment_airway.py first."
    )

CASE = scene_segmentation_node.GetAttribute("AirwayCase")
if CASE not in {"preop", "postop"}:
    raise RuntimeError(
        "The live AirwayLungSegmentation node has no valid AirwayCase tag."
    )

print("Using scene case:", CASE)

CUT_ENDPOINTS_NODE_NAME = "AirwayCutEndpoints"

cut_endpoints_path = (
    project_path / "segmentation" / "assets" / CASE / "refined_endpoints.json"
)

# Flow extension length, as a multiple of the local vessel/airway
# radius at each cut (matches ClipVesselLogic's own default so the
# scripted result matches the manual "Clip Vessel" module).
EXTENSION_RATIO = 5.0
WALL_ENTITY_ID = 1
BOUNDARY_IDS_PATH = (
    project_path / "segmentation" / "assets" / CASE / "AirwayCFDBoundaries.json"
)


# ============================================================
# HELPERS
# ============================================================

def new_vmtk_instance(class_name):

    modules = [
        vtkvmtk,
        vtkvmtkComputationalGeometry,
        vtkvmtkMisc,
    ]

    for module in modules:
        if module is not None and hasattr(module, class_name):
            return getattr(module, class_name)()

    raise RuntimeError(
        f"Could not find VMTK class '{class_name}'. "
        "Make sure the SlicerVMTK extension is installed and loaded."
    )


def remove_node_if_present(node_name):

    try:
        existing_node = slicer.util.getNode(node_name)
    except Exception:
        existing_node = None

    if existing_node is not None:
        slicer.mrmlScene.RemoveNode(existing_node)


def distance2(a, b):
    return vtk.vtkMath.Distance2BetweenPoints(a, b)


def deep_copy_polydata(poly_data):

    copy = vtk.vtkPolyData()
    copy.DeepCopy(poly_data)
    return copy


def clean_polydata(poly_data):

    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(poly_data)
    cleaner.Update()

    triangle_filter = vtk.vtkTriangleFilter()
    triangle_filter.SetInputConnection(cleaner.GetOutputPort())
    triangle_filter.PassLinesOff()
    triangle_filter.PassVertsOff()
    triangle_filter.Update()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(triangle_filter.GetOutputPort())
    normals.SetAutoOrientNormals(1)
    normals.SetFlipNormals(0)
    normals.SetConsistency(1)
    normals.SplittingOff()
    normals.Update()

    return deep_copy_polydata(normals.GetOutput())


def largest_region(poly_data):

    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputData(poly_data)
    connectivity.SetExtractionModeToLargestRegion()
    connectivity.Update()

    geometry = vtk.vtkGeometryFilter()
    geometry.SetInputConnection(connectivity.GetOutputPort())
    geometry.Update()

    return deep_copy_polydata(geometry.GetOutput())


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


def ensure_cut_endpoints_node():

    # These are the manually-refined cut locations (moved de visu for a
    # better cut), kept as a separate node/label namespace from the
    # "CenterlineEndpoints" node used earlier by calculate_centerline.py so
    # the two point sets never get confused with one another.
    try:
        return slicer.util.getNode(CUT_ENDPOINTS_NODE_NAME)
    except Exception:
        pass

    with open(cut_endpoints_path, "r") as endpoints_file:
        endpoints_data = json.load(endpoints_file)

    endpoints_markup_data = endpoints_data["markups"][0]
    coordinate_system = endpoints_markup_data.get("coordinateSystem", "LPS")
    control_points = endpoints_markup_data["controlPoints"]

    if not control_points:
        raise RuntimeError(
            f"No control points found in {cut_endpoints_path}."
        )

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

    return cut_endpoints_node


def get_airway_surface_polydata():

    segmentation_node = scene_segmentation_node
    segmentation = segmentation_node.GetSegmentation()
    airways_segment_id = segmentation.GetSegmentIdBySegmentName("Airways")

    if not airways_segment_id:
        raise RuntimeError(
            "Airways segment was not found in AirwayLungSegmentation."
        )

    segmentation_node.CreateClosedSurfaceRepresentation()

    poly_data = vtk.vtkPolyData()
    segmentation_node.GetClosedSurfaceRepresentation(
        airways_segment_id,
        poly_data
    )

    if poly_data.GetNumberOfPoints() == 0:
        raise RuntimeError("Airways closed surface is empty.")

    return segmentation_node, airways_segment_id, deep_copy_polydata(poly_data)


def get_endpoint_positions(markups_node):

    positions = []

    for point_index in range(markups_node.GetNumberOfControlPoints()):
        position = [0.0, 0.0, 0.0]
        markups_node.GetNthControlPointPositionWorld(point_index, position)
        positions.append(position)

    return positions



def add_model_node(name, poly_data, color, opacity=1.0, line_width=None):

    remove_node_if_present(name)

    model_node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLModelNode",
        name
    )
    model_node.SetAndObserveMesh(poly_data)
    model_node.CreateDefaultDisplayNodes()
    model_node.GetDisplayNode().SetColor(*color)
    model_node.GetDisplayNode().SetOpacity(opacity)

    if line_width is not None:
        model_node.GetDisplayNode().SetLineWidth(line_width)

    model_node.SetDisplayVisibility(True)
    return model_node


def to_patch_name(label):

    patch_name = re.sub(r"[^0-9A-Za-z_]+", "_", label.strip())
    patch_name = re.sub(r"_+", "_", patch_name).strip("_")
    patch_name = patch_name.lower()

    if not patch_name:
        patch_name = "boundary"

    if patch_name[0].isdigit():
        patch_name = f"patch_{patch_name}"

    return patch_name


def extract_boundaries(boundary_surface_poly_data):

    boundary_extractor = new_vmtk_instance("vtkvmtkPolyDataBoundaryExtractor")
    boundary_extractor.SetInputData(boundary_surface_poly_data)
    boundary_extractor.Update()

    boundaries = deep_copy_polydata(boundary_extractor.GetOutput())

    if boundaries.GetNumberOfCells() == 0:
        raise RuntimeError("No open boundaries were found on the airway surface.")

    return boundaries


def boundary_cell_barycenter(boundaries_poly_data, cell_index):

    points = boundaries_poly_data.GetCell(cell_index).GetPoints()
    barycenter = [0.0, 0.0, 0.0]

    if vtkvmtk is not None and hasattr(vtkvmtk, "vtkvmtkBoundaryReferenceSystems"):
        vtkvmtk.vtkvmtkBoundaryReferenceSystems.ComputeBoundaryBarycenter(
            points,
            barycenter
        )
        return barycenter

    number_of_points = points.GetNumberOfPoints()

    for point_index in range(number_of_points):
        point = points.GetPoint(point_index)
        barycenter[0] += point[0]
        barycenter[1] += point[1]
        barycenter[2] += point[2]

    barycenter[0] /= number_of_points
    barycenter[1] /= number_of_points
    barycenter[2] /= number_of_points

    return barycenter


def assign_boundary_names(boundaries_poly_data, endpoints_node):

    endpoint_info = []

    for point_index in range(endpoints_node.GetNumberOfControlPoints()):
        position = [0.0, 0.0, 0.0]
        endpoints_node.GetNthControlPointPositionWorld(point_index, position)
        label = endpoints_node.GetNthControlPointLabel(point_index)
        endpoint_info.append(
            {
                "label": label,
                "patch_name": to_patch_name(label),
                "position": position,
            }
        )

    boundary_info = []
    remaining_indices = set(range(len(endpoint_info)))

    for boundary_id in range(boundaries_poly_data.GetNumberOfCells()):
        barycenter = boundary_cell_barycenter(boundaries_poly_data, boundary_id)

        if not remaining_indices:
            raise RuntimeError(
                "More open boundaries were found than available endpoint labels."
            )

        matched_index = min(
            remaining_indices,
            key=lambda idx: distance2(barycenter, endpoint_info[idx]["position"])
        )
        remaining_indices.remove(matched_index)

        boundary_info.append(
            {
                "boundary_id": boundary_id,
                "entity_id": WALL_ENTITY_ID + 1 + boundary_id,
                "label": endpoint_info[matched_index]["label"],
                "patch_name": endpoint_info[matched_index]["patch_name"],
                "barycenter_ras": barycenter,
            }
        )

    return boundary_info


def set_wall_and_cap_entity_ids(poly_data, array_name):

    entity_ids_array = poly_data.GetCellData().GetArray(array_name)

    if entity_ids_array is None:
        raise RuntimeError(
            f"Expected cell data array '{array_name}' on capped surface."
        )

    for cell_index in range(poly_data.GetNumberOfCells()):
        entity_id = int(round(entity_ids_array.GetTuple1(cell_index)))
        if entity_id <= 0:
            entity_ids_array.SetTuple1(cell_index, WALL_ENTITY_ID)

    poly_data.GetCellData().SetScalars(entity_ids_array)
    poly_data.Modified()


def extract_cells_by_entity_id(poly_data, array_name, entity_id):

    threshold = vtk.vtkThreshold()
    threshold.SetInputData(poly_data)
    threshold.SetInputArrayToProcess(
        0,
        0,
        0,
        vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS,
        array_name
    )
    threshold.SetLowerThreshold(entity_id - 0.5)
    threshold.SetUpperThreshold(entity_id + 0.5)
    threshold.Update()

    geometry = vtk.vtkGeometryFilter()
    geometry.SetInputConnection(threshold.GetOutputPort())
    geometry.Update()

    return deep_copy_polydata(geometry.GetOutput())


def write_boundary_mapping(boundary_info):

    boundary_mapping = {
        "wall": {
            "patch_name": "wall",
            "entity_id": WALL_ENTITY_ID,
        },
        "caps": {
            info["patch_name"]: {
                "label": info["label"],
                "entity_id": info["entity_id"],
                "barycenter_ras": info["barycenter_ras"],
            }
            for info in boundary_info
        }
    }

    with open(BOUNDARY_IDS_PATH, "w") as boundary_file:
        json.dump(boundary_mapping, boundary_file, indent=4)

    return boundary_mapping


# ============================================================
# LOAD REQUIRED INPUTS
# ============================================================

print("")
print("======================================")
print("Preparing airway clipping inputs")
print("======================================")

cut_endpoints_node = ensure_cut_endpoints_node()
endpoint_positions = get_endpoint_positions(cut_endpoints_node)

if len(endpoint_positions) < 2:
    raise RuntimeError(
        "At least two airway cut endpoints are required for airway clipping."
    )

network_model_node = slicer.util.getNode("AirwayNetworkModel")
network_poly_data = network_model_node.GetPolyData()

if network_poly_data is None or network_poly_data.GetNumberOfPoints() == 0:
    raise RuntimeError(
        "AirwayNetworkModel is missing or empty. Run calculate_centerline.py first."
    )

segmentation_node, airways_segment_id, airway_surface_poly_data = (
    get_airway_surface_polydata()
)

airway_surface_poly_data = clean_polydata(airway_surface_poly_data)

print("Cut endpoints:", len(endpoint_positions))
print("Network points:", network_poly_data.GetNumberOfPoints())
print("Airway surface points:", airway_surface_poly_data.GetNumberOfPoints())


# ============================================================
# CLIP AIRWAY SURFACE AT ENDPOINTS AND ADD FLOW EXTENSIONS
#
# Delegates to ClipVesselLogic, the same logic used by the interactive
# "Clip Vessel" module (SlicerVMTK), so this matches running that
# module manually with AirwayNetworkModel as centerlines and
# AirwayCutEndpoints as clip points.
#
# Flow extensions are also generated here, via ClipVesselLogic's own
# extension step (addFlowExtensions=True) rather than a separately
# configured vtkvmtkPolyDataFlowExtensionsFilter call: this reuses its
# adaptive defaults (extension length as a multiple of the local
# radius, extension radius matching the local radius, centerline
# -direction orientation) instead of the fixed, non-adaptive values an
# earlier version of this script used, which produced extensions that
# didn't scale naturally with the airway's size at each cut.
# Capping is intentionally left to a later step (cap=False) so the
# caps can be tagged with per-boundary CellEntityIds for CFD patch
# naming, which ClipVesselLogic's own capping does not do.
# ============================================================

print("")
print("======================================")
print("Clipping airway surface and adding flow extensions")
print("======================================")

clip_vessel_logic = ClipVessel.ClipVesselLogic()

extended_open_surface_poly_data = clip_vessel_logic.clipVessel(
    airway_surface_poly_data,
    network_model_node,
    cut_endpoints_node,
    False,
    True,
    EXTENSION_RATIO,
    "CENTERLINE_DIRECTION"
)

if clip_vessel_logic.lastUnclippedPoints:
    print(
        "WARNING: no cut was made at:",
        ", ".join(clip_vessel_logic.lastUnclippedPoints)
    )
    print(
        "These points are positioned exactly at, or beyond, the "
        "airway surface -- move them slightly inward."
    )

extended_open_surface_model_node = add_model_node(
    "AirwayExtendedSurfaceOpen",
    extended_open_surface_poly_data,
    color=(0.0, 0.6, 1.0),
    opacity=0.5
)

print(
    "Extended open surface points:",
    extended_open_surface_poly_data.GetNumberOfPoints()
)


# ============================================================
# IDENTIFY OPEN BOUNDARIES FOR NAMED CAPS
# ============================================================

print("")
print("======================================")
print("Identifying airway boundary openings")
print("======================================")

extended_boundaries_poly_data = extract_boundaries(
    extended_open_surface_poly_data
)

boundary_info = assign_boundary_names(
    extended_boundaries_poly_data,
    cut_endpoints_node
)


for info in boundary_info:
    print(
        f"Boundary {info['boundary_id']}: {info['label']} -> "
        f"patch '{info['patch_name']}' (entity id {info['entity_id']})"
    )


# ============================================================
# CAP EXTENDED SURFACE
# ============================================================

print("")
print("======================================")
print("Capping extended surface")
print("======================================")

# Flat caps rather than a smoothed/domed cap: cleaner, planar inlet/
# outlet patches are what a CFD boundary condition actually wants, and
# the flow extensions already added above provide the flow-development
# length, so there's no need for the cap itself to blend into the wall
# shape. This is the same filter (with zero displacement) that
# ClipVesselLogic uses for its own "Cap output surface" option.
capper = new_vmtk_instance("vtkvmtkCapPolyData")
capper.SetInputData(extended_open_surface_poly_data)
capper.SetCellEntityIdsArrayName("CellEntityIds")
capper.SetCellEntityIdOffset(WALL_ENTITY_ID + 1)
capper.SetDisplacement(0.0)
capper.SetInPlaneDisplacement(0.0)
capper.Update()

capped_surface_poly_data = deep_copy_polydata(capper.GetOutput())
set_wall_and_cap_entity_ids(capped_surface_poly_data, "CellEntityIds")
capped_surface_poly_data = clean_polydata(capped_surface_poly_data)

capped_surface_model_node = add_model_node(
    "AirwayExtendedSurfaceCapped",
    capped_surface_poly_data,
    color=(0.0, 1.0, 0.0),
    opacity=0.4
)

capped_surface_model_node.SetAttribute("AirwayCase", CASE)
capped_surface_model_node.SetAttribute("BoundaryPatch.wall", str(WALL_ENTITY_ID))

for info in boundary_info:
    capped_surface_model_node.SetAttribute(
        f"BoundaryPatch.{info['patch_name']}",
        str(info['entity_id'])
    )

wall_poly_data = extract_cells_by_entity_id(
    capped_surface_poly_data,
    "CellEntityIds",
    WALL_ENTITY_ID
)
wall_model_node = add_model_node(
    "wall",
    wall_poly_data,
    color=(0.8, 0.8, 0.8),
    opacity=0.2
)
wall_model_node.SetDisplayVisibility(False)

cap_model_nodes = []

for info in boundary_info:
    cap_poly_data = extract_cells_by_entity_id(
        capped_surface_poly_data,
        "CellEntityIds",
        info["entity_id"]
    )

    cap_model_node = add_model_node(
        info["patch_name"],
        cap_poly_data,
        color=(1.0, 0.0, 1.0),
        opacity=1.0
    )
    cap_model_node.SetAttribute("BoundaryLabel", info["label"])
    cap_model_node.SetAttribute("BoundaryPatchName", info["patch_name"])
    cap_model_node.SetAttribute("CellEntityId", str(info["entity_id"]))
    cap_model_nodes.append(cap_model_node)

boundary_mapping = write_boundary_mapping(boundary_info)

print(
    "Capped extended surface points:",
    capped_surface_poly_data.GetNumberOfPoints()
)
print("Boundary mapping written to:", BOUNDARY_IDS_PATH)


# ============================================================
# DISPLAY
# ============================================================

segmentation_display_node = segmentation_node.GetDisplayNode()
if segmentation_display_node is not None:
    segmentation_display_node.SetOpacity3D(0.15)

cut_endpoints_node.SetDisplayVisibility(True)
network_model_node.SetDisplayVisibility(True)
extended_open_surface_model_node.SetDisplayVisibility(False)
capped_surface_model_node.SetDisplayVisibility(True)


# ============================================================
# FINAL REPORT
# ============================================================

print("")
print("======================================")
print("AIRWAY CFD SURFACE PREPARATION COMPLETE")
print("======================================")
print("")
print("Airways segment ID:", airways_segment_id)
print("Cut endpoints node:", cut_endpoints_node.GetName())
print("Network model:", network_model_node.GetName())
print("Extended surface model:", extended_open_surface_model_node.GetName())
print("Capped CFD surface model:", capped_surface_model_node.GetName())
print("")
print("Visible result:", capped_surface_model_node.GetName())
print("")
print("Boundary patches:")
print(f"  wall -> entity id {WALL_ENTITY_ID}")
for info in boundary_info:
    print(
        f"  {info['patch_name']} -> entity id {info['entity_id']} "
        f"(from {info['label']})"
    )
print("")
print("Boundary mapping file:", BOUNDARY_IDS_PATH)
print("")
print("======================================")
