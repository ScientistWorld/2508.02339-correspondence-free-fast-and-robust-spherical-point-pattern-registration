#!/bin/bash
# Run the paper's proposed method (SPMC+FRS).
#
# Usage:
#   bash scripts/method.sh

set -euo pipefail
cd /home/user

N_ROTATIONS="${N_ROTATIONS:-100}"
ROTATION_START="${ROTATION_START:-0}"
RAW_RESULTS="${RAW_RESULTS:-scoring/raw_results.json}"

echo "Running paper methods on the Robust Vector Alignment Dataset..."
python3 scripts/run_experiment.py \
    --n-rotations "${N_ROTATIONS}" \
    --rotation-start "${ROTATION_START}" \
    --raw-output "${RAW_RESULTS}"

echo "Re-aggregating scores with the method-agnostic evaluator..."
RAW_RESULTS="${RAW_RESULTS}" bash scripts/evaluate.sh

echo "Method evaluation complete."
