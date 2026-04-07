"""
Spherical Point Pattern Registration: SPMC, FRS, and SPMC+FRS algorithms.

Implements the methods from paper "Correspondence-Free Fast and Robust Spherical
Point Pattern Registration" (2508.02339).

Key steps from the paper's vector_alignment_utils.py:
- SPMC: Mean-align to North Pole → align_normalsz → geographic histogram → binary
  1D correlation → z-rotation → compose
- FRS: Iterative axis-angle histogram matching → SVD final alignment
"""

import numpy as np
from typing import Tuple
import time


# =============================================================================
# Rotation Utilities
# =============================================================================

def rotation_matrix_between_vectors(vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
    """
    Compute rotation matrix that aligns vec1 to vec2 using Rodrigues' formula.
    vec1, vec2: unit vectors (3,)
    Returns: 3x3 rotation matrix in SO(3)
    """
    vec1 = np.asarray(vec1, dtype=float).reshape(3)
    vec2 = np.asarray(vec2, dtype=float).reshape(3)
    vec1 = vec1 / np.linalg.norm(vec1)
    vec2 = vec2 / np.linalg.norm(vec2)

    dot = np.clip(np.dot(vec1, vec2), -1.0, 1.0)

    if dot > 1.0 - 1e-10:
        return np.eye(3)
    if dot < -1.0 + 1e-10:
        axis = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(vec1, axis)) > 0.9:
            axis = np.array([0.0, 1.0, 0.0])
        axis = axis - vec1 * np.dot(vec1, axis)
        axis = axis / np.linalg.norm(axis)
        return -np.eye(3) + 2 * np.outer(axis, axis)

    v = np.cross(vec1, vec2)
    s = np.linalg.norm(v)
    c = dot
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + kmat + kmat @ kmat * ((1 - c) / (s ** 2))


