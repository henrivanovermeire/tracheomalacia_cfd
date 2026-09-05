"""Export reproducible report images from the current 3D Slicer scene.

Run at the end of a case-specific Slicer workflow, after clipping and stenosis
measurement:

    exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/export_report_figures.py").read())

The script reads the case from AirwayLungSegmentation's AirwayCase attribute and
writes PNG files under report/figures. It temporarily changes display and camera
settings, then restores the scene as closely as possible.
"""

import math
from pathlib import Path

import slicer
import vtk


PROJECT_PATH = Path("/home/hvoverme/tracheomalacia_cfd")
OUTPUT_DIRECTORY = PROJECT_PATH / "report" / "figures"
SEGMENTATION_NODE_NAME = "AirwayLungSegmentation"
AIRWAY_SEGMENT_NAME = "Airways"
CFD_MODEL_NODE_NAME = "AirwayExtendedSurfaceCapped"
BACKGROUND_COLOR = (1.0, 1.0, 1.0)
AIRWAY_COLOR = (0.70, 0.82, 0.95)
MEASUREMENT_AIRWAY_OPACITY = 0.24


def first_node(name, required=False):
    node = slicer.mrmlScene.GetFirstNodeByName(name)
    if required and node is None:
        raise RuntimeError(f"Required scene node '{name}' was not found.")
    return node


def get_case(segmentation_node):
    case = segmentation_node.GetAttribute("AirwayCase")
    if case not in {"preop", "postop"}:
        raise RuntimeError(
            f"'{SEGMENTATION_NODE_NAME}' has no valid AirwayCase attribute."
        )
    return case


def get_three_d_view():
    layout_manager = slicer.app.layoutManager()
    if layout_manager is None or layout_manager.threeDViewCount == 0:
        raise RuntimeError("No 3D view is available in the current Slicer layout.")
    widget = layout_manager.threeDWidget(0)
    return widget.threeDView(), widget.mrmlViewNode()


def get_camera_node(view_node):
    camera_node = slicer.modules.cameras.logic().GetViewActiveCameraNode(view_node)
    if camera_node is None:
        raise RuntimeError("No active camera is associated with the 3D view.")
    return camera_node


def snapshot_display_state():
    state = []
    nodes = slicer.util.getNodesByClass("vtkMRMLDisplayNode")
    for node in nodes:
        values = {"visibility": node.GetVisibility()}
        if hasattr(node, "GetOpacity"):
            values["opacity"] = node.GetOpacity()
        if hasattr(node, "GetOpacity3D"):
            values["opacity3d"] = node.GetOpacity3D()
        if hasattr(node, "GetColor"):
            values["color"] = node.GetColor()
        if hasattr(node, "GetVisibility2D"):
            values["visibility2d"] = node.GetVisibility2D()
        if hasattr(node, "GetVisibility3D"):
            values["visibility3d"] = node.GetVisibility3D()
        state.append((node, values))
    return state


def restore_display_state(state):
    for node, values in state:
        if node is None or node.GetScene() is None:
            continue
        node.SetVisibility(values["visibility"])
        if "opacity" in values and hasattr(node, "SetOpacity"):
            node.SetOpacity(values["opacity"])
        if "opacity3d" in values and hasattr(node, "SetOpacity3D"):
            node.SetOpacity3D(values["opacity3d"])
        if "color" in values and hasattr(node, "SetColor"):
            node.SetColor(*values["color"])
        if "visibility2d" in values and hasattr(node, "SetVisibility2D"):
            node.SetVisibility2D(values["visibility2d"])
        if "visibility3d" in values and hasattr(node, "SetVisibility3D"):
            node.SetVisibility3D(values["visibility3d"])


def hide_all_display_nodes():
    for node in slicer.util.getNodesByClass("vtkMRMLDisplayNode"):
        node.SetVisibility(False)


def set_node_visibility(node, visible=True, opacity=None, color=None):
    if node is None:
        return
    node.CreateDefaultDisplayNodes()
    display = node.GetDisplayNode()
    if display is None:
        return
    display.SetVisibility(visible)
    if hasattr(display, "SetVisibility3D"):
        display.SetVisibility3D(visible)
    if opacity is not None:
        display.SetOpacity(opacity)
    if color is not None and hasattr(display, "SetColor"):
        display.SetColor(*color)


def segmentation_surface_bounds(segmentation_node):
    segmentation = segmentation_node.GetSegmentation()
    segment_id = segmentation.GetSegmentIdBySegmentName(AIRWAY_SEGMENT_NAME)
    if not segment_id:
        raise RuntimeError(f"Segment '{AIRWAY_SEGMENT_NAME}' was not found.")
    segmentation_node.CreateClosedSurfaceRepresentation()
    surface = vtk.vtkPolyData()
    segmentation_node.GetClosedSurfaceRepresentation(segment_id, surface)
    if surface.GetNumberOfPoints() == 0:
        raise RuntimeError("The Airways closed-surface representation is empty.")
    return surface.GetBounds(), segment_id


