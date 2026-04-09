#!/bin/bash
# Install Python packages into the container overlay.
#
# Python dependencies belong here, not in container.def.
# Keep the environment minimal because the reproduction is CPU-only.

set -euo pipefail

# The workspace is bind-mounted over /home/user at runtime, so installing
# packages under /home/user would be hidden from the job container. Installing
# into /usr/local also fails under this fakeroot overlay, so place Python
# dependencies in /opt and add that path at runtime from scripts/run.sh.
PYTHON_TARGET="/opt/python-packages"
mkdir -p "${PYTHON_TARGET}"
uv pip install --target "${PYTHON_TARGET}" numpy
