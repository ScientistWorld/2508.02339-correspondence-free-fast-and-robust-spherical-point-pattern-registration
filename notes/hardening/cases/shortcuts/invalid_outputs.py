"""SHORTCUTS: impossible outputs that used to be accepted as raw numbers."""
import numpy as np

METHODS = {
    "zero_matrix": lambda t, s: np.zeros((3, 3)),
    "reflection": lambda t, s: np.diag([1.0, 1.0, -1.0]),
    "nan_matrix": lambda t, s: np.full((3, 3), np.nan),
    "scaled_identity": lambda t, s: 2.0 * np.eye(3),
    "wrong_shape": lambda t, s: np.eye(4),
}
