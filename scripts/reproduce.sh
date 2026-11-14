#!/bin/bash
# Reproduce the reference end to end (CPU only, no internet needed once
# scripts/download.sh has been run):
#   1. verify the downloaded public assets
#   2. run SPMC / FRS / SPMC+FRS through the public train evaluator
#   3. run them through the hidden test
#   4. optionally (RUN_COMPLEXITY=1) the unscored Fig. 6 timing diagnostic
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd):/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"

for required in data/downloads/vector_alignment_dataset/A1_A.pkl \
                data/downloads/vector_alignment_dataset/RandomRotation100.pkl \
                data/downloads/world_geojson/world.geojson; do
    if [ ! -f "$required" ]; then
        echo "ERROR: missing $required - run scripts/download.sh first" >&2
        exit 1
    fi
done

echo "[1/3] Train evaluation (released dataset) -> scoring/scores_train.json"
bash scripts/evaluate_train.sh
cp scoring/scores_train.json scoring/scores.json

echo "[2/3] Hidden test -> scoring/scores_test.json"
bash scripts/evaluate_test.sh

if [ "${RUN_COMPLEXITY:-0}" = "1" ]; then
    echo "[3/3] Unscored runtime-scaling diagnostic (paper Fig. 6)"
    bash scripts/complexity.sh
else
    echo "[3/3] Skipping unscored runtime diagnostic (set RUN_COMPLEXITY=1)"
fi
python3 validate.py
