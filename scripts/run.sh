#!/bin/bash
# Job script for spherical point pattern registration.
#
# This runs inside the compute container with:
#   - Workspace mounted at /home/user
#   - numpy available via setup.sh
#   - Paper dataset at /home/user/method/paper_code/vector_alignment_dataset/

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"

echo "=========================================="
echo "Spherical Point Pattern Registration"
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

# Run a configurable offline evaluation. The CPU queue available here behaves
# like a 1-hour test queue, so default to a 20-rotation slice that still covers
# all 5 patterns x 7 configs while finishing reliably. Full 100-rotation sweeps
# remain available by overriding N_ROTATIONS/ROTATION_START.
N_ROTATIONS="${N_ROTATIONS:-20}"
ROTATION_START="${ROTATION_START:-0}"
RAW_RESULTS="${RAW_RESULTS:-scoring/raw_results.json}"
SCORES_OUTPUT="${SCORES_OUTPUT:-scoring/scores.json}"
if [ -f "${RAW_RESULTS}" ]; then
    echo "Found existing raw checkpoint at ${RAW_RESULTS}; completed configs will be skipped automatically."
fi
echo "Running evaluation (SPMC, FRS, SPMC+FRS) on 5 patterns x 7 configs x ${N_ROTATIONS} rotations starting at ${ROTATION_START}..."
N_ROTATIONS="${N_ROTATIONS}" ROTATION_START="${ROTATION_START}" RAW_RESULTS="${RAW_RESULTS}" SCORES_OUTPUT="${SCORES_OUTPUT}" bash scripts/method.sh

echo "Validating scoring artifacts..."
python3 validate.py --compare

echo ""
echo "=========================================="
echo "All done! Results in scoring/scores.json"
echo "=========================================="
