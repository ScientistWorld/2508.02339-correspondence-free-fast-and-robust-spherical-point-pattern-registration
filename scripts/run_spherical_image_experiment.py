#!/usr/bin/env python3
"""Run the paper's spherical-image adaptation experiment."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from data.dataset import get_rotations
from data.spherical_images import (
    IMAGE_CONFIGS,
    actual_clutter_fraction,
    get_source_image,
    get_template_image,
    image_to_spherical_points,
    require_spherical_image_assets,
)
from method.spherical_registration import rotation_error, spmc_frs


def _load_existing(output_path: Path) -> dict:
    if not output_path.exists():
        return {"identity": {}, "spmc_frs": {}}
    loaded = json.loads(output_path.read_text())
    raw = {"identity": {}, "spmc_frs": {}}
    for method_name in raw:
        for key, values in loaded.get(method_name, {}).items():
            raw[method_name][key] = {
                "errors": [float(v) for v in values.get("errors", [])],
                "times": [float(v) for v in values.get("times", [])],
            }
    return raw


def _save_existing(raw_results: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {}
    for method_name, by_config in raw_results.items():
        serializable[method_name] = {}
        for config_name, values in by_config.items():
            serializable[method_name][config_name] = {
                "errors": [float(v) for v in values["errors"]],
                "times": [float(v) for v in values["times"]],
            }
    output_path.write_text(json.dumps(serializable, indent=2))


def run_spherical_image_evaluation(
    n_rotations: int,
    output_path: str,
    verbose: bool = True,
) -> None:
    require_spherical_image_assets()
    rotations = get_rotations()[:n_rotations]
    template_points = image_to_spherical_points(get_template_image())
    raw_path = Path(output_path)
    raw_results = _load_existing(raw_path)

    for config_name in IMAGE_CONFIGS:
        for method_name in raw_results:
            raw_results[method_name].setdefault(config_name, {"errors": [], "times": []})

        completed = min(len(raw_results[m][config_name]["errors"]) for m in raw_results)
        if completed >= len(rotations):
            if verbose:
                clutter = 100.0 * actual_clutter_fraction(config_name)
                print(f"Skipping {config_name}; already completed with clutter {clutter:.2f}%")
            continue

        if verbose:
            clutter = 100.0 * actual_clutter_fraction(config_name)
            print(
                f"{config_name}: resuming from rotation {completed}/{len(rotations)} "
                f"(actual clutter {clutter:.2f}%)"
            )

        for ridx, rotation in enumerate(rotations[completed:], start=completed):
            source_image = get_source_image(config_name, rotation)
            source_points = image_to_spherical_points(source_image)

            raw_results["identity"][config_name]["errors"].append(rotation_error(np.eye(3), rotation))
            raw_results["identity"][config_name]["times"].append(0.0)

            start = time.perf_counter()
            R_est, _, _ = spmc_frs(template_points, source_points)
            elapsed = time.perf_counter() - start
            raw_results["spmc_frs"][config_name]["errors"].append(rotation_error(R_est, rotation))
            raw_results["spmc_frs"][config_name]["times"].append(elapsed)

            _save_existing(raw_results, raw_path)
            if verbose:
                print(f"  rotation {ridx + 1}/{len(rotations)} checkpointed")

    if verbose:
        print(f"Spherical-image raw results saved to {raw_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the paper's spherical-image benchmark")
    parser.add_argument("--n-rotations", type=int, default=100, help="Number of released rotations to evaluate")
    parser.add_argument(
        "--output",
        default="scoring/raw_spherical_image_results.json",
        help="Output path for raw spherical-image metrics",
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce console output")
    args = parser.parse_args()

    run_spherical_image_evaluation(
        n_rotations=args.n_rotations,
        output_path=args.output,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
