# Experiments

Every experiment below is produced by the evaluators themselves: they run each
registered method (`METHODS` dicts under `method/`), compute the geodesic error
of every returned rotation, and aggregate. `scripts/evaluate_train.sh` uses the
public instances; `scripts/evaluate_test.sh` (ranked) uses fresh secret
realisations of the same generators. A failed run (invalid matrix, exception,
import failure, empty registry, CPU budget of 1 s/instance exceeded) gets the
worst value of every metric (180 deg errors, 0 success).

## robust_alignment_all (weight 0.45)
Spherical pattern registration: 5 template patterns (A1-A5: localized
trajectory, complex trajectory, small islands, large islands, non-uniform
density) x 7 source corruption levels (B1 none; B2 Gaussian noise 0.01; B3-B7
noise plus 10/25/50/75/90% uniform outliers) x 100 random rotations = 3,500.
Metrics: `median_rotation_error_deg` (primary), `mean_rotation_error_deg`,
`success_rate_1deg`, `p95_rotation_error_deg`, `max_rotation_error_deg`.

## robust_alignment_high_outliers (weight 0.20)
The 1,500 instances of the above with 50/75/90% added outliers.
Metrics: `median_rotation_error_deg` (primary), `p90_rotation_error_deg`,
`success_rate_1deg`.

## spherical_image_alignment_all (weight 0.10)
A 360x180 world-map image (rendered from a public GeoJSON) is the template;
each source adds random rectangles/ellipses covering 0/5/10/15/19.3% of the
sphere, is rotated and re-rasterised. Both images are converted to point sets
(pixels with intensity > 0.21) by the evaluator. 5 levels x 100 rotations.
Metrics: `median_rotation_error_deg` (primary), `mean_rotation_error_deg`,
`success_rate_1deg`.

## spherical_image_alignment_high_clutter (weight 0.05)
The 100 image instances with ~19.3% clutter.
Metrics: `median_rotation_error_deg` (primary), `max_rotation_error_deg`.

## sparse_alignment (weight 0.20)
Template and source are independent 1,000- or 3,000-point samples of the same
pattern (no shared points); the source also gets 0.01 noise and 10% uniform
outliers. 5 patterns x 2 sizes x 50 rotations = 500.
Metrics: `median_rotation_error_deg` (primary), `mean_rotation_error_deg`,
`success_rate_5deg`.

## Not scored
Wall-clock runtime and its scaling with the number of points
(`scripts/complexity.sh`, written to `outputs/`) are machine-dependent and
reported only as diagnostics; compute is constrained by the CPU budget instead.
