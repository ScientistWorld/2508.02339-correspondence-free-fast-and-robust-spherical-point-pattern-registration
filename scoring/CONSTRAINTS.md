# Scientist Constraints

## Problem setup
Correspondence-free rotation estimation between two unordered sets of 3D unit
vectors. A method is a function `(template (N,3), source (M,3)) -> R (3x3)`
with `source ~= template @ R.T`, registered in a `METHODS` dict in a module
under `method/` (see `briefing/evaluation.md`).

## Held fixed by the evaluators (do not try to change them)
- Instances, ground truth, corruption levels, clutter, sample sizes, the number
  of instances, the 1 deg / 5 deg success thresholds and the image intensity
  threshold are all generated inside `eval/`; the hidden test uses fresh secret
  realisations.
- Errors are recomputed from your returned matrices; nothing your code writes
  is read. Invalid matrices (non-finite, non-orthonormal, det != +1),
  exceptions and crashes fail the whole run (worst values everywhere).
- Compute budget: 1 CPU-second per instance (OS-measured, BLAS threads pinned
  to 1) per instance group. Exceeding it fails the run.

## Data you may use
The public pattern dataset via `data/dataset.py` (5 templates, the released
source sets and rotations) and `data/spherical_images.py` (world-map rendering,
clutter and image/point conversion helpers) for development. The hidden test
does not reuse those specific realisations or rotations.

## Prohibited
- Reading anything under `eval/`, the hidden-test secret, or evaluator memory
  while your method runs; tampering with `data/downloads/` (the evaluators
  verify SHA-256 hashes and fail every method if an asset changed).
- Hard-coding answers or fingerprints of the public instances.
- Using any information beyond the two point sets passed to the function.

## Allowed
Any correspondence-free estimator: histogram / correlation methods, moment
methods, robust optimisation, search over rotations, learned components
(trained only on data you generate or the public data), point-to-point
matching computed by the method itself, subsampling, multiple hypotheses -
as long as it fits the CPU budget and returns a proper rotation.
