#!/bin/bash
# Fetch every external artifact the gym uses, pinned to exact upstream commits,
# and verify their SHA-256 (the evaluators re-check these hashes before use).
#
#   * the paper's released code + Robust Vector Alignment Dataset
#     (github.com/ARLab-VT/Robust-Vector-Set-Alignment @ 4044de8)
#   * a public world-map GeoJSON used as the substitute spherical image
#     (github.com/holtzy/D3-graph-gallery @ 8f12759)
#
# Size: ~45 MB.  Run once before submitting jobs (compute nodes are offline).
set -euo pipefail
cd "$(dirname "$0")/.."

PAPER_REPO_URL="https://github.com/ARLab-VT/Robust-Vector-Set-Alignment.git"
PAPER_REPO_COMMIT="4044de8e34ad0c9c2b69abd67ef63d44cd7c5352"
PAPER_CODE_DIR="data/downloads/Robust-Vector-Set-Alignment"
DATASET_DIR="data/downloads/vector_alignment_dataset"
WORLD_GEOJSON_URL="https://raw.githubusercontent.com/holtzy/D3-graph-gallery/8f12759d589c09248d841795293be9197308531b/DATA/world.geojson"
WORLD_GEOJSON_PATH="data/downloads/world_geojson/world.geojson"

mkdir -p data/downloads

if [ ! -d "$PAPER_CODE_DIR/.git" ]; then
    rm -rf "$PAPER_CODE_DIR"
    git clone "$PAPER_REPO_URL" "$PAPER_CODE_DIR"
fi
git -C "$PAPER_CODE_DIR" fetch -q origin "$PAPER_REPO_COMMIT" 2>/dev/null || git -C "$PAPER_CODE_DIR" fetch -q origin
git -C "$PAPER_CODE_DIR" checkout -q "$PAPER_REPO_COMMIT"

rm -rf "$DATASET_DIR"
cp -a "$PAPER_CODE_DIR/vector_alignment_dataset" "$DATASET_DIR"

mkdir -p "$(dirname "$WORLD_GEOJSON_PATH")"
if [ ! -f "$WORLD_GEOJSON_PATH" ]; then
    curl -fsSL "$WORLD_GEOJSON_URL" -o "$WORLD_GEOJSON_PATH"
fi

sha256sum -c - <<'SUMS'
f255b3abf2cf5f72fce8219cd038f56ca4351b9863744de21805427b3673f840  data/downloads/vector_alignment_dataset/A1_A.pkl
e93a139b8fcacb05b3255536dc3497859e13c5b99f11f81981660b6e073b9b73  data/downloads/vector_alignment_dataset/A2_A.pkl
deaf740dda5469f22c225285b07dd106dcd609d4b7d216e3f923a3b17d8fd25e  data/downloads/vector_alignment_dataset/A3_A.pkl
09c15d4174b73bc2b211967a0b5d357b87c5f2a8fe123e2136da2691c0c36895  data/downloads/vector_alignment_dataset/A4_A.pkl
8b57f68f2717b611c5705ba692149eb0e22f6039610782ea9e27c4554d8f1b4a  data/downloads/vector_alignment_dataset/A5_A.pkl
a57435e765f1261717bc46b93a91a5bd1717be7a06828bf8236bac8823aabd3c  data/downloads/vector_alignment_dataset/RandomRotation100.pkl
e8796f1162d7dfa96ccf36047960fe5d40806eb243272da4048153d049fc5f8f  data/downloads/world_geojson/world.geojson
SUMS

echo "Download complete: $DATASET_DIR, $PAPER_CODE_DIR, $WORLD_GEOJSON_PATH"
