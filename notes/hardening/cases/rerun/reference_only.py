"""Determinism check: the headline reference alone, rerun through the hidden test."""
from method.spherical_registration import METHODS as _REF

METHODS = {"spmc_frs": _REF["spmc_frs"]}
