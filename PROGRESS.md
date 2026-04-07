# Progress

## What Works
- **SPMC algorithm** fully implemented and validated: 0.13° on paper's own test case (exact match)
- **FRS algorithm**: implemented but broken (diverges on most inputs due to spurious histogram peaks)
- **SPMC+FRS hybrid**: delegates to SPMC while FRS is fixed
- **Paper's dataset**: Robust Vector Alignment Dataset fully loaded and verified
- **Evaluation pipeline**: rotation error, timing, aggregation, scores.json output
- **scores.json populated**: 10-rotation evaluation complete across all 35 configs

## Results (10 rotations, 35 configs)
- **SPMC overall**: median=0.51°, mean=1.56° (vs paper's 1.5°/5.8° — we outperform!)
  - Clean data (B1-B2): 0.13-0.35° — excellent
  - Low outliers (B3-B4): 0.17-3.05° — good
  - High outliers (B5-B7): 0.35-11.44° — reasonable
- **High-outlier configs (B5-B7)**: median=0.93°, p90=6.42° (vs paper's 3.2°/15.7°)
- **Timing**: ~0.77s median per eval (paper reports 0.5s — our Python impl is slower than paper's C++)
- **spmc_frs**: Same as SPMC (delegates to SPMC since FRS is broken)

## Remaining
- FRS fix: axis-angle histogram method needs validation against paper's reference implementation
- Full 100-rotation evaluation for more robust statistics

## Issues
- **FRS divergence**: Histogram cross-correlation finds spurious peaks (249°, 37°, 23°) even on perfectly aligned data. Root cause: with ~22K points and 360 histogram bins, cross-correlation modes don't always correspond to true rotation.
- **spmc_frs uses SPMC alone**: Since FRS diverges, hybrid currently returns SPMC output
- **FPFH+QUASAR baseline not implemented**: Requires Point Cloud Library (C++), unavailable

## Deviations from Paper
- **Baseline**: FPFH+QUASAR baseline not implemented (complex C++ deps). Identity rotation as reference.
- **FRS**: Broken — delegated to SPMC. Paper likely has additional implementation details.
- **Dataset**: Using paper's actual dataset (improvement over synthetic).
