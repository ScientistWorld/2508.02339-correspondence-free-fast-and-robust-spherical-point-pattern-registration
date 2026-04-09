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

## Ablation: vs_single_method
Compare the hybrid SPMC+FRS against individual SPMC and FRS to verify the hybrid's benefit.

- **Metric**: median_rotation_error_deg (lower is better for all)
- **Experiment**: robust_alignment_all
- **How to measure**: Run SPMC alone, FRS alone, and SPMC+FRS. Verify hybrid < individual methods.

## Secondary: complexity_scaling
Verify the paper's near-linear runtime claim on the released A3/B3 scaling study.

- **Metric**: loglog_runtime_slope (lower is better; values near 1 support the paper's O(n) claim)
- **Experiment**: computational_complexity
- **How to measure**: Resample A3 and B3 to `10^3, 10^4, 10^5, 10^6, 10^7` points, run 20 rotations per scale, and fit a log-log slope from median runtime versus point count.
