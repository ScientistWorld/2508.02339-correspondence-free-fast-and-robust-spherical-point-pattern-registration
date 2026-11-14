# Correspondence-Free Fast and Robust Spherical Point Pattern Registration

<!-- scope-note -->
> [!NOTE]
> **Not a full reproduction of the paper.** This environment keeps the paper's core problem at a reduced scale so it is easy to run. It measures an AI scientist's idea and how well it is carried out, not the full research loop.

<!-- hardening-note -->
> [!NOTE]
> **Red-teamed and hardened.** A red team tried to score on this environment's hidden test without doing better research, and the environment was then fixed against the shortcuts that worked: see [`REDTEAM.md`](REDTEAM.md) and [`HARDENING.md`](HARDENING.md). The environment as it was before is kept as branch [`pre-hardening`](../../tree/pre-hardening).

| This paper | Scientist World, the framework this environment belongs to |
|:---:|:---:|
| <a href="https://arxiv.org/abs/2508.02339"><img alt="This paper on arXiv" src="https://img.shields.io/badge/arXiv-2508.02339-b31b1b?logo=arxiv&logoColor=white"></a> | <a href="https://arxiv.org/abs/2611.08478"><img alt="Scientist World on arXiv" src="https://img.shields.io/badge/arXiv-2611.08478-b31b1b?logo=arxiv&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world"><img alt="Scientist World code" src="https://img.shields.io/badge/Code-Scientist_World-181717?logo=github&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world_cli"><img alt="Command line code" src="https://img.shields.io/badge/Code-Command_line-181717?logo=github&logoColor=white"></a> |

| **Paper ID** | [2508.02339](https://arxiv.org/abs/2508.02339) |
|:---|:---|
| **Domain** | Computer Vision / 3D Registration / Rotation Estimation |
| **TL;DR** | Three O(n) algorithms (SPMC, FRS, SPMC+FRS) for estimating rotations between spherical point sets without correspondences, achieving >10x speed and >10x accuracy over state-of-the-art methods. |

## Summary

The paper addresses rotation estimation between two sets of points on a unit sphere (S²) without requiring correspondences between individual points. Previous approaches use spherical cross-correlation with O(n³) complexity. The authors propose three algorithms: SPMC (closed-form via circular cross-correlation after mean alignment), FRS (iterative axis-by-axis cross-correlation), and SPMC+FRS (their combination). All three achieve O(n) complexity and are robust to up to 90% outlier points, outperforming FPFH+QUASAR by over 10x in both speed and accuracy on synthetic and real-world datasets.

## Problem

Given two sets of 3D unit vectors (points on the unit sphere S²), find the rotation matrix R in SO(3) that best aligns a source set to a template set — without any correspondences between individual points in the two sets, and in the presence of noise and outliers.

## The paper's method

The paper proposes three novel algorithms for correspondence-free spherical point pattern registration in O(n) time, replacing expensive O(n³) spherical cross-correlation approaches:

1. **SPMC** (Spherical Pattern Matching by Correlation) — closed-form solution
2. **FRS** (Fast Rotation Search) — iterative optimization
3. **SPMC+FRS** — hybrid combining both

## Key results of the paper

- SPMC+FRS achieves median rotational error < 1° across all 5 datasets and 7 outlier configurations (3500 evaluations), vs. FPFH+QUASAR which varies from 0.04° to >100°
- Computation time: < 1 second for all cases (vs. ~23 seconds for FPFH+QUASAR)
- O(n) scaling confirmed experimentally from 10³ to 10⁷ points
- Robust point cloud registration on ModelNet40 with overlap as low as 65%

## Run it

```bash
pip install sciworld
sw research 2508.02339 --mode innovate --agent claude-code
sw evaluate 2508.02339
```

## More

The full problem statement, method notes, evaluation protocol and reproduction log are in [DETAILS.md](DETAILS.md).

