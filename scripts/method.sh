#!/bin/bash
# Run the paper's proposed method (SPMC+FRS).
#
# Usage:
#   bash scripts/method.sh

set -e
cd /home/user

echo "Running SPMC+FRS method..."
python scripts/run_experiment.py --method spmc_frs 2>/dev/null || python -c "
import sys
sys.path.insert(0, '.')
from eval.evaluate import run_evaluation
from method.spherical_registration import spmc_frs

run_evaluation(
    output_path='scoring/scores.json',
    data_dir='data/rvad',
    methods={'spmc_frs': lambda t, s: spmc_frs(t, s)},
    n_rotations=100,
    verbose=True
)
"

echo "Method evaluation complete."
