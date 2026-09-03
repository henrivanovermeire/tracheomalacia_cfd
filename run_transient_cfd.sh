#!/usr/bin/env bash
# Run a prepared transient OpenFOAM case in Docker.
# Usage: NPROCS=48 ./run_transient_cfd.sh postop_transient [--timing|--pilot|--full]
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"; CASE_NAME="${1:-postop_transient}"; MODE="${2:---timing}"
[[ "$MODE" == --timing || "$MODE" == --pilot || "$MODE" == --full ]] || { echo "Mode must be --timing, --pilot, or --full" >&2; exit 1; }
NPROCS="${NPROCS:-48}"; IMAGE="${OPENFOAM_IMAGE:-opencfd/openfoam-default:latest}"; ROOT="$SCRIPT_DIR/openFOAM"; CASE_DIR="$ROOT/$CASE_NAME"; END_TIME=0.05; LOG_NAME=log.pimpleFoam.timing
if [[ "$MODE" == --pilot ]]; then END_TIME=0.55; LOG_NAME=log.pimpleFoam.pilot; fi
if [[ "$MODE" == --full ]]; then END_TIME=2.0; LOG_NAME=log.pimpleFoam.full; fi
[[ -d "$CASE_DIR/constant/polyMesh" && -f "$CASE_DIR/system/controlDict" ]] || { echo "Incomplete transient case: $CASE_DIR" >&2; exit 1; }
docker run --rm --user "$(id -u):$(id -g)" --env HOME=/tmp --volume "$ROOT:/cases" --workdir "/cases/$CASE_NAME" "$IMAGE" bash -c "
 if ! command -v pimpleFoam >/dev/null 2>&1; then source /usr/lib/openfoam/openfoam2512/etc/bashrc; fi
 set -Eeo pipefail; cd '/cases/$CASE_NAME'
 foamDictionary system/controlDict -entry endTime -set '$END_TIME'
 foamDictionary system/decomposeParDict -entry numberOfSubdomains -set '$NPROCS'
 for d in [0-9]*; do if [[ -d \"\$d\" && \"\$d\" != 0 ]]; then rm -rf \"\$d\"; fi; done
 rm -rf processor* postProcessing; checkMesh -allTopology -allGeometry > log.checkMesh.transient
 decomposePar -force
 set +e
 mpirun --allow-run-as-root --use-hwthread-cpus -np '$NPROCS' pimpleFoam -parallel 2>&1 | tee '$LOG_NAME'
 status=\${PIPESTATUS[0]}
 set -e
 if [[ \$status -ne 0 ]]; then
     echo 'pimpleFoam failed with status' \$status >&2
     exit \$status
 fi
 reconstructPar
 postProcess -func CourantNo -latestTime > log.postProcess.CourantNo 2>&1 || true
 checkMesh -allTopology -allGeometry > log.checkMesh.transient.final
"
echo "Transient $MODE run complete: $CASE_DIR"
