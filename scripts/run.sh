#!/bin/bash
# Hardening verification job (CPU only):
#   * reference (method/: SPMC, FRS, SPMC+FRS) through the new train evaluator
#     and the new hidden test -> scoring/scores_{train,test}.json, scores.json
#   * better/weaker variants, baselines, brute force and every REDTEAM shortcut
#     through the hidden test -> notes/hardening/results/
set -euo pipefail
cd /home/user
export PYTHONPATH="/home/user:/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
for required in data/downloads/vector_alignment_dataset/A1_A.pkl \
                data/downloads/vector_alignment_dataset/RandomRotation100.pkl \
                data/downloads/world_geojson/world.geojson; do
    [ -f "$required" ] || { echo "ERROR: missing $required" >&2; exit 1; }
done
bash notes/hardening/run_cases.sh
