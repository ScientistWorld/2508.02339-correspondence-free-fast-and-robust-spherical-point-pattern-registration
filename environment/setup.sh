#!/bin/bash
# Install Python packages into the container overlay.
#
# Python dependencies belong here, not in container.def.
# Keep the environment minimal because the reproduction is CPU-only.

set -euo pipefail

uv pip install --system numpy
