#!/usr/bin/env bash
# Prepare, remotely execute, and fetch transient timing/pilot/full-cycle results.
# Usage: ./run_transient_workflow.sh <ssh-host> [--timing|--pilot|--full] [--selected|--coarse-poc]
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"; REMOTE_TARGET="${1:-}"; MODE="${2:---timing}"; PROFILE_ARG="${3:---selected}"; [[ -n "$REMOTE_TARGET" ]] || { echo "Usage: $0 <ssh-host> [--timing|--pilot|--full] [--selected|--coarse-poc]" >&2; exit 1; }
[[ "$MODE" == --timing || "$MODE" == --pilot || "$MODE" == --full ]] || { echo "Mode must be --timing, --pilot, or --full" >&2; exit 1; }
[[ "$PROFILE_ARG" == --selected || "$PROFILE_ARG" == --coarse-poc ]] || { echo "Profile must be --selected or --coarse-poc" >&2; exit 1; }
TRANSIENT_PROFILE="${PROFILE_ARG#--}"
REMOTE_USER="${REMOTE_USER:-root}"; REMOTE_REPO="${REMOTE_REPO:-/root/tracheomalacia_cfd}"; NPROCS="${NPROCS:-48}"
if [[ "$TRANSIENT_PROFILE" == coarse-poc ]]; then
  CASE_NAME="${CASE_NAME:-postop_transient_coarse_poc}"
else
  CASE_NAME="${CASE_NAME:-postop_transient}"
fi
[[ "$REMOTE_TARGET" == *@* ]] && REMOTE_HOST="$REMOTE_TARGET" || REMOTE_HOST="$REMOTE_USER@$REMOTE_TARGET"
NPROCS="$NPROCS" TRANSIENT_PROFILE="$TRANSIENT_PROFILE" "$SCRIPT_DIR/prepare_transient_case.sh" "$CASE_NAME"
rsync -ah "$SCRIPT_DIR/run_transient_cfd.sh" "$REMOTE_HOST:$REMOTE_REPO/run_transient_cfd.sh"
ssh "$REMOTE_HOST" "chmod +x '$REMOTE_REPO/run_transient_cfd.sh'; rm -rf '$REMOTE_REPO/openFOAM/$CASE_NAME'; mkdir -p '$REMOTE_REPO/openFOAM/$CASE_NAME'"
rsync -ah --delete --info=progress2 "$SCRIPT_DIR/openFOAM/$CASE_NAME/" "$REMOTE_HOST:$REMOTE_REPO/openFOAM/$CASE_NAME/"
ssh "$REMOTE_HOST" "cd '$REMOTE_REPO' && NPROCS='$NPROCS' ./run_transient_cfd.sh '$CASE_NAME' '$MODE'"
REMOTE_REPO="$REMOTE_REPO" "$SCRIPT_DIR/fetch_cfd_results.sh" "$REMOTE_HOST" "$CASE_NAME"
echo "Fetched: $SCRIPT_DIR/results/$CASE_NAME/$CASE_NAME.foam"
