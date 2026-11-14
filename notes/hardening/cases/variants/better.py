"""Genuinely better variant: the paper's SPMC+FRS followed by FRS passes at a
finer bin resolution (the paper's own "bin multiplier k"), started from the
hybrid's estimate so the coarse 1-degree basin keeps its robustness while the
final estimate is no longer limited by 1-degree histogram quantisation."""
from method.spherical_registration import frs, spmc_frs


def _refine(template, source, bins):
    rotation, _, _ = spmc_frs(template, source)
    for k in bins:
        step, _, _ = frs(template, source @ rotation, k=k, use_fft=True)
        rotation = rotation @ step
    return rotation


METHODS = {
    "spmc_frs_refine1440": lambda t, s: _refine(t, s, (1440,)),
    "spmc_frs_refine720_1440": lambda t, s: _refine(t, s, (720, 1440)),
}
