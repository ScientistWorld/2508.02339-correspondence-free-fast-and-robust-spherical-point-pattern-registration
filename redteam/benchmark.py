"""Audit runner: genuine rotations and externally measured wall times, no eval imports.

Only uses data and the installed method, both visible to a future scientist.
All 100 rotations are generated; no knowledge of the hidden slice is used.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np

from data.dataset import CONFIGS, PATTERNS, get_rotations, get_source, get_template
from method.spherical_registration import register_rotation


def unit(x):
    x = np.asarray(x, dtype=float)
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def error(r, truth):
    return float(np.degrees(np.arccos(np.clip((np.trace(truth @ r.T)-1)/2, -1, 1))))


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def run(folder, seed, complexity=True):
    np.random.seed(seed)
    output = Path(folder)
    raw_path = output / "raw_results.json"
    raw = json.loads(raw_path.read_text()) if raw_path.exists() else {"spmc_frs": {}}
    rotations = get_rotations()
    for pattern in PATTERNS:
        template = unit(get_template(pattern))
        for config in CONFIGS:
            key = f"{pattern}_{config}"
            base = unit(get_source(pattern, config))
            row = raw["spmc_frs"].setdefault(key, {"errors": [], "times": []})
            for rotation in rotations[len(row["errors"]):]:
                source = base @ rotation.T
                start = time.perf_counter()
                result, _, _ = register_rotation(template, source)
                elapsed = time.perf_counter() - start
                row["errors"].append(error(result, rotation))
                row["times"].append(elapsed)
            save(raw_path, raw)
            print(output.name, key, len(row["errors"]), flush=True)
    if not complexity:
        return
    # Fixed A3/B3 and all 20 rotations at the two scored, original point counts.
    # Smaller unscored scales also measured to retain the full Fig. 6 protocol.
    path = output / "raw_complexity_results.json"
    raw_c = json.loads(path.read_text()) if path.exists() else {"spmc_frs": {}}
    template_base = np.asarray(get_template("A3"), dtype=np.float32)
    source_base = np.asarray(get_source("A3", "B3"), dtype=np.float32)
    template_base /= np.linalg.norm(template_base, axis=1, keepdims=True)
    source_base /= np.linalg.norm(source_base, axis=1, keepdims=True)
    for scale in (10**3, 10**4, 10**5, 10**6, 10**7):
        row = raw_c["spmc_frs"].setdefault(str(scale), {"times": []})
        if len(row["times"]) >= 20:
            continue
        rng = np.random.default_rng(scale)
        template = template_base[rng.choice(len(template_base), scale, replace=True)].copy()
        template /= np.clip(np.linalg.norm(template, axis=1, keepdims=True), 1e-12, None)
        rng = np.random.default_rng(scale+17)
        base = source_base[rng.choice(len(source_base), scale, replace=True)].copy()
        base /= np.clip(np.linalg.norm(base, axis=1, keepdims=True), 1e-12, None)
        for rotation in rotations[len(row["times"]):20]:
            source = base @ rotation.T
            start = time.perf_counter()
            result, _, _ = register_rotation(template, source)
            row["times"].append(time.perf_counter()-start)
            # Also record accuracy so a fast failure at scale is visible in the audit.
            row.setdefault("errors", []).append(error(result, rotation))
            save(path, raw_c)
        print(output.name, "scale", scale, flush=True)
        del template, base, source


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("folder")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-complexity", action="store_true")
    args = p.parse_args()
    run(args.folder, args.seed, not args.no_complexity)
