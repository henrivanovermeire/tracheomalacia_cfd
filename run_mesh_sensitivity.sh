#!/usr/bin/env bash
# Run a quality-consistent HXT baseline plus three progressively finer meshes.
# Usage: ./run_mesh_sensitivity.sh <ssh-host> [--resume]
#        ./run_mesh_sensitivity.sh --skip-runs
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
REMOTE_TARGET=""; SKIP_RUNS=false; RESUME=false
for arg in "$@"; do
 case "$arg" in
  --skip-runs) SKIP_RUNS=true;; --resume) RESUME=true;; --help|-h) echo "Usage: $0 <ssh-host> [--resume] | $0 --skip-runs"; exit 0;;
  --*) echo "Unknown option: $arg" >&2; exit 1;;
  *) [[ -z "$REMOTE_TARGET" ]] || { echo "Only one SSH host is allowed." >&2; exit 1; }; REMOTE_TARGET="$arg";;
 esac
done
[[ "$SKIP_RUNS" == true || -n "$REMOTE_TARGET" ]] || { echo "Supply an SSH host or --skip-runs." >&2; exit 1; }
BASE_CASE="${BASE_CASE:-postop}"; NPROCS="${NPROCS:-60}"
CASES=(postop_hxt_025 postop_hxt_020 postop_hxt_015 postop_hxt_012); SIZES=(0.25 0.20 0.15 0.12)
BASE_U="$SCRIPT_DIR/openFOAM/$BASE_CASE/0/U"
grep -Eq 'volumetricFlowRate[[:space:]]+constant[[:space:]]+3[.]3333e-5' "$BASE_U" || { echo "Expected 2 L/min inlet in $BASE_U" >&2; exit 1; }
for i in 0 1 2 3; do
 case_name="${CASES[$i]}"; mesh_size="${SIZES[$i]}"; foam="$SCRIPT_DIR/results/$case_name/$case_name.foam"
 if [[ "$SKIP_RUNS" == false ]]; then
  if [[ "$RESUME" == true && -f "$foam" && -s "$SCRIPT_DIR/results/$case_name/log.simpleFoam.parallel" ]]; then echo "--- Reusing fetched $case_name";
  else
   echo "=== Running $case_name at $mesh_size mm ==="
   BASE_CASE="$BASE_CASE" FINE_CASE="$case_name" MESH_SIZE="$mesh_size" NPROCS="$NPROCS" "$SCRIPT_DIR/run_fine_cfd.sh" "$REMOTE_TARGET"
  fi
 fi
 [[ -f "$foam" ]] || { echo "Missing reconstructed case marker: $foam" >&2; exit 1; }
 HOME=/tmp pvpython "$SCRIPT_DIR/assignment/scripts/extract_cfd_metrics.py" "$foam" --label "$case_name"
 python3 "$SCRIPT_DIR/assignment/scripts/extract_patch_flows.py" "$case_name"
 python3 "$SCRIPT_DIR/assignment/scripts/parse_openfoam_residuals.py" "$SCRIPT_DIR/results/$case_name/log.simpleFoam.parallel" --csv "$SCRIPT_DIR/assignment/data/${case_name}_residuals.csv" --figure "$SCRIPT_DIR/report/figures/${case_name}_residuals.tex"
done
python3 "$SCRIPT_DIR/assignment/scripts/aggregate_mesh_sensitivity.py"
make -B -C "$SCRIPT_DIR/report"
echo "======================================"
echo "MESH SENSITIVITY WORKFLOW COMPLETE"
echo "Data:    $SCRIPT_DIR/assignment/data/mesh_sensitivity.csv"
echo "Metrics: $SCRIPT_DIR/report/figures/assignment5_mesh_metrics.tex"
echo "Errors:  $SCRIPT_DIR/report/figures/assignment5_mesh_differences.tex"
echo "======================================"
