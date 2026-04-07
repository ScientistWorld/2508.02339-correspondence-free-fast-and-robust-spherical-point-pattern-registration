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

# Ensure paper dataset is available
if [ ! -f "method/paper_code/vector_alignment_dataset/A1_A.pkl" ]; then
    echo "Paper dataset not found. Cloning..."
    git clone https://github.com/ARLab-VT/Robust-Vector-Set-Alignment method/paper_code
fi

# Run full 100-rotation evaluation
echo "Running SPMC evaluation (5 patterns x 7 configs x 100 rotations = 3500 evals)..."
python3 scripts/run_experiment.py --n-rotations 100 --output scoring/scores.json

echo ""
echo "=========================================="
echo "All done! Results in scoring/scores.json"
echo "=========================================="
