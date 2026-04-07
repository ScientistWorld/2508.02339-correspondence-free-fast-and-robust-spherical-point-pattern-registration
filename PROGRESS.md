# Progress

## What Works
- **SPMC algorithm** fully implemented and validated: 0.13° on paper's own test case (exact match)
- **FRS algorithm**: implemented but broken (diverges on most inputs)
- **SPMC+FRS hybrid**: delegates to SPMC while FRS is fixed
- **Paper's dataset**: Robust Vector Alignment Dataset fully loaded and verified
- **Evaluation pipeline**: rotation error computation, timing, aggregation, scores.json output
- **Synthetic data generator**: 5 template patterns, 7 outlier configs, 100 rotations

## Results
- **SPMC on paper's test case (A1/B3/r5)**: 0.13° error — **exact match** with paper's reported 0.13°
- **SPMC quick eval (10 rotations × 35 configs)**:
  - Overall median: 0.47° (vs paper's 1.5° for SPMC, 0.8° for hybrid)
  - Clean data (B1-B2): 0.13-0.24° — excellent
  - Low outliers (B3-B4): 0.17-3.05° — good
  - High outliers (B5-B7): 0.35-11.44° — reasonable
- **Full 100-rotation evaluation**: submitted and running (~1h expected)
- **Performance**: ~0.2s per evaluation (vs paper's 0.5s for SPMC)

## Remaining
- Full evaluation results from compute cluster
- FRS fix: axis-angle histogram method needs validation
- Computational complexity scaling experiment

## Issues
- **FRS divergence**: The iterative histogram-based rotation search finds spurious shifts (249°, 37°, 23° on already-aligned data). This is a fundamental issue with the axis-angle histogram approach when there are outliers or density variations. Root cause: the histogram matching finds the mode of the circular cross-correlation, but with ~22K points and many histogram bins, the mode may not correspond to the true rotation.
- **spmc_frs uses SPMC alone**: Since FRS diverges, hybrid currently returns SPMC output
- **FPFH+QUASAR baseline not implemented**: Requires Point Cloud Library (C++), unavailable in our environment

## Deviations from Paper
- **Baseline**: FPFH+QUASAR baseline not implemented (complex C++ deps). Identity rotation used as reference.
- **FRS**: Not working — delegated to SPMC. The paper likely has additional implementation details we haven't captured.
- **Dataset**: Using paper's actual dataset (not synthetic) — this is an improvement, not a deviation.
