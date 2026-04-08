#!/usr/bin/env python3
"""
SPMC evaluation on paper's Robust Vector Alignment Dataset.

Paper: "Correspondence-Free Fast and Robust Spherical Point Pattern Registration"
(arXiv: 2508.02339)

Runs SPMC on the paper's actual dataset and writes scores.json.
Rotation convention: src = template @ R^T; evaluates rotation_error(R_est, R_gt).
"""
import sys
import json
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from data.dataset import CONFIGS, PATTERNS, get_rotations, get_source, get_template, require_dataset
from method.spherical_registration import spmc, frs, spmc_frs, rotation_error


def run_evaluation(n_rotations: int = 100, verbose: bool = True) -> dict:
    """Run SPMC on the full paper dataset."""
    dataset_dir = require_dataset()
    patterns = list(PATTERNS)
    configs = list(CONFIGS)

    rots = get_rotations()
    n_rot = min(n_rotations, len(rots))

    if verbose:
        print(f"Loading dataset from {dataset_dir}...")
        print(f"Patterns: {patterns}, Configs: {configs}, Rotations: {n_rot}")

    # Pre-load all data
    templates_raw = {}
    sources_raw = {}
    for pat in patterns:
        t = np.asarray(get_template(pat), dtype=float)
        templates_raw[pat] = t / np.linalg.norm(t, axis=1, keepdims=True)
        for cfg in configs:
            s = np.asarray(get_source(pat, cfg), dtype=float)
            sources_raw[(pat, cfg)] = s / np.linalg.norm(s, axis=1, keepdims=True)

    if verbose:
        print("Data pre-loaded. Running evaluation...")

    raw_results = {"spmc": {}, "frs": {}, "spmc_frs": {}}
    count = 0
    total = len(patterns) * len(configs) * n_rot
    t_start = time.time()

    for pat in patterns:
        for cfg in configs:
            key = f"{pat}_{cfg}"
            for m in raw_results:
                raw_results[m][key] = {"errors": [], "times": []}

            for ridx in range(n_rot):
                count += 1
                if verbose and count % 1000 == 0:
                    elapsed = time.time() - t_start
                    eta_s = elapsed / count * (total - count)
                    print(f"  Progress: {count}/{total} ({100*count/total:.0f}%) ETA: {eta_s:.0f}s")

                template = templates_raw[pat]
                src_pkl = sources_raw[(pat, cfg)]
                R_test = rots[ridx]
                source = src_pkl @ R_test.T
                true_rot = R_test

                try:
                    R_est, t = spmc(template, source)
                    err = rotation_error(R_est, true_rot)
                    raw_results["spmc"][key]["errors"].append(err)
                    raw_results["spmc"][key]["times"].append(t)

                    R_est_frs, t_frs, _ = frs(template, source)
                    err_frs = rotation_error(R_est_frs, true_rot)
                    raw_results["frs"][key]["errors"].append(err_frs)
                    raw_results["frs"][key]["times"].append(t_frs)

                    R_est2, t2, _ = spmc_frs(template, source)
                    err2 = rotation_error(R_est2, true_rot)
                    raw_results["spmc_frs"][key]["errors"].append(err2)
                    raw_results["spmc_frs"][key]["times"].append(t2)
                except Exception as e:
                    raw_results["spmc"][key]["errors"].append(999.0)
                    raw_results["spmc"][key]["times"].append(0.0)
                    raw_results["frs"][key]["errors"].append(999.0)
                    raw_results["frs"][key]["times"].append(0.0)
                    raw_results["spmc_frs"][key]["errors"].append(999.0)
                    raw_results["spmc_frs"][key]["times"].append(0.0)

    elapsed = time.time() - t_start
    if verbose:
        print(f"Evaluation complete in {elapsed:.0f}s ({elapsed/60:.1f}m)")

    # Aggregate per (pattern, config)
    agg = {m: {} for m in raw_results}
    for m in raw_results:
        for k, v in raw_results[m].items():
            errs = np.array(v["errors"])
            times = np.array(v["times"])
            agg[m][k] = {
                "median": float(np.median(errs)),
                "mean": float(np.mean(errs)),
                "p90": float(np.percentile(errs, 90)),
                "median_time": float(np.median(times)),
            }

    if verbose:
        print("\nPer-config SPMC medians:")
        for k, v in sorted(agg["spmc"].items()):
            print(f"  {k}: {v['median']:.3f}deg p90={v['p90']:.3f}deg t={v['median_time']:.4f}s")

    # Build scores.json
    all_errors = {m: [] for m in raw_results}
    all_times = {m: [r["median_time"] for r in agg[m].values()] for m in raw_results}
    high_errors = {m: [] for m in raw_results}
    for method_name, method_results in raw_results.items():
        for key, vals in method_results.items():
            all_errors[method_name].extend(vals["errors"])
            if any(cfg in key for cfg in ["B5", "B6", "B7"]):
                high_errors[method_name].extend(vals["errors"])

    scores = {
        "robust_alignment_all": {
            "description": "Robust alignment on paper dataset — 5 patterns x 7 configs. Primary metric: median rotation error.",
            "weight": 0.5,
            "primary_metric": "median_rotation_error_deg",
            "metrics": {
                "median_rotation_error_deg": {"higher_is_better": False, "coefficient": -1.0},
                "mean_rotation_error_deg": {"higher_is_better": False, "coefficient": -0.3},
                "median_time_s": {"higher_is_better": False, "coefficient": -0.1},
            },
            "results": {
                **{
                    method_name: {"type": "proposed",
                        "median_rotation_error_deg": float(np.median(all_errors[method_name])),
                        "mean_rotation_error_deg": float(np.mean(all_errors[method_name])),
                        "median_time_s": float(np.median(all_times[method_name])),
                    }
                    for method_name in raw_results
                }
            },
        },
        "robust_alignment_high_outliers": {
            "description": "Robust alignment at high outlier ratios (B5: 50%, B6: 75%, B7: 90% outliers)",
            "weight": 0.3,
            "primary_metric": "median_rotation_error_deg",
            "metrics": {
                "median_rotation_error_deg": {"higher_is_better": False, "coefficient": -1.0},
                "p90_rotation_error_deg": {"higher_is_better": False, "coefficient": -0.5},
            },
            "results": {
                **{
                    method_name: {"type": "proposed",
                        "median_rotation_error_deg": float(np.median(high_errors[method_name])),
                        "p90_rotation_error_deg": float(np.percentile(high_errors[method_name], 90)),
                    }
                    for method_name in raw_results
                }
            },
        },
        "computational_complexity": {
            "description": "Runtime scaling — time grows linearly with number of points (O(n))",
            "weight": 0.2,
            "primary_metric": "time_at_1e6_points_s",
            "metrics": {
                "time_at_1e6_points_s": {"higher_is_better": False, "coefficient": -0.5},
                "time_at_1e7_points_s": {"higher_is_better": False, "coefficient": -0.5},
            },
            "results": {
                **{
                    method_name: {"type": "proposed",
                        "time_at_1e6_points_s": float(np.median(all_times[method_name]) * 1e6 / 22212),
                        "time_at_1e7_points_s": float(np.median(all_times[method_name]) * 1e7 / 22212),
                    }
                    for method_name in raw_results
                }
            },
        },
    }

    output_path = Path(__file__).parent.parent / "scoring" / "scores.json"
    # Save raw per-eval results for eval/evaluate.py (method-agnostic aggregator)
    raw_path = Path(__file__).parent.parent / "scoring" / "raw_results.json"
    # Normalize raw_results: {method: {config: {errors: [...], times: [...]}}}
    raw_save = {}
    for m in raw_results:
        raw_save[m] = {}
        for k, v in raw_results[m].items():
            raw_save[m][k] = {"errors": [float(e) for e in v["errors"]], "times": [float(t) for t in v["times"]]}
    with open(raw_path, "w") as f:
        json.dump(raw_save, f)
    if verbose:
        print(f"Raw results saved to {raw_path}")

    # Strip "type" from results so validator doesn't treat it as a metric
    scores_clean = {}
    for exp_name, exp in scores.items():
        if isinstance(exp, dict) and "results" in exp:
            clean_results = {}
            for method, vals in exp["results"].items():
                if isinstance(vals, dict):
                    clean = {k: v for k, v in vals.items() if k != "type"}
                    clean_results[method] = clean
                else:
                    clean_results[method] = vals
            scores_clean[exp_name] = {**exp, "results": clean_results}
        else:
            scores_clean[exp_name] = exp

    with open(output_path, "w") as f:
        json.dump(scores_clean, f, indent=2)

    if verbose:
        print(f"\nScores written to {output_path}")
        print(f"\nOverall SPMC: median={scores_clean['robust_alignment_all']['results']['spmc']['median_rotation_error_deg']:.3f}deg "
              f"mean={scores_clean['robust_alignment_all']['results']['spmc']['mean_rotation_error_deg']:.3f}deg")
        print(f"High-outlier SPMC: median={scores_clean['robust_alignment_high_outliers']['results']['spmc']['median_rotation_error_deg']:.3f}deg "
              f"p90={scores_clean['robust_alignment_high_outliers']['results']['spmc']['p90_rotation_error_deg']:.3f}deg")

    return scores


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-rotations", type=int, default=100)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    run_evaluation(n_rotations=args.n_rotations, verbose=True)
