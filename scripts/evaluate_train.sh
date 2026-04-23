#!/bin/bash
# Aggregate the visible train slice of precomputed raw evaluation results.
#
# Usage mirrors scripts/evaluate.sh:
#   bash scripts/evaluate_train.sh
#   RAW_RESULTS=/tmp/raw.json RAW_COMPLEXITY_RESULTS=/tmp/raw_complexity.json \
#   SCORES_OUTPUT=/tmp/scores_train.json \
#     bash scripts/evaluate_train.sh

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONPATH="/home/user${PYTHONPATH:+:${PYTHONPATH}}"

RAW_RESULTS="${RAW_RESULTS:-scoring/raw_results.json}"
RAW_COMPLEXITY_RESULTS="${RAW_COMPLEXITY_RESULTS:-scoring/raw_complexity_results.json}"
SCORES_OUTPUT="${SCORES_OUTPUT:-scoring/scores_train.json}"

if [ ! -f "${RAW_RESULTS}" ]; then
    echo "ERROR: no raw benchmark results found"
    echo "Expected: ${RAW_RESULTS}"
    exit 1
fi

mkdir -p "$(dirname "${SCORES_OUTPUT}")"

echo "Aggregating train slice ${RAW_RESULTS} -> ${SCORES_OUTPUT}..."
python3 eval/train/evaluate.py \
    --input "${RAW_RESULTS}" \
    --complexity-input "${RAW_COMPLEXITY_RESULTS}" \
    --output "${SCORES_OUTPUT}"

echo "Train-slice evaluation complete. Results in ${SCORES_OUTPUT}"
