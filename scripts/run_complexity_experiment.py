#!/usr/bin/env python3
"""
Measure runtime scaling for SPMC, FRS, and SPMC+FRS on the paper's A3/B3 setup.

This reproduces the paper's separate computational-complexity study by resampling
the released A3 template and B3 source distribution to larger point counts, then
timing each method across 20 rotations from the released R100 set.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from data.dataset import get_rotations, get_source, get_template, require_dataset
from method.spherical_registration import frs, spmc, spmc_frs


DEFAULT_SCALES = (10**3, 10**4, 10**5, 10**6, 10**7)


def _parse_scales(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def _resample_points(points: np.ndarray, count: int, seed: int) -> np.ndarray:
    """Resample to a target size while preserving the released distribution."""
    rng = np.random.default_rng(seed)
    indices = rng.choice(points.shape[0], size=count, replace=True)
    sampled = np.asarray(points[indices], dtype=np.float32)
    norms = np.linalg.norm(sampled, axis=1, keepdims=True)
    return sampled / np.clip(norms, 1e-12, None)


def _load_existing(output_path: Path) -> dict:
    if not output_path.exists():
        return {"spmc": {}, "frs": {}, "spmc_frs": {}}
    loaded = json.loads(output_path.read_text())
    raw = {"spmc": {}, "frs": {}, "spmc_frs": {}}
    for method_name in raw:
        for scale_name, values in loaded.get(method_name, {}).items():
            raw[method_name][scale_name] = {
                "times": [float(v) for v in values.get("times", [])],
            }
    return raw


def _save_existing(raw_results: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {}
    for method_name, by_scale in raw_results.items():
        serializable[method_name] = {}
        for scale_name, values in by_scale.items():
            serializable[method_name][scale_name] = {
                "times": [float(v) for v in values["times"]],
            }
    output_path.write_text(json.dumps(serializable, indent=2))


def run_complexity_evaluation(
    scales: list[int],
    n_rotations: int,
    output_path: str,
    verbose: bool = True,
) -> None:
    require_dataset()
    template_base = np.asarray(get_template("A3"), dtype=np.float32)
    source_base = np.asarray(get_source("A3", "B3"), dtype=np.float32)
    template_base = template_base / np.linalg.norm(template_base, axis=1, keepdims=True)
    source_base = source_base / np.linalg.norm(source_base, axis=1, keepdims=True)
    rotations = get_rotations()[:n_rotations]

    out_path = Path(output_path)
    raw_results = _load_existing(out_path)

    for scale in scales:
        scale_key = str(scale)
        for method_name in raw_results:
            raw_results[method_name].setdefault(scale_key, {"times": []})

        completed = min(len(raw_results[m][scale_key]["times"]) for m in raw_results)
        if completed >= len(rotations):
            if verbose:
                print(f"Skipping scale {scale_key}; already completed {completed} rotations")
            continue

        if verbose:
            print(f"Scale {scale_key}: resuming from rotation {completed}/{len(rotations)}")

        template = _resample_points(template_base, scale, seed=scale)
        source_seed = _resample_points(source_base, scale, seed=scale + 17)

        for ridx, rotation in enumerate(rotations[completed:], start=completed):
            source = source_seed @ rotation.T

            _, t_spmc = spmc(template, source)
            raw_results["spmc"][scale_key]["times"].append(t_spmc)

            _, t_frs, _ = frs(template, source)
            raw_results["frs"][scale_key]["times"].append(t_frs)

            _, t_hybrid, _ = spmc_frs(template, source)
            raw_results["spmc_frs"][scale_key]["times"].append(t_hybrid)

            _save_existing(raw_results, out_path)
            if verbose:
                print(f"  rotation {ridx + 1}/{len(rotations)} checkpointed")

    if verbose:
        print(f"Complexity raw results saved to {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the paper's complexity benchmark")
    parser.add_argument(
        "--scales",
        default=",".join(str(scale) for scale in DEFAULT_SCALES),
        help="Comma-separated point counts",
    )
    parser.add_argument("--n-rotations", type=int, default=20, help="Number of rotations to evaluate")
    parser.add_argument(
        "--output",
        default="scoring/raw_complexity_results.json",
        help="Output path for raw complexity timings",
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce console output")
    args = parser.parse_args()

    run_complexity_evaluation(
        scales=_parse_scales(args.scales),
        n_rotations=args.n_rotations,
        output_path=args.output,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
