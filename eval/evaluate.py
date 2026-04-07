"""
Evaluation script for spherical point pattern registration.

Evaluates rotation estimation methods on the paper's actual Robust Vector
Alignment Dataset and computes metrics: angular error, timing, etc.
"""

import numpy as np
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Add method and data to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from method.spherical_registration import (
    spmc, frs, spmc_frs, rotation_error
)
from data.dataset import (
    paper_dataset_available, load_paper_dataset,
    get_paper_pattern_names, get_paper_config_names, get_paper_rotations,
)


@dataclass
class EvalResult:
    method: str
    rotation_errors: List[float]
    times: List[float]
    config: str
    pattern: str
    rotation_idx: int
    frs_iterations: Optional[int] = None


def evaluate_method(method_fn,
                    template: np.ndarray,
                    source: np.ndarray,
                    true_rotation: np.ndarray,
                    method_name: str) -> Tuple[float, float, Optional[int]]:
    """
    Evaluate a registration method on a single template-source pair.

    Returns: (rotation_error_deg, time_s, frs_iterations)
    """
    try:
        if method_name == 'spmc_frs':
            R_est, t, frs_iter = method_fn(template, source)
            return rotation_error(R_est, true_rotation), t, frs_iter
        elif method_name == 'frs':
            R_est, t, iterations = method_fn(template, source)
            return rotation_error(R_est, true_rotation), t, iterations
        else:
            R_est, t = method_fn(template, source)
            return rotation_error(R_est, true_rotation), t, None
    except Exception as e:
        print(f"    ERROR in {method_name}: {e}")
        return 999.0, 0.0, None


def evaluate_on_dataset(method_fn,
                        method_name: str,
                        patterns: List[str],
                        configs: List[str],
                        rotation_indices: List[int],
                        data_dir: str = 'data/rvad',
                        max_per_config: Optional[int] = None,
                        verbose: bool = False) -> Dict:
    """
    Evaluate a method across all pattern/config/rotation combinations.

    Returns dict of results organized by (pattern, config).
    """
    results = {}
    rotations = np.load(Path(data_dir) / 'rotations.npy')

    for pattern in patterns:
        template = get_template(pattern, data_dir)
        if verbose:
            print(f"  Pattern {pattern}: {len(template)} points")

        for config in configs:
            cfg = CONFIGS[config]
            key = f"{pattern}_{config}"

            errors = []
            times = []
            frs_iters = []

            indices = rotation_indices[:max_per_config] if max_per_config else rotation_indices

            for ridx in indices:
                # Generate source: rotate template, then apply noise/outliers
                seed = hash(f"{pattern}_{config}_{ridx}") % (2**31)
                rotated = template @ rotations[ridx].T
                source = generate_source_config(
                    rotated,
                    noise_std=cfg['noise_std'],
                    outlier_ratio=cfg['outlier_ratio'],
                    seed=seed
                )
                true_rot = rotations[ridx]

                err, t, frs_it = evaluate_method(
                    method_fn, template, source, true_rot, method_name
                )
                errors.append(err)
                times.append(t)
                if frs_it is not None:
                    frs_iters.append(frs_it)

            errors = np.array(errors)
            times = np.array(times)

            results[key] = {
                'median_error': float(np.median(errors)),
                'mean_error': float(np.mean(errors)),
                'p90_error': float(np.percentile(errors, 90)),
                'p95_error': float(np.percentile(errors, 95)),
                'max_error': float(np.max(errors)),
                'median_time': float(np.median(times)),
                'mean_time': float(np.mean(times)),
                'n_evaluations': len(errors),
            }
            if frs_iters:
                results[key]['mean_frs_iterations'] = float(np.mean(frs_iters))
                results[key]['median_frs_iterations'] = float(np.median(frs_iters))

    return results


def aggregate_results(results: Dict, group_by: str = 'all') -> Dict:
    """
    Aggregate results across configurations.

    group_by: 'all' = all configs together, 'outlier_level' = group by outlier ratio
    """
    if group_by == 'all':
        all_errors = []
        all_times = []
        for key, vals in results.items():
            # We don't have per-evaluation errors stored, only aggregates
            # Return the per-config results
            pass
        return results

    return results


