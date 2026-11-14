#!/bin/bash
# Hardening verification bundle (CPU). Resume-safe: finished steps are skipped.
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="$(pwd):/opt/python-packages${PYTHONPATH:+:${PYTHONPATH}}"
R=notes/hardening/results
C=notes/hardening/cases
mkdir -p "$R"
python3 notes/hardening/scenarios.py restore

run_step() {
    local name="$1"; shift
    if [ -f "$R/.done_$name" ]; then echo "[skip] $name"; return 0; fi
    local tries=$(( $(cat "$R/.tries_$name" 2>/dev/null || echo 0) + 1 ))
    echo "$tries" > "$R/.tries_$name"
    if [ "$tries" -gt 3 ]; then echo "[give up] $name (interrupted 3 times)"; return 0; fi
    echo "[run] $name attempt $tries $(date -u +%H:%M:%S)"
    "$@"
    touch "$R/.done_$name"
}
{ python3 -c "import numpy, PIL, sys; print('numpy', numpy.__version__, 'pillow', PIL.__version__, 'python', sys.version.split()[0])"; id; nproc; } > "$R/env.txt" 2>&1
cat "$R/env.txt"

T="python3 eval/test/evaluate.py"
TR="python3 eval/train/evaluate.py"

# Reference: the shipped method/ directory (spmc, frs, spmc_frs) -> final artifacts.
run_step ref_train env PER_INSTANCE_OUTPUT="$R/reference_train_instances.json" bash scripts/evaluate_train.sh
run_step ref_test env PER_INSTANCE_OUTPUT="$R/reference_test_instances.json" bash scripts/evaluate_test.sh
run_step ref_scores_json cp scoring/scores_train.json scoring/scores.json

# Every step below is one short evaluator run (<~15 min): the CPU node is
# drained every ~25 min and an interrupted step restarts from scratch.
TI() { echo --per-instance-output "$R/$1_test_instances.json"; }
run_step v_refine1440_test $T --method-dir $C/v_refine1440 --output $R/v_refine1440_scores_test.json $(TI v_refine1440)
run_step baselines_test $T --method-dir baseline --output $R/baselines_scores_test.json $(TI baselines)
run_step shortcuts_test $T --method-dir $C/shortcuts --output $R/shortcuts_scores_test.json
run_step scenario_stale python3 notes/hardening/scenarios.py stale_artifacts
run_step scenario_tamper_template python3 notes/hardening/scenarios.py tamper_template
run_step scenario_tamper_rotations python3 notes/hardening/scenarios.py tamper_rotations
run_step ref_test_rerun $T --method-dir $C/rerun --output $R/reference_rerun_scores_test.json
run_step budget_test $T --method-dir $C/budget --output $R/budget_scores_test.json
run_step v_refine720_1440_test $T --method-dir $C/v_refine720_1440 --output $R/v_refine720_1440_scores_test.json $(TI v_refine720_1440)
run_step bruteforce_test $T --method-dir $C/bruteforce --output $R/bruteforce_scores_test.json $(TI bruteforce)
run_step shortcuts_train $TR --method-dir $C/shortcuts --output $R/shortcuts_scores_train.json
run_step baselines_train $TR --method-dir baseline --output $R/baselines_scores_train.json
run_step v_refine1440_train $TR --method-dir $C/v_refine1440 --output $R/v_refine1440_scores_train.json

python3 notes/hardening/analyze.py
