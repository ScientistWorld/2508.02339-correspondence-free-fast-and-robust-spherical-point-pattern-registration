# Evaluation Targets

## Primary: rotation_accuracy
Reduce the median rotational angular error on the Robust Vector Alignment Dataset.

- **Metric**: median_rotation_error_deg (lower is better)
- **Experiment**: robust_alignment_all
- **How to measure**: Run the method on all 5 patterns × 7 configs × 100 rotations, compute median angular error.

## Constraint: runtime_efficiency
Methods must remain fast on the released benchmark, not just accurate.

- **Metric**: median_time_s (lower is better)
- **Experiment**: robust_alignment_all
- **How to measure**: Run the same 5 patterns × 7 configs × 100 rotations protocol and record per-instance runtime.

## Constraint: high_outlier_robustness
Methods must remain reliable when the source set is dominated by clutter.

- **Metric**: median_rotation_error_deg and p90_rotation_error_deg (lower is better)
- **Experiment**: robust_alignment_high_outliers
- **How to measure**: Evaluate only the released `B5`, `B6`, and `B7` settings and summarize both the typical error and the high-error tail.

## Constraint: complexity_scaling
Methods should preserve the paper's practical efficiency claim as the point
count grows on the dedicated `A3/B3` scaling study.

- **Metric**: time_at_1e6_points_s and time_at_1e7_points_s (lower is better)
- **Experiment**: computational_complexity
- **How to measure**: Run the paper's `10^3` to `10^7` point scaling protocol on the released `A3/B3` setup and report the median runtime at the scored scales.

## Current scored scope

The current gym score is defined by the experiments that appear in `scoring/scores.json`.
At verification time, that means:
- `robust_alignment_all`
- `robust_alignment_high_outliers`
- `computational_complexity`
