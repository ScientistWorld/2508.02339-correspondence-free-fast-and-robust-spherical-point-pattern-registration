#!/bin/bash
set -euo pipefail
cd /home/user
python3 -B redteam/case.py --restore
# Preserve completed benchmarks and the evidence from their first run.
# Fast artifact checks precede the remaining full-data methods.
cases=(reference_seed0 reference_seed1 reference_seed2 better_fft
       shortcut_fabricated_zero shortcut_impossible_negative shortcut_empty
       shortcut_missing_accuracy shortcut_filter_easy shortcut_null shortcut_nan
       shortcut_short_arrays shortcut_stale_identity shortcut_write_final
       weaker_spmc weaker_identity shortcut_fixed_rotations
       shortcut_answer_enumeration better_resolution)
for name in "${cases[@]}"; do
    if [ -f "redteam/$name/status.json" ]; then
        echo "Completed checkpoint: $name"
        continue
    fi
    bash "redteam/$name/run.sh" 2>&1 | tee -a "redteam/$name/run.log"
done
python3 redteam/summarize.py
