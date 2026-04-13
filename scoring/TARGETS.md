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

## Current scored scope

The current gym score is defined only by experiments that already appear in `scoring/scores.json`.
At verification time, that means:
- `robust_alignment_all`
- `robust_alignment_high_outliers`

The paper's separate computational-complexity study remains documented in `scoring/reference.json`, but it is not yet part of the verified scored baseline because it has not been reproduced in `scores.json`.

## Pending reference target

The next submission is intended to add:
- `computational_complexity`

This uses the paper's dedicated Fig. 6 protocol on `A3/B3` with the released rotations and scale list `10^3, 10^4, 10^5, 10^6, 10^7`.
