# Reproduction Milestones

**Current: method_runs**

## Progress Log

### [2026-04-09 10:55] - method_runs
- Removed the last non-canonical score-writing path: `scripts/run_experiment.py` now writes only raw per-instance results, leaving `scoring/scores.json` exclusively to `eval/evaluate.py`
- Pruned the checked-in `scoring/scores.json` to only directly measured experiments, removing the stale computational-complexity block
- Kept the milestone at `method_runs` pending fresh compute-side evidence from the full 100-rotation CPU run

### [2026-04-08 22:02] - method_runs
- Removed the unmeasured computational-complexity extrapolation from the canonical evaluator so future scores only report experiments actually run
- Confirmed the previous CPU submission was cancelled before producing evidence, so milestone remains `method_runs`
- Prepared a fresh submission state for the full 100-rotation offline evaluation

### [2026-04-08 21:58] - method_runs
- Re-audited the local method code and confirmed the workspace still contains the paper's actual SPMC, FRS, and SPMC+FRS algorithms
- Tightened the offline evaluation scripts without changing the algorithm path, then committed and pushed the submission state
- Kept the milestone at `method_runs` pending the fresh compute-side 100-rotation evaluation

### [2026-04-08 18:29] - method_runs
- Corrected the environment packaging to follow protocol: Python dependencies now live in `environment/setup.sh`, and `environment/container.def` is OS-level only
- Revalidated the workspace locally with `python validate.py --compare`
- Prepared the workspace for a full 100-rotation CPU submission; milestone remains `method_runs` until fresh compute results land

### [2026-04-08 04:18] - method_runs
- Ran the real `scripts/method.sh -> scripts/evaluate.sh -> validate.py --compare` path locally with `N_ROTATIONS=1`
- Confirmed the cleaned offline pipeline produces `scoring/raw_results.json` and a valid `scoring/scores.json`
- Kept the milestone at `method_runs` until the submitted full 100-rotation CPU run finishes

### [2026-04-08 04:05] - method_runs
- Cleaned the execution path so `run.sh` performs one consistent offline evaluation flow
- Restricted `scripts/evaluate.sh` to the method-agnostic aggregator in `eval/`
- Updated checklist/progress bookkeeping to remove stale `core_claim` assertions before the next validation run

### [2026-04-08 00:53] - method_runs
- Audited the previous agent's workspace before trusting the claimed `core_claim`
- Confirmed the codebase implements the paper's actual SPMC, FRS, and SPMC+FRS algorithms rather than a surrogate
- Determined that `scoring/scores.json` was stale and still reflected the pre-fix hybrid path, so the prior milestone claim was not yet supportable
- Fixed the remaining hybrid rotation-convention bug (`source @ R_spmc` before FRS refinement)
- Revalidated representative cases locally against the paper's released code and kept the workspace at `method_runs` pending a fresh compute-side evaluation

### [2026-04-08 00:36] - method_runs
- Audited the local implementation against the paper's released `vector_alignment_utils.py`
- Fixed FRS to match the paper's source-to-source final SVD estimate instead of aligning to the template
- Implemented the actual hybrid `SPMC+FRS` path instead of delegating to SPMC alone
- Restored the paper's default non-FFT circular shift search and corrected shift-to-degree scaling
- Updated the evaluation harness and run scripts to score `spmc`, `frs`, and `spmc_frs` offline on compute nodes

## Stop Justification
