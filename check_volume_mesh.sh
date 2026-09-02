#!/usr/bin/env bash
# Validate an already converted OpenFOAM volume mesh and detect prism layers.
#
# Usage:
#   ./check_volume_mesh.sh [case] [--require-layers]
#
# Examples:
#   ./check_volume_mesh.sh postop
#   ./check_volume_mesh.sh postop --require-layers
#
# The script does not convert the Gmsh mesh or run the solver. Run run_cfd.sh
# once (or gmshToFoam manually) so constant/polyMesh exists. The complete report
# is written to openFOAM/<case>/log.checkMesh.full.

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CASE_NAME="postop"
CASE_NAME_SET=false
REQUIRE_LAYERS=false

for argument in "$@"; do
    case "${argument}" in
        --require-layers)
            REQUIRE_LAYERS=true
            ;;
        --help|-h)
            echo "Usage: $0 [case] [--require-layers]"
            exit 0
            ;;
        --*)
            echo "Error: unknown option '${argument}'." >&2
            echo "Usage: $0 [case] [--require-layers]" >&2
            exit 1
            ;;
        *)
            if [[ "${CASE_NAME_SET}" == true ]]; then
                echo "Error: more than one case name was supplied." >&2
                exit 1
            fi
            CASE_NAME="${argument}"
            CASE_NAME_SET=true
            ;;
    esac
done

OPENFOAM_IMAGE="${OPENFOAM_IMAGE:-opencfd/openfoam-default:latest}"
OPENFOAM_DIR="${SCRIPT_DIR}/openFOAM"
CASE_DIR="${OPENFOAM_DIR}/${CASE_NAME}"
POLYMESH_DIR="${CASE_DIR}/constant/polyMesh"
LOG_FILE="${CASE_DIR}/log.checkMesh.full"

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker is not installed or not available on PATH." >&2
    exit 1
fi

if [[ ! -f "${CASE_DIR}/system/controlDict" ]]; then
    echo "Error: incomplete OpenFOAM case: ${CASE_DIR}" >&2
    exit 1
fi

for mesh_file in points faces owner neighbour boundary; do
    if [[ ! -s "${POLYMESH_DIR}/${mesh_file}" ]]; then
        echo "Error: converted OpenFOAM mesh file is missing: ${POLYMESH_DIR}/${mesh_file}" >&2
        echo "Run ./run_cfd.sh ${CASE_NAME} once to convert airways.msh, or convert it manually." >&2
        exit 1
    fi
done

echo "======================================"
echo "Checking OpenFOAM volume mesh"
echo "======================================"
echo "Image:          ${OPENFOAM_IMAGE}"
echo "Case:           ${CASE_NAME}"
echo "Mesh:           ${POLYMESH_DIR}"
echo "Require layers: ${REQUIRE_LAYERS}"
echo "Report:         ${LOG_FILE}"

set +e
docker run --rm \
    --user "$(id -u):$(id -g)" \
    --env HOME=/tmp \
    --volume "${OPENFOAM_DIR}:/cases" \
    --workdir "/cases/${CASE_NAME}" \
    "${OPENFOAM_IMAGE}" \
    bash -c "
        if ! command -v checkMesh >/dev/null 2>&1; then
            source /usr/lib/openfoam/openfoam2512/etc/bashrc
        fi
        cd '/cases/${CASE_NAME}'
        checkMesh -allTopology -allGeometry
    " 2>&1 | tee "${LOG_FILE}"
pipeline_status=("${PIPESTATUS[@]}")
check_status=${pipeline_status[0]}
tee_status=${pipeline_status[1]}
set -e

if [[ ${tee_status} -ne 0 ]]; then
    echo "Error: could not write ${LOG_FILE} (tee status ${tee_status})." >&2
    exit "${tee_status}"
fi
if [[ ${check_status} -ne 0 ]]; then
    echo "Error: checkMesh failed with status ${check_status}. See ${LOG_FILE}." >&2
    exit "${check_status}"
fi

for patch in inlet outlet_1 outlet_2 outlet_3 wall; do
    if ! grep -Eq "^[[:space:]]*${patch}[[:space:]]" "${LOG_FILE}"; then
        echo "Error: required boundary patch '${patch}' is absent from the checkMesh report." >&2
        exit 1
    fi
done

if ! grep -Eq "Number of regions:[[:space:]]+1" "${LOG_FILE}"; then
    echo "Error: mesh does not report exactly one connected region." >&2
    exit 1
fi

prism_count="$(awk '/^[[:space:]]*prisms:/ {print $2; exit}' "${LOG_FILE}")"
tetra_count="$(awk '/^[[:space:]]*tetrahedra:/ {print $2; exit}' "${LOG_FILE}")"
polyhedron_count="$(awk '/^[[:space:]]*polyhedra:/ {print $2; exit}' "${LOG_FILE}")"
prism_count="${prism_count:-0}"
tetra_count="${tetra_count:-0}"
polyhedron_count="${polyhedron_count:-0}"

severe_nonortho="$(sed -n 's/.*Number of severely non-orthogonal (> 70 degrees) faces: *\([0-9][0-9]*\).*/\1/p' "${LOG_FILE}" | tail -n 1)"
severe_nonortho="${severe_nonortho:-0}"
max_aspect="$(sed -n 's/.*Max aspect ratio = *\([^ ]*\).*/\1/p' "${LOG_FILE}" | tail -n 1)"
max_nonortho="$(sed -n 's/.*Mesh non-orthogonality Max: *\([^ ]*\).*/\1/p' "${LOG_FILE}" | tail -n 1)"
max_skewness="$(sed -n 's/.*Max skewness = *\([^ ]*\).*/\1/p' "${LOG_FILE}" | tail -n 1)"
min_volume="$(sed -n 's/.*Min volume = *\([^ ]*\).*/\1/p' "${LOG_FILE}" | tail -n 1)"

echo ""
echo "======================================"
echo "MESH CHECK SUMMARY"
echo "======================================"
echo "Tetrahedra:                    ${tetra_count}"
echo "Prisms:                        ${prism_count}"
echo "Polyhedra:                     ${polyhedron_count}"
echo "Maximum aspect ratio:          ${max_aspect:-not parsed}"
echo "Maximum non-orthogonality:     ${max_nonortho:-not parsed}"
echo "Faces above 70 degrees:        ${severe_nonortho}"
echo "Maximum skewness:              ${max_skewness:-not parsed}"
echo "Minimum cell volume:           ${min_volume:-not parsed}"

if [[ "${prism_count}" -gt 0 ]]; then
    echo "Boundary-layer indicator:      prism cells are present"
    echo ""
    echo "Important: prism presence alone does not prove good layers. Inspect the"
    echo "wall-normal layers in ParaView, especially at the stenosis, carina, and"
    echo "small branches, for collapse, intersections, and abrupt termination."
else
    echo "Boundary-layer indicator:      NO prism cells detected"
    if [[ "${REQUIRE_LAYERS}" == true ]]; then
        echo "Error: --require-layers was specified, but checkMesh reported zero prisms." >&2
        exit 2
    fi
fi

if [[ "${severe_nonortho}" -gt 0 ]]; then
    echo "Warning: ${severe_nonortho} faces exceed 70 degrees non-orthogonality." >&2
fi

echo "Required patches:              present"
echo "Connected fluid regions:       1"
echo "checkMesh result:              passed"
echo "Full report:                   ${LOG_FILE}"
