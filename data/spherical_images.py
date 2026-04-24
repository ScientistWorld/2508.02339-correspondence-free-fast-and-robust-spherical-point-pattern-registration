"""Utilities for the paper's spherical-image adaptation experiment.

This module stays method-agnostic: it generates the spherical-image benchmark
inputs and converts images to spherical point clouds without importing from
``method/``.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


WORLD_GEOJSON = Path(__file__).resolve().parent / "downloads" / "world_geojson" / "world.geojson"
IMAGE_WIDTH = 360
IMAGE_HEIGHT = 180
INTENSITY_THRESHOLD = 0.21
IMAGE_CONFIGS = ("Img1", "Img2", "Img3", "Img4", "Img5")
CLUTTER_TARGETS = {
    "Img1": 0.0,
    "Img2": 0.05,
    "Img3": 0.10,
    "Img4": 0.15,
    "Img5": 0.193,
}
_TEMPLATE_CACHE: np.ndarray | None = None


def spherical_images_available() -> bool:
    return WORLD_GEOJSON.exists()


def require_spherical_image_assets() -> Path:
    if not spherical_images_available():
        raise FileNotFoundError(
            f"Spherical image asset not found at {WORLD_GEOJSON}. "
            "Run `bash scripts/download.sh` first."
        )
    return WORLD_GEOJSON


def _lon_to_x(lon: float, width: int) -> float:
    return ((lon + 180.0) / 360.0) * width


def _lat_to_y(lat: float, height: int) -> float:
    return ((90.0 - lat) / 180.0) * height


def _unwrap_ring(points: list[tuple[float, float]], width: int) -> list[tuple[float, float]]:
    if not points:
        return []
    unwrapped = [points[0]]
    prev_x = points[0][0]
    offset = 0.0
    for x, y in points[1:]:
        x_shifted = x + offset
        while x_shifted - prev_x > width / 2:
            offset -= width
            x_shifted = x + offset
        while x_shifted - prev_x < -width / 2:
            offset += width
            x_shifted = x + offset
        unwrapped.append((x_shifted, y))
        prev_x = x_shifted
    return unwrapped


def _draw_polygon(draw: ImageDraw.ImageDraw, ring: list[list[float]], width: int, height: int) -> None:
    projected = [(_lon_to_x(lon, width), _lat_to_y(lat, height)) for lon, lat in ring]
    unwrapped = _unwrap_ring(projected, width)
    for x_shift in (-width, 0, width):
        shifted = [(x + x_shift, y) for x, y in unwrapped]
        draw.polygon(shifted, fill=255)


def _iter_rings(geometry: dict) -> list[list[list[float]]]:
    geom_type = geometry["type"]
    coords = geometry["coordinates"]
    if geom_type == "Polygon":
        return [coords[0]]
    if geom_type == "MultiPolygon":
        return [polygon[0] for polygon in coords]
    raise ValueError(f"Unsupported geometry type: {geom_type}")


def render_world_template(width: int = IMAGE_WIDTH, height: int = IMAGE_HEIGHT) -> np.ndarray:
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is not None and _TEMPLATE_CACHE.shape == (height, width):
        return _TEMPLATE_CACHE.copy()

    geojson_path = require_spherical_image_assets()
    image = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(image)
    payload = json.loads(geojson_path.read_text())

    for feature in payload["features"]:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        for ring in _iter_rings(geometry):
            _draw_polygon(draw, ring, width, height)

    template = (np.asarray(image, dtype=np.float32) / 255.0).clip(0.0, 1.0)
    _TEMPLATE_CACHE = template
    return template.copy()


def add_clutter(template: np.ndarray, config_name: str, seed: int) -> np.ndarray:
    target_fraction = CLUTTER_TARGETS[config_name]
    cluttered = template.copy()
    if target_fraction <= 0:
        return cluttered

    rng = np.random.default_rng(seed)
    clutter_mask = np.zeros_like(template, dtype=np.float32)
    target_pixels = int(round(target_fraction * clutter_mask.size))
    canvas = Image.fromarray((clutter_mask * 255).astype(np.uint8), mode="L")
    draw = ImageDraw.Draw(canvas)

    attempts = 0
    while int(np.count_nonzero(np.asarray(canvas))) < target_pixels and attempts < 4096:
        attempts += 1
        shape = "ellipse" if rng.random() < 0.5 else "rectangle"
        w = int(rng.integers(6, 36))
        h = int(rng.integers(4, 24))
        x0 = int(rng.integers(0, IMAGE_WIDTH))
        y0 = int(rng.integers(0, IMAGE_HEIGHT))
        x1 = min(IMAGE_WIDTH - 1, x0 + w)
        y1 = min(IMAGE_HEIGHT - 1, y0 + h)
        if shape == "ellipse":
            draw.ellipse((x0, y0, x1, y1), fill=255)
            if x1 >= IMAGE_WIDTH - 2:
                draw.ellipse((x0 - IMAGE_WIDTH, y0, x1 - IMAGE_WIDTH, y1), fill=255)
        else:
            draw.rectangle((x0, y0, x1, y1), fill=255)
            if x1 >= IMAGE_WIDTH - 2:
                draw.rectangle((x0 - IMAGE_WIDTH, y0, x1 - IMAGE_WIDTH, y1), fill=255)

    clutter_mask = (np.asarray(canvas, dtype=np.float32) / 255.0).clip(0.0, 1.0)
    return np.maximum(cluttered, clutter_mask)


def image_to_spherical_points(image: np.ndarray, threshold: float = INTENSITY_THRESHOLD) -> np.ndarray:
    if image.ndim == 3:
        intensity = image.mean(axis=-1)
    else:
        intensity = image
    active_y, active_x = np.where(intensity > threshold)
    if active_x.size == 0:
        return np.zeros((0, 3), dtype=np.float32)

    polar_deg = (active_y.astype(np.float32) + 0.5) * (180.0 / image.shape[0])
    azimuth_deg = (active_x.astype(np.float32) + 0.5) * (360.0 / image.shape[1])
    polar = np.deg2rad(polar_deg)
    azimuth = np.deg2rad(azimuth_deg)
    sin_polar = np.sin(polar)
    points = np.stack(
        [
            sin_polar * np.cos(azimuth),
            sin_polar * np.sin(azimuth),
            np.cos(polar),
        ],
        axis=1,
    )
    return points.astype(np.float32)


def spherical_points_to_image(points: np.ndarray, width: int = IMAGE_WIDTH, height: int = IMAGE_HEIGHT) -> np.ndarray:
    image = np.zeros((height, width), dtype=np.float32)
    if points.size == 0:
        return image

    norms = np.linalg.norm(points, axis=1, keepdims=True)
    unit = points / np.clip(norms, 1e-12, None)
    polar = np.degrees(np.arccos(np.clip(unit[:, 2], -1.0, 1.0)))
    azimuth = np.degrees(np.arctan2(unit[:, 1], unit[:, 0]))
    azimuth[azimuth < 0.0] += 360.0

    y = np.clip(np.floor((polar / 180.0) * height).astype(int), 0, height - 1)
    x = np.clip(np.floor((azimuth / 360.0) * width).astype(int), 0, width - 1)
    image[y, x] = 1.0
    return image


def get_template_image() -> np.ndarray:
    return render_world_template()


def get_cluttered_base_image(config_name: str) -> np.ndarray:
    seed = 1000 + IMAGE_CONFIGS.index(config_name)
    return add_clutter(get_template_image(), config_name, seed=seed)


def get_source_image(config_name: str, rotation: np.ndarray) -> np.ndarray:
    base_points = image_to_spherical_points(get_cluttered_base_image(config_name))
    rotated_points = base_points @ rotation.T
    return spherical_points_to_image(rotated_points)


def get_template_points() -> np.ndarray:
    return image_to_spherical_points(get_template_image())


def actual_clutter_fraction(config_name: str) -> float:
    template = get_template_image()
    cluttered = get_cluttered_base_image(config_name)
    added = np.logical_and(cluttered > 0.5, template <= 0.5)
    return float(np.count_nonzero(added) / added.size)
