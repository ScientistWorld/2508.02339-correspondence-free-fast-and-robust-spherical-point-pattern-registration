"""Genuinely better variants of the paper's hybrid.

polish: after the paper's SPMC+FRS (1-degree bins, unchanged), run FRS once more
  on 0.25-degree bins whose histograms are smoothed with a 1-degree Gaussian
  kernel (correlation computed in the Fourier domain).  Smoothing keeps the
  noise/aliasing robustness of 1-degree bins while removing their quantisation;
  a trust region rejects any polish that moves the estimate by > 2 degrees, so
  it can only refine, never derail, the coarse solution.
dual: also run FRS from the classical principal-axes (moment) initialisation and
  keep whichever of the two solutions puts more aligned source points on the
  template's (smoothed 2-degree) density.
"""
import numpy as np

from baseline.baselines import principal_axes
from method.spherical_registration import (estimate_rotation_svd, frs, pcl_array_to_rotation_angle_array,
                                           rotation_angles_to_matrix, spmc_frs)

_K = 1440
_SIGMA_DEG = 1.0
_TRUST_DEG = 2.0
_d = np.minimum(np.arange(_K), _K - np.arange(_K)) * 360.0 / _K
_GAIN = np.abs(np.fft.fft(np.exp(-0.5 * (_d / _SIGMA_DEG) ** 2))) ** 2


def _hists(points):
    angles = pcl_array_to_rotation_angle_array(points)
    return [np.fft.fft(np.histogram(angles[:, a], bins=_K, range=(0.0, 360.0))[0].astype(float)) for a in range(3)]


def smooth_frs(template, source, max_iterations=20):
    fixed = _hists(template)
    current = source.copy()
    for _ in range(max_iterations):
        moving = _hists(current)
        shifts = [float(np.argmax(np.fft.ifft(f * np.conj(m) * _GAIN).real)) * 360.0 / _K
                  for f, m in zip(fixed, moving)]
        if all(s == 0.0 for s in shifts):
            break
        current = current @ rotation_angles_to_matrix(*shifts).T
    return estimate_rotation_svd(source, current)


def _angle_deg(rotation):
    return float(np.degrees(np.arccos(np.clip((np.trace(rotation) - 1.0) / 2.0, -1.0, 1.0))))


def polish(template, source, rotation):
    step = smooth_frs(template, source @ rotation)
    return rotation @ step if _angle_deg(step) <= _TRUST_DEG else rotation


NLAT, NLON = 90, 180


def _cells(points):
    lat = np.arccos(np.clip(points[:, 2], -1.0, 1.0))
    lon = np.arctan2(points[:, 1], points[:, 0]) % (2 * np.pi)
    return (np.minimum((lat / np.pi * NLAT).astype(np.int64), NLAT - 1) * NLON
            + np.minimum((lon / (2 * np.pi) * NLON).astype(np.int64), NLON - 1))


def _density(points):
    hist = np.bincount(_cells(points), minlength=NLAT * NLON).reshape(NLAT, NLON).astype(float)
    for _ in range(2):
        hist = (np.roll(hist, 1, axis=1) + hist + np.roll(hist, -1, axis=1)) / 3.0
        hist = (np.vstack([hist[:1], hist[:-1]]) + hist + np.vstack([hist[1:], hist[-1:]])) / 3.0
    area = np.sin((np.arange(NLAT) + 0.5) / NLAT * np.pi)[:, None]
    return (hist / np.maximum(area, 0.05)).ravel()


def dual(template, source):
    candidates = [spmc_frs(template, source)[0]]
    init = principal_axes(template, source)
    candidates.append(init @ frs(template, source @ init)[0])
    density = _density(template)
    scores = [density[_cells(source @ r)].mean() for r in candidates]
    return candidates[int(np.argmax(scores))]


METHODS = {
    "spmc_frs_polish": lambda t, s: polish(t, s, spmc_frs(t, s)[0]),
    "dual_init_frs": dual,
    "dual_init_frs_polish": lambda t, s: polish(t, s, dual(t, s)),
}
