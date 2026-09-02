#!/usr/bin/env pvpython
"""Render a publication-quality velocity-vector image from an OpenFOAM case.

Example:
    pvpython assignment/scripts/render_flow_vectors.py \
        results/postop_assignment4/postop_assignment4.foam \
        --output report/figures/assignment4_velocity_vectors.png
"""

import argparse
from pathlib import Path

from paraview.simple import (
    Calculator,
    CellDatatoPointData,
    ColorBy,
    CreateView,
    GetColorTransferFunction,
    GetOpacityTransferFunction,
    GetScalarBar,
    Glyph,
    Hide,
    OpenFOAMReader,
    Render,
    SaveScreenshot,
    Show,
    Slice,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("foam_case", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("report/figures/assignment4_velocity_vectors.png"),
    )
    parser.add_argument(
        "--slice-origin",
        nargs=3,
        type=float,
        default=(0.00502, 0.11207, 1.33540),
        metavar=("X", "Y", "Z"),
        help="Slice origin in OpenFOAM coordinates (metres)",
    )
    parser.add_argument(
        "--slice-normal",
        nargs=3,
        type=float,
        default=(0.0, 1.0, 0.0),
        metavar=("NX", "NY", "NZ"),
        help="Slice-plane normal (default: coronal projection normal)",
    )
    parser.add_argument("--glyph-stride", type=int, default=32)
    parser.add_argument("--glyph-scale", type=float, default=0.00035)
    parser.add_argument("--width", type=int, default=2400)
    parser.add_argument("--height", type=int, default=1800)
    parser.add_argument("--velocity-max", type=float, default=10.0)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    reader = OpenFOAMReader(
        registrationName=args.foam_case.stem,
        FileName=str(args.foam_case.resolve()),
    )
    reader.UpdatePipelineInformation()
    if hasattr(reader, "MeshRegions"):
        reader.MeshRegions = ["internalMesh"]
    if hasattr(reader, "CellArrays"):
        reader.CellArrays = ["U", "p"]
    time_values = list(reader.TimestepValues) if reader.TimestepValues else [0.0]
    final_time = max(time_values)
    reader.UpdatePipeline(final_time)

    # Convert the cell-centred OpenFOAM velocity to points for smooth slice
    # interpolation and vector glyph orientation.
    point_fields = CellDatatoPointData(
        registrationName="Cell data to point data", Input=reader
    )
    point_fields.ProcessAllArrays = 1
    point_fields.UpdatePipeline(final_time)

    velocity = Calculator(registrationName="Velocity magnitude", Input=point_fields)
    velocity.ResultArrayName = "VelocityMagnitude"
    velocity.Function = "mag(U)"
    velocity.UpdatePipeline(final_time)

    section = Slice(registrationName="Flow visualization plane", Input=velocity)
    section.SliceType = "Plane"
    section.SliceType.Origin = list(args.slice_origin)
    section.SliceType.Normal = list(args.slice_normal)
    section.UpdatePipeline(final_time)

    glyphs = Glyph(registrationName="Velocity vectors", Input=velocity, GlyphType="Arrow")
    glyphs.OrientationArray = ["POINTS", "U"]
    glyphs.ScaleArray = ["POINTS", "VelocityMagnitude"]
    glyphs.ScaleFactor = args.glyph_scale
    if hasattr(glyphs, "GlyphMode"):
        glyphs.GlyphMode = "Every Nth Point"
    if hasattr(glyphs, "Stride"):
        glyphs.Stride = max(1, args.glyph_stride)
    if hasattr(glyphs, "MaximumNumberOfSamplePoints"):
        glyphs.MaximumNumberOfSamplePoints = 1400
    glyphs.UpdatePipeline(final_time)

    view = CreateView("RenderView")
    view.ViewSize = [args.width, args.height]
    view.Background = [1.0, 1.0, 1.0]
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 1
    view.CenterAxesVisibility = 0
    view.AxesGrid.Visibility = 0

    # The visible external surface provides anatomical context without obscuring
    # vectors on the internal section.
    airway_display = Show(reader, view)
    airway_display.Representation = "Surface"
    airway_display.Opacity = 0.16
    airway_display.AmbientColor = [0.65, 0.68, 0.72]
    airway_display.DiffuseColor = [0.65, 0.68, 0.72]
    ColorBy(airway_display, None)

    velocity_lut = GetColorTransferFunction("VelocityMagnitude")
    velocity_lut.ApplyPreset("Viridis", True)
    velocity_lut.RescaleTransferFunction(0.0, args.velocity_max)
    velocity_opacity = GetOpacityTransferFunction("VelocityMagnitude")
    velocity_opacity.RescaleTransferFunction(0.0, args.velocity_max)
    glyph_display = Show(glyphs, view)
    glyph_display.Representation = "Surface"
    ColorBy(glyph_display, ("POINTS", "VelocityMagnitude"))
    glyph_display.LookupTable = velocity_lut
    velocity_lut.RescaleTransferFunction(0.0, args.velocity_max)
    velocity_opacity.RescaleTransferFunction(0.0, args.velocity_max)
    glyph_display.SetScalarBarVisibility(view, True)

    scalar_bar = GetScalarBar(velocity_lut, view)
    scalar_bar.Title = "Velocity magnitude"
    scalar_bar.ComponentTitle = "m/s"
    scalar_bar.TitleColor = [0.0, 0.0, 0.0]
    scalar_bar.LabelColor = [0.0, 0.0, 0.0]
    scalar_bar.WindowLocation = "Upper Right Corner"
    scalar_bar.ScalarBarLength = 0.35
    scalar_bar.TitleFontSize = 18
    scalar_bar.LabelFontSize = 16

    Hide(point_fields, view)
    Hide(velocity, view)
    Hide(section, view)

    # Anatomical frontal view: the camera is anterior (+Y in RAS) and looks
    # posteriorly. This displays the patient's right on the image left, as in
    # conventional frontal medical imaging.
    view.CameraPosition = [0.007, 0.32, 1.337]
    view.CameraFocalPoint = [0.007, 0.112, 1.337]
    view.CameraViewUp = [0.0, 0.0, 1.0]
    view.CameraParallelProjection = 1
    view.ResetCamera()
    view.CameraParallelScale *= 0.88

    Render(view)
    SaveScreenshot(
        str(args.output.resolve()),
        view,
        ImageResolution=[args.width, args.height],
        TransparentBackground=0,
        CompressionLevel=2,
    )
    print(f"Rendered final time: {final_time:g}")
    print(f"Velocity range: 0 to {args.velocity_max:g} m/s")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
