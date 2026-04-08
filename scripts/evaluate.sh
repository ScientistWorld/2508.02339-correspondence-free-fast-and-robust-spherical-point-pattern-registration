#!/bin/bash
# Aggregate precomputed raw evaluation results into scoring/scores.json.
#
# This script intentionally stays within eval/ so future methods can reuse the
# same scoring logic without importing from method/.
#
# Usage:
#   bash scripts/evaluate.sh
#   RAW_RESULTS=/tmp/raw.json SCORES_OUT=/tmp/scores.json bash scripts/evaluate.sh

set -euo pipefail
cd /home/user

RAW_RESULTS="${RAW_RESULTS:-scoring/raw_results.json}"
SCORES_OUT="${SCORES_OUT:-scoring/scores.json}"

if [ ! -f "${RAW_RESULTS}" ]; then
    echo "ERROR: raw results not found at ${RAW_RESULTS}"
    echo "Run scripts/method.sh or another method-specific generator first."
    exit 1
fi

mkdir -p "$(dirname "${SCORES_OUT}")"

echo "Aggregating ${RAW_RESULTS} -> ${SCORES_OUT}..."
python3 eval/evaluate.py \
    --input "${RAW_RESULTS}" \
    --output "${SCORES_OUT}"

echo "Evaluation complete. Results in ${SCORES_OUT}"
