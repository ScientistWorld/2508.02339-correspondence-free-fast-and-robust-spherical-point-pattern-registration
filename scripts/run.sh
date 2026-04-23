#!/bin/bash
# Job script for the split-evaluation runner.
#
# This executes the remaining held-out scoring work against the frozen
# reproduction artifacts:
#   1. regenerate the missing complexity raw timings on CPU,
#   2. refresh canonical scoring/scores.json,
#   3. write scoring/scores_train.json and scoring/scores_test.json,
#   4. validate the resulting bundle.

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONPATH="/home/user${PYTHONPATH:+:${PYTHONPATH}}"

echo "=========================================="
echo "Spherical Point Pattern Registration: Split Evaluation"
echo "=========================================="

for required_path in \
    "scoring/raw_results.json" \
    "data/vector_alignment_dataset/A3_A.pkl" \
    "data/vector_alignment_dataset/A3_A_B3.pkl" \
    "data/vector_alignment_dataset/RandomRotation100.pkl"
do
    if [ ! -f "${required_path}" ]; then
        echo "ERROR: required artifact missing: ${required_path}"
        exit 1
    fi
done

echo "Checking runtime Python dependencies..."
python3 - <<'PY'
import numpy
print(f"numpy OK: {numpy.__version__}")
PY

COMPLEXITY_SCALES="${COMPLEXITY_SCALES:-1000,10000,100000,1000000,10000000}"
COMPLEXITY_ROTATIONS="${COMPLEXITY_ROTATIONS:-20}"
RAW_COMPLEXITY_RESULTS="${RAW_COMPLEXITY_RESULTS:-scoring/raw_complexity_results.json}"

if [ -f "${RAW_COMPLEXITY_RESULTS}" ]; then
    echo "Found existing complexity checkpoint at ${RAW_COMPLEXITY_RESULTS}; completed rotations will be skipped automatically."
fi

echo "Running computational-complexity benchmark..."
python3 scripts/run_complexity_experiment.py \
    --scales "${COMPLEXITY_SCALES}" \
    --n-rotations "${COMPLEXITY_ROTATIONS}" \
    --output "${RAW_COMPLEXITY_RESULTS}"

echo "Refreshing canonical scores.json..."
RAW_COMPLEXITY_RESULTS="${RAW_COMPLEXITY_RESULTS}" \
    bash scripts/evaluate.sh

echo "Writing split train/test scores..."
RAW_COMPLEXITY_RESULTS="${RAW_COMPLEXITY_RESULTS}" \
    bash scripts/evaluate_train.sh
RAW_COMPLEXITY_RESULTS="${RAW_COMPLEXITY_RESULTS}" \
    bash scripts/evaluate_test.sh

echo "Validating scoring artifacts..."
python3 validate.py --compare

echo ""
echo "=========================================="
echo "All done! Results in scoring/scores.json, scoring/scores_train.json, and scoring/scores_test.json"
echo "=========================================="
