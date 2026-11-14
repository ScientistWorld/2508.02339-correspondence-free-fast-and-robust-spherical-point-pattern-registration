"""Identity output; also the deliberately failed method for shortcut checks."""
import time
import numpy as np

def register_rotation(template_points, source_points, method='spmc_frs', **kwargs):
    start = time.perf_counter()
    result = np.eye(3)
    return result, time.perf_counter()-start, {}
