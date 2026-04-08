#!/bin/bash
# Install Python packages into the container overlay.
#
# Python dependencies belong here, not in container.def.
# Keep the environment minimal because the reproduction is CPU-only.

set -euo pipefail

export HOME=/home/user
export PYTHON_TARGET="${HOME}/python-packages/lib/python3.10/site-packages"

mkdir -p "${PYTHON_TARGET}"

# The build runs under fakeroot and cannot reliably write into /usr/local, and
# user-site installs are disabled by the scheduler wrapper. Install into an
# explicit writable target under /home/user instead.
python3 -m pip install --target "${PYTHON_TARGET}" numpy
