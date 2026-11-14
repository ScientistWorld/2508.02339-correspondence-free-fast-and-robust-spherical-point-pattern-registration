#!/bin/bash
# Score the simple correspondence-free baselines in baseline/baselines.py
# (identity, principal-axes moment matching) with the train evaluator.
# Output: outputs/scores_baseline_train.json (not a ranked artifact).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p outputs
METHOD_DIR=baseline SCORES_OUTPUT="${SCORES_OUTPUT:-outputs/scores_baseline_train.json}" \
    bash scripts/evaluate_train.sh
