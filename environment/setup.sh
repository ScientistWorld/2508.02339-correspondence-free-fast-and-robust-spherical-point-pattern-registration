#!/bin/bash
# Install Python packages into the container overlay.
#
# Python dependencies belong here, not in container.def.
# Keep the environment minimal because the reproduction is CPU-only.

set -euo pipefail

# The workspace is bind-mounted over /home/user at runtime, so installing
# packages under /home/user would be hidden from the job container. Installing
# into /usr/local also fails under this fakeroot overlay, so place Python
# dependencies in /opt and keep them on PYTHONPATH via container.def.
PYTHON_TARGET="/opt/python-packages"
mkdir -p "${PYTHON_TARGET}"

# Bypass the scheduler's uv/pip shell wrappers here. The wrappers succeeded,
# but they still emitted fakeroot writability warnings to stderr; using the
# container's real pip with --target keeps the install scoped to /opt.
command python3 -m pip install --target "${PYTHON_TARGET}" numpy pillow
