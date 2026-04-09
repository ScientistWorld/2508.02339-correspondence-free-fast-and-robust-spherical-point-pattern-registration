#!/bin/bash
# Job script for the paper's computational-complexity benchmark.
#
# This runs inside the compute container with:
#   - Workspace mounted at /home/user
#   - numpy available via setup.sh
#   - Paper dataset at /home/user/method/paper_code/vector_alignment_dataset/

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"

echo "=========================================="
echo "Spherical Point Pattern Registration: Complexity Benchmark"
echo "=========================================="

# Compute nodes have no internet. All assets must exist before submission.
if [ ! -f "method/paper_code/vector_alignment_dataset/A1_A.pkl" ]; then
    echo "ERROR: paper dataset missing at method/paper_code/vector_alignment_dataset/"
    exit 1
fi

echo "Checking runtime Python dependencies..."
python3 - <<'PY'
import numpy
print(f"numpy OK: {numpy.__version__}")
PY

# Run the paper's Fig. 6 complexity protocol on CPU. The implementation is
# resume-safe per scale and rotation, so interrupted jobs can continue.
COMPLEXITY_SCALES="${COMPLEXITY_SCALES:-1000,10000,100000,1000000,10000000}"
COMPLEXITY_ROTATIONS="${COMPLEXITY_ROTATIONS:-20}"
RAW_COMPLEXITY_RESULTS="${RAW_COMPLEXITY_RESULTS:-scoring/raw_complexity_results.json}"
SCORES_OUTPUT="${SCORES_OUTPUT:-scoring/scores.json}"
if [ -f "${RAW_COMPLEXITY_RESULTS}" ]; then
    echo "Found existing complexity checkpoint at ${RAW_COMPLEXITY_RESULTS}; completed rotations will be skipped automatically."
fi
echo "Running complexity benchmark on A3/B3 for scales ${COMPLEXITY_SCALES} with ${COMPLEXITY_ROTATIONS} rotations..."
COMPLEXITY_SCALES="${COMPLEXITY_SCALES}" COMPLEXITY_ROTATIONS="${COMPLEXITY_ROTATIONS}" \
RAW_COMPLEXITY_RESULTS="${RAW_COMPLEXITY_RESULTS}" SCORES_OUTPUT="${SCORES_OUTPUT}" \
    bash scripts/complexity.sh

echo "Validating scoring artifacts..."
python3 validate.py --compare

echo ""
echo "=========================================="
echo "All done! Results in scoring/scores.json"
echo "=========================================="
