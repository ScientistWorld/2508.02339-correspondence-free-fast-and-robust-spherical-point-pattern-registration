#!/bin/bash
# Install Python packages into the container overlay.
#
# uv pip install --system is 10-100x faster than pip install.
# The overlay persists across job submissions without rebuilding the container.

set -e

uv pip install --system numpy
