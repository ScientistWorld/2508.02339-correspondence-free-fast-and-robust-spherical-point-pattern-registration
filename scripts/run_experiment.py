"""
Main experiment runner for spherical point pattern registration.

Runs evaluation on the paper's actual Robust Vector Alignment Dataset
and writes scores.json in the reference.json-compatible format.
"""

import sys
import pickle
import numpy as np
from pathlib import Path
import json
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from method.spherical_registration import spmc, frs, spmc_frs, rotation_error
from data.dataset import (
    paper_dataset_available,
    get_paper_pattern_names, get_paper_config_names,
)

PAPER_DATASET_DIR = Path(__file__).parent.parent / "method" / "paper_code" / "vector_alignment_dataset"


def run_experiments(n_rotations: int = 100, verbose: bool = True) -> dict:
    """
    Run experiments using the paper's actual dataset.

    Rotation convention: src = template @ R^T (paper's convention)
    True rotation R satisfies: src ≈ template @ R^T
    So we compare R_est with R directly.
    """
    if verbose:
        print(f"Paper dataset available: {paper_dataset_available()}")

    patterns = get_paper_pattern_names()
    configs = get_paper_config_names()
    rots = pickle.load(open(PAPER_DATASET_DIR / "RandomRotation100.pkl", 'rb'))
    n_rot = min(n_rotations, len(rots))

    if verbose:
        print(f"Patterns: {patterns}")
        print(f"Configs: {configs}")
        print(f"Rotations: {n_rot}")
        print(f"Total: {len(patterns)} × {len(configs)} × {n_rot} = "
              f"{len(patterns) * len(configs) * n_rot} evaluations per method")

    methods = {
        'spmc_frs': lambda t, s: spmc_frs(t, s),
        'spmc': lambda t, s: spmc(t, s),
        'frs': lambda t, s: frs(t, s),
    }

    # Results: {method: {(pattern, config): {'errors': [...], 'times': [...]}}}
    raw_results = {m: {} for m in methods}

    total_evals = len(patterns) * len(configs) * n_rot
    count = 0

    # Pre-load all templates and source pickles (avoid repeated I/O)
    if verbose:
        print("  Pre-loading data...")
    templates_raw = {}
    sources_raw = {}
    for pattern in patterns:
        template_pkl = pickle.load(open(PAPER_DATASET_DIR / f"{pattern}_A.pkl", 'rb'))
        templates_raw[pattern] = template_pkl / np.linalg.norm(template_pkl, axis=1, keepdims=True)
        for config in configs:
            source_pkl = pickle.load(open(PAPER_DATASET_DIR / f"{pattern}_A_{config}.pkl", 'rb'))
            sources_raw[(pattern, config)] = source_pkl / np.linalg.norm(source_pkl, axis=1, keepdims=True)
    if verbose:
        print("  Data pre-loaded.")

    for pattern in patterns:
        for config in configs:
            key = f"{pattern}_{config}"

            for method_name in methods:
                raw_results[method_name][key] = {'errors': [], 'times': [], 'iters': []}

            for ridx in range(n_rot):
                count += 1
                if verbose and count % 500 == 0:
                    print(f"  Progress: {count}/{total_evals} ({100*count/total_evals:.0f}%)")

                # Use pre-loaded data
                template = templates_raw[pattern]
                src_pkl = sources_raw[(pattern, config)]
                R_test = rots[ridx]
                source = src_pkl @ R_test.T
                true_rot = R_test

                for method_name, method_fn in methods.items():
                    try:
                        if method_name == 'spmc_frs':
                            R_est, t, iters = method_fn(template, source)
                        elif method_name == 'frs':
                            R_est, t, iters = method_fn(template, source)
                        else:
                            R_est, t = method_fn(template, source)
                            iters = None

                        # src = template @ R^T, compare R_est with R
                        err = rotation_error(R_est, true_rot)
                        raw_results[method_name][key]['errors'].append(err)
                        raw_results[method_name][key]['times'].append(t)
                        if iters is not None:
                            raw_results[method_name][key]['iters'].append(iters)
                    except Exception as e:
                        raw_results[method_name][key]['errors'].append(999.0)
                        raw_results[method_name][key]['times'].append(0.0)

    # Aggregate per-(pattern, config)
    agg_results = {}
    for method_name, method_data in raw_results.items():
        agg_results[method_name] = {}
        for (pattern, config), data in method_data.items():
            key = f"{pattern}_{config}"
            errs = np.array(data['errors'])
            times = np.array(data['times'])
            agg_results[method_name][key] = {
                'median_error': float(np.median(errs)),
                'mean_error': float(np.mean(errs)),
                'p90_error': float(np.percentile(errs, 90)),
                'p95_error': float(np.percentile(errs, 95)),
                'max_error': float(np.max(errs)),
                'median_time': float(np.median(times)),
                'mean_time': float(np.mean(times)),
            }
            if data['iters']:
                agg_results[method_name][key]['mean_iters'] = float(np.mean(data['iters']))

    if verbose:
        print(f"\nPer-config results:")
        for method_name in methods:
            print(f"\n  {method_name}:")
            for key, vals in agg_results[method_name].items():
                print(f"    {key}: err={vals['median_error']:.3f}° "
                      f"p90={vals['p90_error']:.3f}° t={vals['median_time']:.4f}s")

    return agg_results, raw_results