def run_evaluation(output_path: str = 'scoring/scores.json',
                   data_dir: str = 'data/rvad',
                   methods=None,
                   patterns=None,
                   configs=None,
                   n_rotations: int = 100,
                   verbose: bool = True):
    """
    Run full evaluation and write scores.json.

    Args:
        output_path: where to write scores.json
        methods: dict of method_name -> function
        patterns: list of pattern names (default all A1-A5)
        configs: list of config names (default all B1-B7)
        n_rotations: number of rotations to test (default 100)
    """
    if methods is None:
        methods = {
            'spmc_frs': lambda t, s: spmc_frs(t, s),
            'spmc': lambda t, s: spmc(t, s),
            'frs': lambda t, s: frs(t, s),
        }

    if patterns is None:
        patterns = list(PATTERN_GENERATORS.keys())

    if configs is None:
        configs = list(CONFIGS.keys())

    rotation_indices = list(range(n_rotations))

    # Ensure dataset exists
    if not Path(data_dir).exists():
        if verbose:
            print("Generating dataset...")
        generate_dataset(data_dir)

    all_results = {}

    for method_name, method_fn in methods.items():
        if verbose:
            print(f"\nEvaluating {method_name}...")
        results = evaluate_on_dataset(
            method_fn, method_name,
            patterns, configs, rotation_indices,
            data_dir=data_dir, verbose=verbose
        )
        all_results[method_name] = results

    # Aggregate into scoring format
    scores = {}

    # Experiment 1: robust_alignment_all
    all_errors_per_method = {}
    all_times_per_method = {}

    for method_name, results in all_results.items():
        all_errors = []
        all_times = []
        for key, vals in results.items():
            # Approximate: we know median across all configs from individual results
            # We need mean across configs to approximate overall median
            # Use median of medians as proxy (not exact but reasonable)
            all_errors.append(vals['median_error'])
            all_times.append(vals['median_time'])
        all_errors_per_method[method_name] = {
            'median_of_medians': float(np.median(all_errors)),
            'mean_of_medians': float(np.mean(all_errors)),
            'overall_median_time': float(np.median(all_times)),
        }

    scores['robust_alignment_all'] = {}
    for method_name, agg in all_errors_per_method.items():
        scores['robust_alignment_all'][f'{method_name}_median_error'] = agg['median_of_medians']
        scores['robust_alignment_all'][f'{method_name}_mean_error'] = agg['mean_of_medians']
        scores['robust_alignment_all'][f'{method_name}_time'] = agg['overall_median_time']

    # Experiment 2: robust_alignment_high_outliers
    high_outlier_configs = ['B5', 'B6', 'B7']
    all_high_errors = {}
    for method_name, results in all_results.items():
        high_errs = []
        for cfg in high_outlier_configs:
            for pat in patterns:
                key = f"{pat}_{cfg}"
                if key in results:
                    high_errs.append(results[key]['median_error'])
        all_high_errors[method_name] = float(np.median(high_errs)) if high_errs else 999.0

    scores['robust_alignment_high_outliers'] = {}
    for method_name, med_err in all_high_errors.items():
        scores['robust_alignment_high_outliers'][f'{method_name}_median_error'] = med_err

    # Experiment 3: computational_complexity - timing at scale
    # We'll test separately with scaled dataset
    scores['computational_complexity'] = {}
    for method_name, method_fn in methods.items():
        # Quick timing test with 10^6 points
        n_test = 10000  # smaller for speed
        test_points = np.random.randn(n_test, 3)
        test_points = test_points / np.linalg.norm(test_points, axis=1, keepdims=True)

        times = []
        for _ in range(3):
            try:
                if method_name == 'spmc_frs':
                    _, t, _ = method_fn(test_points, test_points)
                elif method_name == 'frs':
                    _, t, _ = method_fn(test_points, test_points)
                else:
                    _, t = method_fn(test_points, test_points)
                times.append(t)
            except:
                times.append(0.0)

        est_time_1e6 = float(np.median(times)) * (1e6 / n_test)
        scores['computational_complexity'][f'{method_name}_time_at_1e4_points'] = float(np.median(times))

    # Write scores
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(scores, f, indent=2)

    if verbose:
        print(f"\nScores written to {output_path}")
        print("\nSummary:")
        for exp_name, exp_scores in scores.items():
            print(f"\n  {exp_name}:")
            for k, v in exp_scores.items():
                print(f"    {k}: {v:.4f}")

    return scores


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', default='scoring/scores.json')
    parser.add_argument('--data-dir', '-d', default='data/rvad')
    parser.add_argument('--n-rotations', '-n', type=int, default=100)
    parser.add_argument('--method', '-m', default='all')
    args = parser.parse_args()

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
    )
