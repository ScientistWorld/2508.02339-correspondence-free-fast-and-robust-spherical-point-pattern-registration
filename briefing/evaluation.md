# Evaluation

## Metrics

### Primary Metric: Rotational Angular Error
The angular error between the estimated rotation matrix R_est and ground truth rotation matrix R_true. Computed as:
```
error = arccos((trace(R_true^T * R_est) - 1) / 2) * (180/pi)
```
This gives the minimum rotation angle (in degrees) needed to go from R_est to R_true. Lower is better.

### Secondary Metric: Computation Time
Wall-clock time in seconds to compute the rotation estimate. Lower is better.

### Constraint: Outlier Handling
The method must maintain accuracy across varying outlier ratios (0% to 90%) and noise levels (Gaussian noise with std 0.01).

## Baselines and Targets

Based on the paper's reported results:
- **Feature-matching baseline**: Median angular error varies widely (0.04° to >100°) depending on dataset difficulty; median computation is on the order of tens of seconds
- **Paper-reported top method**: Median angular error below 1° across the full robust-alignment benchmark; runtime under 1 second
- **Random baseline**: For random rotation guesses, median error would be roughly tens of degrees and far worse than the reported methods

## Evaluation Protocol

### Scored Gym Benchmark: Released Spherical Pattern Registration
- 5 template spherical patterns (A1–A5) with distinct characteristics
- 7 source configurations per template (B1–B7):
  - B1: no noise, no outliers (one-to-one correspondence)
  - B2: Gaussian noise (std=0.01), no outliers
  - B3: 10% outliers + noise
  - B4: 25% outliers + noise
  - B5: 50% outliers + noise
  - B6: 75% outliers + noise
  - B7: 90% outliers + noise
- 100 random rotations (R100) applied per configuration
- Total: 5 × 7 × 100 = 3500 evaluations per method
- Report median and distribution of angular errors across all configurations

### Additional Paper Experiment: Point Cloud Registration (ModelNet40)
- Complete-to-complete (Comp2Comp): both source and target have 2500 points from same object
- Partial-to-complete (Part2Comp): source is partial view, target is complete object
- Report rotation error (degrees) and translation error (meters)

### Additional Paper Experiment: Spherical Image Rotation Estimation
- Template: 2D world map projected onto sphere
- Source: same image with added clutter (0% to ~19%) and random rotations
- Report median angular error

## Current Reusable Gym Scope

The packaged scoring and reusable evaluation scripts in this workspace already cover the released spherical-pattern registration benchmark and the separate complexity study. This turn also adds a reusable spherical-image benchmark path (`scripts/spherical_images.sh` plus raw/eval support), but its fresh compute-side results are still pending, so it is not yet part of the checked-in scored artifact set. The point-cloud experiment remains documented for paper context only.
