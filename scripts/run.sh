#!/bin/bash
# CPU submission for the paper's spherical-image adaptation experiment.
#
# The robust-alignment and complexity artifacts are already checked in from
# earlier compute runs. This job adds fresh compute-side evidence for the new
# spherical-image benchmark without discarding those prior results.

set -euo pipefail
cd /home/user
export PYTHONPATH="/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONPATH="/home/user${PYTHONPATH:+:${PYTHONPATH}}"

echo "=========================================="
echo "Spherical Point Pattern Registration: Spherical-Image Benchmark"
echo "=========================================="

for required_path in \
    "data/downloads/vector_alignment_dataset/A1_A.pkl" \
    "data/downloads/vector_alignment_dataset/RandomRotation100.pkl" \
    "data/downloads/world_geojson/world.geojson"
do
    if [ ! -f "${required_path}" ]; then
        echo "ERROR: required dataset asset missing: ${required_path}"
        exit 1
    fi
done

echo "Checking runtime Python dependencies..."
python3 - <<'PY'
import numpy
import PIL
print(f"numpy OK: {numpy.__version__}")
print(f"pillow OK: {PIL.__version__}")
PY

echo "Removing stale spherical-image artifacts..."
rm -f scoring/raw_spherical_image_results.json

echo "Running released spherical-image benchmark (5 clutter settings x 100 rotations)..."
RAW_RESULTS="scoring/raw_results.json" \
RAW_COMPLEXITY_RESULTS="scoring/raw_complexity_results.json" \
RAW_SPHERICAL_IMAGE_RESULTS="scoring/raw_spherical_image_results.json" \
SCORES_OUTPUT="scoring/scores.json" \
    N_ROTATIONS=100 \
    bash scripts/spherical_images.sh

echo "Validating refreshed scoring bundle..."
python3 validate.py --compare

echo "=========================================="
echo "Spherical-image benchmark finished"
echo "=========================================="
