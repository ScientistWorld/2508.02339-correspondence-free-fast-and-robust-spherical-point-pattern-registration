# Problem Definition

## Research Question

Given two sets of 3D unit vectors (points on the unit sphere S²), find the rotation matrix R in SO(3) that best aligns a template set to a source set — without any correspondences between individual points, with arbitrary point order, and in the presence of noise, outliers, structured clutter and sparse sampling.

## Why It Matters

Rotation estimation between spherical point sets (the Wahba problem for 3D unit vectors) underlies attitude estimation, point-cloud registration via spherical embeddings, image stitching and spherical-image alignment. Correspondences are usually unavailable or unreliable, and approaches that search the rotation space densely become expensive as the required angular resolution grows. A method that is accurate, robust and fast enough for real-time use is the goal.

## Success Criteria

A successful solution must:
1. **Estimate rotation accurately** across very different spherical patterns (localized trajectories, scattered islands, non-uniform densities, a world-map image)
2. **Handle outliers and clutter**: stay accurate when up to 90% extra random points, or structured clutter, are added to the source
3. **Handle sparse, independent sampling**: template and source may be different samples of the same underlying pattern
4. **Stay fast**: well under one CPU-second per registration, scaling linearly with the number of points
5. **Be correspondence-free**: no prior matching between points; point order carries no information

Success is measured by the geodesic angular error (degrees) between the estimated and ground-truth rotations, summarised by medians, tails and success rates; see `briefing/evaluation.md`.
