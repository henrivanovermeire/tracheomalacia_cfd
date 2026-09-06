#!/usr/bin/env pvpython
"""Extract transient pressure, flow, and resistance on two fixed airway planes.

Example:

    pvpython assignment/scripts/extract_transient_metrics.py \
        results/postop_transient_coarse_poc/postop_transient_coarse_poc.foam

The case must be reconstructed so that the OpenFOAM reader exposes all saved
solution times. Time zero is intentionally omitted.
"""

import argparse
import csv
import json
import math
from pathlib import Path

from paraview import servermanager
from paraview.simple import IntegrateVariables, OpenFOAMReader, Slice


CSV_FIELDS = [
    "time_s",
    "waveform_phase",
    "superior_area_m2",
    "superior_kinematic_pressure_m2_s2",
    "superior_pressure_pa",
    "superior_flow_m3_s",
    "inferior_area_m2",
    "inferior_kinematic_pressure_m2_s2",
    "inferior_pressure_pa",
    "inferior_flow_m3_s",
    "pressure_drop_pa",
    "mean_section_flow_m3_s",
    "resistance_pa_s_m3",
    "resistance_pa_per_l_min",
    "resistance_masked",
]


def leaf_datasets(dataset):
    """Yield non-composite VTK datasets from a fetched ParaView result."""
    if hasattr(dataset, "GetNumberOfBlocks"):
        for index in range(dataset.GetNumberOfBlocks()):
            block = dataset.GetBlock(index)
            if block is not None:
                yield from leaf_datasets(block)
    else:
        yield dataset


def array_from_dataset(dataset, name):
    leaves = list(leaf_datasets(dataset))
    for leaf in leaves:
        for attributes in (
            leaf.GetPointData(),
            leaf.GetCellData(),
            leaf.GetFieldData(),
        ):
            array = attributes.GetArray(name)
            if array is not None:
                return array
    available = []
    for leaf in leaves:
        for attributes in (leaf.GetPointData(), leaf.GetCellData(), leaf.GetFieldData()):
            available.extend(
                attributes.GetArrayName(index)
                for index in range(attributes.GetNumberOfArrays())
            )
    raise RuntimeError("Array {!r} not found; available arrays: {}".format(name, available))


def scalar_value(array):
    if array.GetNumberOfTuples() < 1:
        raise RuntimeError("Array {!r} contains no values.".format(array.GetName()))
    return float(array.GetComponent(0, 0))


def vector_value(array):
    if array.GetNumberOfTuples() < 1 or array.GetNumberOfComponents() < 3:
        raise RuntimeError("Array {!r} is not a 3-vector.".format(array.GetName()))
    return [float(array.GetComponent(0, axis)) for axis in range(3)]


def dot(first, second):
    return sum(first[index] * second[index] for index in range(3))


def normalize(vector):
    magnitude = math.sqrt(dot(vector, vector))
    if magnitude <= 1.0e-12:
        raise ValueError("Plane normal cannot have zero magnitude.")
    return [component / magnitude for component in vector]


def waveform_phase(time_value):
    """Return the prescribed phase for the single 0--2 s breathing cycle."""
    if time_value < 0.0 or time_value > 2.0:
        return "outside defined waveform"
    if time_value < 0.5:
        return "accelerating inspiration"
    if time_value < 1.0:
        return "decelerating inspiration"
    if time_value < 1.5:
        return "accelerating expiration"
    return "decelerating expiration"


def make_plane_pipeline(reader, name, definition):
    normal = normalize(definition["normal"])
    section = Slice(registrationName="transient_section_{}".format(name), Input=reader)
    section.SliceType = "Plane"
    section.SliceType.Origin = definition["origin"]
    section.SliceType.Normal = normal
    integrated = IntegrateVariables(
        registrationName="transient_integrated_{}".format(name), Input=section
    )
    return {"normal": normal, "slice": section, "integrated": integrated}


def measure_plane(pipeline, time_value):
    pipeline["slice"].UpdatePipeline(time_value)
    pipeline["integrated"].UpdatePipeline(time_value)
    data = servermanager.Fetch(pipeline["integrated"])
    area = scalar_value(array_from_dataset(data, "Area"))
    if area <= 0.0:
        raise RuntimeError("Slice has non-positive area at time {}.".format(time_value))
    pressure_integral = scalar_value(array_from_dataset(data, "p"))
    velocity_integral = vector_value(array_from_dataset(data, "U"))
    return {
        "area_m2": area,
        "kinematic_pressure_m2_s2": pressure_integral / area,
        "flow_m3_s": dot(velocity_integral, pipeline["normal"]),
    }


