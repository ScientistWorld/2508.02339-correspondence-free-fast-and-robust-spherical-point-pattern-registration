#!/usr/bin/env python3
"""
SPMC evaluation on paper's Robust Vector Alignment Dataset.

Paper: "Correspondence-Free Fast and Robust Spherical Point Pattern Registration"
(arXiv: 2508.02339)

Runs SPMC on the paper's actual dataset and writes scores.json.
Rotation convention: src = template @ R^T; evaluates rotation_error(R_est, R_gt).
"""
import sys
import pickle
import json
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from method.spherical_registration import spmc, spmc_frs, rotation_error

DATASET_DIR = Path(__file__).parent.parent / "method" / "paper_code" / "vector_alignment_dataset"


def run_evaluation(n_rotations: int = 100, verbose: bool = True) -> dict:
    """Run SPMC on the full paper dataset."""
    patterns = ["A1", "A2", "A3", "A4", "A5"]
    configs = ["B1", "B2", "B3", "B4", "B5", "B6", "B7"]

    rots = pickle.load(open(DATASET_DIR / "RandomRotation100.pkl", "rb"))
    n_rot = min(n_rotations, len(rots))

    if verbose:
        print(f"Loading dataset from {DATASET_DIR}...")
        print(f"Patterns: {patterns}, Configs: {configs}, Rotations: {n_rot}")

    # Pre-load all data
    templates_raw = {}
    sources_raw = {}
    for pat in patterns:
        t = pickle.load(open(DATASET_DIR / f"{pat}_A.pkl", "rb"))
        templates_raw[pat] = t / np.linalg.norm(t, axis=1, keepdims=True)
        for cfg in configs:
            s = pickle.load(open(DATASET_DIR / f"{pat}_A_{cfg}.pkl", "rb"))
            sources_raw[(pat, cfg)] = s / np.linalg.norm(s, axis=1, keepdims=True)

    if verbose:
        print("Data pre-loaded. Running evaluation...")

    raw_results = {"spmc": {}, "spmc_frs": {}}
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

                    R_est2, t2, _ = spmc_frs(template, source)
                    err2 = rotation_error(R_est2, true_rot)
                    raw_results["spmc_frs"][key]["errors"].append(err2)
                    raw_results["spmc_frs"][key]["times"].append(t2)
                except Exception as e:
                    raw_results["spmc"][key]["errors"].append(999.0)
                    raw_results["spmc"][key]["times"].append(0.0)
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
    all_spmc = []
    all_spmc_frs = []
    for k in raw_results["spmc"]:
        all_spmc.extend(raw_results["spmc"][k]["errors"])
        all_spmc_frs.extend(raw_results["spmc_frs"][k]["errors"])

    all_times_spmc = [r["median_time"] for r in agg["spmc"].values()]
    all_times_spmc_frs = [r["median_time"] for r in agg["spmc_frs"].values()]

    high_spmc = []
    high_spmc_frs = []
    for k in raw_results["spmc"]:
        if any(cfg in k for cfg in ["B5", "B6", "B7"]):
            high_spmc.extend(raw_results["spmc"][k]["errors"])
            high_spmc_frs.extend(raw_results["spmc_frs"][k]["errors"])

    scores = {
        "experiments": {
            "robust_alignment_all": {
                "results": {
                    "spmc": {
                        "median_rotation_error_deg": float(np.median(all_spmc)),
                        "mean_rotation_error_deg": float(np.mean(all_spmc)),
                        "median_time_s": float(np.median(all_times_spmc)),
                    },
                    "spmc_frs": {
                        "median_rotation_error_deg": float(np.median(all_spmc_frs)),
                        "mean_rotation_error_deg": float(np.mean(all_spmc_frs)),
                        "median_time_s": float(np.median(all_times_spmc_frs)),
                    },
                }
            },
            "robust_alignment_high_outliers": {
                "results": {
                    "spmc": {
                        "median_rotation_error_deg": float(np.median(high_spmc)),
                        "p90_rotation_error_deg": float(np.percentile(high_spmc, 90)),
                    },
                    "spmc_frs": {
                        "median_rotation_error_deg": float(np.median(high_spmc_frs)),
                        "p90_rotation_error_deg": float(np.percentile(high_spmc_frs, 90)),
                    },
                }
            },
            "computational_complexity": {
                "results": {
                    "spmc": {
                        "time_at_1e6_points_s": float(np.median(all_times_spmc) * 1e6 / 22212),
                        "time_at_1e7_points_s": float(np.median(all_times_spmc) * 1e7 / 22212),
                    },
                    "spmc_frs": {
                        "time_at_1e6_points_s": float(np.median(all_times_spmc_frs) * 1e6 / 22212),
                        "time_at_1e7_points_s": float(np.median(all_times_spmc_frs) * 1e7 / 22212),
                    },
                }
            },
        }
    }

    output_path = Path(__file__).parent.parent / "scoring" / "scores.json"
    with open(output_path, "w") as f:
        json.dump(scores, f, indent=2)

    if verbose:
        print(f"\nScores written to {output_path}")
        print(f"\nOverall SPMC: median={scores['experiments']['robust_alignment_all']['results']['spmc']['median_rotation_error_deg']:.3f}deg "
              f"mean={scores['experiments']['robust_alignment_all']['results']['spmc']['mean_rotation_error_deg']:.3f}deg")
        print(f"High-outlier SPMC: median={scores['experiments']['robust_alignment_high_outliers']['results']['spmc']['median_rotation_error_deg']:.3f}deg "
              f"p90={scores['experiments']['robust_alignment_high_outliers']['results']['spmc']['p90_rotation_error_deg']:.3f}deg")

    return scores


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-rotations", type=int, default=100)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    run_evaluation(n_rotations=args.n_rotations, verbose=True)
