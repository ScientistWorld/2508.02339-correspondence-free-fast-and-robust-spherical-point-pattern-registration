"""Brute force the paper's method exists to avoid: enumerate a fixed grid of
6,000 rotations covering SO(3) and keep the one whose rotated template best
overlaps a smoothed density map of the source (a discretised spherical
cross-correlation).  Sized to stay inside the evaluator's CPU budget."""
import numpy as np

_G = 6000
_q = np.random.default_rng(12345).normal(size=(_G, 4))
_q /= np.linalg.norm(_q, axis=1, keepdims=True)
_w, _x, _y, _z = _q.T
_GRID = np.stack([
    np.stack([1 - 2 * (_y * _y + _z * _z), 2 * (_x * _y - _z * _w), 2 * (_x * _z + _y * _w)], axis=1),
    np.stack([2 * (_x * _y + _z * _w), 1 - 2 * (_x * _x + _z * _z), 2 * (_y * _z - _x * _w)], axis=1),
    np.stack([2 * (_x * _z - _y * _w), 2 * (_y * _z + _x * _w), 1 - 2 * (_x * _x + _y * _y)], axis=1),
], axis=1)
NLAT, NLON = 90, 180


def _cells(points):
    lat = np.arccos(np.clip(points[..., 2], -1.0, 1.0))
    lon = np.arctan2(points[..., 1], points[..., 0]) % (2 * np.pi)
    i = np.minimum((lat / np.pi * NLAT).astype(np.int64), NLAT - 1)
    j = np.minimum((lon / (2 * np.pi) * NLON).astype(np.int64), NLON - 1)
    return i * NLON + j


def _density(points):
    hist = np.bincount(_cells(points), minlength=NLAT * NLON).reshape(NLAT, NLON).astype(float)
    for _ in range(2):
        hist = (np.roll(hist, 1, axis=1) + hist + np.roll(hist, -1, axis=1)) / 3.0
        hist = (np.vstack([hist[:1], hist[:-1]]) + hist + np.vstack([hist[1:], hist[-1:]])) / 3.0
    area = np.sin((np.arange(NLAT) + 0.5) / NLAT * np.pi)[:, None]
    return (hist / np.maximum(area, 0.05)).ravel()


def bruteforce_grid(template, source):
    template = template / np.linalg.norm(template, axis=1, keepdims=True)
    source = source / np.linalg.norm(source, axis=1, keepdims=True)
    rng = np.random.default_rng(0)
    sample = template[rng.choice(len(template), min(1500, len(template)), replace=False)]
    density = _density(source)
    best, best_score = np.eye(3), -np.inf
    for start in range(0, _G, 500):
        chunk = _GRID[start:start + 500]
        moved = (chunk.reshape(-1, 3) @ sample.T).reshape(len(chunk), 3, -1).transpose(0, 2, 1)
        scores = density[_cells(moved)].sum(axis=1)
        k = int(np.argmax(scores))
        if scores[k] > best_score:
            best, best_score = chunk[k].copy(), scores[k]
    return best


METHODS = {"bruteforce_grid": bruteforce_grid}
