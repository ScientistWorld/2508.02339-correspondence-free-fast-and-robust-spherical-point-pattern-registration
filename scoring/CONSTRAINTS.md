# Scientist Constraints

## Problem Setup
Work on correspondence-free rotation estimation between two sets of 3D unit vectors on the unit sphere. The task is to recover the source-to-template rotation without access to ground-truth point matches.

## Data
Use the released Robust Vector Alignment Dataset through [data/dataset.py](/home/user/data/dataset.py). The scored benchmark holds fixed:
- all 5 template patterns `A1` through `A5`
- all 7 source configurations `B1` through `B7`
- all 100 released rotations from `RandomRotation100.pkl`

No external training data, synthetic replacement benchmark, or filtered subset may replace this scored evaluation.

## Outputs
Each method must output a 3x3 rotation matrix in `SO(3)` for each source/template pair. Scoring assumes the same rotation-matrix convention used by the current evaluator.

## Evaluation Rules
- Use the geodesic rotation error in degrees: `arccos((trace(R_true^T R_est) - 1) / 2)`.
- Measure runtime on the same inputs used for accuracy evaluation.
- For the complexity experiment, hold fixed the paper's `A3/B3` setup, the released `RandomRotation100.pkl` rotations, and the scale list `10^3, 10^4, 10^5, 10^6, 10^7`.
- Report results under the same experiment names and metric names used in `scoring/reference.json` and `scoring/scores.json`.

## Prohibited Shortcuts
- No use of point correspondences, nearest-neighbor matches, or injected pair labels during the scored benchmark.
- No hardcoding of known rotations or any other information derived from the benchmark answers.
- No changing the benchmark distribution by removing difficult patterns or outlier settings.

## Allowed Freedom
Scientists may change the representation, objective, optimizer, model family, or implementation details, provided the constraints above remain fixed and the method stays within the same correspondence-free rotation-estimation problem.
