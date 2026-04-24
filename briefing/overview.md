# Overview

- **Paper ID:** 2508.02339
- **Title:** Correspondence-Free Fast and Robust Spherical Point Pattern Registration
- **Domain:** Computer Vision / 3D Registration / Rotation Estimation
- **TL;DR:** Three O(n) algorithms (SPMC, FRS, SPMC+FRS) for estimating rotations between spherical point sets without correspondences, achieving >10x speed and >10x accuracy over state-of-the-art methods.

## Short Summary

The paper addresses rotation estimation between two sets of points on a unit sphere (S²) without requiring correspondences between individual points. Previous approaches use spherical cross-correlation with O(n³) complexity. The authors propose three algorithms: SPMC (closed-form via circular cross-correlation after mean alignment), FRS (iterative axis-by-axis cross-correlation), and SPMC+FRS (their combination). All three achieve O(n) complexity and are robust to up to 90% outlier points, outperforming FPFH+QUASAR by over 10x in both speed and accuracy on synthetic and real-world datasets.

## Key Results
- SPMC+FRS achieves median rotational error < 1° across all 5 datasets and 7 outlier configurations (3500 evaluations), vs. FPFH+QUASAR which varies from 0.04° to >100°
- Computation time: < 1 second for all cases (vs. ~23 seconds for FPFH+QUASAR)
- O(n) scaling confirmed experimentally from 10³ to 10⁷ points
- Robust point cloud registration on ModelNet40 with overlap as low as 65%

## Reproduction Status
- Reproduced the released Experiment 1 benchmark end to end on the paper's dataset for all 5 patterns, 7 outlier configurations, and 100 rotations per configuration
- Reproduced `spmc_frs` at **0.597°** median error overall and **0.621°** on the high-outlier subset, both better than the paper's reported values for the same experiment
- Reproduced the separate computational-complexity scaling study, with canonical scores for the `10^6` and `10^7` point settings recorded in `scoring/scores.json`
- Added a reproducible spherical-image benchmark path this turn, but it still needs a fresh compute-side run before the checked-in scores can claim that experiment
- The packaged gym still does **not** reproduce the paper's point-cloud-registration adaptation, so the workspace scope remains narrower than the full paper
