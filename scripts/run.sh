#!/bin/bash
# Job script for spherical point pattern registration.
#
# This runs inside the compute container with:
#   - Workspace mounted at /home/user
#   - numpy available via setup.sh
#   - CPU-only computation (O(n) algorithms)

set -e
cd /home/user

echo "=========================================="
echo "Spherical Point Pattern Registration"
echo "=========================================="

# Generate dataset
echo "[1/4] Generating dataset..."
python3 -c "from data.dataset import generate_dataset; generate_dataset('data/rvad')"

# Run experiments
echo "[2/4] Running experiments (SPMC, FRS, SPMC+FRS)..."
python3 scripts/run_experiment.py

# Run baseline
echo "[3/4] Running baseline..."
bash scripts/baseline.sh || true

# Final evaluation
echo "[4/4] Final evaluation..."
bash scripts/evaluate.sh

echo ""
echo "=========================================="
echo "All done! Results in scoring/scores.json"
echo "=========================================="
