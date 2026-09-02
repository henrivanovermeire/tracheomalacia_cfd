#!/usr/bin/env bash
# Create the Gmsh airway volume mesh without running OpenFOAM.
#
# Usage:
#   ./create_volume_mesh.sh [case]
#
# Examples:
#   ./create_volume_mesh.sh postop
#   MESH_SIZE=0.2 ./create_volume_mesh.sh postop

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CASE_NAME="${1:-postop}"
MESH_SIZE="${MESH_SIZE:-0.25}"

GEO_FILE="${SCRIPT_DIR}/meshes/airways.geo"
STL_FILE="${SCRIPT_DIR}/meshes/airways.stl"
CASE_DIR="${SCRIPT_DIR}/openFOAM/${CASE_NAME}"
MESH_FILE="${CASE_DIR}/airways.msh"

if [[ $# -gt 1 ]]; then
    echo "Usage: $0 [case]" >&2
    exit 1
fi

if ! command -v gmsh >/dev/null 2>&1; then
    echo "Error: gmsh is not installed or not available on PATH." >&2
    exit 1
fi

if [[ ! -f "${GEO_FILE}" ]]; then
    echo "Error: Gmsh geometry file not found: ${GEO_FILE}" >&2
    exit 1
fi

if [[ ! -f "${STL_FILE}" ]]; then
    echo "Error: airway STL not found: ${STL_FILE}" >&2
    echo "Run segmentation/scripts/export_segmentation.py in Slicer first." >&2
    exit 1
fi

if [[ ! -d "${CASE_DIR}" ]]; then
    echo "Error: OpenFOAM case directory not found: ${CASE_DIR}" >&2
    exit 1
fi

if ! [[ "${MESH_SIZE}" =~ ^([0-9]+([.][0-9]*)?|[.][0-9]+)$ ]] || [[ "${MESH_SIZE}" =~ ^0+([.]0*)?$ ]]; then
    echo "Error: MESH_SIZE must be a positive number in millimetres (received '${MESH_SIZE}')." >&2
    exit 1
fi

echo "======================================"
echo "Generating Gmsh volume mesh"
echo "======================================"
echo "Case:      ${CASE_NAME}"
echo "Geometry:  ${GEO_FILE}"
echo "STL:       ${STL_FILE}"
echo "Mesh size: ${MESH_SIZE} mm"
echo "Output:    ${MESH_FILE}"

# MSH 2.2 provides broad gmshToFoam compatibility. The relative Merge path in
# airways.geo is resolved from the geometry file's directory.
gmsh "${GEO_FILE}" \
    -3 \
    -format msh2 \
    -setnumber lc "${MESH_SIZE}" \
    -o "${MESH_FILE}"

if [[ ! -s "${MESH_FILE}" ]]; then
    echo "Error: Gmsh did not produce a non-empty mesh: ${MESH_FILE}" >&2
    exit 1
fi

echo ""
echo "======================================"
echo "VOLUME MESH CREATION COMPLETE"
echo "======================================"
echo "Mesh: ${MESH_FILE}"
mesh