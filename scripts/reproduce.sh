#!/bin/bash
# Reproduce the paper's results end-to-end.
#
# This script runs inside the compute container and:
#   1. Verifies the paper's dataset is available
#   2. Runs SPMC, FRS, and SPMC+FRS evaluation on the paper's dataset
#   3. Optionally runs the paper's computational-complexity benchmark
#   4. Runs evaluation and writes scoring/scores.json
#
# Assumes:
#   - Container is built with numpy available
#   - Working directory is /home/user
#   - Paper dataset at data/downloads/vector_alignment_dataset/

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONPATH="/home/user${PYTHONPATH:+:${PYTHONPATH}}"

echo "=========================================="
echo "End-to-End Reproduction"
echo "=========================================="

# Step 1: Verify dataset is already present. Compute nodes have no internet.
echo "[1/4] Verifying paper dataset..."
for required_path in \
    "data/downloads/vector_alignment_dataset/A1_A.pkl" \
    "data/downloads/vector_alignment_dataset/RandomRotation100.pkl"
do
    if [ ! -f "${required_path}" ]; then
        echo "  ERROR: dataset missing required asset ${required_path}. Run scripts/download.sh before reproduce.sh."
        exit 1
    fi
done
echo "  Dataset already present."

# Step 2: Run the paper methods and aggregate scores
echo "[2/4] Running SPMC, FRS, and SPMC+FRS evaluation on paper's dataset..."
N_ROTATIONS="${N_ROTATIONS:-100}" bash scripts/method.sh

# Step 3: Optional complexity benchmark
if [ "${RUN_COMPLEXITY:-0}" = "1" ]; then
    echo "[3/4] Running computational-complexity benchmark..."
    bash scripts/complexity.sh
else
    echo "[3/4] Skipping computational-complexity benchmark (set RUN_COMPLEXITY=1 to enable)"
fi

# Step 4: Validate and report results
echo "[4/4] Validating scoring artifacts..."
python3 validate.py --compare
echo "  Results written to scoring/scores.json"
echo ""
echo "=========================================="
echo "Reproduction complete!"
echo "=========================================="
