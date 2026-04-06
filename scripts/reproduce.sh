#!/bin/bash
# Reproduce the paper's results end-to-end.
#
# This script runs inside the compute container and should:
#   1. Generate the synthetic dataset
#   2. Run the paper's method (SPMC, FRS, SPMC+FRS)
#   3. Run the baseline
#   4. Run evaluation and write scoring/scores.json
#
# Assumes:
#   - Container is built
#   - Working directory is /home/user

set -e
cd /home/user

echo "=========================================="
echo "End-to-End Reproduction"
echo "=========================================="

# Step 1: Ensure dataset
echo "[1/4] Generating dataset..."
python -c "from data.dataset import generate_dataset; generate_dataset('data/rvad')"

# Step 2: Run the paper's methods
echo "[2/4] Running paper's methods..."
python scripts/run_experiment.py

# Step 3: Run baseline
echo "[3/4] Running baseline..."
bash scripts/baseline.sh || true

# Step 4: Evaluate
echo "[4/4] Evaluating..."
bash scripts/evaluate.sh

echo ""
echo "=========================================="
echo "Reproduction complete!"
echo "Results: scoring/scores.json"
echo "=========================================="
