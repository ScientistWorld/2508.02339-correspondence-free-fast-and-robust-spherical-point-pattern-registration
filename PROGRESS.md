# Progress

## What Works
- SPMC algorithm (closed-form via 1D circular cross-correlation after mean alignment)
- FRS algorithm (iterative axis-by-axis rotation search with axis direction angles)
- SPMC+FRS hybrid algorithm (SPMC initialization + FRS refinement)
- Synthetic dataset generator: 5 template patterns (A1-A5), 7 configs (B1-B7), 100 rotations
- Evaluation pipeline: angular error computation, timing, aggregation
- Baseline: identity rotation (no registration) for reference

## Results
- Pending: first full evaluation run on compute cluster
- Expected: SPMC+FRS median error < 5° on all configs (paper reports < 1°)
- Expected: SPMC and FRS individually worse than hybrid
- Expected: all methods < 1 second per evaluation

## Remaining
- Full evaluation on 3500 evaluations × 3 methods
- Validation of O(n) complexity
- Comparison against reference numbers

## Issues
- Compute node execution required (local node lacks numpy)
- Git operations slow due to large paper image files in git index

## Deviations from Paper
- Dataset: paper uses 5 specific template patterns (A1-A5) with specific point counts and characteristics. We replicate the pattern generation approach (localized trajectory, complex trajectory, small islands, large islands, non-uniform density) but use similar generation methods rather than exact replication.
- No FPFH+QUASAR baseline implemented (complex C++ library dependencies). Identity rotation baseline used instead.
