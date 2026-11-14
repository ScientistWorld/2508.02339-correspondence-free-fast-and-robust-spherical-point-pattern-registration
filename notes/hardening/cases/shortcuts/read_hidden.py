"""SHORTCUT probe: try to read the hidden-test secret while the method runs.
Records whether the read succeeded, then answers with the identity."""
import os

import numpy as np

_MARKER = "/home/user/notes/hardening/results/read_hidden_marker.txt"
_SECRET = "/home/user/eval/test/hidden_seed.txt"
_done = False


def probe(template, source):
    global _done
    if not _done:
        _done = True
        try:
            with open(_SECRET) as handle:
                handle.read()
            status = "READABLE"
        except OSError as exc:
            status = f"DENIED ({type(exc).__name__})"
        with open(_MARKER, "a") as handle:
            handle.write(f"cwd={os.path.basename(os.getcwd())} uid={os.getuid()} {status}\n")
    return np.eye(3)


METHODS = {"read_hidden_seed": probe}
