#!/usr/bin/env bash
# Build a denser postoperative mesh locally, run it on a remote host, and
# fetch the reconstructed OpenFOAM results for local ParaView inspection.
#
# Usage:
#   ./run_fine_cfd.sh <ssh-host> [--visualize]
#
# Examples:
#   ./run_fine_cfd.sh 159.203.184.188
#   ./run_fine_cfd.sh root@159.203.184.188 --visualize
#   MESH_SIZE=0.12 NPROCS=60 ./run_fine_cfd.sh 159.203.184.188
#
# Configuration through environment variables:
#   BASE_CASE    Source OpenFOAM configuration (default: postop)
#   FINE_CASE    Fine-mesh case name (default: postop_fine)
#   MESH_SIZE    Gmsh element size in mm (default: 0.15)
#   NPROCS       MPI rank/decomposition count (default: 60)
#   REMOTE_USER  SSH user for a bare hostname/IP (default: root)
#   REMOTE_REPO  Repository path on the remote host
#                (default: /root/tracheomalacia_cfd)

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_TARGET=""
VISUALIZE=false

for argument in "$@"; do
    case "${argument}" in
        --visualize)
            VISUALIZE=true
            ;;
        --help|-h)
            echo "Usage: $0 <ssh-host> [--visualize]"
            exit 0
            ;;
        --*)
            echo "Error: unknown option '${argument}'." >&2
            exit 1
            ;;
        *)
            if [[ -n "${REMOTE_TARGET}" ]]; then
                echo "Error: more than one SSH host was supplied." >&2
                exit 1
            fi
            REMOTE_TARGET="${argument}"
            ;;
    esac
done

if [[ -z "${REMOTE_TARGET}" ]]; then
    echo "Usage: $0 <ssh-host> [--visualize]" >&2
    echo "Example: $0 159.203.184.188" >&2
    exit 1
fi

BASE_CASE="${BASE_CASE:-postop}"
FINE_CASE="${FINE_CASE:-postop_fine}"
MESH_SIZE="${MESH_SIZE:-0.15}"
NPROCS="${NPROCS:-60}"
REMOTE_USER="${REMOTE_USER:-root}"
REMOTE_REPO="${REMOTE_REPO:-/root/tracheomalacia_cfd}"

if [[ "${REMOTE_TARGET}" == *@* ]]; then
    REMOTE_HOST="${REMOTE_TARGET}"
else
    REMOTE_HOST="${REMOTE_USER}@${REMOTE_TARGET}"
fi

BASE_CASE_DIR="${SCRIPT_DIR}/openFOAM/${BASE_CASE}"
FINE_CASE_DIR="${SCRIPT_DIR}/openFOAM/${FINE_CASE}"
REMOTE_CASE_DIR="${REMOTE_REPO}/openFOAM/${FINE_CASE}"

for command_name in ssh rsync sed; do
    if ! command -v "${command_name}" >/dev/null 2>&1; then
        echo "Error: ${command_name} is not installed or not available on PATH." >&2
        exit 1
    fi
done

if [[ ! -d "${BASE_CASE_DIR}/0" || ! -d "${BASE_CASE_DIR}/constant" || ! -d "${BASE_CASE_DIR}/system" ]]; then
    echo "Error: incomplete baseline case: ${BASE_CASE_DIR}" >&2
    exit 1
fi

if ! [[ "${NPROCS}" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: NPROCS must be a positive integer (received '${NPROCS}')." >&2
    exit 1
fi

echo "======================================"
echo "Preparing fine-mesh case"
echo "======================================"
echo "Baseline:    ${BASE_CASE}"
echo "Fine case:   ${FINE_CASE}"
echo "Mesh size:   ${MESH_SIZE} mm"
echo "MPI ranks:   ${NPROCS}"
echo "Remote host: ${REMOTE_HOST}"

# The fine case is a generated workspace. Recreate it from the baseline case's
# initial conditions and dictionaries, without copying any old solution or mesh.
rm -rf -- "${FINE_CASE_DIR}"
mkdir -p "${FINE_CASE_DIR}"
cp -a "${BASE_CASE_DIR}/0" "${FINE_CASE_DIR}/0"
cp -a "${BASE_CASE_DIR}/constant" "${FINE_CASE_DIR}/constant"
cp -a "${BASE_CASE_DIR}/system" "${FINE_CASE_DIR}/system"
rm -rf -- "${FINE_CASE_DIR}/constant/polyMesh"

# decomposePar requires this value to equal the mpirun process count.
sed -E -i \
    "s/^[[:space:]]*numberOfSubdomains[[:space:]]+[0-9]+[[:space:]]*;/numberOfSubdomains ${NPROCS};/" \
    "${FINE_CASE_DIR}/system/decomposeParDict"

if ! grep -Eq "^[[:space:]]*numberOfSubdomains[[:space:]]+${NPROCS}[[:space:]]*;" \
    "${FINE_CASE_DIR}/system/decomposeParDict"; then
    echo "Error: failed to set numberOfSubdomains to ${NPROCS}." >&2
    exit 1
fi

echo ""
echo "--- Creating ${MESH_SIZE} mm volume mesh locally"
MESH_SOURCE_CASE="${BASE_CASE}" MESH_SIZE="${MESH_SIZE}" \
    "${SCRIPT_DIR}/create_volume_mesh.sh" "${FINE_CASE}"

echo ""
echo "======================================"
echo "Transferring fine case to remote host"
echo "======================================"

# Ensure that the remote uses the same runner as this local checkout.
rsync -ah "${SCRIPT_DIR}/run_cfd.sh" "${REMOTE_HOST}:${REMOTE_REPO}/run_cfd.sh"
ssh "${REMOTE_HOST}" "chmod +x '${REMOTE_REPO}/run_cfd.sh'"

# Replacing the dedicated fine case is intentional. It prevents stale fields or
# processor directories from an earlier mesh from contaminating this run.
ssh "${REMOTE_HOST}" \
    "rm -rf '${REMOTE_CASE_DIR}' && mkdir -p '${REMOTE_CASE_DIR}'"
rsync -ah --delete --info=progress2 \
    "${FINE_CASE_DIR}/" \
    "${REMOTE_HOST}:${REMOTE_CASE_DIR}/"

echo ""
echo "======================================"
echo "Running fine CFD case remotely"
echo "======================================"
ssh "${REMOTE_HOST}" \
    "cd '${REMOTE_REPO}' && NPROCS='${NPROCS}' ./run_cfd.sh '${FINE_CASE}'"

echo ""
echo "======================================"
echo "Fetching reconstructed fine results"
echo "======================================"
REMOTE_REPO="${REMOTE_REPO}" \
    "${SCRIPT_DIR}/fetch_cfd_results.sh" "${REMOTE_HOST}" "${FINE_CASE}"

FOAM_MARKER="${SCRIPT_DIR}/results/${FINE_CASE}/${FINE_CASE}.foam"

if [[ "${VISUALIZE}" == true ]]; then
    if ! command -v paraview >/dev/null 2>&1; then
        echo "Error: --visualize was requested, but paraview is not available on PATH." >&2
        exit 1
    fi
    echo "Opening fine-mesh result in ParaView: ${FOAM_MARKER}"
    paraview "${FOAM_MARKER}" >/dev/null 2>&1 &
fi

echo ""
echo "======================================"
echo "FINE-MESH CFD WORKFLOW COMPLETE"
echo "======================================"
echo "Results: ${FOAM_MARKER}"
