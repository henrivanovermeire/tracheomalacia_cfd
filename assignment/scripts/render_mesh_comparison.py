#!/usr/bin/env pvpython
"""Render matched full and cutaway views of two Gmsh airway meshes.

The script converts MSH files to temporary legacy VTK files with Gmsh, then
uses ParaView to render identical anatomical-frontal cameras for both mesh
levels. Example:

    pvpython assignment/scripts/render_mesh_comparison.py \
        openFOAM/postop_hxt_025/airways.msh \
        openFOAM/postop_hxt_015/airways.msh
"""

import argparse
import subprocess
import tempfile
from pathlib import Path

from paraview.simple import (

    ColorBy,
    CreateView,
    LegacyVTKReader,
    Render,
    SaveScreenshot,
    Show,
)


def convert_mesh(mesh_path, output_path):
    subprocess.run(
        [
            "gmsh",
            str(mesh_path.resolve()),
            "-save",
            "-format",
            "vtk",
            "-o",
            str(output_path),
        ],
        check=True,
    )


def configure_view(width, height, focal_point, parallel_scale):
    view = CreateView("RenderView")
    view.ViewSize = [width, height]
    view.Background = [1.0, 1.0, 1.0]
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 0
    view.CenterAxesVisibility = 0
    view.AxesGrid.Visibility = 0

    # Anatomical frontal view: anterior (+Y) toward posterior, superior upward.
    view.CameraPosition = [focal_point[0], focal_point[1] + 180.0, focal_point[2]]
    view.CameraFocalPoint = list(focal_point)
    view.CameraViewUp = [0.0, 0.0, 1.0]
    view.CameraParallelProjection = 1
    view.CameraParallelScale = parallel_scale
    return view


def style_mesh(source, view, line_width):
    display = Show(source, view)
    display.Representation = "Surface With Edges"
    display.AmbientColor = [0.78, 0.84, 0.91]
    display.DiffuseColor = [0.78, 0.84, 0.91]
    display.EdgeColor = [0.13, 0.17, 0.22]
    display.LineWidth = line_width
    ColorBy(display, None)
    return display


def save(view, output_path, width, height):
    Render(view)
    SaveScreenshot(
        str(output_path.resolve()),
        view,
        ImageResolution=[width, height],
        TransparentBackground=0,
        CompressionLevel=2,
    )


def render_full(reader, output_path, width, height):
    view = configure_view(width, height, (7.0, 113.5, 1337.5), 32.5)
    style_mesh(reader, view, 0.7)
    save(view, output_path, width, height)


def render_closeup(reader, output_path, width, height):
    # A matched surface close-up is used because legacy Gmsh VTK files contain
    # mixed boundary and volume cells, for which a generic clip may produce an
    # empty or misleading cut surface.
    view = configure_view(width, height, (4.5, 113.0, 1321.0), 12.0)
    style_mesh(reader, view, 0.9)
    save(view, output_path, width, height)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline_mesh", type=Path)
    parser.add_argument("selected_mesh", type=Path)
    parser.add_argument(
        "--output-directory", type=Path, default=Path("report/figures")
    )

    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=1600)
    args = parser.parse_args()

    for path in (args.baseline_mesh, args.selected_mesh):
        if not path.is_file():
            raise FileNotFoundError(path)
    args.output_directory.mkdir(parents=True, exist_ok=True)

    cases = (
        (args.baseline_mesh, "assignment5_mesh_025"),
        (args.selected_mesh, "assignment5_mesh_015"),
    )
    with tempfile.TemporaryDirectory(prefix="airway_mesh_render_") as temporary:
        temporary = Path(temporary)
        for mesh_path, stem in cases:
            vtk_path = temporary / f"{stem}.vtk"
            convert_mesh(mesh_path, vtk_path)
            reader = LegacyVTKReader(registrationName=stem, FileNames=[str(vtk_path)])
            reader.UpdatePipeline()
            render_full(
                reader,
                args.output_directory / f"{stem}_full.png",
                args.width,
                args.height,
            )
            render_closeup(
                reader,
                args.output_directory / f"{stem}_closeup.png",
                args.width,
                args.height,
            )

    print("Mesh comparison panels written to:", args.output_directory)


if __name__ == "__main__":
    main()
