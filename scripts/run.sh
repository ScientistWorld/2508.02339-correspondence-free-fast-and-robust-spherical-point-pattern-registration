#!/bin/bash
# Fresh CPU rerun of the released robust-alignment benchmark from the restored
# dataset path. This intentionally ignores previously cached main-benchmark
# artifacts so the next turn has container-side evidence from this clone.

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONPATH="/home/user${PYTHONPATH:+:${PYTHONPATH}}"

echo "=========================================="
echo "Spherical Point Pattern Registration: Fresh Benchmark Rerun"
echo "=========================================="

for required_path in \
    "data/downloads/vector_alignment_dataset/A1_A.pkl" \
    "data/downloads/vector_alignment_dataset/A5_A_B7.pkl" \
    "data/downloads/vector_alignment_dataset/RandomRotation100.pkl"
do
    if [ ! -f "${required_path}" ]; then
        echo "ERROR: required dataset asset missing: ${required_path}"
        exit 1
    fi
done

echo "Checking runtime Python dependencies..."
python3 - <<'PY'
import numpy
print(f"numpy OK: {numpy.__version__}")
PY

echo "Removing stale main-benchmark artifacts..."
rm -f scoring/raw_results.json scoring/scores.json

echo "Running released Experiment 1 benchmark (5 patterns x 7 configs x 100 rotations)..."
RAW_COMPLEXITY_RESULTS="tmp/no_complexity_results.json" \
    N_ROTATIONS=100 \
    bash scripts/method.sh

echo "Validating refreshed scoring bundle..."
python3 validate.py --compare

echo "=========================================="
echo "Benchmark rerun finished"
echo "=========================================="
