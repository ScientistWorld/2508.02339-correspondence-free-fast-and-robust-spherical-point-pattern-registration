#!/bin/bash
# Reproduce the paper's results end-to-end.
#
# This script runs inside the compute container and:
#   1. Ensures the paper's dataset is available
#   2. Runs SPMC (and spmc_frs) evaluation on the paper's dataset
#   3. Runs evaluation and writes scoring/scores.json
#
# Assumes:
#   - Container is built with numpy available
#   - Working directory is /home/user
#   - Paper dataset at method/paper_code/vector_alignment_dataset/

set -e
cd /home/user

echo "=========================================="
echo "End-to-End Reproduction"
echo "=========================================="

# Step 1: Ensure dataset (clone from GitHub if not present)
echo "[1/3] Ensuring paper dataset..."
if [ ! -f "method/paper_code/vector_alignment_dataset/A1_A.pkl" ]; then
    echo "  Cloning paper repo..."
    git clone https://github.com/ARLab-VT/Robust-Vector-Set-Alignment method/paper_code
else
    echo "  Dataset already present."
fi

# Step 2: Run evaluation on paper's actual dataset
echo "[2/3] Running SPMC evaluation on paper's dataset..."
python3 scripts/run_experiment.py --n-rotations 100 --output scoring/scores.json

# Step 3: Report results
echo "[3/3] Results written to scoring/scores.json"
echo ""
echo "=========================================="
echo "Reproduction complete!"
echo "=========================================="
