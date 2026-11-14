#!/usr/bin/env python3
"""Environment-level shortcut scenarios from REDTEAM.md, re-run on the hardened
evaluators. Every mutation is backed up first and restored in `finally` (and at
the start of any later call, in case a job died mid-scenario)."""
import json
import pickle
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "notes" / "hardening" / "results"
DS = ROOT / "data" / "downloads" / "vector_alignment_dataset"
BACKUPS = {DS / "A1_A.pkl": RES / "backup_A1_A.pkl",
           DS / "RandomRotation100.pkl": RES / "backup_RandomRotation100.pkl"}


def restore() -> None:
    for target, backup in BACKUPS.items():
        if backup.exists():
            shutil.copyfile(backup, target)
            backup.unlink()


def evaluate(split: str, method_dir: str, out: Path) -> None:
    subprocess.run([sys.executable, f"eval/{split}/evaluate.py", "--method-dir", method_dir, "--output", str(out)],
                   cwd=ROOT, check=True)


def main(name: str) -> None:
    RES.mkdir(parents=True, exist_ok=True)
    restore()
    if name == "restore":
        return
    if name == "stale_artifacts":
        # Forged final score + forged raw per-instance numbers left on disk.
        out = RES / "stale_artifacts_scores_test.json"
        out.write_text(json.dumps({"experiments": {"robust_alignment_all": {"results": {
            "identity": {"median_rotation_error_deg": -123.0}}}}}))
        raw = ROOT / "scoring" / "raw_results.json"
        raw.write_text(json.dumps({"identity": {f"A{p}_B{c}": {"errors": [0.0] * 100, "times": [0.0] * 100}
                                                for p in range(1, 6) for c in range(1, 8)}}))
        try:
            evaluate("test", "baseline", out)
        finally:
            raw.unlink(missing_ok=True)
    elif name == "tamper_rotations":
        # REDTEAM shortcut_fixed_rotations: replace the public answers by identities.
        import numpy as np
        target = DS / "RandomRotation100.pkl"
        shutil.copyfile(target, BACKUPS[target])
        try:
            target.write_bytes(pickle.dumps(np.stack([np.eye(3)] * 100)))
            evaluate("test", "baseline", RES / "tamper_rotations_scores_test.json")
            evaluate("train", "baseline", RES / "tamper_rotations_scores_train.json")
        finally:
            restore()
    elif name == "tamper_template":
        # Swap a public template the hidden test reads for an easier one.
        target = DS / "A1_A.pkl"
        shutil.copyfile(target, BACKUPS[target])
        try:
            target.write_bytes(pickle.dumps(pickle.loads(target.read_bytes())[:1000]))
            evaluate("test", "method", RES / "tamper_template_scores_test.json")
        finally:
            restore()
    else:
        raise SystemExit(f"unknown scenario {name}")


if __name__ == "__main__":
    main(sys.argv[1])
