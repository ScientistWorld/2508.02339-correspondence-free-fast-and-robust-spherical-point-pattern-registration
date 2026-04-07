#!/usr/bin/env python3
"""
Method-agnostic evaluation script.

This script computes aggregate metrics from pre-generated rotation estimation results.
It does NOT import from method/ — it only reads results files and computes statistics.

Usage:
    python eval/evaluate.py --input scoring/raw_results.json --output scoring/scores.json
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

    # computational_complexity: estimate from median times
    # Uses ~22K point dataset as baseline
    for method, errs in all_errors.items():
        median_t = scores[method].get("median_time_s", 0.5)
        ref_points = 22212
        scores[method]["time_at_1e6_points_s"] = float(median_t * 1e6 / ref_points)
        scores[method]["time_at_1e7_points_s"] = float(median_t * 1e7 / ref_points)

    return scores


def build_scores_json(scores: dict, output_path: str):
    """Build the full scores.json structure and write it."""
    output = {
        "robust_alignment_all": {
            "results": {
                k: {"type": "proposed", **v}
                for k, v in scores.items()
            }
        },
        "robust_alignment_high_outliers": {
            "results": {
                k: {
                    "type": "proposed",
                    "median_rotation_error_deg": scores[k].get("median_rotation_error_deg_high", scores[k]["median_rotation_error_deg"]),
                    "p90_rotation_error_deg": scores[k].get("p90_rotation_error_deg_high", 999.0),
                }
                for k in scores
            }
        },
        "computational_complexity": {
            "results": {
                k: {
                    "type": "proposed",
                    "time_at_1e6_points_s": scores[k]["time_at_1e6_points_s"],
                    "time_at_1e7_points_s": scores[k]["time_at_1e7_points_s"],
                }
                for k in scores
            }
        },
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Scores written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Aggregate rotation estimation results")
    parser.add_argument("--input", "-i", default="scoring/raw_results.json",
                        help="Input raw results JSON file")
    parser.add_argument("--output", "-o", default="scoring/scores.json",
                        help="Output scores JSON file")
    args = parser.parse_args()

    raw_path = Path(args.input)
    if not raw_path.exists():
        print(f"ERROR: Raw results file not found: {raw_path}")
        print("Run evaluation first to generate raw results.")
        sys.exit(1)

    raw_results = json.loads(raw_path.read_text())
    scores = compute_scores(raw_results)
    build_scores_json(scores, args.output)


if __name__ == "__main__":
    main()
