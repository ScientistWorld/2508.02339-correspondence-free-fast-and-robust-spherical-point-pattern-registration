#!/bin/bash
# Run a simple reusable baseline on the paper's released dataset.
#
# This is not the paper's FPFH+QUASAR baseline. It is a trivial identity
# baseline so future methods can sanity-check the evaluation stack without
# additional third-party dependencies.

set -euo pipefail
cd /home/user

RAW_RESULTS="${RAW_RESULTS:-scoring/raw_results_identity.json}"
SCORES_OUT="${SCORES_OUT:-scoring/scores_identity.json}"

RAW_RESULTS_PATH="${RAW_RESULTS}" python3 - <<'PY'
import json
import os
from pathlib import Path

import numpy as np

from data.dataset import CONFIGS, PATTERNS, get_rotations, get_source, get_template, require_dataset


def rotation_error_deg(r_est: np.ndarray, r_true: np.ndarray) -> float:
    trace_term = np.clip((np.trace(r_true @ r_est.T) - 1.0) / 2.0, -1.0, 1.0)
    return float(abs(np.degrees(np.arccos(trace_term))))


require_dataset()
rots = get_rotations()
raw = {"identity": {}}

for pattern in PATTERNS:
    template = np.asarray(get_template(pattern), dtype=float)
    template = template / np.linalg.norm(template, axis=1, keepdims=True)
    for config in CONFIGS:
        source_base = np.asarray(get_source(pattern, config), dtype=float)
        source_base = source_base / np.linalg.norm(source_base, axis=1, keepdims=True)
        key = f"{pattern}_{config}"
        raw["identity"][key] = {"errors": [], "times": []}
        for rotation in rots:
            _ = source_base @ rotation.T
            raw["identity"][key]["errors"].append(rotation_error_deg(np.eye(3), rotation))
            raw["identity"][key]["times"].append(0.0)

raw_path = Path(os.environ["RAW_RESULTS_PATH"])
raw_path.parent.mkdir(parents=True, exist_ok=True)
with raw_path.open("w") as handle:
    json.dump(raw, handle)
print(f"Wrote {raw_path}")
PY

RAW_RESULTS="${RAW_RESULTS}" SCORES_OUTPUT="${SCORES_OUT}" bash scripts/evaluate.sh
