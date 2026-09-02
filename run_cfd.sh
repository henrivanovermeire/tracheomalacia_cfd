#!/usr/bin/env bash
# Convert an existing Gmsh volume mesh and run the OpenFOAM simulation.
#
# Generate the input mesh first with create_volume_mesh.sh, locally or on
# another machine, then place it at openFOAM/<case>/airways.msh.
#
# Usage:
#   ./run_cfd.sh [case] [--visualize]
#
# Examples:
#   ./run_cfd.sh postop
#   NPROCS=60 ./run_cfd.sh postop
#   ./run_cfd.sh postop --visualize

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CASE_NAME="postop"
CASE_NAME_SET=false
VISUALIZE=false

for argument in "$@"; do
    case "${argument}" in
        --visualize)
            VISUALIZE=true
            ;;
        --help|-h)
            echo "Usage: $0 [case] [--visualize]"
            exit 0
            ;;
        --*)
            echo "Error: unknown option '${argument}'." >&2
            echo "Usage: $0 [case] [--visualize]" >&2
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
NPROCS="${NPROCS:-8}"
OPENFOAM_DIR="${SCRIPT_DIR}/openFOAM"
CASE_DIR="${OPENFOAM_DIR}/${CASE_NAME}"
MESH_FILE="${CASE_DIR}/airways.msh"

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker is not installed or not available on PATH." >&2
    exit 1
fi

if [[ ! -d "${CASE_DIR}/0" || ! -d "${CASE_DIR}/constant" || ! -d "${CASE_DIR}/system" ]]; then
    echo "Error: incomplete OpenFOAM case directory: ${CASE_DIR}" >&2
    echo "Expected 0/, constant/, and system/ directories." >&2
    exit 1
fi

if [[ ! -s "${MESH_FILE}" ]]; then
    echo "Error: volume mesh not found or empty: ${MESH_FILE}" >&2
    echo "Run ./create_volume_mesh.sh ${CASE_NAME} first or copy a verified airways.msh here." >&2
    exit 1
fi

if ! [[ "${NPROCS}" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: NPROCS must be a positive integer (received '${NPROCS}')." >&2
    exit 1
fi

echo "======================================"
echo "Running OpenFOAM case in Docker"
echo "======================================"
echo "Image:     ${OPENFOAM_IMAGE}"
echo "Case:      ${CASE_NAME}"
echo "Mesh:      ${MESH_FILE}"
echo "Processes: ${NPROCS}"

docker run --rm \
    --user "$(id -u):$(id -g)" \
    --env HOME=/tmp \
    --volume "${OPENFOAM_DIR}:/cases" \
    --workdir "/cases/${CASE_NAME}" \
    "${OPENFOAM_IMAGE}" \
    bash -c "
        if ! command -v simpleFoam >/dev/null 2>&1; then
            source /usr/lib/openfoam/openfoam2512/etc/bashrc
        fi
        set -Eeo pipefail

        # The image entrypoint may reset the current directory.
        cd '/cases/${CASE_NAME}'
        if [[ ! -f system/controlDict ]]; then
            echo 'Error: mounted case is missing system/controlDict.' >&2
            exit 1
        fi
        echo \"--- Working directory: \$(pwd)\"

        echo '--- Converting Gmsh mesh to OpenFOAM'
        gmshToFoam airways.msh

        echo '--- Scaling mesh from millimetres to metres'
        transformPoints -scale '(0.001 0.001 0.001)'

        echo '--- Verifying required boundary patches'
        for patch in inlet outlet_1 outlet_2 outlet_3 wall; do
            if ! grep -qw \"\${patch}\" constant/polyMesh/boundary; then
                echo \"Error: required patch '\${patch}' is missing after gmshToFoam.\" >&2
                echo 'Inspect the physical surfaces in the Gmsh mesh before running CFD.' >&2
                exit 1
            fi
        done

        echo '--- Checking mesh'
        checkMesh

        echo '--- Removing previous CFD results and domain decomposition'
        # Remove numeric result-time directories while preserving 0/, which
        # contains the initial and boundary conditions. This avoids mixing
        # fields generated with an older boundary-patch configuration into the
        # new reconstructed case.
        for time_dir in [0-9]*; do
            if [[ -d \"\${time_dir}\" && \"\${time_dir}\" != '0' && \"\${time_dir}\" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
                rm -rf -- \"\${time_dir}\"
            fi
        done
        rm -rf processor*

        echo '--- Decomposing case'
        decomposePar -force

        echo '--- Running simpleFoam in parallel'
        rm -f log.simpleFoam.parallel 2>/dev/null || true
        set +e
        mpirun --allow-run-as-root --use-hwthread-cpus -np ${NPROCS} simpleFoam -parallel 2>&1 | tee log.simpleFoam.parallel
        pipeline_status=(\"\${PIPESTATUS[@]}\")
        solver_status=\${pipeline_status[0]}
        tee_status=\${pipeline_status[1]}
        set -e
        echo \"--- simpleFoam exit status: \${solver_status}\"

        if [[ \${tee_status} -ne 0 ]]; then
            echo \"Warning: could not write solver log (tee status \${tee_status}); continuing.\" >&2
        fi

        if compgen -G 'processor*/[1-9]*' >/dev/null; then
            echo '--- Reconstructing retained results'
            reconstructPar
        else
            echo 'Error: no decomposed result times were produced.' >&2
            exit 1
        fi

        echo '--- Final mesh check'
        checkMesh

        if [[ \${solver_status} -ne 0 ]]; then
            echo \"Error: simpleFoam/mpirun exited with status \${solver_status}.\" >&2
            exit \${solver_status}
        fi
    "

echo ""
echo "======================================"
echo "CFD PIPELINE COMPLETE"
echo "======================================"
echo "Results: ${CASE_DIR}"

if [[ "${VISUALIZE}" == true ]]; then
    if ! command -v paraview >/dev/null 2>&1; then
        echo "Error: --visualize was requested, but paraview is not available on PATH." >&2
        exit 1
    fi

    FOAM_MARKER="${CASE_DIR}/${CASE_NAME}.foam"
    touch "${FOAM_MARKER}"
    echo "Opening reconstructed case in ParaView: ${FOAM_MARKER}"
    paraview "${FOAM_MARKER}" >/dev/null 2>&1 &
fi
