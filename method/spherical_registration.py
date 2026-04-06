"""
Spherical Point Pattern Registration: SPMC, FRS, and SPMC+FRS algorithms.

Paper: "Correspondence-Free Fast and Robust Spherical Point Pattern Registration"
(2508.02339)
"""

import numpy as np
from typing import Tuple, Optional
import time


# =============================================================================
# Rotation Utilities
# =============================================================================

def rotation_matrix_between_vectors(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """
    Compute rotation matrix that aligns v2 to v1 using Rodrigues' formula.
    v1, v2: unit vectors (3,)
    Returns: 3x3 rotation matrix in SO(3)
    """
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)

    dot = np.clip(np.dot(v1, v2), -1.0, 1.0)

    if dot > 1.0 - 1e-10:
        return np.eye(3)
    if dot < -1.0 + 1e-10:
        # 180 degree rotation — find axis perpendicular to v1
        axis = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(v1, axis)) > 0.9:
            axis = np.array([0.0, 1.0, 0.0])
        axis = axis - v1 * np.dot(v1, axis)
        axis = axis / np.linalg.norm(axis)
        return -np.eye(3) + 2 * np.outer(axis, axis)

    axis = np.cross(v2, v1)
    axis = axis / np.linalg.norm(axis)
    angle = np.arccos(dot)

    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
    return R


