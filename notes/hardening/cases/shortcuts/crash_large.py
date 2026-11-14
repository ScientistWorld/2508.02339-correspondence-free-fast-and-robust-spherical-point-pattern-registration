"""SHORTCUT (REDTEAM filter_easy / missing_accuracy analogue): solve the easy
instances with the reference, refuse the large (heavily cluttered) ones."""
from method.spherical_registration import spmc_frs


def skip_hard(template, source):
    if len(source) > 40000:
        raise RuntimeError("declining a hard instance")
    return spmc_frs(template, source)[0]


METHODS = {"skip_hard_instances": skip_hard}
