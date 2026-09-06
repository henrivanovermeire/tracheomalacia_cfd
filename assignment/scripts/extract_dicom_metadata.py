#!/usr/bin/env python3
"""Extract non-identifying geometry/acquisition metadata from local DICOM series."""

import argparse
import json
import struct
from pathlib import Path

LONG_VR = {b"OB", b"OD", b"OF", b"OL", b"OV", b"OW", b"SQ", b"SV", b"UC", b"UR", b"UT", b"UV", b"UN"}
TAGS = {
    (0x0008, 0x103E): "series_description",
    (0x0018, 0x0015): "body_part_examined",

    (0x0018, 0x0050): "slice_thickness_mm",
    (0x0018, 0x1030): "protocol_name",
    (0x0020, 0x0032): "image_position_patient_mm",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0030): "pixel_spacing_mm",
}


def decode(vr, raw):
    if vr == b"US" and len(raw) >= 2:
        return struct.unpack("<H", raw[:2])[0]
    if vr == b"SS" and len(raw) >= 2:
        return struct.unpack("<h", raw[:2])[0]
    text = raw.rstrip(b"\0 ").decode("utf-8", errors="replace")
    if vr in {b"DS", b"IS"}:
        values = [item for item in text.split("\\") if item]
        parsed = [float(item) for item in values]
        return parsed[0] if len(parsed) == 1 else parsed
    return text


def read_explicit_vr_little_endian(path):
    data = path.read_bytes()
    if len(data) < 132 or data[128:132] != b"DICM":
        raise ValueError(f"Not a Part-10 DICOM file: {path}")
    found = {}
    # Locate the required standard tags directly. This supports both explicit-
    # and implicit-VR little-endian datasets and avoids parsing unrelated
    # undefined-length private sequences.
    for tag, name in TAGS.items():
        marker = struct.pack("<HH", *tag)
        offset = data.find(marker, 132)
        if offset < 0 or offset + 8 > len(data):
            continue
        candidate_vr = data[offset + 4:offset + 6]
        if candidate_vr.isalpha() and len(candidate_vr) == 2:
            vr = candidate_vr
            if vr in LONG_VR:
                length = struct.unpack_from("<I", data, offset + 8)[0]
                value_offset = offset + 12
            else:
                length = struct.unpack_from("<H", data, offset + 6)[0]
                value_offset = offset + 8
        else:
            length = struct.unpack_from("<I", data, offset + 4)[0]
            value_offset = offset + 8
            vr = b"US" if tag in {(0x0028, 0x0010), (0x0028, 0x0011)} else b"DS" if tag in {(0x0018, 0x0050), (0x0020, 0x0032), (0x0028, 0x0030)} else b"LO"
        if length != 0xFFFFFFFF and value_offset + length <= len(data):
            found[name] = decode(vr, data[value_offset:value_offset + length])
    return found


def summarize(folder):
    files = sorted(folder.glob("*.dcm"))
    if not files:
        raise FileNotFoundError(f"No DICOM files in {folder}")
    first = read_explicit_vr_little_endian(files[0])
    positions = []
    for path in files:
        metadata = read_explicit_vr_little_endian(path)
        position = metadata.get("image_position_patient_mm")
        if isinstance(position, list) and len(position) == 3:
            positions.append(position)
    slice_spacing = None
    if len(positions) > 1:
        coordinates = sorted(position[2] for position in positions)
        differences = [abs(b - a) for a, b in zip(coordinates, coordinates[1:]) if abs(b - a) > 1e-9]
        if differences:
            slice_spacing = sum(differences) / len(differences)
    return {
        "file_count": len(files),
        "voxel_dimensions": [first.get("columns"), first.get("rows"), len(files)],
        "pixel_spacing_mm": first.get("pixel_spacing_mm"),
        "mean_slice_spacing_mm_from_positions": slice_spacing,
        "slice_thickness_mm": first.get("slice_thickness_mm"),
        "series_description": first.get("series_description", "not recorded"),
        "protocol_name": first.get("protocol_name", "not recorded"),

        "body_part_examined": first.get("body_part_examined", "not recorded"),
        "respiratory_phase": "not explicitly recorded in inspected standard tags",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("segmentation/source"))
    parser.add_argument("--output", type=Path, default=Path("assignment/data/dicom_geometry.json"))
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "privacy": "Only non-identifying geometry and acquisition descriptors are retained.",
        "preop": summarize(args.source / "DICOM_preop"),
        "postop": summarize(args.source / "DICOM_postop"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print(args.output)


if __name__ == "__main__":
    main()
