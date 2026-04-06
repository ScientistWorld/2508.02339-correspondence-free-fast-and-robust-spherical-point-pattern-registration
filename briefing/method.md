# Paper's Method

## Key Contribution

The paper proposes three novel algorithms for correspondence-free spherical point pattern registration in O(n) time, replacing expensive O(n³) spherical cross-correlation approaches:

1. **SPMC** (Spherical Pattern Matching by Correlation) — closed-form solution
2. **FRS** (Fast Rotation Search) — iterative optimization
3. **SPMC+FRS** — hybrid combining both

## Approach

### SPMC Algorithm
1. Compute mean direction of each point set (template A and source B)
2. Compute rotation matrices R_A and R_B that align each mean direction to North Pole [0,0,1]
3. Rotate all points so both sets have their means at North Pole
4. Convert each set to a 2D binary histogram (360 azimuthal × 180 polar bins)
5. Sum over polar dimension to get 1D histograms (360 bins each)
6. Perform 1D circular cross-correlation between histograms to find optimal azimuthal shift s*
7. Compute final rotation: R_opt = R_A^(-1) * R_z(s*) * R_B

### FRS Algorithm (Fast Rotation Search)
1. Compute axis direction angles (θ_x, θ_y, θ_z) for all points in template and source sets using atan2
2. Create 1D histograms along each axis (k×360 bins, k=1 by default)
3. Iteratively:
   - Compute cross-correlation for each axis to find optimal shifts (s_x, s_y, s_z)
   - Construct rotation matrix R = R_z(s_z) * R_y(s_y) * R_x(s_x)
   - Rotate source set by R
   - Stop if shifts converge (all equal target shift s_T=0) or max iterations (50) reached
4. Final rotation computed from initial and final source set using closed-form SVD

### SPMC+FRS Hybrid
- Run SPMC first for initialization
- Use SPMC's result as starting point for FRS refinement

### Computational Complexity
- SPMC: O(n) — histogram construction is linear, cross-correlation is O(1) (fixed histogram size)
- FRS: O(n) per iteration, converges in ~11 iterations on average (max 50)
- Overall: O(n) time complexity

### Spherical Embeddings for Point Clouds
For 3D point cloud registration:
- **EGI** (Extended Gaussian Image): project surface normals onto unit sphere
- **CASE** (Centroid Aware Spherical Embedding): project rays from centroid to points onto unit sphere