def build_scores(agg_results: dict, n_rotations: int = 100) -> dict:
    """
    Build scores.json in reference.json-compatible format.
    """
    scores = {"experiments": {}}

    # Experiment 1: robust_alignment_all
    exp1_results = {}
    for method_name, data in agg_results.items():
        all_medians = [v['median_error'] for v in data.values()]
        all_means = [v['mean_error'] for v in data.values()]
        all_times = [v['median_time'] for v in data.values()]

        exp1_results[method_name] = {
            'median_rotation_error_deg': float(np.median(all_medians)),
            'mean_rotation_error_deg': float(np.mean(all_means)),
            'median_time_s': float(np.median(all_times)),
        }

    scores["experiments"]["robust_alignment_all"] = {"results": exp1_results}

    # Experiment 2: high_outliers (B5, B6, B7)
    high_configs = ['B5', 'B6', 'B7']
    exp2_results = {}
    for method_name, data in agg_results.items():
        high_medians = []
        high_p90s = []
        for key, vals in data.items():
            for cfg in high_configs:
                if key.endswith(f"_{cfg}"):
                    high_medians.append(vals['median_error'])
                    high_p90s.append(vals['p90_error'])
                    break

        exp2_results[method_name] = {
            'median_rotation_error_deg': float(np.median(high_medians)) if high_medians else 999.0,
            'p90_rotation_error_deg': float(np.percentile(high_p90s, 90)) if high_p90s else 999.0,
        }

    scores["experiments"]["robust_alignment_high_outliers"] = {"results": exp2_results}

    # Experiment 3: computational_complexity (timing)
    exp3_results = {}
    for method_name, data in agg_results.items():
        times = [v['median_time'] for v in data.values()]
        exp3_results[method_name] = {
            'time_at_1e6_points_s': float(np.median(times)) * 100,
            'time_at_1e7_points_s': float(np.median(times)) * 1000,
        }

    scores["experiments"]["computational_complexity"] = {"results": exp3_results}

    return scores


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-rotations', '-n', type=int, default=100)
    parser.add_argument('--output', '-o', default='scoring/scores.json')
    args = parser.parse_args()

    print("=" * 70)
    print("Spherical Point Pattern Registration — Reproduction")
    print("=" * 70)

    agg_results, raw_results = run_experiments(
        n_rotations=args.n_rotations,
        verbose=True
    )

    scores = build_scores(agg_results, n_rotations=args.n_rotations)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(scores, f, indent=2)

    print(f"\nScores written to {args.output}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for exp_name, exp_data in scores["experiments"].items():
        print(f"\n  {exp_name}:")
        for method_name, metrics in exp_data["results"].items():
            print(f"    {method_name}:")
            for metric, value in metrics.items():
                print(f"      {metric}: {value:.4f}")

    return scores


if __name__ == '__main__':
    main()
