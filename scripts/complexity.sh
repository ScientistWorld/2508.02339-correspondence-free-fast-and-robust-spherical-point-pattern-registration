#!/bin/bash
# Run the paper's computational-complexity benchmark (Fig. 6).
#
# Usage:
#   bash scripts/complexity.sh

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"

COMPLEXITY_SCALES="${COMPLEXITY_SCALES:-1000,10000,100000,1000000,10000000}"
COMPLEXITY_ROTATIONS="${COMPLEXITY_ROTATIONS:-20}"
RAW_COMPLEXITY_RESULTS="${RAW_COMPLEXITY_RESULTS:-scoring/raw_complexity_results.json}"
SCORES_OUTPUT="${SCORES_OUTPUT:-scoring/scores.json}"

echo "Running computational-complexity benchmark on A3/B3..."
python3 scripts/run_complexity_experiment.py \
    --scales "${COMPLEXITY_SCALES}" \
    --n-rotations "${COMPLEXITY_ROTATIONS}" \
    --output "${RAW_COMPLEXITY_RESULTS}"

echo "Re-aggregating scores with the method-agnostic evaluator..."
RAW_COMPLEXITY_RESULTS="${RAW_COMPLEXITY_RESULTS}" SCORES_OUTPUT="${SCORES_OUTPUT}" \
    bash scripts/evaluate.sh

echo "Complexity benchmark complete."
