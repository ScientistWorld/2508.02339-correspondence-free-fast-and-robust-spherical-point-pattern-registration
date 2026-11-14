#!/usr/bin/env python3
"""UNSCORED diagnostic: runtime scaling of the registered methods (paper Fig. 6).

The paper resamples the A3 template (and the A3/B3 source) to 10^3 ... 10^7
points and times each algorithm over 20 rotations.  Wall-clock time depends on
the machine and its load, so this script only writes a diagnostic JSON; no
ranked score depends on it.  The ranked constraint on compute is the
evaluators' kernel-measured CPU budget (1 CPU-second per instance).
Accuracy at every scale is recorded next to the time so a fast failure is
visible.
"""

from __future__ import annotations

import argparse
import importlib
import json
import time
from pathlib import Path

import numpy as np

from data.dataset import get_rotations, get_source, get_template, require_dataset


def _unit(points: np.ndarray) -> np.ndarray:
    return points / np.clip(np.linalg.norm(points, axis=1, keepdims=True), 1e-12, None)


def _resample(points: np.ndarray, count: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return _unit(np.asarray(points[rng.choice(len(points), size=count, replace=True)], dtype=np.float64))


def _error(estimate: np.ndarray, truth: np.ndarray) -> float:
    return float(np.degrees(np.arccos(np.clip((np.trace(truth.T @ estimate) - 1) / 2, -1, 1))))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scales", default="1000,10000,100000,1000000,10000000")
    parser.add_argument("--n-rotations", type=int, default=20)
    parser.add_argument("--module", default="method.spherical_registration")
    parser.add_argument("--output", default="outputs/complexity_timing.json")
    args = parser.parse_args()

    require_dataset()
    methods = importlib.import_module(args.module).METHODS
    template_base = _unit(np.asarray(get_template("A3"), dtype=np.float64))
    source_base = _unit(np.asarray(get_source("A3", "B3"), dtype=np.float64))
    rotations = get_rotations()[: args.n_rotations]
    out = Path(args.output)
    results = json.loads(out.read_text()) if out.exists() else {}
    for scale in [int(s) for s in args.scales.split(",") if s.strip()]:
        template = _resample(template_base, scale, scale)
        base = _resample(source_base, scale, scale + 17)
        for name, fn in methods.items():
            row = results.setdefault(name, {}).setdefault(str(scale), {"times_s": [], "errors_deg": []})
            for rotation in rotations[len(row["times_s"]):]:
                source = base @ rotation.T
                start = time.perf_counter()
                estimate = fn(template, source)
                row["times_s"].append(time.perf_counter() - start)
                row["errors_deg"].append(_error(np.asarray(estimate), rotation))
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(results, indent=1))
            print(f"{name} n={scale}: median time {np.median(row['times_s']):.3f}s, "
                  f"median error {np.median(row['errors_deg']):.3f} deg", flush=True)


if __name__ == "__main__":
    main()
