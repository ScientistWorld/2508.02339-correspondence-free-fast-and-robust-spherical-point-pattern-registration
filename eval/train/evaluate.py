#!/usr/bin/env python3
"""Train evaluator (visible) for correspondence-free spherical registration.

Same interface, metrics, failure rules and CPU budget as the hidden test, but
on PUBLIC instances so a method can be developed against it:

* robust alignment: the paper's released Robust Vector Alignment Dataset
  (5 templates x 7 released source sets B1-B7 x the released 100 rotations
  R100), i.e. exactly the paper's Experiment 1 protocol;
* spherical images: the world-map substitute with one public clutter
  realisation per level (seeds 1000-1004) rotated by R100;
* sparse alignment: independent 1,000 / 3,000-point subsamples generated from
  a public seed.

The hidden test uses the same generators with fresh secret realisations, so a
method tuned to these specific public instances does not carry over.  Every
registered method (``method/*.py`` defining ``METHODS``) is run in a separate
process; every number is recomputed here from the returned matrices.

Usage:  python3 eval/train/evaluate.py [--output scoring/scores_train.json]
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
SOURCE_SHA256 = {
    "A1_B1": "cd678aa76737615dd17aaa8b3d677525f5dd67c32fe4e4765142b391b5ebc2f8",
    "A1_B2": "07c74d2e38d6971449dd9df1ae96c9475d9b94f64ff809e25bab97f3d30c260f",
    "A1_B3": "9dc1909d30b2e405dda8851d02c69c6ea5d09a2beaf21050d30c24cd17a007c7",
    "A1_B4": "6a5fcdcce3e4658a6efabc5ffce043aa7a84c4c03a459b1ec68ff3156041f0f2",
    "A1_B5": "2f4a5ffe6f11791bd8609b784040600bc9786c88cbd390bd3bb040f142160d93",
    "A1_B6": "8d8f74e8016cd2b77bf9b084dd3fc3e2ed8e2701854513a94bbcef5271e8091d",
    "A1_B7": "890266a3faf1692d075d4e5a474093c520563db3fa32009b81a095af0569edf2",
    "A2_B1": "b9907a679c197cbd3076e8f0b047c615b66f3f46670c675b6edf2a67d049012e",
    "A2_B2": "6d41e86689b663f3e7ef8e5e81273c73512bc748245e66c3026cd62adba6e721",
    "A2_B3": "06676bf4137e6e83b0e3576a916ea42801fab4f5355a7ebf8295b6c44b54d519",
    "A2_B4": "797b60a3d48ab9a982cc4733e31389a7e5c36502d3873c9cbb146e9b1b460633",
    "A2_B5": "83ad13763a6c68a80e37d972329f547c4a45a93bb53e92fa17439503776ca80a",
    "A2_B6": "ca43f8392cf16d68346ea0bb213a253d628a0df9d073bcc307aad3954393d20e",
    "A2_B7": "5fb07d473f9544a1e9bd77b26eb2dac87bb6cad1f09cd24ff1e5f64d486d2701",
    "A3_B1": "bfe72b0da0531a3472461b7f1bcb400cf9a9fda6f8d497c38070a6838fbaae13",
    "A3_B2": "67ad112c0da86406caea5d46ce438a75e5b73125704812f47e55b1be49f459e7",
    "A3_B3": "a4bec220c5df01e7a5262dae8af15ef32da6349bd8d203dc529bbd0995ca8588",
    "A3_B4": "983a0f6adbb49c8c6ef480b45694371383c0449709312fca815febbd0208ecbb",
    "A3_B5": "e3ea05779a6ca67d20845e9650a6a6ecbab17ba7ee7373abf4fbdc042ae8a3b1",
    "A3_B6": "ee301b1d299a3e58133779f523dea617f3bf3451b2c208f0b3bb16a91f9d3431",
    "A3_B7": "33caeab7b6b4fdd8391d1a6eff255810ab4b2685bf9dbd03c3e407cd15444bc1",
    "A4_B1": "0e827ef9d3e9a18607a40afd5cafba77c90c090ba6f5fc2ee3bd47bdd4460ab1",
    "A4_B2": "bee832b43e38fc686500d4837efa59802267aa0cfe19264978db0c6c38c5be27",
    "A4_B3": "fad37c6a9837bc082f3d18025fe93347ba477691a5e0b0a84eda29430c9191f6",
    "A4_B4": "f809b6564ee533f8feae43a0cbd40f1c8de2d46bc8a040e4122c0a92c7f813ea",
    "A4_B5": "ed3b1c76ad7475155ad9e134d518047048ed259d35dd1db152bca77ddd078204",
    "A4_B6": "953df25e3264e0cabcc1a9dd2954e75f2221cf0fdb8c769f6809378aa15b92d4",
    "A4_B7": "c334f632419613b73f445ce8dcbc3d4df535225cab1dea179c1cdc4661525651",
    "A5_B1": "116b6846df68d4dc6f72dfbab3ef0644ec8c82eed2758baf7d6ee3db71851a83",
    "A5_B2": "b32cd9ce9acfc5429d55543d6a8c79550fecb866d938acf4640f89a93cb81476",
    "A5_B3": "319f0dd0769926e42cfdbf4467f71e5b236a7b59e5f8308c01918b0fa1dac1a0",
    "A5_B4": "51cff092a1ef1eb84d8fbef436c9569a8cda506e3396641a35652adaf9142614",
    "A5_B5": "4f411e0b0f2ca0dcefec7895eef4acafe02531f91e8574b2bde11cef1fba3144",
    "A5_B6": "dcb89302808c1179476ea29c7212ac2d8bb151ba6062b8a080ef9e7f2becad8b",
    "A5_B7": "670a62d99f1690ea80d008de3b7687a4b0900293f97f589aab2727dc8889df2e",
}
ROTATIONS_SHA256 = "a57435e765f1261717bc46b93a91a5bd1717be7a06828bf8236bac8823aabd3c"
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
PUBLIC_SEED = 20250802          # train-only generator seed (public)
IMAGE_CLUTTER_SEEDS = {"Img1": 1000, "Img2": 1001, "Img3": 1002, "Img4": 1003, "Img5": 1004}

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


def load_released_sources() -> dict:
    return {key: _unit(pickle.loads(_verified_bytes(DATASET_DIR / f"{key.split('_')[0]}_A_{key.split('_')[1]}.pkl",
                                                    digest)))
            for key, digest in SOURCE_SHA256.items()}


def load_released_rotations() -> np.ndarray:
    rotations = np.asarray(pickle.loads(_verified_bytes(DATASET_DIR / "RandomRotation100.pkl", ROTATIONS_SHA256)),
                           dtype=np.float64)
    if rotations.shape != (100, 3, 3):
        raise IntegrityError(f"unexpected rotation array shape {rotations.shape}")
    return rotations


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
    """Public train instances (released data + public seeds)."""

    def __init__(self, templates: dict, sources: dict, rotations: np.ndarray, world: np.ndarray):
        self.templates = templates
        self.sources = sources
        self.rotations = rotations
        self.world = world
        self.world_points = image_to_points(world)
        self.cluttered = {config: image_to_points(add_clutter(world, fraction,
                                                              np.random.default_rng(IMAGE_CLUTTER_SEEDS[config])))
                          for config, fraction in IMAGE_CLUTTER.items()}

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
                for ci, config in enumerate(CONFIGS):
                    released = self.sources[f"{pattern}_{config}"]
                    for j in range(ROBUST_ROTATIONS):
                        if labels_only:
                            yield config, None, None, None
                            continue
                        rng = np.random.default_rng([PUBLIC_SEED, 1, pi, ci, j])
                        rotation = self.rotations[j]
                        yield config, template, released[rng.permutation(len(released))] @ rotation.T, rotation
        elif group == "images":
            for ci, config in enumerate(IMAGE_CLUTTER):
                base = self.cluttered[config]
                for j in range(IMAGE_ROTATIONS):
                    if labels_only:
                        yield config, None, None, None
                        continue
                    rng = np.random.default_rng([PUBLIC_SEED, 2, ci, j])
                    rotation = self.rotations[j]
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
                        rng = np.random.default_rng([PUBLIC_SEED, 3, pi, si, j])
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
    parser = argparse.ArgumentParser(description="Train evaluator: run every registered method on public instances")
    parser.add_argument("--output", default=str(WORKSPACE / "scoring" / "scores_train.json"))
    parser.add_argument("--method-dir", default=str(WORKSPACE / "method"))
    parser.add_argument("--per-instance-output", default=os.environ.get("PER_INSTANCE_OUTPUT", ""))
    args = parser.parse_args()

    integrity_error = None
    factory = None
    try:
        factory = InstanceFactory(load_templates(), load_released_sources(), load_released_rotations(),
                                  render_world_template())
    except IntegrityError as exc:
        integrity_error = str(exc)
        print(f"ERROR: {integrity_error}; every method is scored as failed", file=sys.stderr)

    env = child_env()
    results = {experiment: {"results": {}} for experiment in EXPERIMENTS}
    diagnostics = {"numpy": np.__version__, "cpu_seconds_per_instance_budget": CPU_SECONDS_PER_INSTANCE,
                   "integrity_error": integrity_error, "methods": {}}
    per_instance = {}
    labels = {group: factory.labels(group) for group in GROUP_ORDER} if factory else {}

    with tempfile.TemporaryDirectory(prefix="train_eval_") as tmp:
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
            print(f"[train] {name}: {info['status']}" + (f" ({info.get('failure')})" if failure else ""), flush=True)
            for experiment, values in score_method(errors_by_group, labels).items():
                results[experiment]["results"][name] = values
            diagnostics["methods"][name] = info
            if errors_by_group is not None:
                per_instance[name] = {g: {"labels": labels[g], "errors": [round(float(e), 6) for e in errors_by_group[g]]}
                                      for g in GROUP_ORDER}

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"experiments": results, "_diagnostics": diagnostics}, indent=2) + "\n")
    print(f"Train scores written to {output}")
    if args.per_instance_output:
        Path(args.per_instance_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.per_instance_output).write_text(json.dumps(per_instance))


if __name__ == "__main__":
    main()
