# Evaluation Targets

Each target below is an entry in `scoring/scores_test.json` (hidden test) and
`scoring/scores_train.json` (public instances).

## Primary: rotation_accuracy (benefit)
Reduce the median geodesic rotation error on spherical pattern registration.
- Experiment / metric: `robust_alignment_all.median_rotation_error_deg` (lower is better)
- Also: `mean_rotation_error_deg`, `success_rate_1deg`, `p95_rotation_error_deg`, `max_rotation_error_deg`

## Constraint: high_outlier_robustness
Accuracy must hold when 50-90% of the source points are uniform outliers.
- `robust_alignment_high_outliers`: `median_rotation_error_deg`, `p90_rotation_error_deg`, `success_rate_1deg`

## Constraint: no_catastrophic_failures
Gains in the median must not come from trading in gross failures.
- `robust_alignment_all`: `p95_rotation_error_deg`, `max_rotation_error_deg`, `mean_rotation_error_deg`;
  `spherical_image_alignment_high_clutter.max_rotation_error_deg`; `sparse_alignment.success_rate_5deg`

## Secondary: spherical_image_alignment
Rotation estimation between a world-map spherical image and cluttered, rotated copies.
- `spherical_image_alignment_all`: `median_rotation_error_deg`, `mean_rotation_error_deg`, `success_rate_1deg`
- `spherical_image_alignment_high_clutter`: `median_rotation_error_deg`, `max_rotation_error_deg`

## Headroom: sparse_alignment
Registration of independent sparse samples (1,000 / 3,000 points) of the same pattern.
- `sparse_alignment`: `median_rotation_error_deg`, `mean_rotation_error_deg`, `success_rate_5deg`

## Constraint (enforced, not a metric): compute
At most 1 CPU-second per instance on average (kernel-measured); exceeding it
fails the run with worst values everywhere. Wall-clock time is not scored.