def extrema(rows, field, include_masked=True):
    values = [
        row[field]
        for row in rows
        if row[field] is not None
        and (include_masked or not row["resistance_masked"])
    ]
    return {"min": min(values), "max": max(values)} if values else {"min": None, "max": None}


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            if csv_row["resistance_pa_s_m3"] is None:
                csv_row["resistance_pa_s_m3"] = ""
                csv_row["resistance_pa_per_l_min"] = ""
            writer.writerow(csv_row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("foam_case", type=Path, help="Reconstructed OpenFOAM .foam case")
    parser.add_argument(
        "--sections",
        type=Path,
        default=Path("assignment/data/resistance_sections.json"),
        help="Fixed centerline-normal plane definitions",
    )
    parser.add_argument("--density", type=float, default=1.204, help="Air density in kg/m^3")
    parser.add_argument(
        "--flow-threshold-fraction",
        type=float,
        default=0.05,
        help="Mask resistance below this fraction of peak absolute mean flow",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("assignment/data"))
    parser.add_argument(
        "--label", default="postop_transient_coarse_poc", help="Output filename/case label"
    )
    args = parser.parse_args()

    if args.density <= 0.0:
        parser.error("--density must be positive")
    if not 0.0 <= args.flow_threshold_fraction <= 1.0:
        parser.error("--flow-threshold-fraction must be between 0 and 1")
    if args.foam_case.suffix != ".foam" or not args.foam_case.is_file():
        parser.error("foam_case must be an existing .foam file")

    with args.sections.open() as source:
        definitions = json.load(source)["planes"]

    reader = OpenFOAMReader(
        registrationName=args.label, FileName=str(args.foam_case.resolve())
    )
    reader.UpdatePipelineInformation()
    if hasattr(reader, "MeshRegions"):
        reader.MeshRegions = ["internalMesh"]
    if hasattr(reader, "CellArrays"):
        reader.CellArrays = ["U", "p"]

    time_values = sorted(
        {float(value) for value in (reader.TimestepValues or []) if float(value) > 0.0}
    )
    if not time_values:
        raise RuntimeError("The case exposes no nonzero saved times; is it reconstructed?")

    pipelines = {
        name: make_plane_pipeline(reader, name, definitions[name])
        for name in ("superior", "inferior")
    }
    rows = []
    for time_value in time_values:
        reader.UpdatePipeline(time_value)
        superior = measure_plane(pipelines["superior"], time_value)
        inferior = measure_plane(pipelines["inferior"], time_value)
        pressure_drop_pa = args.density * (
            superior["kinematic_pressure_m2_s2"]
            - inferior["kinematic_pressure_m2_s2"]
        )
        mean_flow = 0.5 * (superior["flow_m3_s"] + inferior["flow_m3_s"])
        rows.append(
            {
                "time_s": time_value,
                "waveform_phase": waveform_phase(time_value),
                "superior_area_m2": superior["area_m2"],
                "superior_kinematic_pressure_m2_s2": superior["kinematic_pressure_m2_s2"],
                "superior_pressure_pa": args.density * superior["kinematic_pressure_m2_s2"],
                "superior_flow_m3_s": superior["flow_m3_s"],
                "inferior_area_m2": inferior["area_m2"],
                "inferior_kinematic_pressure_m2_s2": inferior["kinematic_pressure_m2_s2"],
                "inferior_pressure_pa": args.density * inferior["kinematic_pressure_m2_s2"],
                "inferior_flow_m3_s": inferior["flow_m3_s"],
                "pressure_drop_pa": pressure_drop_pa,
                "mean_section_flow_m3_s": mean_flow,
                "resistance_pa_s_m3": None,
                "resistance_pa_per_l_min": None,
                "resistance_masked": False,
            }
        )

    peak_absolute_flow = max(abs(row["mean_section_flow_m3_s"]) for row in rows)
    mask_threshold = args.flow_threshold_fraction * peak_absolute_flow
    for row in rows:
        flow = row["mean_section_flow_m3_s"]
        row["resistance_masked"] = abs(flow) < mask_threshold or flow == 0.0
        if not row["resistance_masked"]:
            resistance = row["pressure_drop_pa"] / flow
            row["resistance_pa_s_m3"] = resistance
            row["resistance_pa_per_l_min"] = resistance / 60000.0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "{}_metrics.csv".format(args.label)
    json_path = args.output_dir / "{}_metrics.json".format(args.label)
    write_csv(rows, csv_path)

    summary = {
        "schema_version": 1,
        "case": args.label,
        "foam_case": str(args.foam_case),
        "sections_source": str(args.sections),
        "air_density_kg_m3": args.density,
        "saved_nonzero_time_count": len(rows),
        "time_range_s": [rows[0]["time_s"], rows[-1]["time_s"]],
        "peak_absolute_mean_section_flow_m3_s": peak_absolute_flow,
        "resistance_mask": {
            "flow_threshold_fraction": args.flow_threshold_fraction,
            "absolute_flow_threshold_m3_s": mask_threshold,
            "masked_row_count": sum(row["resistance_masked"] for row in rows),
        },
        "extrema": {
            "pressure_drop_pa": extrema(rows, "pressure_drop_pa"),
            "mean_section_flow_m3_s": extrema(rows, "mean_section_flow_m3_s"),
            "resistance_pa_s_m3": extrema(rows, "resistance_pa_s_m3", False),
            "resistance_pa_per_l_min": extrema(rows, "resistance_pa_per_l_min", False),
        },
    }
    with json_path.open("w") as output:
        json.dump(summary, output, separators=(",", ":"))
        output.write("\n")

    print("Processed {} nonzero saved times.".format(len(rows)))
    print("Resistance flow mask: |Q| < {:.8g} m3/s".format(mask_threshold))
    print("CSV: {}".format(csv_path))
    print("JSON: {}".format(json_path))


if __name__ == "__main__":
    main()
