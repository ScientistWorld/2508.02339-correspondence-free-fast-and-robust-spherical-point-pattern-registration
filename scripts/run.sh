#!/bin/bash
# Reproduce the reference end to end on a CPU node (no internet needed once
# scripts/download.sh has been run): SPMC, FRS and SPMC+FRS through the public
# train evaluator and the hidden test -> scoring/scores_{train,test}.json and
# scoring/scores.json. (The hardening verification bundle that produced
# HARDENING.md is notes/hardening/run_cases.sh.)
set -euo pipefail
cd /home/user
bash scripts/reproduce.sh
