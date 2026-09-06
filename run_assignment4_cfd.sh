#!/usr/bin/env bash
# Generate, remotely run, and fetch the Assignment 4 postoperative CFD case.
#
# Usage:
#   ./run_assignment4_cfd.sh <ssh-host> [--visualize]
#
# Example:
#   ./run_assignment4_cfd.sh root@159.203.184.188
#   NPROCS=60 ./run_assignment4_cfd.sh 159.203.184.188 --visualize
#
# Defaults:
#   source geometry/configuration: postop
#   generated case:              postop_assignment4
#   global tetrahedral size:      0.25 mm
#   inlet minute volume:          2 L/min (inherited from openFOAM/postop/0/U)

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BASE_CASE="${BASE_CASE:-postop}"
ASSIGNMENT4_CASE="${ASSIGNMENT4_CASE:-postop_assignment4}"
MESH_SIZE="${MESH_SIZE:-0.25}"
NPROCS="${NPROCS:-60}"
BASE_U="${SCRIPT_DIR}/openFOAM/${BASE_CASE}/0/U"

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Usage: $0 <ssh-host> [--visualize]" >&2
    exit 1
fi

if [[ ! -f "${BASE_U}" ]]; then
    echo "Error: baseline velocity dictionary not found: ${BASE_U}" >&2
    exit 1
fi

if ! grep -Eq 'volumetricFlowRate[[:space:]]+constant[[:space:]]+3[.]3333e-5[[:space:]]*;' "${BASE_U}"; then
    echo "Error: ${BASE_U} does not prescribe the expected 2 L/min inlet" >&2
    echo "       (volumetricFlowRate constant 3.3333e-5)." >&2
    exit 1
fi

echo "======================================"
echo "ASSIGNMENT 4 CFD WORKFLOW"
echo "======================================"
echo "Base case:       ${BASE_CASE}"
echo "Generated case:  ${ASSIGNMENT4_CASE}"
echo "Mesh size:       ${MESH_SIZE} mm"
echo "Inlet flow:      2 L/min"
echo "MPI ranks:       ${NPROCS}"
echo ""

BASE_CASE="${BASE_CASE}" \
FINE_CASE="${ASSIGNMENT4_CASE}" \
MESH_SIZE="${MESH_SIZE}" \
NPROCS="${NPROCS}" \
    "${SCRIPT_DIR}/run_fine_cfd.sh" "$@"
