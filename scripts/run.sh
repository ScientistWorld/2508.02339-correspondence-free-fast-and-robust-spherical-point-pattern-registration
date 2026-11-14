#!/bin/bash
set -euo pipefail
cd /home/user
export PYTHONPATH="/home/user:/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
bash redteam/run_all.sh
