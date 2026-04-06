#!/bin/bash
# Run baseline methods for comparison.
#
# Baseline: identity rotation (no registration) — worst-case reference.
# Median error should be ~57 degrees (random guess over SO(3)).
#
# Usage:
#   bash scripts/baseline.sh

set -e
cd /home/user

echo "Running baseline (identity rotation)..."

python3 -c "
import sys
import numpy as np
import json
from pathlib import Path
sys.path.insert(0, '.')
from data.dataset import CONFIGS, PATTERN_GENERATORS, get_template, get_rotations, generate_source_config
from method.spherical_registration import rotation_error

patterns = list(PATTERN_GENERATORS.keys())
configs = list(CONFIGS.keys())
rotations = get_rotations('data/rvad')
n_rotations = len(rotations)

# Baseline: identity rotation (no registration at all)
errors_per_config = {}
for pattern in patterns:
    template = get_template(pattern, 'data/rvad')
    for config in configs:
        cfg = CONFIGS[config]
        key = f'{pattern}_{config}'
        errs = []
        for ridx in range(n_rotations):
            seed = hash(f'{pattern}_{config}_{ridx}') % (2**31)
            rotated = template @ rotations[ridx].T
            source = generate_source_config(rotated, noise_std=cfg['noise_std'],
                                            outlier_ratio=cfg['outlier_ratio'], seed=seed)
            true_rot = rotations[ridx]
            # Identity rotation = no registration at all
            err = rotation_error(np.eye(3), true_rot)
            errs.append(err)
        errs = np.array(errs)
        errors_per_config[key] = {
            'median_error': float(np.median(errs)),
            'mean_error': float(np.mean(errs)),
            'p90_error': float(np.percentile(errs, 90)),
        }
        print(f'  {key}: median={errors_per_config[key][\"median_error\"]:.2f} deg, p90={errors_per_config[key][\"p90_error\"]:.2f} deg')

# Aggregate
all_medians = [v['median_error'] for v in errors_per_config.values()]
all_means = [v['mean_error'] for v in errors_per_config.values()]

scores = {
    'experiments': {
        'robust_alignment_all': {
            'results': {
                'identity_baseline': {
                    'median_rotation_error_deg': float(np.median(all_medians)),
                    'mean_rotation_error_deg': float(np.mean(all_means)),
                    'median_time_s': 0.0,
                }
            }
        },
        'robust_alignment_high_outliers': {
            'results': {
                'identity_baseline': {
                    'median_rotation_error_deg': float(np.median(all_medians)),
                    'p90_rotation_error_deg': float(np.percentile(all_medians, 90)),
                }
            }
        },
        'computational_complexity': {
            'results': {
                'identity_baseline': {
                    'time_at_1e6_points_s': 0.0,
                    'time_at_1e7_points_s': 0.0,
                }
            }
        }
    }
}

Path('scoring/scores.json').parent.mkdir(parents=True, exist_ok=True)
with open('scoring/scores.json', 'w') as f:
    json.dump(scores, f, indent=2)

print(f'Baseline results written to scoring/scores.json')
print(f'Overall median error: {np.median(all_medians):.2f} deg (random baseline ~57 deg)')
"
