#!/usr/bin/env bash
# Fetch reconstructed OpenFOAM results from a remote CFD host.
#
# Usage:
#   ./fetch_cfd_results.sh <ssh-host> [case]
#
# Examples:
#   ./fetch_cfd_results.sh root@203.0.113.10 postop
#   REMOTE_REPO=/opt/tracheomalacia_cfd ./fetch_cfd_results.sh cfd-host postop
#
# The remote repository defaults to /root/tracheomalacia_cfd. Override it with
# REMOTE_REPO when the repository is stored elsewhere.

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_TARGET="${1:-}"
CASE_NAME="${2:-postop}"
REMOTE_USER="${REMOTE_USER:-root}"
REMOTE_REPO="${REMOTE_REPO:-/root/tracheomalacia_cfd}"

# A bare IP address or hostname uses root by default. An explicitly supplied
# user (for example, ubuntu@host) always takes precedence.
if [[ "${REMOTE_TARGET}" == *@* ]]; then
    REMOTE_HOST="${REMOTE_TARGET}"
else
    REMOTE_HOST="${REMOTE_USER}@${REMOTE_TARGET}"
fi
LOCAL_RESULTS_ROOT="${RESULTS_DIR:-${SCRIPT_DIR}/results}"
LOCAL_CASE_DIR="${LOCAL_RESULTS_ROOT}/${CASE_NAME}"
REMOTE_CASE_DIR="${REMOTE_REPO}/openFOAM/${CASE_NAME}"

if [[ -z "${REMOTE_TARGET}" || $# -gt 2 ]]; then
    echo "Usage: $0 <ssh-host> [case]" >&2
    echo "Example: $0 root@203.0.113.10 postop" >&2
    exit 1
fi

if ! command -v ssh >/dev/null 2>&1; then
    echo "Error: ssh is not installed or not available on PATH." >&2
    exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
    echo "Error: rsync is not installed or not available on PATH." >&2
    exit 1
fi

echo "======================================"
echo "Fetching reconstructed CFD results"
echo "======================================"
echo "Remote: ${REMOTE_HOST}:${REMOTE_CASE_DIR}"
echo "Local:  ${LOCAL_CASE_DIR}"

# Fail clearly before starting a potentially large transfer. A reconstructed
# case must contain the standard OpenFOAM case configuration on the remote host.
ssh "${REMOTE_HOST}" \
    "test -d '${REMOTE_CASE_DIR}/constant' && test -d '${REMOTE_CASE_DIR}/system'" || {
    echo "Error: remote OpenFOAM case was not found or is incomplete: ${REMOTE_CASE_DIR}" >&2
    exit 1
}

mkdir -p "${LOCAL_CASE_DIR}"

# Fetch the reconstructed case and mesh, but omit per-rank decomposition data.
# Those processor directories can be very large and are unnecessary in ParaView
# after reconstructPar has completed.
rsync -ah --delete --info=progress2 \
    --exclude='processor*/' \
    "${REMOTE_HOST}:${REMOTE_CASE_DIR}/" \
    "${LOCAL_CASE_DIR}/"

FOAM_MARKER="${LOCAL_CASE_DIR}/${CASE_NAME}.foam"
touch "${FOAM_MARKER}"

echo ""
echo "======================================"
echo "CFD RESULT FETCH COMPLETE"
echo "======================================"
echo "ParaView case: ${FOAM_MARKER}"
echo ""
echo "Open with:"
echo "  paraview '${FOAM_MARKER}'"
