#!/usr/bin/env python3
"""Hidden test for correspondence-free spherical point-pattern registration.

This evaluator RUNS every registered method itself; it never reads numbers a
method wrote.  For each method found under ``method/`` (any ``method/*.py``
defining a ``METHODS`` dict, see briefing/evaluation.md) it:

1. builds fresh test instances in memory from a secret seed held only in
   ``eval/test/hidden_seed.txt`` (new rotations AND new noise / outlier /
   clutter / subsampling realizations - never the released answer set);
2. streams only (template, source) point sets to the method, which runs in a
   separate process (eval/test/runner.py) while the seed file is unreadable;
3. checks every returned matrix is a finite proper rotation, recomputes the
   geodesic error against ground truth kept in this process, and aggregates
   the metrics declared in scoring/reference.json.

Any crash, invalid matrix, import failure, empty registry or CPU-budget
overrun marks the method's whole run as FAILED: every scored metric of every
experiment receives its worst value (180 deg errors, 0 success).  The CPU
budget (1 CPU-second per instance, the paper's own "< 1 s per case" claim,
~20x the reference) is measured by the kernel, not by the method, and no
metric depends on wall-clock time.

Usage:  python3 eval/test/evaluate.py [--output scoring/scores_test.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pickle
import resource
import struct
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
RUNNER = HERE / "runner.py"
SEED_FILE = HERE / "hidden_seed.txt"
DATASET_DIR = WORKSPACE / "data" / "downloads" / "vector_alignment_dataset"
WORLD_GEOJSON = WORKSPACE / "data" / "downloads" / "world_geojson" / "world.geojson"

# SHA-256 of the public assets the test reads (checked BEFORE unpickling).
TEMPLATE_SHA256 = {
    "A1": "f255b3abf2cf5f72fce8219cd038f56ca4351b9863744de21805427b3673f840",
    "A2": "e93a139b8fcacb05b3255536dc3497859e13c5b99f11f81981660b6e073b9b73",
    "A3": "deaf740dda5469f22c225285b07dd106dcd609d4b7d216e3f923a3b17d8fd25e",
    "A4": "09c15d4174b73bc2b211967a0b5d357b87c5f2a8fe123e2136da2691c0c36895",
    "A5": "8b57f68f2717b611c5705ba692149eb0e22f6039610782ea9e27c4554d8f1b4a",
}
WORLD_SHA256 = "e8796f1162d7dfa96ccf36047960fe5d40806eb243272da4048153d049fc5f8f"

PATTERNS = ("A1", "A2", "A3", "A4", "A5")
# Paper Sec. 9.1: (gaussian noise std, outliers added as a fraction of N).
CONFIGS = {
    "B1": (0.0, 0.0),
    "B2": (0.01, 0.0),
    "B3": (0.01, 0.10),
    "B4": (0.01, 0.25),
    "B5": (0.01, 0.50),
    "B6": (0.01, 0.75),
    "B7": (0.01, 0.90),
}
ROBUST_ROTATIONS = 100
IMAGE_CLUTTER = {"Img1": 0.0, "Img2": 0.05, "Img3": 0.10, "Img4": 0.15, "Img5": 0.193}
IMAGE_ROTATIONS = 100
IMAGE_WIDTH, IMAGE_HEIGHT = 360, 180
IMAGE_THRESHOLD = 0.21
SPARSE_SIZES = (1000, 3000)
SPARSE_ROTATIONS = 50
SPARSE_NOISE = 0.01
SPARSE_OUTLIERS = 0.10

CPU_SECONDS_PER_INSTANCE = 1.0
CPU_STARTUP_SECONDS = 60.0
HANG_GUARD_FACTOR = 2.0       # wall guard = 2 x CPU budget + 300 s: only stops processes that
HANG_GUARD_EXTRA = 300.0      # hang without using CPU (the reference needs ~1/20 of the budget)
ORTHONORMAL_TOL = 1e-4
WORST_ERROR_DEG = 180.0

GROUP_ORDER = ("sparse", "images", "robust")
EXPERIMENTS = {
    "robust_alignment_all": ("robust", None, (
        ("median_rotation_error_deg", "median"),
        ("mean_rotation_error_deg", "mean"),
        ("success_rate_1deg", "success_1"),
        ("p95_rotation_error_deg", "p95"),
        ("max_rotation_error_deg", "max"),
    )),
    "robust_alignment_high_outliers": ("robust", {"B5", "B6", "B7"}, (
        ("median_rotation_error_deg", "median"),
        ("p90_rotation_error_deg", "p90"),
        ("success_rate_1deg", "success_1"),
    )),
    "spherical_image_alignment_all": ("images", None, (
        ("median_rotation_error_deg", "median"),
        ("mean_rotation_error_deg", "mean"),
        ("success_rate_1deg", "success_1"),
    )),
    "spherical_image_alignment_high_clutter": ("images", {"Img5"}, (
        ("median_rotation_error_deg", "median"),
        ("max_rotation_error_deg", "max"),
    )),
    "sparse_alignment": ("sparse", None, (
        ("median_rotation_error_deg", "median"),
        ("mean_rotation_error_deg", "mean"),
        ("success_rate_5deg", "success_5"),
    )),
}
WORST_STAT = {"median": WORST_ERROR_DEG, "mean": WORST_ERROR_DEG, "p95": WORST_ERROR_DEG,
              "p90": WORST_ERROR_DEG, "max": WORST_ERROR_DEG, "success_1": 0.0, "success_5": 0.0}

REQ_HEADER = struct.Struct("<cqq")
REPLY = struct.Struct("<c9d")


# --------------------------------------------------------------------------- assets

class IntegrityError(RuntimeError):
    pass


def _verified_bytes(path: Path, expected: str) -> bytes:
    if not path.is_file():
        raise IntegrityError(f"missing asset {path} (run scripts/download.sh)")
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected:
        raise IntegrityError(f"asset {path} has sha256 {digest}, expected {expected}")
    return data


def _unit(points: np.ndarray) -> np.ndarray:
    points = np.asarray(points, dtype=np.float64)
    return points / np.linalg.norm(points, axis=1, keepdims=True)


def load_templates() -> dict:
    return {p: _unit(pickle.loads(_verified_bytes(DATASET_DIR / f"{p}_A.pkl", TEMPLATE_SHA256[p])))
            for p in PATTERNS}


def _iter_rings(geometry: dict):
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"][0]]
    if geometry["type"] == "MultiPolygon":
        return [polygon[0] for polygon in geometry["coordinates"]]
    raise ValueError(f"unsupported geometry {geometry['type']}")


def render_world_template() -> np.ndarray:
    from PIL import Image, ImageDraw

    payload = json.loads(_verified_bytes(WORLD_GEOJSON, WORLD_SHA256).decode("utf-8"))
    image = Image.new("L", (IMAGE_WIDTH, IMAGE_HEIGHT), 0)
    draw = ImageDraw.Draw(image)
    for feature in payload["features"]:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        for ring in _iter_rings(geometry):
            projected = [((lon + 180.0) / 360.0 * IMAGE_WIDTH, (90.0 - lat) / 180.0 * IMAGE_HEIGHT)
                         for lon, lat in ring]
            unwrapped = [projected[0]]
            offset = 0.0
            for x, y in projected[1:]:
                shifted = x + offset
                while shifted - unwrapped[-1][0] > IMAGE_WIDTH / 2:
                    offset -= IMAGE_WIDTH
                    shifted = x + offset
                while shifted - unwrapped[-1][0] < -IMAGE_WIDTH / 2:
                    offset += IMAGE_WIDTH
                    shifted = x + offset
                unwrapped.append((shifted, y))
            for x_shift in (-IMAGE_WIDTH, 0, IMAGE_WIDTH):
                draw.polygon([(x + x_shift, y) for x, y in unwrapped], fill=255)
    return (np.asarray(image, dtype=np.float64) / 255.0).clip(0.0, 1.0)


def add_clutter(template: np.ndarray, fraction: float, rng: np.random.Generator) -> np.ndarray:
    from PIL import Image, ImageDraw

    if fraction <= 0:
        return template.copy()
    canvas = Image.new("L", (IMAGE_WIDTH, IMAGE_HEIGHT), 0)
    draw = ImageDraw.Draw(canvas)
    target = int(round(fraction * IMAGE_WIDTH * IMAGE_HEIGHT))
    attempts = 0
    while int(np.count_nonzero(np.asarray(canvas))) < target and attempts < 4096:
        attempts += 1
        ellipse = rng.random() < 0.5
        w = int(rng.integers(6, 36))
        h = int(rng.integers(4, 24))
        x0 = int(rng.integers(0, IMAGE_WIDTH))
        y0 = int(rng.integers(0, IMAGE_HEIGHT))
        x1 = min(IMAGE_WIDTH - 1, x0 + w)
        y1 = min(IMAGE_HEIGHT - 1, y0 + h)
        shape = draw.ellipse if ellipse else draw.rectangle
        shape((x0, y0, x1, y1), fill=255)
        if x1 >= IMAGE_WIDTH - 2:
            shape((x0 - IMAGE_WIDTH, y0, x1 - IMAGE_WIDTH, y1), fill=255)
    clutter = np.asarray(canvas, dtype=np.float64) / 255.0
    return np.maximum(template, clutter)


def image_to_points(image: np.ndarray) -> np.ndarray:
    ys, xs = np.nonzero(image > IMAGE_THRESHOLD)
    polar = np.deg2rad((ys + 0.5) * (180.0 / image.shape[0]))
    azimuth = np.deg2rad((xs + 0.5) * (360.0 / image.shape[1]))
    return np.stack([np.sin(polar) * np.cos(azimuth), np.sin(polar) * np.sin(azimuth), np.cos(polar)], axis=1)


def points_to_image(points: np.ndarray) -> np.ndarray:
    unit = _unit(points)
    polar = np.degrees(np.arccos(np.clip(unit[:, 2], -1.0, 1.0)))
    azimuth = np.degrees(np.arctan2(unit[:, 1], unit[:, 0])) % 360.0
    y = np.clip(np.floor(polar / 180.0 * IMAGE_HEIGHT).astype(int), 0, IMAGE_HEIGHT - 1)
    x = np.clip(np.floor(azimuth / 360.0 * IMAGE_WIDTH).astype(int), 0, IMAGE_WIDTH - 1)
    image = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH))
    image[y, x] = 1.0
    return image


# --------------------------------------------------------------------------- instances

def random_rotation(rng: np.random.Generator) -> np.ndarray:
    q = rng.normal(size=4)
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def _corrupt(points: np.ndarray, noise: float, outlier_fraction: float, n_ref: int,
             rng: np.random.Generator) -> np.ndarray:
    source = points.copy()
    if noise > 0:
        source = _unit(source + rng.normal(0.0, noise, size=source.shape))
    n_out = int(outlier_fraction * n_ref)
    if n_out:
        source = np.vstack([source, _unit(rng.normal(size=(n_out, 3)))])
    return source[rng.permutation(len(source))]


class InstanceFactory:
    """Regenerates the identical secret instance stream on every call."""

    def __init__(self, seed: int, templates: dict, world: np.ndarray):
        self.seed = seed
        self.templates = templates
        self.world = world
        self.world_points = image_to_points(world)

    def count(self, group: str) -> int:
        return {"robust": len(PATTERNS) * len(CONFIGS) * ROBUST_ROTATIONS,
                "images": len(IMAGE_CLUTTER) * IMAGE_ROTATIONS,
                "sparse": len(PATTERNS) * len(SPARSE_SIZES) * SPARSE_ROTATIONS}[group]

    def labels(self, group: str) -> list:
        return [label for label, _, _, _ in self.stream(group, labels_only=True)]

    def stream(self, group: str, labels_only: bool = False):
        """Yield (label, template, source, R_true); source ~= template @ R_true.T."""
        if group == "robust":
            for pi, pattern in enumerate(PATTERNS):
                template = self.templates[pattern]
                for ci, (config, (noise, outliers)) in enumerate(CONFIGS.items()):
                    for j in range(ROBUST_ROTATIONS):
                        if labels_only:
                            yield config, None, None, None
                            continue
                        rng = np.random.default_rng([self.seed, 1, pi, ci, j])
                        base = _corrupt(template, noise, outliers, len(template), rng)
                        rotation = random_rotation(rng)
                        yield config, template, base @ rotation.T, rotation
        elif group == "images":
            for ci, (config, fraction) in enumerate(IMAGE_CLUTTER.items()):
                for j in range(IMAGE_ROTATIONS):
                    if labels_only:
                        yield config, None, None, None
                        continue
                    rng = np.random.default_rng([self.seed, 2, ci, j])
                    base = image_to_points(add_clutter(self.world, fraction, rng))
                    rotation = random_rotation(rng)
                    source = image_to_points(points_to_image(base @ rotation.T))
                    yield config, self.world_points, source[rng.permutation(len(source))], rotation
        elif group == "sparse":
            for pi, pattern in enumerate(PATTERNS):
                full = self.templates[pattern]
                for si, size in enumerate(SPARSE_SIZES):
                    for j in range(SPARSE_ROTATIONS):
                        if labels_only:
                            yield f"n{size}", None, None, None
                            continue
                        rng = np.random.default_rng([self.seed, 3, pi, si, j])
                        template = full[rng.choice(len(full), size, replace=False)]
                        picked = full[rng.choice(len(full), size, replace=False)]
                        base = _corrupt(picked, SPARSE_NOISE, SPARSE_OUTLIERS, size, rng)
                        rotation = random_rotation(rng)
                        yield f"n{size}", template, base @ rotation.T, rotation
        else:
            raise ValueError(group)


# --------------------------------------------------------------------------- methods

def discover_methods(method_dir: Path, workdir: Path, env: dict) -> list:
    """Return [(entry_name, module_root, import_name, method_name | None, error | None)]."""
    entries = []
    module_root = str(method_dir.parent)
    for path in sorted(method_dir.glob("*.py")):
        if path.name.startswith("_"):
            continue
        import_name = f"{method_dir.name}.{path.stem}"
        out = workdir / f"list_{path.stem}.json"
        with open(workdir / f"list_{path.stem}.log", "wb") as log:
            proc = subprocess.Popen(
                [sys.executable, str(RUNNER), "--list", "--module-root", module_root,
                 "--import-name", import_name, "--out", str(out)],
                cwd=workdir, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
            _limit_cpu(proc, CPU_STARTUP_SECONDS)
            _wait(proc, HANG_GUARD_FACTOR * CPU_STARTUP_SECONDS + HANG_GUARD_EXTRA)
        try:
            listing = json.loads(out.read_text())
        except (OSError, json.JSONDecodeError):
            listing = {"methods": None, "error": f"module import process exited with code {proc.returncode}"}
        if listing.get("error"):
            entries.append((path.stem, module_root, import_name, None, listing["error"]))
        elif listing.get("methods") is None:
            continue  # helper module without a METHODS registry
        elif not listing["methods"]:
            entries.append((path.stem, module_root, import_name, None, "METHODS registry is empty"))
        else:
            for name in listing["methods"]:
                entries.append((name, module_root, import_name, name, None))
    counts = {}
    for entry in entries:
        counts[entry[0]] = counts.get(entry[0], 0) + 1
    entries = [(f"{e[2].split('.', 1)[1]}.{e[0]}" if counts[e[0]] > 1 else e[0],) + e[1:] for e in entries]
    if not entries:
        entries.append(("no_registered_method", module_root, "", None,
                        f"no module in {method_dir} defines a METHODS registry"))
    return entries


def _limit_cpu(proc: subprocess.Popen, seconds: float) -> None:
    """Kernel-enforced CPU-time cap (RLIMIT_CPU counts CPU already used, so setting it
    right after start is exact). Load on the machine does not change CPU time."""
    soft = int(math.ceil(seconds))
    try:
        resource.prlimit(proc.pid, resource.RLIMIT_CPU, (soft, soft + 5))
        resource.prlimit(proc.pid, resource.RLIMIT_CORE, (0, 0))
    except (ProcessLookupError, OSError):
        pass


def _wait(proc: subprocess.Popen, hang_guard: float) -> None:
    try:
        proc.wait(timeout=hang_guard)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def _children_cpu() -> float:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def _log_tail(path: Path, lines: int = 6) -> str:
    try:
        return " | ".join(path.read_text(errors="replace").strip().splitlines()[-lines:])
    except OSError:
        return ""


def run_group(entry, factory: InstanceFactory, group: str, workdir: Path, env: dict):
    """Run one method on one instance group. Returns (errors | None, failure, cpu_seconds)."""
    name, module_root, import_name, method_name, _ = entry
    n = factory.count(group)
    budget = CPU_SECONDS_PER_INSTANCE * n + CPU_STARTUP_SECONDS
    req_read, req_write = os.pipe()
    rep_read, rep_write = os.pipe()
    log_path = workdir / f"run_{name}_{group}.log"
    cpu_before = _children_cpu()
    with open(log_path, "wb") as log:
        proc = subprocess.Popen(
            [sys.executable, str(RUNNER), "--run", "--module-root", module_root, "--import-name", import_name,
             "--method", method_name, "--in-fd", str(req_read), "--out-fd", str(rep_write)],
            pass_fds=(req_read, rep_write), cwd=workdir, env=env, stdin=subprocess.DEVNULL,
            stdout=log, stderr=subprocess.STDOUT)
    _limit_cpu(proc, budget)
    os.close(req_read)
    os.close(rep_write)
    guard = threading.Timer(HANG_GUARD_FACTOR * budget + HANG_GUARD_EXTRA, proc.kill)
    guard.daemon = True
    guard.start()
    requests = os.fdopen(req_write, "wb", buffering=1 << 20)
    replies = os.fdopen(rep_read, "rb", buffering=0)
    errors = np.full(n, np.nan)
    failure = None
    try:
        for i, (_, template, source, truth) in enumerate(factory.stream(group)):
            requests.write(REQ_HEADER.pack(b"I", len(template), len(source)))
            requests.write(np.ascontiguousarray(template, dtype="<f8").tobytes())
            requests.write(np.ascontiguousarray(source, dtype="<f8").tobytes())
            requests.flush()
            raw = b""
            while len(raw) < REPLY.size:
                chunk = replies.read(REPLY.size - len(raw))
                if not chunk:
                    raise EOFError("method process terminated")
                raw += chunk
            status, *values = REPLY.unpack(raw)
            if status != b"O":
                failure = f"method raised an exception on instance {i}"
                break
            rotation = np.array(values, dtype=np.float64).reshape(3, 3)
            problem = rotation_problem(rotation)
            if problem:
                failure = f"invalid output on instance {i}: {problem}"
                break
            errors[i] = geodesic_error_deg(rotation, truth)
        if failure is None:
            requests.write(REQ_HEADER.pack(b"E", 0, 0))
            requests.flush()
    except (BrokenPipeError, EOFError, OSError) as exc:
        failure = f"method process died ({type(exc).__name__}: {exc})"
    finally:
        for stream in (requests, replies):
            try:
                stream.close()
            except OSError:
                pass
        if failure is not None and proc.poll() is None:
            proc.kill()
        proc.wait()
        guard.cancel()
        guard.join(timeout=5)
    cpu = _children_cpu() - cpu_before
    if failure is None and proc.returncode != 0:
        failure = f"method process exited with code {proc.returncode}"
    if cpu > budget:
        failure = f"CPU budget exceeded: {cpu:.1f}s > {budget:.1f}s for {n} instances"
    if failure is not None:
        tail = _log_tail(log_path)
        return None, failure + (f" [log: {tail}]" if tail else ""), cpu
    return errors, None, cpu


def rotation_problem(rotation: np.ndarray) -> str | None:
    if not np.all(np.isfinite(rotation)):
        return "non-finite entries"
    deviation = float(np.max(np.abs(rotation.T @ rotation - np.eye(3))))
    if deviation > ORTHONORMAL_TOL:
        return f"not orthonormal (max |R^T R - I| = {deviation:.3g})"
    if np.linalg.det(rotation) <= 0:
        return "determinant is not +1 (reflection)"
    return None


def geodesic_error_deg(estimate: np.ndarray, truth: np.ndarray) -> float:
    cosine = (np.trace(truth.T @ estimate) - 1.0) / 2.0
    return float(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))))


# --------------------------------------------------------------------------- scoring

def statistic(kind: str, errors: np.ndarray) -> float:
    if kind == "median":
        return float(np.median(errors))
    if kind == "mean":
        return float(np.mean(errors))
    if kind == "p95":
        return float(np.percentile(errors, 95))
    if kind == "p90":
        return float(np.percentile(errors, 90))
    if kind == "max":
        return float(np.max(errors))
    if kind == "success_1":
        return float(np.mean(errors <= 1.0))
    if kind == "success_5":
        return float(np.mean(errors <= 5.0))
    raise ValueError(kind)


def score_method(errors_by_group: dict | None, labels: dict) -> dict:
    scores = {}
    for experiment, (group, subset, metrics) in EXPERIMENTS.items():
        values = {}
        for metric, kind in metrics:
            if errors_by_group is None:
                values[metric] = WORST_STAT[kind]
                continue
            errors = errors_by_group[group]
            if subset is not None:
                errors = errors[np.array([label in subset for label in labels[group]])]
            values[metric] = statistic(kind, errors)
        scores[experiment] = values
    return scores


class SeedLock:
    """Keep the secret unreadable while untrusted method code runs."""

    def __enter__(self):
        try:
            os.chmod(SEED_FILE, 0)
        except OSError as exc:
            print(f"WARNING: could not lock {SEED_FILE}: {exc}", file=sys.stderr)
        return self

    def __exit__(self, *exc):
        try:
            os.chmod(SEED_FILE, 0o644)
        except OSError:
            pass
        return False


def read_seed() -> int:
    try:
        os.chmod(SEED_FILE, 0o644)
    except OSError:
        pass
    return int(SEED_FILE.read_text().strip(), 16)


def child_env() -> dict:
    env = dict(os.environ)
    paths = [str(WORKSPACE), "/opt/python-packages"] + [p for p in env.get("PYTHONPATH", "").split(":") if p]
    env["PYTHONPATH"] = ":".join(dict.fromkeys(paths))
    env["GYM_WORKSPACE"] = str(WORKSPACE)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS"):
        env[var] = "1"
    return env


def main() -> None:
    parser = argparse.ArgumentParser(description="Hidden test: run every registered method on secret instances")
    parser.add_argument("--output", default=str(WORKSPACE / "scoring" / "scores_test.json"))
    parser.add_argument("--method-dir", default=str(WORKSPACE / "method"))
    parser.add_argument("--per-instance-output", default=os.environ.get("PER_INSTANCE_OUTPUT", ""))
    args = parser.parse_args()

    seed = read_seed()
    integrity_error = None
    factory = None
    try:
        factory = InstanceFactory(seed, load_templates(), render_world_template())
    except IntegrityError as exc:
        integrity_error = str(exc)
        print(f"ERROR: {integrity_error}; every method is scored as failed", file=sys.stderr)
    del seed

    env = child_env()
    results = {experiment: {"results": {}} for experiment in EXPERIMENTS}
    diagnostics = {"numpy": np.__version__, "cpu_seconds_per_instance_budget": CPU_SECONDS_PER_INSTANCE,
                   "integrity_error": integrity_error, "methods": {}}
    per_instance = {}
    labels = {group: factory.labels(group) for group in GROUP_ORDER} if factory else {}

    with tempfile.TemporaryDirectory(prefix="hidden_test_") as tmp, SeedLock():
        workdir = Path(tmp)
        entries = discover_methods(Path(args.method_dir).resolve(), workdir, env)
        for entry in entries:
            name, error = entry[0], entry[4]
            info = {"status": "ok", "cpu_seconds": {}}
            errors_by_group = {}
            failure = error or integrity_error
            if failure is None:
                for group in GROUP_ORDER:
                    errors, failure, cpu = run_group(entry, factory, group, workdir, env)
                    info["cpu_seconds"][group] = round(cpu, 2)
                    if failure is not None:
                        failure = f"{group}: {failure}"
                        break
                    errors_by_group[group] = errors
            if failure is not None:
                info["status"] = "failed"
                info["failure"] = failure[:2000]
                errors_by_group = None
            print(f"[test] {name}: {info['status']}" + (f" ({info.get('failure')})" if failure else ""), flush=True)
            for experiment, values in score_method(errors_by_group, labels).items():
                results[experiment]["results"][name] = values
            diagnostics["methods"][name] = info
            if errors_by_group is not None:
                per_instance[name] = {g: {"labels": labels[g], "errors": [round(float(e), 6) for e in errors_by_group[g]]}
                                      for g in GROUP_ORDER}

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"experiments": results, "_diagnostics": diagnostics}, indent=2) + "\n")
    print(f"Test scores written to {output}")
    if args.per_instance_output:
        Path(args.per_instance_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.per_instance_output).write_text(json.dumps(per_instance))


if __name__ == "__main__":
    main()
