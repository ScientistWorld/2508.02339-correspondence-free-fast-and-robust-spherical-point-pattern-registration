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
- SPMC, FRS and SPMC+FRS are implemented in `method/spherical_registration.py` (a faithful NumPy port of the released code) and registered in its `METHODS` dict.
- Experiment 1 (released dataset, 5 patterns x 7 configurations x 100 rotations): SPMC+FRS **0.597 deg** median on the public instances and **0.587 deg** on the hidden test (fresh realisations of the same protocol); per-configuration medians match the paper's Fig. 4 (A1 row identical; A5 SPMC 0.24 -> 11.32 deg). The hybrid beats SPMC and FRS alone, as the paper claims.
- Experiment 3 (spherical images, public world-map substitute): SPMC+FRS **0.69 / 0.87 deg** median (train / hidden test) vs. the paper's 0.89 deg; Img5 median 1.34 / 1.19 deg vs. 1.32 deg.
- The paper's runtime study (Fig. 6) was reproduced in earlier iterations (git history); runtime is no longer a ranked metric (machine-dependent). Compute is constrained by a 1 CPU-second-per-instance budget; SPMC+FRS uses ~0.07 s.
- Added beyond the paper: `sparse_alignment` (independent 1k/3k-point samples), where the reference fails grossly on ~26% of instances.
- Not reproduced: the FPFH+QUASAR comparator and the point-cloud-registration experiments (ModelNet40 / 3DMatch / KITTI).
- Evaluation was hardened in the final iteration (see `HARDENING.md`): the hidden test runs every registered method itself on secret instances.
