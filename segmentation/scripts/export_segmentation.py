"""Export the final capped airway model as a case-specific STL for Gmsh.

Run from the 3D Slicer Python console after cut_airways_centerline.py:

    exec(open("/home/hvoverme/tracheomalacia_cfd/segmentation/scripts/export_segmentation.py").read())

The case is read from the AirwayCase tag on the final model. The output is
written to meshes/<case>/airways.stl so pre-op and post-op surfaces cannot
silently overwrite each other.
"""

from pathlib import Path

import slicer
import vtk


MODEL_NODE_NAME = "AirwayExtendedSurfaceCapped"
PROJECT_PATH = Path("/home/hvoverme/tracheomalacia_cfd")

model_node = slicer.mrmlScene.GetFirstNodeByName(MODEL_NODE_NAME)
if model_node is None or not model_node.IsA("vtkMRMLModelNode"):
    raise RuntimeError(
        f"Model node '{MODEL_NODE_NAME}' was not found. "
        "Run cut_airways_centerline.py first."
    )

CASE = model_node.GetAttribute("AirwayCase")
if CASE not in {"preop", "postop"}:
    raise RuntimeError(
        f"'{MODEL_NODE_NAME}' has no valid AirwayCase tag. Re-run "
        "cut_airways_centerline.py from a tagged segmentation scene."
    )

OUTPUT_PATH = PROJECT_PATH / "meshes" / CASE / "airways.stl"

print("")
print("======================================")
print("Exporting capped airway surface")
print("======================================")
print("Using model case:", CASE)

surface = model_node.GetPolyData()
if surface is None or surface.GetNumberOfPoints() == 0:
    raise RuntimeError(f"Model node '{MODEL_NODE_NAME}' has no surface data.")

# STL stores triangles only. Processing a copy leaves the Slicer scene and its
# CFD CellEntityIds unchanged.
triangulator = vtk.vtkTriangleFilter()
triangulator.SetInputData(surface)
triangulator.PassLinesOff()
triangulator.PassVertsOff()
triangulator.Update()

cleaner = vtk.vtkCleanPolyData()
cleaner.SetInputConnection(triangulator.GetOutputPort())
cleaner.Update()

export_surface = vtk.vtkPolyData()
export_surface.DeepCopy(cleaner.GetOutput())
if export_surface.GetNumberOfPolys() == 0:
    raise RuntimeError(f"Model node '{MODEL_NODE_NAME}' contains no polygons.")

# A closed surface is required for tetrahedral volume meshing.
boundary_edges = vtk.vtkFeatureEdges()
boundary_edges.SetInputData(export_surface)
boundary_edges.BoundaryEdgesOn()
boundary_edges.FeatureEdgesOff()
boundary_edges.NonManifoldEdgesOff()
boundary_edges.ManifoldEdgesOff()
boundary_edges.Update()
open_edge_count = boundary_edges.GetOutput().GetNumberOfCells()
if open_edge_count != 0:
    raise RuntimeError(
        f"The final model has {open_edge_count} open boundary edges. "
        "Verify that all extensions were capped before exporting."
    )

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

writer = vtk.vtkSTLWriter()
writer.SetFileName(str(OUTPUT_PATH))
writer.SetFileTypeToBinary()
writer.SetInputData(export_surface)
write_succeeded = writer.Write()

if write_succeeded != 1 or not OUTPUT_PATH.is_file():
    raise RuntimeError(f"Failed to write STL file: {OUTPUT_PATH}")

print("Source model:", MODEL_NODE_NAME)
print("Points:", export_surface.GetNumberOfPoints())
print("Triangles:", export_surface.GetNumberOfPolys())
print("Open boundary edges:", open_edge_count)
print("Output:", OUTPUT_PATH)
print("")
print("AIRWAY STL EXPORT COMPLETE")
print("======================================")
