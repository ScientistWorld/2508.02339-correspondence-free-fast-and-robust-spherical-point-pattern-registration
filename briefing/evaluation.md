# Evaluation

## What you submit

Put a Python module in `method/` (any `method/<name>.py`) that defines a
dictionary `METHODS` mapping a method name to a function

```python
def estimate(template: np.ndarray, source: np.ndarray) -> np.ndarray:
    """template (N,3), source (M,3): float64 unit vectors, no correspondences,
    arbitrary point order. Return a 3x3 rotation R with source ~= template @ R.T
    (R rotates the template onto the source)."""
```

Every entry of every `METHODS` dict on disk is scored; you may register several.
A module without `METHODS` is treated as a helper and ignored. The evaluators
run each method in a separate process, feed it point sets one instance at a
time, and compute every number themselves from the returned matrices. Nothing a
method prints or writes to disk is read.

- `bash scripts/evaluate_train.sh` → `scoring/scores_train.json` (public instances, use it while developing)
- `bash scripts/evaluate_test.sh` → `scoring/scores_test.json` (hidden test: same generators, fresh secret realisations; this is what is ranked)

Both take no arguments, use the same metrics and the same rules.

## Error measure

Geodesic rotation error in degrees between the returned `R` and the ground truth:
`arccos((trace(R_true^T R) - 1) / 2)`, in [0, 180].

## Validity, failures, compute

- Each returned matrix must be finite, 3x3, orthonormal (max |RᵀR − I| ≤ 1e-4) and have determinant +1. Matrices are never repaired.
- **Any** invalid output, exception, import error, empty `METHODS` dict, or process crash marks the method's whole run as **failed**: every metric of every experiment gets its worst value (180° for error metrics, 0 for success rates). Skipping hard instances therefore never pays.
- **Compute budget:** each method gets 1 CPU-second per instance (plus 60 s start-up) per instance group, measured by the operating system on the method's process tree, BLAS threads pinned to 1. Exceeding it fails the run. This is the problem's speed requirement (registration well under a second per case, linear in the number of points); no metric depends on wall-clock time.

## Experiments and metrics

All instances: a template point set and a rotated, corrupted source; rotations are uniform on SO(3).

| Experiment | Instances | Metrics (direction) |
|---|---|---|
| `robust_alignment_all` (weight 0.45) | 5 spherical patterns × 7 corruption levels × 100 rotations = 3,500 | median error ↓ (primary), mean error ↓, success rate ≤1° ↑, 95th-percentile error ↓, max error ↓ |
| `robust_alignment_high_outliers` (0.20) | the 1,500 instances with 50/75/90% added outliers | median ↓ (primary), 90th percentile ↓, success ≤1° ↑ |
| `spherical_image_alignment_all` (0.10) | world-map image vs cluttered, rotated, re-rasterised copies; 5 clutter levels (0–19.3% of the sphere) × 100 | median ↓ (primary), mean ↓, success ≤1° ↑ |
| `spherical_image_alignment_high_clutter` (0.05) | the 100 instances with ~19.3% clutter | median ↓ (primary), max ↓ |
| `sparse_alignment` (0.20) | template and source are independent 1,000- or 3,000-point samples of a pattern (no shared points), source with noise and 10% outliers; 5 patterns × 2 sizes × 50 | median ↓ (primary), mean ↓, success ≤5° ↑ |

Corruption levels of the pattern experiments: B1 none (source = template points, shuffled); B2 Gaussian noise σ = 0.01 on each coordinate then renormalised; B3–B7 the same noise plus 10/25/50/75/90% (of the template size) points drawn uniformly on the sphere. Image point sets are the pixels of a 360×180 equirectangular image whose intensity exceeds 0.21 (pixel centres mapped to the sphere); the evaluator does this conversion.

Train uses the public released pattern dataset (`data/downloads/vector_alignment_dataset`, the 7 released source sets per pattern and the released 100 rotations), one public clutter realisation per image level, and public seeds for the sparse samples. The hidden test regenerates every source, clutter mask, subsample and rotation from a secret seed, so instance-specific tuning to the public data does not transfer.

## Ranking

Each scored metric's improvement over the stored reference (in its better direction), divided by its spread across ranked attempts, times its coefficient in `scoring/reference.json` and the experiment weight, summed. Coefficients set importance, not units.
