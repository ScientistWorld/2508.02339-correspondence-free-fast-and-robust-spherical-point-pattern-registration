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

# Compute nodes have no internet. All assets must exist before submission.
if [ ! -f "method/paper_code/vector_alignment_dataset/A1_A.pkl" ]; then
    echo "ERROR: paper dataset missing at method/paper_code/vector_alignment_dataset/"
    exit 1
fi

# Run configurable evaluation; default to a 20-rotation validation pass.
N_ROTATIONS="${N_ROTATIONS:-20}"
echo "Running evaluation (SPMC, FRS, SPMC+FRS) on 5 patterns x 7 configs x ${N_ROTATIONS} rotations..."
python3 scripts/run_experiment.py --n-rotations "${N_ROTATIONS}" --output scoring/scores.json

echo ""
echo "=========================================="
echo "All done! Results in scoring/scores.json"
echo "=========================================="
