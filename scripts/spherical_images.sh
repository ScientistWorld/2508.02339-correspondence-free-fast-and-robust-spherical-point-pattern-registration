#!/bin/bash
# Run the paper's spherical-image adaptation benchmark.

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONPATH="/home/user${PYTHONPATH:+:${PYTHONPATH}}"

N_ROTATIONS="${N_ROTATIONS:-100}"
RAW_SPHERICAL_IMAGE_RESULTS="${RAW_SPHERICAL_IMAGE_RESULTS:-scoring/raw_spherical_image_results.json}"
SCORES_OUTPUT="${SCORES_OUTPUT:-scoring/scores.json}"

echo "Running spherical-image benchmark on the released R100 rotations..."
python3 scripts/run_spherical_image_experiment.py \
    --n-rotations "${N_ROTATIONS}" \
    --output "${RAW_SPHERICAL_IMAGE_RESULTS}"

echo "Re-aggregating scores with the method-agnostic evaluator..."
RAW_SPHERICAL_IMAGE_RESULTS="${RAW_SPHERICAL_IMAGE_RESULTS}" \
SCORES_OUTPUT="${SCORES_OUTPUT}" \
    bash scripts/evaluate.sh

echo "Spherical-image evaluation complete."
