"""Data access helpers for the Robust Vector Alignment Dataset.

This module is method-agnostic. It exposes the paper's released spherical
registration dataset so both baselines and future methods can use the same
inputs without importing from ``method/``.
"""

from __future__ import annotations

from pathlib import Path
import pickle


DATASET_DIR = Path("/home/user/method/paper_code/vector_alignment_dataset")
PATTERNS = ("A1", "A2", "A3", "A4", "A5")
CONFIGS = ("B1", "B2", "B3", "B4", "B5", "B6", "B7")


def dataset_available() -> bool:
    return (DATASET_DIR / "A1_A.pkl").exists() and (DATASET_DIR / "RandomRotation100.pkl").exists()


def require_dataset() -> Path:
    if not dataset_available():
        raise FileNotFoundError(
            f"Robust Vector Alignment Dataset not found under {DATASET_DIR}. "
            "Run `bash scripts/download.sh` first."
        )
    return DATASET_DIR


def load_pickle(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def get_rotations():
    return load_pickle(require_dataset() / "RandomRotation100.pkl")


def get_template(pattern: str):
    return load_pickle(require_dataset() / f"{pattern}_A.pkl")


def get_source(pattern: str, config: str):
    return load_pickle(require_dataset() / f"{pattern}_A_{config}.pkl")

