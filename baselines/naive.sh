#!/usr/bin/env bash
set -euo pipefail

# Naive baseline: skip meshing and the solver entirely. Guesses Cl from 2D
# thin-airfoil theory (Cl = 2*pi*alpha), Cd = 0, and leaves the y+/residual
# fields null so `yplus_valid` and `convergence` both fail. Must stay below
# task.toml's max_trivial_score (0.05) - if this ever scores meaningfully
# above that, the rubric weighting needs to change, not this baseline.

OUTPUT_DIR="${OUTPUT_DIR:-/tmp/output}"
OUTPUT_FILE="${OUTPUT_DIR}/force_coefficients.json"
mkdir -p "${OUTPUT_DIR}"

python3 - "${OUTPUT_FILE}" <<'PYEOF'
import json
import math
import sys
from pathlib import Path

alpha_rad = math.radians(3.06)
cl_thin_airfoil = 2 * math.pi * alpha_rad

artifact = {
    "Cl": cl_thin_airfoil,
    "Cd": 0.0,
    "CmPitch": 0.0,
    "yPlus_min": None,
    "yPlus_max": None,
    "yPlus_average": None,
    "residual_p_final": None,
    "residual_U_final": None,
    "residual_k_final": None,
    "residual_omega_final": None,
}
Path(sys.argv[1]).write_text(json.dumps(artifact, indent=2))
PYEOF
