# Evaluation Targets

## Primary: rotation_accuracy
Reduce the median rotational angular error on the Robust Vector Alignment Dataset.

- **Metric**: median_rotation_error_deg (lower is better)
- **Experiment**: robust_alignment_all
- **How to measure**: Run the method on all 5 patterns × 7 configs × 100 rotations, compute median angular error.

## Constraint: computation_time
Methods must remain fast. The paper claims O(n) complexity, which is a core contribution.

- **Metric**: median_time_s (lower is better)
- **Experiment**: computational_complexity
- **How to measure**: Time the method on the synthetic dataset.

## Ablation: vs_single_method
Compare the hybrid SPMC+FRS against individual SPMC and FRS to verify the hybrid's benefit.

- **Metric**: median_rotation_error_deg (lower is better for all)
- **Experiment**: robust_alignment_all
- **How to measure**: Run SPMC alone, FRS alone, and SPMC+FRS. Verify hybrid < individual methods.
