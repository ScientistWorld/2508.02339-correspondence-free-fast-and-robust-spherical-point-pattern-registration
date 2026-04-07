#!/bin/bash
# Evaluation script — evaluates rotation estimation methods and writes scoring/scores.json.
#
# Uses the paper's actual Robust Vector Alignment Dataset (method/paper_code/).
# The dataset is cloned by scripts/download.sh and mounted from the workspace.
#
# Usage:
#   bash scripts/evaluate.sh                       # full 100-rotation evaluation
#   bash scripts/evaluate.sh --n-rotations 20      # quick test with fewer rotations

set -e
cd /home/user

mkdir -p scoring

# Run the evaluation (uses paper's actual dataset)
python3 scripts/run_experiment.py \
    --n-rotations "${N_ROTATIONS:-100}" \
    --output scoring/scores.json

echo ""
echo "Evaluation complete. Results in scoring/scores.json"
