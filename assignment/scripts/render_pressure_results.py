#!/usr/bin/env pvpython
"""Render dimensional pressure and sample it along the matched tracheal path."""

import argparse
import csv
import math
import subprocess
from pathlib import Path

from paraview import servermanager
from paraview.simple import (
    Calculator,
    ColorBy,
    CreateView,
    GetColorTransferFunction,
    GetOpacityTransferFunction,
    GetScalarBar,
    OpenFOAMReader,
    ProbeLocation,
    Render,
    SaveScreenshot,
    Show,
)


def leaves(dataset):
    if hasattr(dataset, "GetNumberOfBlocks"):
        for index in range(dataset.GetNumberOfBlocks()):
            block = dataset.GetBlock(index)
            if block is not None:
                yield from leaves(block)
    else:
        yield dataset


def first_scalar(dataset, name):
    for leaf in leaves(dataset):
        for attributes in (leaf.GetPointData(), leaf.GetCellData(), leaf.GetFieldData()):
            array = attributes.GetArray(name)
            if array is not None and array.GetNumberOfTuples() > 0:
                return float(array.GetComponent(0, 0))
    raise RuntimeError(f"Probe did not return array '{name}'.")


def array_range(dataset, name):
    ranges = []
    for leaf in leaves(dataset):
        for attributes in (leaf.GetPointData(), leaf.GetCellData()):
            array = attributes.GetArray(name)
            if array is not None and array.GetNumberOfTuples() > 0:
                ranges.append(array.GetRange(0))
    if not ranges:
        raise RuntimeError(f"Array '{name}' was not available.")
    return min(item[0] for item in ranges), max(item[1] for item in ranges)


def load_centerline_profile(path):
    with path.open() as source:
        rows = list(csv.DictReader(source))
    if len(rows) < 2:
        raise RuntimeError(f"At least two centerline samples are required in {path}.")
    return [
        {
            "distance_mm": float(row["distance_from_superior_mm"]),
            "point_m": [
                float(row["center_x_ras_mm"]) / 1000.0,
                float(row["center_y_ras_mm"]) / 1000.0,
                float(row["center_z_ras_mm"]) / 1000.0,
            ],
        }
        for row in rows
    ]


def write_pressure_csv(samples, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=["distance_from_superior_mm", "kinematic_pressure_m2_s2", "pressure_pa"],
        )
        writer.writeheader()
        writer.writerows(samples)