def node_bounds(node):
    if node is None:
        return None
    if node.IsA("vtkMRMLModelNode"):
        poly_data = node.GetPolyData()
        if poly_data is not None and poly_data.GetNumberOfPoints() > 0:
            return poly_data.GetBounds()
    bounds = [0.0] * 6
    if hasattr(node, "GetRASBounds"):
        node.GetRASBounds(bounds)
        if all(math.isfinite(value) for value in bounds):
            return bounds
    return None


def combined_bounds(nodes, fallback_bounds):
    valid = [node_bounds(node) for node in nodes]
    valid = [bounds for bounds in valid if bounds is not None]
    if not valid:
        return fallback_bounds
    return (
        min(bounds[0] for bounds in valid),
        max(bounds[1] for bounds in valid),
        min(bounds[2] for bounds in valid),
        max(bounds[3] for bounds in valid),
        min(bounds[4] for bounds in valid),
        max(bounds[5] for bounds in valid),
    )


def configure_frontal_camera(camera, bounds, render_window):
    center = (
        0.5 * (bounds[0] + bounds[1]),
        0.5 * (bounds[2] + bounds[3]),
        0.5 * (bounds[4] + bounds[5]),
    )
    x_span = max(bounds[1] - bounds[0], 1.0)
    y_span = max(bounds[3] - bounds[2], 1.0)
    z_span = max(bounds[5] - bounds[4], 1.0)
    width, height = render_window.GetSize()
    aspect = max(float(width) / max(height, 1), 0.25)

    # View from anterior toward posterior. With superior as view-up, this gives
    # the conventional frontal presentation: patient right appears image left.
    distance = 4.0 * max(x_span, y_span, z_span)
    camera.SetFocalPoint(*center)
    camera.SetPosition(center[0], center[1] + distance, center[2])
    camera.SetViewUp(0.0, 0.0, 1.0)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(0.58 * max(z_span, x_span / aspect))
    camera.SetClippingRange(max(0.1, distance - 2.5 * y_span), distance + 2.5 * y_span)


def capture_png(three_d_view, output_path):
    render_window = three_d_view.renderWindow()
    render_window.Render()
    image_filter = vtk.vtkWindowToImageFilter()
    image_filter.SetInput(render_window)
    image_filter.SetInputBufferTypeToRGB()
    image_filter.ReadFrontBufferOff()
    image_filter.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(output_path))
    writer.SetInputConnection(image_filter.GetOutputPort())
    writer.Write()
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError(f"Failed to write screenshot: {output_path}")


def configure_view(view_node):
    view_node.SetBackgroundColor(*BACKGROUND_COLOR)
    view_node.SetBackgroundColor2(*BACKGROUND_COLOR)
    view_node.SetBoxVisible(False)
    view_node.SetAxisLabelsVisible(False)
    if hasattr(view_node, "SetOrientationMarkerType"):
        view_node.SetOrientationMarkerType(0)


def capture_segmentation(case, three_d_view, view_node, camera, segmentation_node, bounds):
    hide_all_display_nodes()
    display = segmentation_node.GetDisplayNode()
    display.SetVisibility(True)
    display.SetVisibility3D(True)
    display.SetOpacity3D(1.0)
    configure_frontal_camera(camera, bounds, three_d_view.renderWindow())
    capture_png(three_d_view, OUTPUT_DIRECTORY / f"{case}_segmentation.png")


def capture_cfd_surface(case, three_d_view, camera, model_node, fallback_bounds):
    hide_all_display_nodes()
    set_node_visibility(model_node, opacity=1.0, color=AIRWAY_COLOR)
    bounds = node_bounds(model_node) or fallback_bounds
    configure_frontal_camera(camera, bounds, three_d_view.renderWindow())
    capture_png(three_d_view, OUTPUT_DIRECTORY / f"{case}_cfd_surface.png")


