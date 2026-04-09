# Experiment Overview

This file describes what each experiment in `scores.json` is trying to establish.

## robust_alignment_all
Tests whether the rotation registration method achieves low angular error on the paper's
Robust Vector Alignment Dataset across all outlier configurations. The dataset contains
5 distinct point cloud patterns with varying complexity (from uniform trajectories to
non-uniform density distributions), each evaluated under 7 different outlier configurations
(0% to 90% outlier ratios). This is the primary experiment establishing whether the
method solves the correspondence-free rotation estimation problem.

## robust_alignment_high_outliers
Tests whether the rotation registration method remains robust under extreme clutter
conditions (50%, 75%, and 90% outlier ratios). This subset isolates the hardest clutter
regime in the released benchmark, where many methods degrade sharply as unrelated source
points dominate the observation. The paper specifically claims robustness up to 90%
outliers, making this a key validation of the robustness claim.