def create_gnuplot(csv_path, tex_path):
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    report_dir = tex_path.resolve().parents[1]
    output_relative = tex_path.resolve().relative_to(report_dir).as_posix()
    script_path = tex_path.resolve().with_suffix(".gp")
    script = f'''set terminal cairolatex pdf color size 15cm,8.5cm font ",10"
set output "{output_relative}"
set datafile separator comma
set key off
set grid xtics ytics back lc rgb "#d0d0d0"
set xlabel "Centerline distance from mapped superior limit (mm)"
set ylabel "Area-interpolated centerline pressure (Pa)"
set title "Postoperative pressure through the anatomically matched region"
plot "{csv_path.resolve().as_posix()}" using 1:3 every ::1 with lines lw 2.2 lc rgb "#2166ac"
unset output
'''
    script_path.write_text(script)
    subprocess.run(["gnuplot", str(script_path)], cwd=report_dir, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("foam_case", type=Path)
    parser.add_argument(
        "--profile", type=Path,
        default=Path("assignment/data/postop_stenosis_profile.csv"),
    )
    parser.add_argument("--density", type=float, default=1.204)
    parser.add_argument(
        "--image", type=Path,
        default=Path("report/figures/assignment4_pressure_distribution.png"),
    )
    parser.add_argument(
        "--plot", type=Path,
        default=Path("report/figures/assignment4_centerline_pressure.tex"),
    )
    parser.add_argument(
        "--csv", type=Path,
        default=Path("assignment/data/postop_assignment4_centerline_pressure.csv"),
    )
    parser.add_argument("--pressure-min", type=float, default=-40.0)
    parser.add_argument("--pressure-max", type=float, default=90.0)
    parser.add_argument("--width", type=int, default=2400)
    parser.add_argument("--height", type=int, default=1800)
    args = parser.parse_args()

    centerline = load_centerline_profile(args.profile)
    reader = OpenFOAMReader(
        registrationName=args.foam_case.stem,
        FileName=str(args.foam_case.resolve()),
    )
    reader.UpdatePipelineInformation()
    if hasattr(reader, "MeshRegions"):
        reader.MeshRegions = ["internalMesh"]
    if hasattr(reader, "CellArrays"):
        reader.CellArrays = ["p", "U"]
    times = list(reader.TimestepValues) if reader.TimestepValues else [0.0]
    final_time = max(times)
    reader.UpdatePipeline(final_time)

    pressure = Calculator(registrationName="Dimensional pressure", Input=reader)
    pressure.ResultArrayName = "PressurePa"
    pressure.Function = f"p*{args.density:.12g}"
    pressure.UpdatePipeline(final_time)

    samples = []
    probe = ProbeLocation(registrationName="Centerline pressure probe", Input=pressure)
    for sample in centerline:
        probe.ProbeType.Center = sample["point_m"]
        probe.UpdatePipeline(final_time)
        data = servermanager.Fetch(probe)
        kinematic = first_scalar(data, "p")
        samples.append(
            {
                "distance_from_superior_mm": sample["distance_mm"],
                "kinematic_pressure_m2_s2": kinematic,
                "pressure_pa": args.density * kinematic,
            }
        )

    write_pressure_csv(samples, args.csv)
    create_gnuplot(args.csv, args.plot)

    fetched_pressure = servermanager.Fetch(pressure)
    actual_range = array_range(fetched_pressure, "PressurePa")

    view = CreateView("RenderView")
    view.ViewSize = [args.width, args.height]
    view.Background = [1.0, 1.0, 1.0]
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 1
    view.CenterAxesVisibility = 0
    view.AxesGrid.Visibility = 0

    display = Show(pressure, view)
    display.Representation = "Surface"
    lut = GetColorTransferFunction("PressurePa")
    lut.ApplyPreset("Cool to Warm", True)
    ColorBy(display, ("CELLS", "PressurePa"))
    opacity = GetOpacityTransferFunction("PressurePa")
    lut.RescaleTransferFunction(args.pressure_min, args.pressure_max)
    opacity.RescaleTransferFunction(args.pressure_min, args.pressure_max)
    display.SetScalarBarVisibility(view, True)
    scalar_bar = GetScalarBar(lut, view)
    scalar_bar.Title = "Gauge pressure"
    scalar_bar.ComponentTitle = "Pa"
    scalar_bar.TitleColor = [0.0, 0.0, 0.0]
    scalar_bar.LabelColor = [0.0, 0.0, 0.0]
    scalar_bar.WindowLocation = "Upper Right Corner"
    scalar_bar.ScalarBarLength = 0.35
    scalar_bar.TitleFontSize = 18
    scalar_bar.LabelFontSize = 16

    view.CameraPosition = [0.007, 0.32, 1.337]
    view.CameraFocalPoint = [0.007, 0.112, 1.337]
    view.CameraViewUp = [0.0, 0.0, 1.0]
    view.CameraParallelProjection = 1
    view.ResetCamera()
    view.CameraParallelScale *= 0.88
    Render(view)
    args.image.parent.mkdir(parents=True, exist_ok=True)
    SaveScreenshot(
        str(args.image.resolve()), view,
        ImageResolution=[args.width, args.height],
        TransparentBackground=0, CompressionLevel=2,
    )

    print(f"Rendered final time: {final_time:g}")
    print(f"Actual pressure range: {actual_range[0]:.6g} to {actual_range[1]:.6g} Pa")
    print(f"Displayed pressure range: {args.pressure_min:g} to {args.pressure_max:g} Pa")
    print(f"Image: {args.image}")
    print(f"Centerline CSV: {args.csv}")
    print(f"Centerline plot: {args.plot}")


if __name__ == "__main__":
    main()
