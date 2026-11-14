#!/bin/bash
# Train (visible) evaluation. Runs EVERY method registered on disk (each
# method/*.py that defines a METHODS dict) on the public instances - the
# paper's released dataset and rotations - and writes scoring/scores_train.json.
# Same interface, metrics, failure rules and CPU budget as the hidden test.
#
# Optional environment overrides:
#   METHOD_DIR           directory of registry modules        (default: method)
#   SCORES_OUTPUT        output file                          (default: scoring/scores_train.json)
#   PER_INSTANCE_OUTPUT  also dump per-instance errors (analysis only)

set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd):/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"

python3 eval/train/evaluate.py \
    --method-dir "${METHOD_DIR:-method}" \
    --output "${SCORES_OUTPUT:-scoring/scores_train.json}"
