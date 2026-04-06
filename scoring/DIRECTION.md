# Research Direction

## Research Problem
This paper addresses correspondence-free rotation estimation between two sets of 3D unit vectors on the unit sphere. The core challenge is that without known point correspondences, the search space over SO(3) is large and continuous, making brute-force search infeasible. The paper's contribution is an O(n) algorithm that solves this without needing any correspondences.

## Core Contribution
The paper introduces a histogram-based approach to the correspondence-free rotation problem:
1. SPMC aligns mean directions to North Pole, then uses 1D circular cross-correlation on azimuthal histograms
2. FRS iteratively refines by cross-correlating axis-direction-angle histograms along all three axes
3. SPMC+FRS combines both: SPMC for initialization, FRS for refinement

The scientist must work within this histogram-correlation framework. The contribution is NOT about deep learning, feature matching, or spectral methods — it is specifically about how histograms of spherical projections can be efficiently cross-correlated to recover rotations.

## Approach Scope
The scientist should focus on improving the histogram-correlation approach:
- Different histogram representations (resolution, weighting, binning strategies)
- Different correlation methods (FFT, phase correlation, normalized cross-correlation)
- Different search strategies (grid search refinement, multi-resolution, branch-and-bound)
- Different initialization strategies
- Different spherical embeddings for the source data

## Out of Bounds
- Replacing the histogram-correlation approach with neural network-based methods (PointNet, GraphNets, etc.)
- Using correspondence-detection methods (FPFH, ISS, Harris3D) as a preprocessing step
- Using spectral/spherical harmonics methods (the paper explicitly avoids these for speed)
- Pure optimization approaches that are not histogram-based
- Any method that requires known correspondences
