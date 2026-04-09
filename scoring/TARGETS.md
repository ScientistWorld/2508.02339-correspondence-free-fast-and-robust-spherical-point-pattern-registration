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

## Ablation: strongest_vs_simpler_variants
Compare the strongest reproduced variant against the simpler reproduced variants to verify that the extra method complexity is justified.

- **Metric**: median_rotation_error_deg (lower is better for all)
- **Experiment**: robust_alignment_all
- **How to measure**: Evaluate all reproduced variants listed in `scores.json` on the same benchmark and check that the strongest variant does not win only by violating the runtime or problem constraints.
