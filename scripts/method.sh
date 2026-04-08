#!/bin/bash
# Run the paper's proposed method (SPMC+FRS).
#
# Usage:
#   bash scripts/method.sh

set -euo pipefail
cd /home/user

N_ROTATIONS="${N_ROTATIONS:-100}"

echo "Running paper methods on the Robust Vector Alignment Dataset..."
python3 scripts/run_experiment.py --n-rotations "${N_ROTATIONS}"

echo "Re-aggregating scores with the method-agnostic evaluator..."
bash scripts/evaluate.sh

echo "Method evaluation complete."
