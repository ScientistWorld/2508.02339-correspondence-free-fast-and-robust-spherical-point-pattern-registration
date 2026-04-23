#!/bin/bash
# Aggregate precomputed raw evaluation results into scoring/scores.json.
#
# This script intentionally stays within eval/ so future methods can reuse the
# same scoring logic without importing from method/.
#
# Usage:
#   bash scripts/evaluate.sh
#   RAW_RESULTS=/tmp/raw.json RAW_COMPLEXITY_RESULTS=/tmp/raw_complexity.json \
#     SCORES_OUTPUT=/tmp/scores.json bash scripts/evaluate.sh

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONPATH="/home/user${PYTHONPATH:+:${PYTHONPATH}}"

RAW_RESULTS="${RAW_RESULTS:-scoring/raw_results.json}"
RAW_COMPLEXITY_RESULTS="${RAW_COMPLEXITY_RESULTS:-scoring/raw_complexity_results.json}"
SCORES_OUTPUT="${SCORES_OUTPUT:-scoring/scores.json}"

if [ ! -f "${RAW_RESULTS}" ] && [ ! -f "${RAW_COMPLEXITY_RESULTS}" ]; then
    echo "ERROR: no raw benchmark results found"
    echo "Expected one of:"
    echo "  ${RAW_RESULTS}"
    echo "  ${RAW_COMPLEXITY_RESULTS}"
    exit 1
fi

mkdir -p "$(dirname "${SCORES_OUTPUT}")"

echo "Aggregating ${RAW_RESULTS} -> ${SCORES_OUTPUT}..."
python3 eval/evaluate.py \
    --input "${RAW_RESULTS}" \
    --complexity-input "${RAW_COMPLEXITY_RESULTS}" \
    --output "${SCORES_OUTPUT}"

echo "Evaluation complete. Results in ${SCORES_OUTPUT}"
