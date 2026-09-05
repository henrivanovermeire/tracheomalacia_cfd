#!/usr/bin/env pvpython
"""Render the fixed postoperative resistance planes on the airway mesh.

Example:
    HOME=/tmp pvpython assignment/scripts/render_resistance_planes.py \
        openFOAM/postop_assignment4/airways.msh
"""

import argparse
import json
import math
import subprocess
import tempfile
from pathlib import Path

from paraview.simple import (
    ColorBy,
    CreateView,
    LegacyVTKReader,
    Plane,
    Render,
    SaveScreenshot,
    Show,
)

PLANE_COLORS = {
    "superior": [0.12, 0.47, 0.71],
    "inferior": [0.90, 0.38, 0.08],
}


def normalize(vector):
    magnitude = math.sqrt(sum(component * component for component in vector))
    if magnitude <= 1e-12:
        raise ValueError("A zero-length plane normal is invalid.")
    return [component / magnitude for component in vector]


def cross(first, second):
    return [
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    ]


def add(first, second):
    return [first[index] + second[index] for index in range(3)]


def scale(vector, factor):
    return [factor * component for component in vector]


def add_plane(name, origin_m, normal, view, size_mm=10.0):
    origin = [1000.0 * coordinate for coordinate in origin_m]
    normal = normalize(normal)
    reference = [0.0, 0.0, 1.0]
    if abs(sum(normal[i] * reference[i] for i in range(3))) > 0.9:
        reference = [1.0, 0.0, 0.0]
    first_axis = normalize(cross(normal, reference))
    second_axis = normalize(cross(normal, first_axis))
    half = 0.5 * size_mm

    plane = Plane(registrationName=f"{name} resistance plane")
    plane.Origin = add(add(origin, scale(first_axis, -half)), scale(second_axis, -half))
    plane.Point1 = add(add(origin, scale(first_axis, half)), scale(second_axis, -half))
    plane.Point2 = add(add(origin, scale(first_axis, -half)), scale(second_axis, half))
    plane.XResolution = 1
    plane.YResolution = 1

    display = Show(plane, view)
    display.Representation = "Surface With Edges"
    display.AmbientColor = PLANE_COLORS[name]
    display.DiffuseColor = PLANE_COLORS[name]
    display.EdgeColor = PLANE_COLORS[name]
    display.Opacity = 0.62
    display.LineWidth = 4.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mesh", type=Path)
    parser.add_argument(
        "--sections",
        type=Path,
        default=Path("assignment/data/resistance_sections.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("report/figures/assignment4_resistance_planes.png"),
    )
    parser.add_argument("--width", type=int, default=2200)
    parser.add_argument("--height", type=int, default=1800)
    args = parser.parse_args()

    if not args.mesh.is_file():
        raise FileNotFoundError(args.mesh)
    with args.sections.open() as source:
        sections = json.load(source)
    if sections.get("coordinate_units") != "m":
        raise ValueError("Resistance-plane coordinates must be stored in metres.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="resistance_planes_") as temporary:
        vtk_path = Path(temporary) / "airway.vtk"
        subprocess.run(
            [
                "gmsh",
                str(args.mesh.resolve()),
                "-save",
                "-format",
                "vtk",
                "-o",
                str(vtk_path),
            ],
            check=True,
        )
        reader = LegacyVTKReader(
            registrationName="Postoperative airway mesh", FileNames=[str(vtk_path)]
        )
        reader.UpdatePipeline()

        view = CreateView("RenderView")
        view.ViewSize = [args.width, args.height]
        view.Background = [1.0, 1.0, 1.0]
        view.UseColorPaletteForBackground = 0
        view.OrientationAxesVisibility = 0
        view.CenterAxesVisibility = 0
        view.AxesGrid.Visibility = 0

        airway_display = Show(reader, view)
        airway_display.Representation = "Surface"
        airway_display.AmbientColor = [0.70, 0.74, 0.78]
        airway_display.DiffuseColor = [0.70, 0.74, 0.78]
        airway_display.Opacity = 0.22
        ColorBy(airway_display, None)

        for name in ("superior", "inferior"):
            plane = sections["planes"][name]
            add_plane(name, plane["origin"], plane["normal"], view)

        view.CameraPosition = [4.5, 295.0, 1338.5]
        view.CameraFocalPoint = [4.5, 113.0, 1338.5]
        view.CameraViewUp = [0.0, 0.0, 1.0]
        view.CameraParallelProjection = 1
        view.CameraParallelScale = 17.0

        Render(view)
        SaveScreenshot(
            str(args.output.resolve()),
            view,
            ImageResolution=[args.width, args.height],
            TransparentBackground=0,
            CompressionLevel=2,
        )

    print("Output:", args.output)
    print("Blue: superior/upstream plane")
    print("Orange: inferior/downstream plane")


if __name__ == "__main__":
    main()
