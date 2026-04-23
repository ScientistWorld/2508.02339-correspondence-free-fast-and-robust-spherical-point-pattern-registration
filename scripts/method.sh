#!/bin/bash
# Run the paper's proposed method (SPMC+FRS).
#
# Usage:
#   bash scripts/method.sh

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONPATH="/home/user${PYTHONPATH:+:${PYTHONPATH}}"

N_ROTATIONS="${N_ROTATIONS:-100}"
ROTATION_START="${ROTATION_START:-0}"
RAW_RESULTS="${RAW_RESULTS:-scoring/raw_results.json}"
SCORES_OUTPUT="${SCORES_OUTPUT:-scoring/scores.json}"

echo "Running paper methods on the Robust Vector Alignment Dataset..."
python3 scripts/run_experiment.py \
    --n-rotations "${N_ROTATIONS}" \
    --rotation-start "${ROTATION_START}" \
    --raw-output "${RAW_RESULTS}" \
    --scores-output "${SCORES_OUTPUT}"

echo "Re-aggregating scores with the method-agnostic evaluator..."
RAW_RESULTS="${RAW_RESULTS}" SCORES_OUTPUT="${SCORES_OUTPUT}" bash scripts/evaluate.sh

echo "Method evaluation complete."
