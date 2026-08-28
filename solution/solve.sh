#!/usr/bin/env bash
set -euo pipefail

# Oracle entrypoint for onera-m6-boundary-layer-repair.
#
# Copies the public case (data/case/) into a writable scratch directory,
# runs the real OpenFOAM pipeline (SCRIPTS/run_meshing.py ->
# SCRIPTS/run_analysis.py), and writes the declared JSON artifact from the
# resulting results/summary.json.
#
# AUTHORING-TIME CAVEAT (remove once resolved): data/case/system/snappyHexMeshDict
# still has the ORIGINAL layer settings that add zero boundary-layer cells
# on the "onera" patch (see MESHING_NOTES.md / results/summary.txt at the
# repo root). This oracle will NOT yet score 1.0 against the yplus_valid /
# convergence / cl_accuracy / cd_accuracy criteria in scorer/compute_score.py.
# Before this task can pass validation + ground-truth, the layer settings
# in data/case/system/snappyHexMeshDict must be retuned (per instruction.md)
# and this script re-run to confirm y+ and residuals both land in range -
# only then can scorer/data/reference.json be generated from a genuine
# converged run.

TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${DATA_DIR:-${TASK_DIR}/data}"
WORK_DIR="${WORK_DIR:-${TASK_DIR}/_work/case}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/output}"
OUTPUT_FILE="${OUTPUT_DIR}/force_coefficients.json"

mkdir -p "${OUTPUT_DIR}"
rm -rf "${WORK_DIR}"
mkdir -p "${WORK_DIR}"
cp -r "${DATA_DIR}/case/." "${WORK_DIR}/"
cp -r "${TASK_DIR}/SCRIPTS" "${WORK_DIR}/SCRIPTS"

cd "${WORK_DIR}"
python3 SCRIPTS/run_meshing.py
python3 SCRIPTS/run_analysis.py

python3 - "${WORK_DIR}" "${OUTPUT_FILE}" <<'PYEOF'
import json
import sys
from pathlib import Path

work_dir, output_file = Path(sys.argv[1]), Path(sys.argv[2])
summary = json.loads((work_dir / "results" / "summary.json").read_text())

coeffs = summary.get("forceCoefficients", {})
yplus = summary.get("yPlus_onera") or {}
residuals = summary.get("final_residuals", {})

artifact = {
    "Cl": coeffs.get("Cl"),
    "Cd": coeffs.get("Cd"),
    "CmPitch": coeffs.get("CmPitch"),
    "yPlus_min": yplus.get("min"),
    "yPlus_max": yplus.get("max"),
    "yPlus_average": yplus.get("average"),
    "residual_p_final": residuals.get("p"),
    "residual_U_final": residuals.get("Ux"),
    "residual_k_final": residuals.get("k"),
    "residual_omega_final": residuals.get("omega"),
}
output_file.write_text(json.dumps(artifact, indent=2))
print(f"Wrote {output_file}")
PYEOF