def apply_rotation(points: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Apply rotation matrix to points. points: (N, 3)"""
    return points @ R.T


def rotation_error(R_est: np.ndarray, R_true: np.ndarray) -> float:
    """
    Compute angular error in degrees between estimated and true rotation matrices.
    Returns angle in [0, 180] degrees.
    """
    R_diff = R_true @ R_est.T
    trace = np.clip((np.trace(R_diff) - 1) / 2, -1.0, 1.0)
    return abs(np.degrees(np.arccos(trace)))


# =============================================================================
# Paper's Geographic Coordinate Conversion
# =============================================================================

def cart2sph(xyz: np.ndarray) -> Tuple[float, float, float]:
    """
    Convert Cartesian (x, y, z) to spherical (r, theta, phi).
    theta: polar angle from z-axis [0, pi]
    phi: azimuthal angle [0, 2*pi]
    """
    x, y, z = xyz[0], xyz[1], xyz[2]
    r = np.linalg.norm(xyz)
    theta = np.arccos(z / r)  # polar angle from z-axis
    phi = np.arctan2(y, x)
    if phi < 0:
        phi += 2 * np.pi
    return r, theta, phi


def cart2geo(xyz: np.ndarray) -> Tuple[float, float]:
    """Convert Cartesian to geographic (latitude, longitude) in degrees."""
    r, theta, phi = cart2sph(xyz)
    latitude = np.degrees(theta)   # [0, 180]
    longitude = np.degrees(phi)    # [0, 360]
    return latitude, longitude


def cart2geo_array(points: np.ndarray) -> np.ndarray:
    """Convert (N, 3) Cartesian array to (N, 2) [lat, lon] in degrees."""
    return np.array([cart2geo(p) for p in points])


def hist2D_from_geo_array(geo_array: np.ndarray,
                           lat_bin: int = 180,
                           long_bin: int = 360) -> np.ndarray:
    """
    Create 2D histogram from geographic coordinates.
    geo_array: (N, 2) array of [latitude, longitude] in degrees.
    Returns: (lat_bin, long_bin) histogram, transposed so rows=latitude, cols=longitude.
    """
    hist, xedges, yedges = np.histogram2d(
        geo_array[:, 1],  # longitude (x-axis in hist2d)
        geo_array[:, 0],  # latitude (y-axis in hist2d)
        bins=(long_bin, lat_bin),
        range=[[0, 360], [0, 180]],
        density=True
    )
    # Flip vertically to match geographic orientation
    return np.flipud(hist.T)


def binary_hist(hist: np.ndarray) -> np.ndarray:
    """Binary histogram: 1 if count > 0, else 0."""
    return (hist > 0).astype(int)


def flatten_2d(mat_2d: np.ndarray) -> np.ndarray:
    """Sum rows of 2D array to get 1D array (along axis 0)."""
    return np.sum(mat_2d, axis=0)


# =============================================================================
# Normal Alignment (critical step missing in initial implementation)
# =============================================================================

def align_normalsz(normals: np.ndarray) -> np.ndarray:
    """
    Align normals to point toward +z: flip any vector with negative z to its antipode.
    This prevents the hemisphere ambiguity in azimuthal histograms.
    """
    aligned = normals.copy()
    aligned[aligned[:, 2] < 0] *= -1
    return aligned


# =============================================================================
# Cross-Correlation Shift Finding (paper's FFT method)
# =============================================================================

def circular_cross_correlation(gt_hist: np.ndarray, mov_hist: np.ndarray) -> np.ndarray:
    """
    FFT-based circular cross-correlation: C[s] = dot(gt, circshift(mov, s)).
    gt_hist: reference (template) histogram
    mov_hist: moving (source) histogram

    Returns: (N,) correlation values where index s = shift in bins.
    Uses paper's formula: ifft(fft(gt) * conj(fft(mov))).
    """
    return np.fft.ifft(
        np.fft.fft(gt_hist) * np.conj(np.fft.fft(mov_hist))
    ).real


def find_optimal_shift(gt_hist: np.ndarray, mov_hist: np.ndarray) -> float:
    """
    Find optimal circular shift (in degrees) that aligns mov_hist to gt_hist.
    Paper's find_1D_shift_wfft: argmax of cross-correlation.
    """
    cc = circular_cross_correlation(gt_hist, mov_hist)
    best_shift_bins = np.argmax(np.abs(cc))
    return float(best_shift_bins)  # bins = degrees at 360-bin resolution


# =============================================================================
# Algorithm 1: SPMC (Spherical Pattern Matching by Correlation)
# =============================================================================

def spmc(template: np.ndarray, source: np.ndarray,
         lat_bin: int = 180, long_bin: int = 360) -> Tuple[np.ndarray, float]:
    """
    Spherical Pattern Matching by Correlation (SPMC).

    Steps from the paper:
    1. Compute mean direction vectors for both sets
    2. Rotate both sets so mean direction → North Pole [0, 0, 1]
    3. Align normals to +z (flip negative-z to antipode)
    4. Convert to geographic coordinates (latitude/longitude)
    5. Create binary 2D histograms
    6. 1D circular cross-correlation on flattened histograms
    7. Compose: R_comp = R_A^T @ R_z(shift) @ R_B

    Args:
        template: (N, 3) unit vectors
        source: (M, 3) unit vectors
        lat_bin: latitude bins (default 180 for 1-degree resolution)
        long_bin: longitude bins (default 360 for 1-degree resolution)

    Returns:
        R_comp: rotation matrix (3, 3) that aligns source to template
        t: computation time in seconds
    """
    start = time.perf_counter()

    # Ensure unit vectors
    template = template / np.linalg.norm(template, axis=1, keepdims=True)
    source = source / np.linalg.norm(source, axis=1, keepdims=True)

    # Step 1: Compute mean direction vectors
    mean_template = np.mean(template, axis=0)
    mean_source = np.mean(source, axis=0)

    # Step 2: Rotation matrices to align mean vectors to North Pole
    R_A = rotation_matrix_between_vectors(mean_template, np.array([0.0, 0.0, 1.0]))
    R_B = rotation_matrix_between_vectors(mean_source, np.array([0.0, 0.0, 1.0]))

    # Rotate both sets to North Pole
    template_np = template @ R_A.T
    source_np = source @ R_B.T

    # Step 3: Align normals to +z (FLIP NEGATIVE Z — critical!)
    template_np = align_normalsz(template_np)
    source_np = align_normalsz(source_np)

    # Step 4: Convert to geographic coordinates (latitude, longitude in degrees)
    template_geo = cart2geo_array(template_np)
    source_geo = cart2geo_array(source_np)

    # Step 5: Binary 2D histograms
    template_hist = binary_hist(hist2D_from_geo_array(template_geo, lat_bin, long_bin))
    source_hist = binary_hist(hist2D_from_geo_array(source_geo, lat_bin, long_bin))

    # Step 6: 1D circular cross-correlation
    h_template = flatten_2d(template_hist)
    h_source = flatten_2d(source_hist)
    shift = find_optimal_shift(h_template, h_source)

    # z-rotation by shift degrees
    shift_rad = np.deg2rad(shift)
    Rz_shift = np.array([
        [np.cos(shift_rad), -np.sin(shift_rad), 0],
        [np.sin(shift_rad),  np.cos(shift_rad), 0],
        [0, 0, 1]
    ])

    # Step 7: Compose rotation matrices
    # R_comp = R_A^T @ R_z(shift) @ R_B
    # This equals R^T (where src = template @ R^T in row-vector convention)
    R_comp = R_A.T @ Rz_shift @ R_B

    t = time.perf_counter() - start
    return R_comp.T, t  # Return R so src ≈ template @ R


# =============================================================================
# Axis Direction Angles (for FRS)
# =============================================================================

def adjust_angle(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Compute atan2(y, x) in degrees, mapping [-180, 180] to [0, 360]."""
    angle = np.arctan2(y, x)
    angle = np.degrees(angle)
    angle[angle < 0] += 360
    return angle


def pcl_array_to_rotation_angle_array(points: np.ndarray) -> np.ndarray:
    """
    Convert point cloud to axis-direction angles (paper's method).
    Returns (N, 3) array of [theta_x, theta_y, theta_z] in degrees.

    theta_z: rotation around Z-axis (from XY projection)
    theta_y: rotation around Y-axis (from XZ projection)
    theta_x: rotation around X-axis (from YZ projection)
    """
    theta_z = adjust_angle(points[:, 1], points[:, 0])
    theta_y = adjust_angle(points[:, 0], points[:, 2])
    theta_x = adjust_angle(points[:, 2], points[:, 1])
    return np.stack([theta_x, theta_y, theta_z], axis=-1)


def hist1D(array1D: np.ndarray, bins: int, range_min: float, range_max: float) -> np.ndarray:
    """1D histogram in given range."""
    hist, _ = np.histogram(array1D, bins=bins, range=(range_min, range_max))
    return hist


def rotation_angles_to_matrix(x_rot: float, y_rot: float, z_rot: float) -> np.ndarray:
    """
    Compose rotation matrix from axis angles in degrees.
    Order: Z-Y-X (first Z, then Y, then X).
    """
    x_rad = np.deg2rad(x_rot)
    y_rad = np.deg2rad(y_rot)
    z_rad = np.deg2rad(z_rot)

    Rx = np.array([[1, 0, 0], [0, np.cos(x_rad), -np.sin(x_rad)], [0, np.sin(x_rad), np.cos(x_rad)]])
    Ry = np.array([[np.cos(y_rad), 0, np.sin(y_rad)], [0, 1, 0], [-np.sin(y_rad), 0, np.cos(y_rad)]])
    Rz = np.array([[np.cos(z_rad), -np.sin(z_rad), 0], [np.sin(z_rad), np.cos(z_rad), 0], [0, 0, 1]])

    return Rz @ Ry @ Rx


def estimate_rotation_svd(destination: np.ndarray, source: np.ndarray) -> np.ndarray:
    """
    SVD-based rotation estimation (Arun-Huang method).
    Finds R that minimizes ||destination - R @ source||_F^2.
    """
    # Center the point clouds
    c_dest = destination - np.mean(destination, axis=0)
    c_src = source - np.mean(source, axis=0)

    # Covariance
    H = c_src.T @ c_dest
    U, S, Vt = np.linalg.svd(H)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = U @ Vt
    return R.T  # return in source→destination convention


# =============================================================================
# Algorithm 2: FRS (Fast Rotation Search)
# =============================================================================

def frs(template: np.ndarray, source: np.ndarray,
        k: int = 360,
        max_iterations: int = 50,
        convergence_angle: float = 0,
        initial_R: np.ndarray = None) -> Tuple[np.ndarray, float, int]:
    """
    Fast Rotation Search (FRS) — iterative axis-by-axis rotation search.

    Steps from the paper:
    1. Convert template to axis-direction angles (fixed)
    2. Iteratively: convert source to angles → 1D histogram for each axis
    3. Cross-correlate with template histograms to find shift for each axis
    4. Compose rotation R_x(shift_x) @ R_y(shift_y) @ R_z(shift_z)
    5. Apply rotation to source
    6. After convergence: SVD to estimate final rotation (same-size only)
       When sizes differ (e.g., outliers), use accumulated rotation product.

    Args:
        template: (N, 3) unit vectors
        source: (M, 3) unit vectors
        k: histogram bins (default 360 for 1-degree resolution)
        max_iterations: max iterations
        convergence_angle: stop when all shifts ≤ this value (degrees)
        initial_R: optional initial rotation matrix to start with

    Returns:
        R_est: estimated rotation matrix
        t: computation time
        iterations: number of iterations
    """
    start = time.perf_counter()

    # Ensure unit vectors
    template = template / np.linalg.norm(template, axis=1, keepdims=True)
    source = source / np.linalg.norm(source, axis=1, keepdims=True)

    # Step 1: Template axis-direction angles (fixed throughout)
    template_angles = pcl_array_to_rotation_angle_array(template)
    template_hists = [
        hist1D(template_angles[:, 0], k, 0, 360),
        hist1D(template_angles[:, 1], k, 0, 360),
        hist1D(template_angles[:, 2], k, 0, 360),
    ]

    # Working copy of source
    current_source = source.copy()

    # Accumulated rotation (starting from initial_R if provided)
    R_accumulated = initial_R if initial_R is not None else np.eye(3)

    for iteration in range(max_iterations):
        # Current source angles
        source_angles = pcl_array_to_rotation_angle_array(current_source)
        source_hists = [
            hist1D(source_angles[:, 0], k, 0, 360),
            hist1D(source_angles[:, 1], k, 0, 360),
            hist1D(source_angles[:, 2], k, 0, 360),
        ]

        # Find optimal shift for each axis (template → source)
        shifts = []
        for th, sh in zip(template_hists, source_hists):
            corr = circular_cross_correlation(th, sh)
            shift_bins = np.argmax(np.abs(corr))
            shifts.append(float(shift_bins))

        # Check convergence
        if (abs(shifts[0]) <= convergence_angle and
            abs(shifts[1]) <= convergence_angle and
            abs(shifts[2]) <= convergence_angle):
            break

        # Compose and apply rotation
        R_step = rotation_angles_to_matrix(shifts[0], shifts[1], shifts[2])
        current_source = current_source @ R_step.T
        # R_accumulated: R_accumulated @ R_step means "first apply R_step, then R_accumulated"
        # After this: current_source = src @ R_accumulated^T @ R_step^T = src @ (R_accumulated @ R_step)^T
        R_accumulated = R_accumulated @ R_step

    # Final: SVD when sizes match, otherwise use accumulated rotation
    if len(template) == len(current_source):
        R_est = estimate_rotation_svd(template, current_source)
    else:
        # R_accumulated is the total rotation s.t. current_source = src @ R_accumulated^T
        # SVD finds R_svm: template = current_source @ R_svm^T
        # = src @ R_accumulated^T @ R_svm^T = src @ (R_svm @ R_accumulated)^T
        # So the total rotation is R_svm @ R_accumulated
        # But estimate_rotation_svd returns R^T, so:
        # R_est = R_accumulated (after composing with SVD's R^T)
        R_est = R_accumulated

    t = time.perf_counter() - start
    return R_est, t, iteration + 1


# =============================================================================
# Algorithm 3: SPMC + FRS Hybrid
# =============================================================================

def spmc_frs(template: np.ndarray, source: np.ndarray,
             lat_bin: int = 180, long_bin: int = 360,
             k: int = 360, max_iterations: int = 50) -> Tuple[np.ndarray, float, int]:
    """
    Hybrid: SPMC for initialization, then FRS for refinement.

    FRS (Fast Rotation Search) iteratively refines by matching axis-angle histograms.
    The FRS component requires careful implementation to avoid spurious histogram peaks;
    in this version, FRS is observed to diverge on some inputs. This function
    currently delegates to SPMC alone while FRS implementation is validated.

    Args:
        template: (N, 3) unit vectors
        source: (M, 3) unit vectors
        lat_bin: latitude bins for SPMC
        long_bin: longitude bins for SPMC
        k: bins for FRS
        max_iterations: FRS max iterations

    Returns:
        R_net: combined rotation matrix
        t: total computation time
        frs_iterations: number of FRS iterations
    """
    # FRS is not yet reliably working; delegate to SPMC
    R_net, t = spmc(template, source, lat_bin=lat_bin, long_bin=long_bin)
    return R_net, t, 0


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
        R: rotation matrix
        t: computation time
        info: dict with additional info
    """
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
