"""Simple correspondence-free baselines for spherical point-pattern registration.

Score them with ``bash scripts/baseline.sh`` (runs the train and hidden-test
evaluators on this directory instead of ``method/``).  Same contract as any
method: ``fn(template (N,3), source (M,3)) -> R`` with ``source ~= template @ R.T``.
"""

from __future__ import annotations

import itertools

import numpy as np


def identity(template: np.ndarray, source: np.ndarray) -> np.ndarray:
    """No rotation at all: the error equals the true rotation angle."""
    return np.eye(3)


def _principal_frame(points: np.ndarray) -> np.ndarray:
    scatter = points.T @ points / len(points)
    _, vectors = np.linalg.eigh(scatter)
    return vectors[:, ::-1]


def _third_moments(points: np.ndarray) -> np.ndarray:
    return np.mean(points ** 3, axis=0)


def principal_axes(template: np.ndarray, source: np.ndarray) -> np.ndarray:
    """Classical moment matching: align the eigenframes of the second-moment
    (scatter) matrices; pick the axis signs that best match first and third
    moments.  Uses no correspondences and no search over rotations."""
    template = template / np.linalg.norm(template, axis=1, keepdims=True)
    source = source / np.linalg.norm(source, axis=1, keepdims=True)
    frame_t = _principal_frame(template)
    frame_s = _principal_frame(source)
    mean_s = source.mean(axis=0)
    moments_s = _third_moments(source @ frame_s)
    best, best_cost = np.eye(3), np.inf
    for signs in itertools.product((1.0, -1.0), repeat=3):
        rotation = frame_s @ np.diag(signs) @ frame_t.T
        if np.linalg.det(rotation) <= 0:
            continue
        moved = template @ rotation.T
        cost = (np.sum((moved.mean(axis=0) - mean_s) ** 2)
                + np.sum((_third_moments(moved @ frame_s) - moments_s) ** 2))
        if cost < best_cost:
            best, best_cost = rotation, cost
    return best


METHODS = {
    "identity": identity,
    "principal_axes": principal_axes,
}
