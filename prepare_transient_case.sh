#!/usr/bin/env bash
# Build a transient case from the selected 0.15 mm HXT mesh.
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_CASE="${SOURCE_CASE:-postop_hxt_015}"
CASE_NAME="${1:-postop_transient}"
NPROCS="${NPROCS:-48}"
SOURCE="$SCRIPT_DIR/results/$SOURCE_CASE"
TARGET="$SCRIPT_DIR/openFOAM/$CASE_NAME"
[[ -d "$SOURCE/constant/polyMesh" ]] || { echo "Missing accepted mesh: $SOURCE/constant/polyMesh" >&2; exit 1; }
rm -rf "$TARGET"; mkdir -p "$TARGET"
cp -a "$SOURCE/constant" "$TARGET/constant"
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
maxCo 2.0;
maxDeltaT 5e-5;
EOF
cat > "$TARGET/system/fvSchemes" <<'EOF'
FoamFile { format ascii; class dictionary; object fvSchemes; }
ddtSchemes { default backward; }
gradSchemes { default Gauss linear; grad(U) cellLimited Gauss linear 1; }
divSchemes
{
    default none;
    div(phi,U) bounded Gauss linearUpwind grad(U);
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
    nNonOrthogonalCorrectors 1;
    residualControl
    {
        p { tolerance 1e-2; relTol 0; }
        U { tolerance 2e-3; relTol 0; }
    }
}
relaxationFactors { fields { p 0.5; } equations { U 0.7; } }
EOF
cat > "$TARGET/system/decomposeParDict" <<EOF
FoamFile { format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $NPROCS;
method scotch;
EOF
echo "Prepared $TARGET from $SOURCE_CASE (0.15 mm HXT mesh)."
echo "Timing: endTime=0.05 s; pilot: endTime=0.55 s; full cycle: endTime=2.0 s."
