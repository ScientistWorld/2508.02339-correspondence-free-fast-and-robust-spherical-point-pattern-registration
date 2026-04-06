#!/bin/bash
# Download all data and models needed for this environment.
#
# This paper uses SYNTHETIC data only — no external downloads needed.
# The "Robust Vector Alignment Dataset" is generated procedurally.
#
# Estimated total download size: 0 MB (all data is synthetic)
# Estimated disk usage: < 100 MB (generated at runtime)

set -e
cd "$(dirname "$0")"

echo "This paper uses synthetic data only — no downloads required."
echo "The dataset will be generated at runtime."
echo "If you need to pre-generate the dataset, run:"
echo "  python -c 'from data.dataset import generate_dataset; generate_dataset()'"
