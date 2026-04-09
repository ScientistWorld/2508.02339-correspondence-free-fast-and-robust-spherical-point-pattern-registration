#!/usr/bin/env python3
"""
Evaluation of SPMC, FRS, and SPMC+FRS on the paper's Robust Vector Alignment Dataset.

Paper: "Correspondence-Free Fast and Robust Spherical Point Pattern Registration"
(arXiv: 2508.02339)

Runs the paper methods on the paper's actual dataset and writes raw_results.json.
The canonical scores.json is produced by eval/evaluate.py.
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


def _save_raw_results(raw_results: dict, output_path: Path) -> None:
    """Persist raw results incrementally so partial progress survives interruptions."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_save = {}
    for method_name, method_results in raw_results.items():
        raw_save[method_name] = {}
        for key, values in method_results.items():
            raw_save[method_name][key] = {
                "errors": [float(err) for err in values["errors"]],
                "times": [float(t) for t in values["times"]],
            }
    with output_path.open("w") as handle:
        json.dump(raw_save, handle)


def run_evaluation(
    n_rotations: int = 100,
    rotation_start: int = 0,
    raw_output: str = "scoring/raw_results.json",
    verbose: bool = True,
) -> dict:
    """Run SPMC, FRS, and SPMC+FRS on the paper dataset for a selected rotation slice."""
    dataset_dir = require_dataset()
    patterns = list(PATTERNS)
    configs = list(CONFIGS)

    rots = get_rotations()
    start_idx = max(0, rotation_start)
    end_idx = min(start_idx + n_rotations, len(rots))
    rot_subset = rots[start_idx:end_idx]
    n_rot = len(rot_subset)
    raw_path = Path(raw_output)

    if verbose:
        print(f"Loading dataset from {dataset_dir}...")
        print(
            f"Patterns: {patterns}, Configs: {configs}, "
            f"Rotations: {n_rot} (slice {start_idx}:{end_idx})"
        )

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

            for local_ridx, rotation in enumerate(rot_subset):
                count += 1
                if verbose and count % 1000 == 0:
                    elapsed = time.time() - t_start
                    eta_s = elapsed / count * (total - count)
                    print(f"  Progress: {count}/{total} ({100*count/total:.0f}%) ETA: {eta_s:.0f}s")

                template = templates_raw[pat]
                src_pkl = sources_raw[(pat, cfg)]
                R_test = rotation
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

            _save_raw_results(raw_results, raw_path)
            if verbose:
                completed = start_idx + local_ridx + 1 if n_rot else start_idx
                print(f"  Checkpointed {key}; processed rotations up to index {completed}")

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

    # Build a local summary for console reporting. The canonical scores.json is
    # written by eval/evaluate.py so we only summarize experiments we measured.
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
    }

    # Save raw per-eval results for eval/evaluate.py (method-agnostic aggregator)
    _save_raw_results(raw_results, raw_path)
    if verbose:
        print(f"Raw results saved to {raw_path}")

    # Strip "type" from the console summary so validator-style consumers would
    # only see metrics if this object is reused programmatically.
    scores_clean = {}
    for exp_name, exp in scores.items():
        clean_results = {}
        for method, vals in exp["results"].items():
            clean_results[method] = {k: v for k, v in vals.items() if k != "type"}
        scores_clean[exp_name] = {**exp, "results": clean_results}

    if verbose:
        print(f"\nOverall SPMC: median={scores_clean['robust_alignment_all']['results']['spmc']['median_rotation_error_deg']:.3f}deg "
              f"mean={scores_clean['robust_alignment_all']['results']['spmc']['mean_rotation_error_deg']:.3f}deg")
        print(f"High-outlier SPMC: median={scores_clean['robust_alignment_high_outliers']['results']['spmc']['median_rotation_error_deg']:.3f}deg "
              f"p90={scores_clean['robust_alignment_high_outliers']['results']['spmc']['p90_rotation_error_deg']:.3f}deg")

    return {"experiments": scores_clean}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-rotations", type=int, default=100)
    parser.add_argument("--rotation-start", type=int, default=0)
    parser.add_argument("--raw-output", type=str, default="scoring/raw_results.json")
    args = parser.parse_args()

    run_evaluation(
        n_rotations=args.n_rotations,
        rotation_start=args.rotation_start,
        raw_output=args.raw_output,
        verbose=True,
    )
