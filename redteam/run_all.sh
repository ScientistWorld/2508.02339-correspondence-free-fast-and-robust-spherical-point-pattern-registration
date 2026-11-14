#!/bin/bash
set -euo pipefail
cd /home/user
bash redteam/reference_seed0/run.sh 2>&1 | tee redteam/reference_seed0/run.log
bash redteam/reference_seed1/run.sh 2>&1 | tee redteam/reference_seed1/run.log
bash redteam/reference_seed2/run.sh 2>&1 | tee redteam/reference_seed2/run.log
bash redteam/better_fft/run.sh 2>&1 | tee redteam/better_fft/run.log
bash redteam/better_resolution/run.sh 2>&1 | tee redteam/better_resolution/run.log
bash redteam/weaker_spmc/run.sh 2>&1 | tee redteam/weaker_spmc/run.log
bash redteam/weaker_identity/run.sh 2>&1 | tee redteam/weaker_identity/run.log
bash redteam/shortcut_fabricated_zero/run.sh 2>&1 | tee redteam/shortcut_fabricated_zero/run.log
bash redteam/shortcut_impossible_negative/run.sh 2>&1 | tee redteam/shortcut_impossible_negative/run.log
bash redteam/shortcut_empty/run.sh 2>&1 | tee redteam/shortcut_empty/run.log
bash redteam/shortcut_missing_accuracy/run.sh 2>&1 | tee redteam/shortcut_missing_accuracy/run.log
bash redteam/shortcut_filter_easy/run.sh 2>&1 | tee redteam/shortcut_filter_easy/run.log
bash redteam/shortcut_null/run.sh 2>&1 | tee redteam/shortcut_null/run.log
bash redteam/shortcut_nan/run.sh 2>&1 | tee redteam/shortcut_nan/run.log
bash redteam/shortcut_short_arrays/run.sh 2>&1 | tee redteam/shortcut_short_arrays/run.log
bash redteam/shortcut_stale_identity/run.sh 2>&1 | tee redteam/shortcut_stale_identity/run.log
bash redteam/shortcut_write_final/run.sh 2>&1 | tee redteam/shortcut_write_final/run.log
bash redteam/shortcut_fixed_rotations/run.sh 2>&1 | tee redteam/shortcut_fixed_rotations/run.log
bash redteam/shortcut_answer_enumeration/run.sh 2>&1 | tee redteam/shortcut_answer_enumeration/run.log
python3 redteam/summarize.py
