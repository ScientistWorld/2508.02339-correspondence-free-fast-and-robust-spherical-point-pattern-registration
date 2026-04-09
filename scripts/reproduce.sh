#!/bin/bash
# Reproduce the paper's results end-to-end.
#
# This script runs inside the compute container and:
#   1. Verifies the paper's dataset is available
#   2. Runs SPMC, FRS, and SPMC+FRS evaluation on the paper's dataset
#   3. Runs evaluation and writes scoring/scores.json
#
# Assumes:
#   - Container is built with numpy available
#   - Working directory is /home/user
#   - Paper dataset at method/paper_code/vector_alignment_dataset/

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"

echo "=========================================="
echo "End-to-End Reproduction"
echo "=========================================="

# Step 1: Verify dataset is already present. Compute nodes have no internet.
echo "[1/3] Verifying paper dataset..."
if [ ! -f "method/paper_code/vector_alignment_dataset/A1_A.pkl" ]; then
    echo "  ERROR: dataset missing. Run scripts/download.sh before reproduce.sh."
    exit 1
else
    echo "  Dataset already present."
fi

# Step 2: Run the paper methods and aggregate scores
echo "[2/3] Running SPMC, FRS, and SPMC+FRS evaluation on paper's dataset..."
N_ROTATIONS="${N_ROTATIONS:-100}" bash scripts/method.sh

# Step 3: Validate and report results
echo "[3/3] Validating scoring artifacts..."
python3 validate.py --compare
echo "  Results written to scoring/scores.json"
echo ""
echo "=========================================="
echo "Reproduction complete!"
echo "=========================================="
