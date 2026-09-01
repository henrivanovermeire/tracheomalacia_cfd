#!/usr/bin/env bash
# Generate the airway mesh and run the OpenFOAM simulation in Docker.
#
# Usage:
#   ./run_cfd.sh [case]
#
# Examples:
#   ./run_cfd.sh postop
#   OPENFOAM_IMAGE=opencfd/openfoam-default:latest ./run_cfd.sh preop

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CASE_NAME="${1:-postop}"
OPENFOAM_IMAGE="${OPENFOAM_IMAGE:-opencfd/openfoam-default:latest}"
NPROCS="${NPROCS:-8}"

GEO_FILE="${SCRIPT_DIR}/meshes/airways.geo"
STL_FILE="${SCRIPT_DIR}/meshes/airways.stl"
OPENFOAM_DIR="${SCRIPT_DIR}/openFOAM"
CASE_DIR="${OPENFOAM_DIR}/${CASE_NAME}"
MESH_FILE="${CASE_DIR}/airways.msh"

if ! command -v gmsh >/dev/null 2>&1; then
    echo "Error: gmsh is not installed or not available on PATH." >&2
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker is not installed or not available on PATH." >&2
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

if [[ ! -d "${CASE_DIR}/0" || ! -d "${CASE_DIR}/constant" || ! -d "${CASE_DIR}/system" ]]; then
    echo "Error: incomplete OpenFOAM case directory: ${CASE_DIR}" >&2
    echo "Expected 0/, constant/, and system/ directories." >&2
    exit 1
fi

if ! [[ "${NPROCS}" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: NPROCS must be a positive integer (received '${NPROCS}')." >&2
    exit 1
fi

echo "======================================"
echo "Generating Gmsh volume mesh"
echo "======================================"
echo "Geometry: ${GEO_FILE}"
echo "STL:      ${STL_FILE}"
echo "Output:   ${MESH_FILE}"

# MSH 2.2 is used for broad compatibility with gmshToFoam. Gmsh resolves
# the relative Merge path in airways.geo from the geometry file's directory.
gmsh "${GEO_FILE}" -3 -format msh2 -o "${MESH_FILE}"

echo ""
echo "======================================"
echo "Running OpenFOAM case in Docker"
echo "======================================"
echo "Image:     ${OPENFOAM_IMAGE}"
echo "Case:      ${CASE_NAME}"
echo "Processes: ${NPROCS}"

# The repository's openFOAM directory is mounted as /cases, making the selected
# case available at /cases/<case>. Running as the host user prevents root-owned
# simulation output. The generated Gmsh/Slicer coordinates are millimetres;
# OpenFOAM expects SI units, so transformPoints scales the converted mesh to m.
docker run --rm \
    --user "$(id -u):$(id -g)" \
    --env HOME=/tmp \
    --volume "${OPENFOAM_DIR}:/cases" \
    --workdir "/cases/${CASE_NAME}" \
    "${OPENFOAM_IMAGE}" \
    bash -c "
        # OpenFOAM's setup scripts probe optional variables and execute
        # commands that may return non-zero during normal initialization.
        # Source them before enabling strict error handling, and do not source
        # them again when this image has already initialized the environment.
        if ! command -v simpleFoam >/dev/null 2>&1; then
            source /usr/lib/openfoam/openfoam2512/etc/bashrc
        fi
        set -Eeo pipefail

        # The OpenCFD image entrypoint may reset the current directory to
        # /home/openfoam, even when Docker --workdir is supplied.
        cd '/cases/${CASE_NAME}'
        if [[ ! -f system/controlDict ]]; then
            echo 'Error: mounted case is missing system/controlDict in /cases/${CASE_NAME}' >&2
            exit 1
        fi
        echo \"--- Working directory: \$(pwd)\"

        echo '--- Converting Gmsh mesh to OpenFOAM'
        gmshToFoam airways.msh

        echo '--- Scaling mesh from millimetres to metres'
        transformPoints -scale '(0.001 0.001 0.001)'

        echo '--- Checking mesh'
        checkMesh

        echo '--- Removing previous domain decomposition'
        # Preserve 0/ and all result times. In particular, 0/ contains the
        # initial and boundary conditions required to start the solver.
        rm -rf processor*

        echo '--- Decomposing case'
        decomposePar -force

        echo '--- Running simpleFoam in parallel'
        mpirun --use-hwthread-cpus -np ${NPROCS} simpleFoam -parallel 2>&1 | tee log.simpleFoam.parallel

        echo '--- Reconstructing latest result'
        reconstructPar -latestTime

        echo '--- Final mesh check'
        checkMesh
    "

echo ""
echo "======================================"
echo "CFD PIPELINE COMPLETE"
echo "======================================"
echo "Results: ${CASE_DIR}"