def capture_measurement(case, three_d_view, camera, segmentation_node, fallback_bounds):
    case_title = case.capitalize()
    path_node = first_node(f"{case_title}StenosisCenterlineSegment")
    if case == "preop":
        contour_node = first_node("PreopMinimumCrossSection")
        point_node = first_node("PreopMinimumSection")
        output_name = "preop_stenosis_measurement.png"
    else:
        contour_node = first_node("PostopMatchedCrossSection")
        point_node = first_node("PostopMeasuredSection")
        output_name = "postop_matched_section.png"

    measurement_nodes = [path_node, contour_node, point_node]
    missing = [
        name
        for name, node in zip(
            ["stenosis centerline segment", "cross-section contour", "section point"],
            measurement_nodes,
        )
        if node is None
    ]
    if missing:
        print("Skipping measurement screenshot; missing:", ", ".join(missing))
        return None

    hide_all_display_nodes()
    display = segmentation_node.GetDisplayNode()
    display.SetVisibility(True)
    display.SetVisibility3D(True)
    display.SetOpacity3D(MEASUREMENT_AIRWAY_OPACITY)
    set_node_visibility(path_node, opacity=1.0, color=(1.0, 0.65, 0.0))
    set_node_visibility(contour_node, opacity=1.0, color=(0.85, 0.0, 0.70))
    set_node_visibility(point_node, opacity=1.0, color=(0.85, 0.0, 0.70))

    bounds = combined_bounds(measurement_nodes, fallback_bounds)
    margin = 8.0
    bounds = (
        bounds[0] - margin,
        bounds[1] + margin,
        bounds[2] - margin,
        bounds[3] + margin,
        bounds[4] - margin,
        bounds[5] + margin,
    )
    configure_frontal_camera(camera, bounds, three_d_view.renderWindow())
    output_path = OUTPUT_DIRECTORY / output_name
    capture_png(three_d_view, output_path)
    return output_path


def main():
    layout_manager = slicer.app.layoutManager()
    if layout_manager is None:
        raise RuntimeError("Slicer layout manager is unavailable.")
    original_layout = layout_manager.layout
    layout_manager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
    slicer.app.processEvents()

    segmentation_node = first_node(SEGMENTATION_NODE_NAME, required=True)
    case = get_case(segmentation_node)
    model_node = first_node(CFD_MODEL_NODE_NAME, required=True)
    model_case = model_node.GetAttribute("AirwayCase")
    if model_case not in {None, case}:
        raise RuntimeError(
            f"Scene case is '{case}', but '{CFD_MODEL_NODE_NAME}' is tagged as "
            f"'{model_case}'."
        )

    three_d_view, view_node = get_three_d_view()
    camera_node = get_camera_node(view_node)
    camera = camera_node.GetCamera()
    render_window = three_d_view.renderWindow()
    segmentation_bounds, _ = segmentation_surface_bounds(segmentation_node)

    display_state = snapshot_display_state()
    camera_state = {
        "position": camera.GetPosition(),
        "focal_point": camera.GetFocalPoint(),
        "view_up": camera.GetViewUp(),
        "parallel_projection": camera.GetParallelProjection(),
        "parallel_scale": camera.GetParallelScale(),
        "clipping_range": camera.GetClippingRange(),
        "background": view_node.GetBackgroundColor(),
        "background2": view_node.GetBackgroundColor2(),
        "box_visible": view_node.GetBoxVisible(),
        "axis_labels_visible": view_node.GetAxisLabelsVisible(),
    }
    if hasattr(view_node, "GetOrientationMarkerType"):
        camera_state["orientation_marker_type"] = view_node.GetOrientationMarkerType()

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    written = []
    try:
        configure_view(view_node)
        capture_segmentation(
            case, three_d_view, view_node, camera, segmentation_node, segmentation_bounds
        )
        written.append(OUTPUT_DIRECTORY / f"{case}_segmentation.png")
        capture_cfd_surface(
            case, three_d_view, camera, model_node, segmentation_bounds
        )
        written.append(OUTPUT_DIRECTORY / f"{case}_cfd_surface.png")
        measurement_path = capture_measurement(
            case, three_d_view, camera, segmentation_node, segmentation_bounds
        )
        if measurement_path is not None:
            written.append(measurement_path)
    finally:
        restore_display_state(display_state)
        camera.SetPosition(*camera_state["position"])
        camera.SetFocalPoint(*camera_state["focal_point"])
        camera.SetViewUp(*camera_state["view_up"])
        camera.SetParallelProjection(camera_state["parallel_projection"])
        camera.SetParallelScale(camera_state["parallel_scale"])
        camera.SetClippingRange(*camera_state["clipping_range"])
        view_node.SetBackgroundColor(*camera_state["background"])
        view_node.SetBackgroundColor2(*camera_state["background2"])
        view_node.SetBoxVisible(camera_state["box_visible"])
        view_node.SetAxisLabelsVisible(camera_state["axis_labels_visible"])
        if "orientation_marker_type" in camera_state:
            view_node.SetOrientationMarkerType(camera_state["orientation_marker_type"])
        render_window.Render()
        layout_manager.setLayout(original_layout)
        slicer.app.processEvents()

    print("")
    print("======================================")
    print("REPORT FIGURE EXPORT COMPLETE")
    print("======================================")
    print("Case:", case)
    for output_path in written:
        print("Wrote:", output_path)
    print("Scene display and camera state restored.")


main()
