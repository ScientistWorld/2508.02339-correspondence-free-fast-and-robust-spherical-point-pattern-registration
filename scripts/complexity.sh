#!/bin/bash
# UNSCORED diagnostic: the paper's runtime-scaling study (Fig. 6) on A3/B3
# resampled to 1e3..1e7 points, 20 rotations. Wall-clock times depend on the
# machine, so they are reported to outputs/complexity_timing.json only and are
# never part of a ranked score.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd):/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
mkdir -p outputs
python3 scripts/run_complexity_experiment.py \
    --scales "${COMPLEXITY_SCALES:-1000,10000,100000,1000000,10000000}" \
    --n-rotations "${COMPLEXITY_ROTATIONS:-20}" \
    --output "${COMPLEXITY_OUTPUT:-outputs/complexity_timing.json}"
