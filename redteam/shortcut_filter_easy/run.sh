#!/bin/bash
set -euo pipefail
cd /home/user
export PYTHONPATH="/home/user:/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
python3 -B redteam/case.py shortcut_filter_easy
