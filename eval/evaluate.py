#!/usr/bin/env python3
"""
Method-agnostic evaluation script.

This script computes aggregate metrics from pre-generated rotation estimation
results. It does NOT import from method/; it only reads result files and
writes scoring/scores.json in the canonical experiment-oriented format.

Usage:
    python eval/evaluate.py --input scoring/raw_results.json \
        --complexity-input scoring/raw_complexity_results.json \
        --output scoring/scores.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np


def compute_scores(raw_results: dict) -> dict:
    """
    Compute aggregate scores from raw rotation estimation results.

    raw_results format:
        {method_name: {(pattern, config): {"errors": [...], "times": [...]}}}
    """
    scores = {}

    # robust_alignment_all: aggregate across all configs
    all_errors = {}
    all_times = {}
    for method, configs in raw_results.items():
        all_errs = []
        all_tms = []
        for cfg, data in configs.items():
            all_errs.extend(data["errors"])
            all_tms.extend(data["times"])
        all_errors[method] = all_errs
        all_times[method] = all_tms

    for method, errs in all_errors.items():
        errs = np.array(errs)
        tms = np.array(all_times[method])
        if method not in scores:
            scores[method] = {}
        scores[method]["median_rotation_error_deg"] = float(np.median(errs))
        scores[method]["mean_rotation_error_deg"] = float(np.mean(errs))
        scores[method]["median_time_s"] = float(np.median(tms))

    # robust_alignment_high_outliers: B5, B6, B7 only
    for method, configs in raw_results.items():
        high_errs = []
        for cfg, data in configs.items():
            if any(c in cfg for c in ["B5", "B6", "B7"]):
                high_errs.extend(data["errors"])
        if high_errs:
            scores[method]["median_rotation_error_deg_high"] = float(np.median(high_errs))
            scores[method]["p90_rotation_error_deg_high"] = float(np.percentile(high_errs, 90))

    return scores


def compute_complexity_scores(raw_results: dict) -> dict:
    """Aggregate median runtimes by point-count scale and fit a log-log slope."""
    scores = {}
    for method, by_scale in raw_results.items():
        method_scores = {}
        xs = []
        ys = []
        for scale_name, values in sorted(by_scale.items(), key=lambda item: int(item[0])):
            times = np.array(values.get("times", []), dtype=float)
            if times.size == 0:
                continue
            scale = int(scale_name)
            median_time = float(np.median(times))
            method_scores[f"time_at_{scale}_points_s"] = median_time
            xs.append(np.log10(scale))
            ys.append(np.log10(max(median_time, 1e-12)))

        if len(xs) >= 2:
            slope, _ = np.polyfit(xs, ys, 1)
            method_scores["loglog_runtime_slope"] = float(slope)

        if method_scores:
            scores[method] = method_scores
    return scores


def build_scores_json(scores: dict, complexity_scores: dict, output_path: str):
    """Build the full scores.json structure and write it."""
    experiments = {}

    if scores:
        experiments["robust_alignment_all"] = {
            "results": {
                method_name: {
                    "median_rotation_error_deg": method_scores["median_rotation_error_deg"],
                    "mean_rotation_error_deg": method_scores["mean_rotation_error_deg"],
                    "median_time_s": method_scores["median_time_s"],
                }
                for method_name, method_scores in scores.items()
            }
        }
        experiments["robust_alignment_high_outliers"] = {
            "results": {
                method_name: {
                    "median_rotation_error_deg": method_scores.get(
                        "median_rotation_error_deg_high",
                        method_scores["median_rotation_error_deg"],
                    ),
                    "p90_rotation_error_deg": method_scores.get(
                        "p90_rotation_error_deg_high",
                        999.0,
                    ),
                }
                for method_name, method_scores in scores.items()
            }
        }

    if complexity_scores:
        experiments["computational_complexity"] = {
            "results": {
                method_name: {
                    key: value
                    for key, value in method_scores.items()
                }
                for method_name, method_scores in complexity_scores.items()
            }
        }

    output = {"experiments": experiments}

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Scores written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Aggregate rotation estimation results")
    parser.add_argument("--input", "-i", default="scoring/raw_results.json",
                        help="Input raw rotation benchmark JSON file")
    parser.add_argument("--complexity-input", default="scoring/raw_complexity_results.json",
                        help="Input raw complexity benchmark JSON file")
    parser.add_argument("--output", "-o", default="scoring/scores.json",
                        help="Output scores JSON file")
    args = parser.parse_args()

    raw_path = Path(args.input)
    complexity_path = Path(args.complexity_input)

    if not raw_path.exists() and not complexity_path.exists():
        print(f"ERROR: No raw results found at {raw_path} or {complexity_path}")
        print("Run a benchmark first to generate raw result files.")
        sys.exit(1)

    scores = {}
    if raw_path.exists():
        raw_results = json.loads(raw_path.read_text())
        scores = compute_scores(raw_results)

    complexity_scores = {}
    if complexity_path.exists():
        raw_complexity_results = json.loads(complexity_path.read_text())
        complexity_scores = compute_complexity_scores(raw_complexity_results)

    build_scores_json(scores, complexity_scores, args.output)


if __name__ == "__main__":
    main()
