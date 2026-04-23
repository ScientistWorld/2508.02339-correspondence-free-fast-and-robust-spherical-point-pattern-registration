#!/usr/bin/env python3
"""Aggregate the held-out test slice of pre-generated rotation results.

The input contract mirrors scripts/evaluate.sh: read a method-agnostic
raw_results.json artifact and write a scores JSON file. This slice scores a
fixed held-out subset of 40 rotations from the released 100-rotation protocol
for every pattern/configuration pair.
"""

import argparse
import json
import math
import statistics
import sys
from pathlib import Path


SLICE_NAME = "test"
ROTATION_INDICES = (
    8, 13, 15, 16, 21, 23, 24, 26, 29, 32,
    37, 38, 39, 40, 41, 44, 48, 49, 50, 51,
    56, 57, 58, 62, 63, 65, 66, 67, 72, 75,
    76, 79, 81, 86, 87, 88, 90, 94, 97, 99,
)
HIGH_OUTLIER_CONFIGS = {"B5", "B6", "B7"}


def _mean(values: list[float]) -> float:
    return float(statistics.fmean(values))


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("percentile requires at least one value")
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (percentile / 100.0) * (len(ordered) - 1)
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    weight = rank - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def _success_rate(values: list[float], threshold_deg: float = 1.0) -> float:
    if not values:
        raise ValueError("success_rate requires at least one value")
    return float(sum(float(v) <= threshold_deg for v in values) / len(values))


def _config_name(config_key: str) -> str:
    return config_key.rsplit("_", 1)[-1]


def _slice_series(values: list[float], config_key: str, field_name: str) -> list[float]:
    missing = [idx for idx in ROTATION_INDICES if idx >= len(values)]
    if missing:
        raise ValueError(
            f"{config_key}.{field_name} has {len(values)} entries, but the {SLICE_NAME} "
            f"slice requires the released 100-rotation artifact"
        )
    return [float(values[idx]) for idx in ROTATION_INDICES]


def compute_scores(raw_results: dict) -> dict:
    method_scores = {}
    high_outlier_scores = {}

    for method_name, configs in raw_results.items():
        all_errors = []
        all_times = []
        high_errors = []

        for config_key, data in configs.items():
            errors = _slice_series(data.get("errors", []), config_key, "errors")
            times = _slice_series(data.get("times", []), config_key, "times")
            all_errors.extend(errors)
            all_times.extend(times)
            if _config_name(config_key) in HIGH_OUTLIER_CONFIGS:
                high_errors.extend(errors)

        if all_errors:
            method_scores[method_name] = {
                "median_rotation_error_deg": _median(all_errors),
                "mean_rotation_error_deg": _mean(all_errors),
                "median_time_s": _median(all_times),
                "success_rate_1deg": _success_rate(all_errors),
                "std_rotation_error_deg": _stdev(all_errors),
                "p95_rotation_error_deg": _percentile(all_errors, 95),
                "max_rotation_error_deg": max(all_errors) if all_errors else 0.0,
            }

        if high_errors:
            high_outlier_scores[method_name] = {
                "median_rotation_error_deg": _median(high_errors),
                "p90_rotation_error_deg": _percentile(high_errors, 90),
                "success_rate_1deg": _success_rate(high_errors),
                "std_rotation_error_deg": _stdev(high_errors),
            }

    experiments = {}
    if method_scores:
        experiments["robust_alignment_all"] = {"results": method_scores}
    if high_outlier_scores:
        experiments["robust_alignment_high_outliers"] = {"results": high_outlier_scores}
    return {"experiments": experiments}


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate test-slice rotation results")
    parser.add_argument("--input", "-i", default="scoring/raw_results.json")
    parser.add_argument("--output", "-o", default="scoring/scores_test.json")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: raw results not found at {input_path}", file=sys.stderr)
        sys.exit(1)

    raw_results = json.loads(input_path.read_text())
    scores = compute_scores(raw_results)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(scores, indent=2) + "\n")
    print(f"Test-slice scores written to {output_path}")


if __name__ == "__main__":
    main()