def align_to_north_pole(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute rotation matrix that aligns the mean direction of points to North Pole [0,0,1],
    and apply it to the points.
    points: (N, 3) array of unit vectors
    Returns: rotated points (N, 3), rotation matrix R
    """
    mean_dir = np.mean(points, axis=0)
    mean_dir = mean_dir / np.linalg.norm(mean_dir)
    north = np.array([0.0, 0.0, 1.0])
    R = rotation_matrix_between_vectors(north, mean_dir)
    rotated = points @ R.T
    return rotated, R


def rotation_matrix_from_axis_angles(theta_x: float, theta_y: float, theta_z: float) -> np.ndarray:
    """Compute rotation matrix from axis angles (in degrees)."""
    cx, sx = np.cos(np.radians(theta_x)), np.sin(np.radians(theta_x))
    cy, sy = np.cos(np.radians(theta_y)), np.sin(np.radians(theta_y))
    cz, sz = np.cos(np.radians(theta_z)), np.sin(np.radians(theta_z))

    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])

    # ZYX order as specified in paper
    return Rz @ Ry @ Rx


def rotation_error(R_est: np.ndarray, R_true: np.ndarray) -> float:
    """
    Compute angular error in degrees between estimated and true rotation matrices.
    Returns angle in [0, 180] degrees.
    """
    R_diff = R_true @ R_est.T
    trace = np.clip(np.trace(R_diff) - 1, -2, 2)
    angle = np.arccos(trace / 2.0)
    return np.degrees(angle)


def apply_rotation(points: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Apply rotation matrix to points."""
    return points @ R.T


def svd_rotation(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Closed-form rotation estimation using SVD (Arun-Huang method).
    Finds R that minimizes ||R @ A - B||_F^2.
    A, B: (N, 3) point sets
    Returns: 3x3 rotation matrix
    """
    H = A.T @ B
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T
    return R


# =============================================================================
# Histogram Utilities
# =============================================================================

def points_to_binary_histogram(points: np.ndarray, bins_az: int = 360, bins_el: int = 180,
                               threshold: int = 0) -> np.ndarray:
    """
    Project S2 points to equirectangular 2D binary histogram.
    points: (N, 3) unit vectors
    bins_az: number of azimuthal bins (0 to 360 degrees)
    bins_el: number of elevation bins (0 to 180 degrees)
    threshold: bins with count >= threshold are set to 1, else 0
    Returns: (bins_el, bins_az) binary histogram
    """
    x, y, z = points[:, 0], points[:, 1], points[:, 2]

    # Azimuthal angle: 0 to 2*pi
    azimuth = np.arctan2(y, x)  # -pi to pi
    azimuth_bin = ((azimuth + np.pi) / (2 * np.pi) * bins_az).astype(int) % bins_az

    # Polar angle (elevation from equator): 0 to pi
    # z = cos(theta), so theta = arccos(z)
    polar = np.arccos(np.clip(z, -1, 1))  # 0 to pi
    polar_bin = (polar / np.pi * bins_el).astype(int)
    polar_bin = np.clip(polar_bin, 0, bins_el - 1)

    hist = np.zeros((bins_el, bins_az), dtype=int)
    for i in range(len(points)):
        hist[polar_bin[i], azimuth_bin[i]] += 1

    # Binary threshold
    binary_hist = (hist >= threshold).astype(int)
    return binary_hist


def histogram_to_1d(hist2d: np.ndarray) -> np.ndarray:
    """
    Sum 2D histogram over polar (elevation) axis to get 1D azimuthal histogram.
    hist2d: (bins_el, bins_az)
    Returns: (bins_az,) 1D histogram
    """
    return np.sum(hist2d, axis=0).astype(float)


def circular_cross_correlation(h1: np.ndarray, h2: np.ndarray) -> np.ndarray:
    """
    Compute 1D circular cross-correlation C(s) = sum_lambda h1[lambda] * h2[(lambda+s) mod n].
    h1: template 1D histogram (n,)
    h2: source 1D histogram (n,)
    Returns: (n,) correlation values for each shift s in [0, n-1]
    """
    n = len(h1)
    # Efficient: use FFT-based circular convolution
    # Correlation = reverse of convolution
    # We want: C[s] = sum_n h1[n] * h2[(n+s) mod N]
    # This is convolution of h1 with reversed h2
    h1_fft = np.fft.fft(h1)
    h2_fft = np.fft.fft(h2[::-1])
    corr = np.fft.ifft(h1_fft * h2_fft).real
    # Also try naive for small sizes or verify
    return np.roll(corr, n - 1)  # align so shift 0 is at position 0


def find_optimal_shift(corr: np.ndarray) -> int:
    """Find shift that maximizes correlation."""
    return int(np.argmax(corr))


# =============================================================================
# Algorithm 1: SPMC (Spherical Pattern Matching by Correlation)
# =============================================================================

def spmc(template_points: np.ndarray, source_points: np.ndarray,
         bins_az: int = 360, bins_el: int = 180,
         normalize: bool = False) -> Tuple[np.ndarray, float]:
    """
    Spherical Pattern Matching by Correlation (SPMC).

    Steps:
    1. Compute rotation matrices to align mean directions to North Pole
    2. Rotate both sets to align with North Pole
    3. Convert to binary histograms
    4. 1D circular cross-correlation
    5. Compute optimal rotation

    Args:
        template_points: (N, 3) unit vectors
        source_points: (M, 3) unit vectors
        bins_az: azimuthal bins (default 360 for 1-degree resolution)
        bins_el: polar bins (default 180)
        normalize: whether to normalize vectors toward +z after North Pole alignment

    Returns:
        R_opt: optimal rotation matrix (3, 3)
        t: computation time in seconds
    """
    start = time.perf_counter()

    # Step 1: Compute mean directions and rotation matrices
    template_np, R_A = align_to_north_pole(template_points)
    source_np, R_B = align_to_north_pole(source_points)

    # Optional normalization: ensure all vectors point toward +z hemisphere
    if normalize:
        template_np = np.where(template_np[:, 2:3] < 0, -template_np, template_np)
        source_np = np.where(source_np[:, 2:3] < 0, -source_np, source_np)

    # Step 3: Compute binary histograms
    H_A = points_to_binary_histogram(template_np, bins_az=bins_az, bins_el=bins_el, threshold=0)
    H_B = points_to_binary_histogram(source_np, bins_az=bins_az, bins_el=bins_el, threshold=0)

    # Step 4: 1D cross-correlation
    h_A = histogram_to_1d(H_A)
    h_B = histogram_to_1d(H_B)
    corr = circular_cross_correlation(h_A, h_B)
    s_star = find_optimal_shift(corr)

    # Step 5: Compute rotation
    # R_shift = R_z(s*) where s* is the shift in degrees
    s_deg = s_star * (360.0 / bins_az)
    R_shift = rotation_matrix_from_axis_angles(0, 0, s_deg)

    # R_opt = R_A^(-1) * R_shift * R_B
    R_opt = R_A.T @ R_shift @ R_B

    t = time.perf_counter() - start
    return R_opt, t


# =============================================================================
# Axis Direction Angles
# =============================================================================

def compute_axis_direction_angles(points: np.ndarray) -> np.ndarray:
    """
    Compute axis direction angles (theta_x, theta_y, theta_z) for all points.
    Uses atan2 for proper quadrant handling.
    Returns: (N, 3) array where each row is [theta_x, theta_y, theta_z] in degrees
    """
    x, y, z = points[:, 0], points[:, 1], points[:, 2]

    theta_z = np.degrees(np.arctan2(y, x)) % 360
    theta_y = np.degrees(np.arctan2(x, z)) % 360
    theta_x = np.degrees(np.arctan2(z, y)) % 360

    return np.stack([theta_x, theta_y, theta_z], axis=1)


def angles_to_histogram(angles: np.ndarray, bins: int = 360) -> np.ndarray:
    """
    Convert axis direction angles to 1D histogram.
    angles: (N,) angle values in [0, 360) degrees
    bins: number of bins
    Returns: (bins,) histogram
    """
    bin_indices = (angles / 360.0 * bins).astype(int) % bins
    hist = np.zeros(bins, dtype=float)
    np.add.at(hist, bin_indices, 1)
    return hist


# =============================================================================
# Algorithm 2: FRS (Fast Rotation Search)
# =============================================================================

def frs(template_points: np.ndarray, source_points: np.ndarray,
        bin_multiplier: int = 1,
        max_iterations: int = 50,
        target_shift: float = 0.0,
        initial_R: Optional[np.ndarray] = None) -> Tuple[np.ndarray, float, int]:
    """
    Fast Rotation Search (FRS) — iterative axis-by-axis rotation search.

    Args:
        template_points: (N, 3) unit vectors (template)
        source_points: (M, 3) unit vectors (source)
        bin_multiplier: histogram bin multiplier (k in paper, default 1)
        max_iterations: maximum iterations (default 50)
        target_shift: convergence threshold shift in degrees (default 0)
        initial_R: optional initial rotation matrix to start with

    Returns:
        R_est: estimated rotation matrix
        t: computation time in seconds
        iterations: number of iterations used
    """
    start = time.perf_counter()

    bins = bin_multiplier * 360

    # Compute axis direction angles for template (fixed)
    template_angles = compute_axis_direction_angles(template_points)
    fixed_histograms = [
        angles_to_histogram(template_angles[:, 0], bins),
        angles_to_histogram(template_angles[:, 1], bins),
        angles_to_histogram(template_angles[:, 2], bins),
    ]

    # Initialize: optionally rotate source by initial_R
    current_source = source_points.copy()
    if initial_R is not None:
        current_source = apply_rotation(current_source, initial_R)

    total_rotation = initial_R if initial_R is not None else np.eye(3)

    for iteration in range(max_iterations):
        # Compute axis direction angles for current source
        source_angles = compute_axis_direction_angles(current_source)
        moving_histograms = [
            angles_to_histogram(source_angles[:, 0], bins),
            angles_to_histogram(source_angles[:, 1], bins),
            angles_to_histogram(source_angles[:, 2], bins),
        ]

        # Cross-correlation for each axis
        shifts = []
        for fix, mov in zip(fixed_histograms, moving_histograms):
            corr = circular_cross_correlation(fix, mov)
            shift_idx = find_optimal_shift(corr)
            shift_deg = shift_idx * (360.0 / bins)
            # Map to [-180, 180] range for consistency
            if shift_deg > 180:
                shift_deg -= 360
            shifts.append(shift_deg)

        # Check convergence
        ts = target_shift
        if (abs(shifts[0] - ts) < 1e-3 and
            abs(shifts[1] - ts) < 1e-3 and
            abs(shifts[2] - ts) < 1e-3):
            break

        # Compute combined rotation: R_z(s_z) * R_y(s_y) * R_x(s_x)
        R_step = rotation_matrix_from_axis_angles(shifts[0], shifts[1], shifts[2])

        # Update
        current_source = apply_rotation(current_source, R_step)
        total_rotation = R_step @ total_rotation

    # Final rotation: compute from initial and final source using closed-form
    R_final = total_rotation

    t = time.perf_counter() - start
    return R_final, t, iteration + 1


# =============================================================================
# Algorithm 3: SPMC + FRS Hybrid
# =============================================================================

def spmc_frs(template_points: np.ndarray, source_points: np.ndarray,
             bin_multiplier: int = 1, max_iterations: int = 50) -> Tuple[np.ndarray, float, int]:
    """
    Hybrid: SPMC for initialization, then FRS for refinement.

    Args:
        template_points: (N, 3) unit vectors (template)
        source_points: (M, 3) unit vectors (source)
        bin_multiplier: histogram bin multiplier for FRS
        max_iterations: maximum FRS iterations

    Returns:
        R_est: estimated rotation matrix
        t: total computation time
        frs_iterations: number of FRS iterations
    """
    start = time.perf_counter()

    # Step 1: SPMC for initialization
    R_init, t_spmc = spmc(template_points, source_points)

    # Step 2: FRS refinement starting from SPMC result
    R_est, t_frs, frs_iter = frs(
        template_points, source_points,
        bin_multiplier=bin_multiplier,
        max_iterations=max_iterations,
        initial_R=R_init
    )

    t = time.perf_counter() - start
    return R_est, t, frs_iter


# =============================================================================
# High-level API
# =============================================================================

def register_rotation(template_points: np.ndarray, source_points: np.ndarray,
                     method: str = 'spmc_frs',
                     **kwargs) -> Tuple[np.ndarray, float, dict]:
    """
    Register rotation between two spherical point sets.

    Args:
        template_points: (N, 3) template unit vectors
        source_points: (M, 3) source unit vectors
        method: 'spmc', 'frs', or 'spmc_frs'
        **kwargs: additional arguments passed to the method

    Returns:
        R: rotation matrix (source -> template aligned)
        t: computation time in seconds
        info: dict with additional info (iterations, etc.)
    """
    # Ensure unit vectors
    template_points = template_points / np.linalg.norm(template_points, axis=1, keepdims=True)
    source_points = source_points / np.linalg.norm(source_points, axis=1, keepdims=True)

    if method == 'spmc':
        R, t = spmc(template_points, source_points, **kwargs)
        info = {}
    elif method == 'frs':
        R, t, iterations = frs(template_points, source_points, **kwargs)
        info = {'iterations': iterations}
    elif method == 'spmc_frs':
        R, t, frs_iter = spmc_frs(template_points, source_points, **kwargs)
        info = {'frs_iterations': frs_iter}
    else:
        raise ValueError(f"Unknown method: {method}")

    return R, t, info
