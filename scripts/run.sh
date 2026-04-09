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

# Run a configurable offline evaluation. Default to the full 100-rotation paper
# protocol so a successful job can support the core claim immediately.
N_ROTATIONS="${N_ROTATIONS:-100}"
echo "Running evaluation (SPMC, FRS, SPMC+FRS) on 5 patterns x 7 configs x ${N_ROTATIONS} rotations..."
bash scripts/method.sh

echo "Validating scoring artifacts..."
python3 validate.py --compare

echo ""
echo "=========================================="
echo "All done! Results in scoring/scores.json"
echo "=========================================="
