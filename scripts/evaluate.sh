#!/bin/bash
# Evaluation script — aggregates method results into scoring/scores.json.
#
# This calls the method-specific evaluation (run_experiment.py) which generates
# raw results, then calls the method-agnostic aggregator (eval/evaluate.py).
#
# Usage:
#   bash scripts/evaluate.sh                       # full 100-rotation evaluation
#   bash scripts/evaluate.sh --n-rotations 20      # quick test with fewer rotations

set -e
cd /home/user

mkdir -p scoring

# Step 1: Run method evaluation (generates scoring/raw_results.json)
echo "Running method evaluation..."
python3 scripts/run_experiment.py \
    --n-rotations "${N_ROTATIONS:-100}" \
    --output scoring/scores.json

# Step 2: Run method-agnostic aggregator
echo "Aggregating results..."
python3 eval/evaluate.py \
    --input scoring/raw_results.json \
    --output scoring/scores.json

echo ""
echo "Evaluation complete. Results in scoring/scores.json"
