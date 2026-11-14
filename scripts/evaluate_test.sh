#!/bin/bash
# Hidden test. Runs EVERY method registered on disk (each method/*.py that
# defines a METHODS dict) on secret instances generated inside eval/test/, and
# writes scoring/scores_test.json. Takes no arguments.
#
# Optional environment overrides (not used by the official run):
#   METHOD_DIR           directory of registry modules        (default: method)
#   SCORES_OUTPUT        output file                          (default: scoring/scores_test.json)
#   PER_INSTANCE_OUTPUT  also dump per-instance errors (analysis only)

set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd):/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"

python3 eval/test/evaluate.py \
    --method-dir "${METHOD_DIR:-method}" \
    --output "${SCORES_OUTPUT:-scoring/scores_test.json}"
