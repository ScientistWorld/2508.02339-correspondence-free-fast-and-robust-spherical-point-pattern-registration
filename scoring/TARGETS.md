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

## Unreproduced reference context

`reference.json` also documents the paper's separate `computational_complexity` experiment for context. That reference experiment is not part of the current scored baseline because no corresponding results are present in `scores.json`.
