#!/bin/bash
# Download paper code and dataset for reproduction.
#
# This paper uses the "Robust Vector Alignment Dataset" from the paper's GitHub repo.
# We clone the paper's official implementation, then copy the dataset into
# data/downloads/ so future methods can use it without depending on method/.
#
# Estimated total download size: ~50 MB
# Estimated disk usage: ~50 MB

set -euo pipefail
cd "$(dirname "$0")"
cd ..

PAPER_REPO_URL="https://github.com/ARLab-VT/Robust-Vector-Set-Alignment.git"
PAPER_CODE_DIR="data/downloads/Robust-Vector-Set-Alignment"
CANONICAL_DATASET_DIR="data/downloads/vector_alignment_dataset"

mkdir -p data/downloads

if [ -d "$PAPER_CODE_DIR/.git" ]; then
    echo "Paper code already exists at $PAPER_CODE_DIR; updating..."
    git -C "$PAPER_CODE_DIR" fetch --depth 1 origin main
    git -C "$PAPER_CODE_DIR" checkout -q FETCH_HEAD
else
    echo "Cloning paper code from GitHub..."
    rm -rf "$PAPER_CODE_DIR"
    git clone --depth 1 "$PAPER_REPO_URL" "$PAPER_CODE_DIR"
fi

SOURCE_DATASET_DIR="$PAPER_CODE_DIR/vector_alignment_dataset"
if [ -d "$SOURCE_DATASET_DIR" ]; then
    mkdir -p data/downloads
    rm -rf "$CANONICAL_DATASET_DIR"
    cp -a "$SOURCE_DATASET_DIR" "$CANONICAL_DATASET_DIR"
    N_FILES=$(ls "$CANONICAL_DATASET_DIR"/*.pkl 2>/dev/null | wc -l)
    echo "Dataset files found: $N_FILES"
else
    echo "ERROR: Dataset directory not found in paper repository: $SOURCE_DATASET_DIR" >&2
    exit 1
fi

echo "Download complete."
echo ""
echo "Dataset location: $CANONICAL_DATASET_DIR"
echo "Paper code location: $PAPER_CODE_DIR"
