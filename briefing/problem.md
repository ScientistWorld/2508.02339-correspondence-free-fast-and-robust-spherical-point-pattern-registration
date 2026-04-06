# Problem Definition

## Research Question

Given two sets of 3D unit vectors (points on the unit sphere S²), find the rotation matrix R in SO(3) that best aligns a source set to a template set — without any correspondences between individual points in the two sets, and in the presence of noise and outliers.

## Why It Matters

Rotation estimation between spherical point sets (the Wahba problem in 3D) is fundamental to many applications: attitude estimation, 3D point cloud registration, image stitching, robotics, and spherical image alignment. Existing methods either rely on known point correspondences (unrealistic in practice) or use expensive O(n³) spectral approaches. A fast, correspondence-free method would enable real-time rotation estimation in these domains.

## Success Criteria

A successful solution must:
1. **Estimate rotation accurately**: Return a rotation matrix R such that applying R to the source set aligns it with the template set
2. **Handle outliers**: Degrade gracefully when the source set contains random outlier points (points with no correspondence)
3. **Run in linear time**: Computational complexity should be O(n) with respect to the number of points
4. **Correspondence-free**: No prior matching or pairing between points in source and template sets
5. **Robust to noise**: Handle Gaussian noise in point positions

Success is measured by rotational angular error (in degrees) between the estimated and ground-truth rotation matrices, and by computation time.
