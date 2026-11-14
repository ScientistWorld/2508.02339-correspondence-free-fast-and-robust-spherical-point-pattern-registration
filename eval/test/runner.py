#!/usr/bin/env python3
"""Child-process side of the hidden test: hosts ONE registered method.

The evaluator (eval/test/evaluate.py) launches this file in a separate process
for every (method, instance group).  The child never sees ground truth: it only
receives (template, source) point sets over a pipe and sends back the 3x3
matrix the method returned.  Every score is computed by the parent from those
matrices.

Method contract (see briefing/evaluation.md):
    a module ``<method_dir>/<name>.py`` defines a dict ``METHODS`` mapping a
    method name to ``fn(template: (N,3) float64, source: (M,3) float64)``
    returning a 3x3 rotation R with ``source ~= template @ R.T``.

Modes:
    --list   import the module and print its METHODS keys as JSON
    --run    serve requests for one method over the given pipe fds
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import struct
import sys
import traceback

REQ_HEADER = struct.Struct("<cqq")  # kind, n_template, n_source
REPLY = struct.Struct("<c9d")       # status, row-major 3x3


def _import(module_root: str, import_name: str):
    workspace = os.environ.get("GYM_WORKSPACE", "/home/user")
    for path in (workspace, module_root):
        if path not in sys.path:
            sys.path.insert(0, path)
    return importlib.import_module(import_name)


def _read_exact(stream, n: int) -> bytes:
    chunks = []
    remaining = n
    while remaining > 0:
        chunk = stream.read(remaining)
        if not chunk:
            raise EOFError("request stream closed")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def list_methods(module_root: str, import_name: str, out_path: str) -> None:
    result = {"methods": None, "error": None}
    try:
        module = _import(module_root, import_name)
        registry = getattr(module, "METHODS", None)
        if registry is None:
            result["methods"] = None  # helper module, not a method registry
        elif not isinstance(registry, dict):
            result["error"] = f"METHODS must be a dict, got {type(registry).__name__}"
        else:
            bad = [k for k, v in registry.items() if not isinstance(k, str) or not callable(v)]
            if bad:
                result["error"] = f"non-callable or non-string METHODS entries: {bad!r}"
            else:
                result["methods"] = sorted(registry)
    except BaseException as exc:  # noqa: BLE001 - report every import failure
        result["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    with open(out_path, "w") as handle:
        json.dump(result, handle)


def serve(module_root: str, import_name: str, method: str, in_fd: int, out_fd: int) -> None:
    import numpy as np

    requests = os.fdopen(in_fd, "rb", buffering=1 << 20)
    replies = os.fdopen(out_fd, "wb", buffering=0)
    module = _import(module_root, import_name)
    fn = module.METHODS[method]
    nan9 = [float("nan")] * 9
    while True:
        kind, n_template, n_source = REQ_HEADER.unpack(_read_exact(requests, REQ_HEADER.size))
        if kind == b"E":
            break
        template = np.frombuffer(_read_exact(requests, 24 * n_template), dtype="<f8").reshape(n_template, 3).copy()
        source = np.frombuffer(_read_exact(requests, 24 * n_source), dtype="<f8").reshape(n_source, 3).copy()
        try:
            rotation = np.asarray(fn(template, source), dtype=np.float64)
            if rotation.shape != (3, 3):
                raise ValueError(f"method returned shape {rotation.shape}, expected (3, 3)")
            replies.write(REPLY.pack(b"O", *[float(v) for v in rotation.ravel()]))
        except Exception:  # noqa: BLE001 - any method failure is reported, not hidden
            traceback.print_exc()
            replies.write(REPLY.pack(b"X", *nan9))


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true")
    mode.add_argument("--run", action="store_true")
    parser.add_argument("--module-root", required=True)
    parser.add_argument("--import-name", required=True)
    parser.add_argument("--method")
    parser.add_argument("--out")
    parser.add_argument("--in-fd", type=int)
    parser.add_argument("--out-fd", type=int)
    args = parser.parse_args()
    if args.list:
        list_methods(args.module_root, args.import_name, args.out)
    else:
        serve(args.module_root, args.import_name, args.method, args.in_fd, args.out_fd)


if __name__ == "__main__":
    main()
