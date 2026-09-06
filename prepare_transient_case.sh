#!/usr/bin/env bash
# Build either the selected-mesh transient case or a coarse proof-of-concept case.
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROFILE="${TRANSIENT_PROFILE:-selected}"
NPROCS="${NPROCS:-48}"
case "$PROFILE" in
  selected)
    SOURCE_CASE="${SOURCE_CASE:-postop_hxt_015}"
    CASE_NAME="${1:-postop_transient}"
    MAX_CO="${MAX_CO:-2.0}"
    MAX_DELTA_T="${MAX_DELTA_T:-5e-5}"
    DIV_U="bounded Gauss linearUpwind grad(U)"
    NON_ORTH_CORRECTORS="1"
    ;;
  coarse-poc)
    SOURCE_CASE="${SOURCE_CASE:-postop_hxt_025}"
    CASE_NAME="${1:-postop_transient_coarse_poc}"
    MAX_CO="${MAX_CO:-0.5}"
    MAX_DELTA_T="${MAX_DELTA_T:-2e-5}"
    DIV_U="bounded Gauss upwind"
    NON_ORTH_CORRECTORS="2"
    ;;
  *)
    echo "TRANSIENT_PROFILE must be 'selected' or 'coarse-poc'" >&2
    exit 1
    ;;
esac
RESULT_SOURCE="$SCRIPT_DIR/results/$SOURCE_CASE"
CASE_SOURCE="$SCRIPT_DIR/openFOAM/$SOURCE_CASE"
TARGET="$SCRIPT_DIR/openFOAM/$CASE_NAME"
rm -rf "$TARGET"; mkdir -p "$TARGET"
if [[ -d "$RESULT_SOURCE/constant/polyMesh" ]]; then
  cp -a "$RESULT_SOURCE/constant" "$TARGET/constant"
elif [[ -f "$CASE_SOURCE/airways.msh" ]]; then
  cp -a "$CASE_SOURCE/constant" "$TARGET/constant"
  cp "$CASE_SOURCE/airways.msh" "$TARGET/airways.msh"
else
  echo "Missing polyMesh and fallback MSH for source case: $SOURCE_CASE" >&2
  exit 1
fi
mkdir -p "$TARGET/0" "$TARGET/system"
python3 "$SCRIPT_DIR/assignment/scripts/generate_breathing_waveform.py" --table "$TARGET/constant/breathingFlowRate.table"
cat > "$TARGET/0/U" <<'EOF'
FoamFile { format ascii; class volVectorField; object U; }
dimensions [0 1 -1 0 0 0 0];
internalField uniform (0 0 0);
boundaryField
{
    inlet
    {
        type flowRateInletVelocity;
        #include "../constant/breathingFlowRate.table"
        value uniform (0 0 0);
    }
    outlet_1 { type pressureInletOutletVelocity; value uniform (0 0 0); }
    outlet_2 { type pressureInletOutletVelocity; value uniform (0 0 0); }
    outlet_3 { type pressureInletOutletVelocity; value uniform (0 0 0); }
    wall { type noSlip; }
}
EOF
cp "$SCRIPT_DIR/openFOAM/postop/0/p" "$TARGET/0/p"
cat > "$TARGET/system/controlDict" <<'EOF'
FoamFile { format ascii; class dictionary; object controlDict; }
application pimpleFoam;
startFrom startTime;
startTime 0;
stopAt endTime;
endTime 2;
deltaT 1e-5;
writeControl adjustableRunTime;
writeInterval 0.02;
purgeWrite 0;
writeFormat binary;
writePrecision 8;
runTimeModifiable true;
adjustTimeStep yes;
maxCo __MAX_CO__;
maxDeltaT __MAX_DELTA_T__;
EOF
cat > "$TARGET/system/fvSchemes" <<'EOF'
FoamFile { format ascii; class dictionary; object fvSchemes; }
ddtSchemes { default backward; }
gradSchemes { default Gauss linear; grad(U) cellLimited Gauss linear 1; }
divSchemes
{
    default none;
    div(phi,U) __DIV_U__;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
fluxRequired { default no; p; }
EOF
cat > "$TARGET/system/fvSolution" <<'EOF'
FoamFile { format ascii; class dictionary; object fvSolution; }
solvers
{
    p { solver GAMG; tolerance 1e-8; relTol 0.01; smoother GaussSeidel; }
    pFinal { $p; relTol 0; }
    U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-8; relTol 0.01; }
    UFinal { $U; relTol 0; }
}
PIMPLE
{
    momentumPredictor yes;
    nOuterCorrectors 3;
    nCorrectors 2;
    nNonOrthogonalCorrectors __NON_ORTH_CORRECTORS__;
    residualControl
    {
        p { tolerance 1e-2; relTol 0; }
        U { tolerance 2e-3; relTol 0; }
    }
}
relaxationFactors { fields { p 0.5; } equations { U 0.7; } }
EOF
sed -i \
  -e "s/__MAX_CO__/$MAX_CO/" \
  -e "s/__MAX_DELTA_T__/$MAX_DELTA_T/" \
  "$TARGET/system/controlDict"
sed -i -e "s|__DIV_U__|$DIV_U|" "$TARGET/system/fvSchemes"
sed -i \
  -e "s/__NON_ORTH_CORRECTORS__/$NON_ORTH_CORRECTORS/" \
  "$TARGET/system/fvSolution"
cat > "$TARGET/system/decomposeParDict" <<EOF
FoamFile { format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $NPROCS;
method scotch;
EOF
echo "Prepared $TARGET from $SOURCE_CASE using transient profile '$PROFILE'."
echo "Controls: maxCo=$MAX_CO, maxDeltaT=$MAX_DELTA_T, div(phi,U)=$DIV_U, non-orthogonal correctors=$NON_ORTH_CORRECTORS."
echo "Timing: endTime=0.05 s; pilot: endTime=0.55 s; full cycle: endTime=2.0 s."
