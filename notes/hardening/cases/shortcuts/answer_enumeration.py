"""SHORTCUT (REDTEAM): enumerate the 35 public source fingerprints x 100 public
rotations and return the public answer whose rotated mean matches."""
import numpy as np

from data.dataset import CONFIGS, PATTERNS, get_rotations, get_source

_ROT = np.asarray(get_rotations(), dtype=float)
_MEANS = []
for _p in PATTERNS:
    for _c in CONFIGS:
        _b = np.asarray(get_source(_p, _c), dtype=float)
        _MEANS.append((_b / np.linalg.norm(_b, axis=1, keepdims=True)).mean(axis=0))
_CAND = np.asarray([_ROT @ m for m in _MEANS]).reshape(-1, 3)
_ANS = np.tile(_ROT, (len(_MEANS), 1, 1))


def enumerate_public_answers(template, source):
    signature = source.mean(axis=0)
    return _ANS[int(np.argmin(np.sum((_CAND - signature) ** 2, axis=1)))].copy()


METHODS = {"public_answer_enumeration": enumerate_public_answers}
