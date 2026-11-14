#!/bin/bash
# Score every registered method on the public benchmark (the train evaluator)
# and write scoring/scores.json (same content as scores_train.json).
set -euo pipefail
cd "$(dirname "$0")/.."
SCORES_OUTPUT="${SCORES_OUTPUT:-scoring/scores.json}" bash scripts/evaluate_train.sh
