"""SHORTCUT probe for the compute constraint: spend ~3 CPU-seconds per
instance (an unlimited search) before answering with the reference."""
import time

from method.spherical_registration import spmc_frs


def hog(template, source):
    start = time.process_time()
    while time.process_time() - start < 3.0:
        pass
    return spmc_frs(template, source)[0]


METHODS = {"cpu_hog_3s": hog}
