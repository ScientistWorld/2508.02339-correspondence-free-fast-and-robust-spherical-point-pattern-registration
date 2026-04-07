#!/bin/bash
# Job script for spherical point pattern registration.
#
# This runs inside the compute container with:
#   - Workspace mounted at /home/user
#   - numpy available via setup.sh
#   - Paper dataset at /home/user/method/paper_code/vector_alignment_dataset/

set -e
cd /home/user

echo "=========================================="
echo "Spherical Point Pattern Registration"
echo "=========================================="

# Ensure paper dataset is available (method/paper_code should be mounted from workspace)
if [ ! -f "method/paper_code/vector_alignment_dataset/A1_A.pkl" ]; then
    echo "Paper dataset not found. Cloning..."
    git clone https://github.com/ARLab-VT/Robust-Vector-Set-Alignment method/paper_code
fi

# Run experiments
echo "[1/2] Running experiments (SPMC, FRS, SPMC+FRS)..."
python3 scripts/run_experiment.py --n-rotations 100 --output scoring/scores.json

# Run baseline
echo "[2/2] Running baseline..."
bash scripts/baseline.sh || true

echo ""
echo "=========================================="
echo "All done! Results in scoring/scores.json"
echo "=========================================="
