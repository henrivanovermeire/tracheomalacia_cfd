#!/usr/bin/env pvpython
"""Extract fixed-plane and outlet metrics from a reconstructed OpenFOAM case.

Run with ParaView's Python interpreter, for example:

    pvpython assignment/scripts/extract_cfd_metrics.py \
        results/postop_assignment4/postop_assignment4.foam

The fixed planes are defined in assignment/data/resistance_sections.json and are
reused unchanged for mesh-sensitivity and transient comparisons.
"""

import argparse
import csv
import json
import math
from pathlib import Path

from paraview import servermanager
from paraview.simple import Calculator, IntegrateVariables, OpenFOAMReader, Slice


def leaf_datasets(dataset):
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
            leaf.GetPointData(), leaf.GetCellData(), leaf.GetFieldData()
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
    raise RuntimeError(f"Array '{name}' not found; available arrays: {available}")


def scalar_value(array):
    if array.GetNumberOfTuples() < 1:
        raise RuntimeError(f"Array '{array.GetName()}' contains no values.")
    return float(array.GetComponent(0, 0))


def vector_value(array):
    if array.GetNumberOfTuples() < 1 or array.GetNumberOfComponents() < 3:
        raise RuntimeError(f"Array '{array.GetName()}' is not a 3-vector.")
    return [float(array.GetComponent(0, axis)) for axis in range(3)]


def dot(first, second):
    return sum(first[index] * second[index] for index in range(3))


def normalize(vector):
    magnitude = math.sqrt(dot(vector, vector))
    if magnitude <= 1e-12:
        raise ValueError("Plane normal cannot have zero magnitude.")
    return [component / magnitude for component in vector]


def data_range(dataset, name):
    ranges = []
    for leaf in leaf_datasets(dataset):
        for attributes in (leaf.GetPointData(), leaf.GetCellData()):
            array = attributes.GetArray(name)
            if array is not None and array.GetNumberOfTuples() > 0:
                ranges.append(array.GetRange(0))
    if not ranges:
        raise RuntimeError(f"No '{name}' values were found on the sliced section.")
    return min(value[0] for value in ranges), max(value[1] for value in ranges)



def measure_plane(reader, time_value, name, definition):
    normal = normalize(definition["normal"])
    section = Slice(registrationName=f"section_{name}", Input=reader)
    section.SliceType = "Plane"
    section.SliceType.Origin = definition["origin"]
    section.SliceType.Normal = normal
    section.UpdatePipeline(time_value)

    integrated = IntegrateVariables(registrationName=f"integrated_{name}", Input=section)
    integrated.UpdatePipeline(time_value)
    integrated_data = servermanager.Fetch(integrated)

    area = scalar_value(array_from_dataset(integrated_data, "Area"))
    pressure_integral = scalar_value(array_from_dataset(integrated_data, "p"))
    velocity_integral = vector_value(array_from_dataset(integrated_data, "U"))
    flow_rate = dot(velocity_integral, normal)

    magnitude = Calculator(registrationName=f"velocity_magnitude_{name}", Input=section)
    magnitude.ResultArrayName = "VelocityMagnitude"
    magnitude.Function = "mag(U)"
    magnitude.UpdatePipeline(time_value)
    magnitude_data = servermanager.Fetch(magnitude)
    _, peak_velocity = data_range(magnitude_data, "VelocityMagnitude")

    return {
        "name": name,
        "role": definition.get("role", ""),
        "origin_m": definition["origin"],
        "normal": normal,
        "area_m2": area,
        "area_average_kinematic_pressure_m2_s2": pressure_integral / area,
        "flow_rate_m3_s": flow_rate,
        "area_average_axial_velocity_m_s": flow_rate / area,
        "peak_velocity_magnitude_m_s": peak_velocity,
    }


