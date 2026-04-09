#!/bin/bash
# Install Python packages into the container overlay.
#
# Python dependencies belong here, not in container.def.
# Keep the environment minimal because the reproduction is CPU-only.

set -euo pipefail

# The workspace is bind-mounted over /home/user at runtime, so installing
# packages under /home/user would be hidden from the job container. Install
# into the overlay's system site-packages instead.
uv pip install --system numpy
