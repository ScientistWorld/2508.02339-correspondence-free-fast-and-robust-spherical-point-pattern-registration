#!/bin/bash
# Download paper code and dataset for reproduction.
#
# This paper uses the "Robust Vector Alignment Dataset" from the paper's GitHub repo.
# We clone the paper's official implementation, then copy the dataset into data/
# so future methods can use it without depending on method/.
#
# Estimated total download size: ~50 MB
# Estimated disk usage: ~50 MB

set -e
cd "$(dirname "$0")"
cd ..

PAPER_CODE_DIR="method/paper_code"

if [ -d "$PAPER_CODE_DIR" ]; then
    echo "Paper code already exists at $PAPER_CODE_DIR"
    echo "To update, run: git -C $PAPER_CODE_DIR pull"
else
    echo "Cloning paper code from GitHub..."
    git clone https://github.com/ARLab-VT/Robust-Vector-Set-Alignment "$PAPER_CODE_DIR"
fi

SOURCE_DATASET_DIR="$PAPER_CODE_DIR/vector_alignment_dataset"
CANONICAL_DATASET_DIR="data/vector_alignment_dataset"
if [ -d "$SOURCE_DATASET_DIR" ]; then
    mkdir -p data
    rm -rf "$CANONICAL_DATASET_DIR"
    cp -a "$SOURCE_DATASET_DIR" "$CANONICAL_DATASET_DIR"
    N_FILES=$(ls "$CANONICAL_DATASET_DIR"/*.pkl 2>/dev/null | wc -l)
    echo "Dataset files found: $N_FILES"
else
    echo "WARNING: Dataset directory not found"
fi

echo "Download complete."
echo ""
echo "Dataset location: $CANONICAL_DATASET_DIR"
echo "Paper code location: $PAPER_CODE_DIR"
