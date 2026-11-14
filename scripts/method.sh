#!/bin/bash
# Run the paper's methods (SPMC, FRS, SPMC+FRS; registered in
# method/spherical_registration.py) through the public train evaluator.
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/evaluate_train.sh
