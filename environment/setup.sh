#!/bin/bash
# Install Python packages into the container overlay.
#
# Python dependencies belong here, not in container.def.
# Keep the environment minimal because the reproduction is CPU-only.

set -euo pipefail

export HOME=/home/user
export PYTHONUSERBASE="${HOME}/.local"

mkdir -p "${PYTHONUSERBASE}"

# The build runs under fakeroot and cannot reliably write into /usr/local.
# Install into the user site instead of using a system prefix.
python3 -m pip install --user numpy
