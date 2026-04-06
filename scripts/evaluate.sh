#!/bin/bash
# Evaluation script — evaluates rotation estimation methods and writes scoring/scores.json.
#
# Design: evaluates methods using the synthetic spherical dataset.
# Outputs: scoring/scores.json with per-experiment, per-method metrics.
#
# Usage:
#   bash scripts/evaluate.sh                       # full evaluation
#   bash scripts/evaluate.sh --method spmc_frs     # single method
#   bash scripts/evaluate.sh --n-rotations 20       # quick test with fewer rotations

set -e
cd /home/user

mkdir -p scoring

python -c "
import sys
sys.path.insert(0, '.')
from eval.evaluate import run_evaluation

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--output', '-o', default='scoring/scores.json')
parser.add_argument('--data-dir', '-d', default='data/rvad')
parser.add_argument('--n-rotations', '-n', type=int, default=100)
parser.add_argument('--method', '-m', default='all')
args = parser.parse_args()

from method.spherical_registration import spmc, frs, spmc_frs

methods = {
    'spmc_frs': lambda t, s: spmc_frs(t, s),
    'spmc': lambda t, s: spmc(t, s),
    'frs': lambda t, s: frs(t, s),
}

if args.method != 'all':
    methods = {args.method: methods[args.method]}

run_evaluation(
    output_path=args.output,
    data_dir=args.data_dir,
    methods=methods,
    n_rotations=args.n_rotations,
    verbose=True
)
"
