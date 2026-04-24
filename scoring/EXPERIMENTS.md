# Experiment Overview

This file describes the experiments that are currently scored in `scores.json`.

## robust_alignment_all
Measures overall performance on the released Robust Vector Alignment Dataset.
Each method is evaluated on all 5 template patterns (`A1`-`A5`), all 7 source
configurations (`B1`-`B7`), and all 100 released rotations. This is the main
benchmark for the gym.

The recorded metrics are:
- `median_rotation_error_deg`
- `mean_rotation_error_deg`
- `median_time_s`

## robust_alignment_high_outliers
Measures robustness on the hardest clutter settings only. This experiment uses
the same released dataset, but restricts evaluation to configurations `B5`,
`B6`, and `B7`, where the source set contains 50%, 75%, and 90% outliers.

The recorded metrics are:
- `median_rotation_error_deg`
- `p90_rotation_error_deg`

This experiment exists because the paper's central claim is not only low
overall error, but also strong performance under severe outlier corruption.

## computational_complexity
Measures the paper's separate runtime-scaling claim on the fixed `A3/B3`
synthetic setup. Each method is timed on the released rotation set while the
number of points scales from `10^3` through `10^7`; the scored summary keeps
the two largest settings that matter for practical asymptotics.

The recorded metrics are:
- `time_at_1e6_points_s`
- `time_at_1e7_points_s`