def write_plane_csv(measurements, path):
    fields = [
        "name", "role", "area_m2", "area_average_kinematic_pressure_m2_s2",
        "flow_rate_m3_s", "area_average_axial_velocity_m_s",
        "peak_velocity_magnitude_m_s",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for measurement in measurements:
            writer.writerow({field: measurement[field] for field in fields})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("foam_case", type=Path)
    parser.add_argument(
        "--sections",
        type=Path,
        default=Path("assignment/data/resistance_sections.json"),
    )
    parser.add_argument("--density", type=float, default=1.204,
                        help="Air density in kg/m^3 (default: 1.204)")
    parser.add_argument("--output-dir", type=Path, default=Path("assignment/data"))
    parser.add_argument("--label", default=None,
                        help="Output label; defaults to the .foam stem")
    args = parser.parse_args()

    with args.sections.open() as source:
        section_definitions = json.load(source)
    label = args.label or args.foam_case.stem

    reader = OpenFOAMReader(registrationName=label, FileName=str(args.foam_case.resolve()))
    reader.UpdatePipelineInformation()
    if hasattr(reader, "MeshRegions"):
        reader.MeshRegions = ["internalMesh"]
    if hasattr(reader, "CellArrays"):
        reader.CellArrays = ["U", "p"]
    time_values = list(reader.TimestepValues) if reader.TimestepValues else [0.0]
    time_value = max(time_values)
    reader.UpdatePipeline(time_value)

    planes = []
    for name in ("superior", "matched", "inferior"):
        planes.append(
            measure_plane(reader, time_value, name, section_definitions["planes"][name])
        )

    by_name = {measurement["name"]: measurement for measurement in planes}
    pressure_drop_kinematic = (
        by_name["superior"]["area_average_kinematic_pressure_m2_s2"]
        - by_name["inferior"]["area_average_kinematic_pressure_m2_s2"]
    )
    pressure_drop_pa = args.density * pressure_drop_kinematic
    section_flow = 0.5 * (
        by_name["superior"]["flow_rate_m3_s"]
        + by_name["inferior"]["flow_rate_m3_s"]
    )
    resistance = pressure_drop_pa / section_flow
    resistance_pa_per_l_min = resistance / 60000.0

    result = {
        "schema_version": 1,
        "case": label,
        "foam_case": str(args.foam_case),
        "time": time_value,
        "air_density_kg_m3": args.density,
        "pressure_definition": "OpenFOAM kinematic pressure; dimensional pressure=rho*p",
        "sections_source": str(args.sections),
        "planes": {measurement["name"]: measurement for measurement in planes},
        "region_metrics": {
            "kinematic_pressure_drop_m2_s2": pressure_drop_kinematic,
            "pressure_drop_pa": pressure_drop_pa,
            "mean_section_flow_rate_m3_s": section_flow,
            "local_resistance_pa_s_m3": resistance,
            "local_resistance_pa_per_l_min": resistance_pa_per_l_min,
        },
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"{label}_cfd_metrics.json"
    csv_path = args.output_dir / f"{label}_sections.csv"
    with json_path.open("w") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    write_plane_csv(planes, csv_path)

    print(f"Case: {label}; time: {time_value:g}")
    for measurement in planes:
        print(
            f"{measurement['name']}: area={measurement['area_m2']:.8g} m2, "
            f"p={measurement['area_average_kinematic_pressure_m2_s2']:.8g} m2/s2, "
            f"Q={measurement['flow_rate_m3_s']:.8g} m3/s, "
            f"Uax={measurement['area_average_axial_velocity_m_s']:.8g} m/s, "
            f"Umax={measurement['peak_velocity_magnitude_m_s']:.8g} m/s"
        )
    print(f"Pressure drop: {pressure_drop_pa:.8g} Pa")
    print(f"Resistance: {resistance:.8g} Pa s/m3")
    print(f"Resistance: {resistance_pa_per_l_min:.8g} Pa/(L/min)")
    print(f"JSON: {json_path}")
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    main()
