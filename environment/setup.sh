#!/bin/bash
# Install Python packages into the container overlay.
#
# Install only the runtime dependency needed by this reproduction.
# Keep setup conservative so container retries do not depend on extra tooling.

set -e

python3 -m pip install numpy
