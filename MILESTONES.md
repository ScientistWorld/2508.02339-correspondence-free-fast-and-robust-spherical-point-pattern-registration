# Reproduction Milestones

**Current: majority**

## Progress Log

### [2026-04-09 13:50] - majority
- Audited the remaining Fig. 6 benchmark path and confirmed the workspace was incorrectly left in a permanent `done` state before the final reference experiment was actually attempted
- Kept the paper algorithm unchanged but vectorized SPMC's geographic conversion so the original `10^3` to `10^7` complexity protocol is practical enough to attempt on compute
- Preparing a final CPU submission for the paper's computational-complexity experiment; milestone remains `majority` until that run finishes

### [2026-04-09 13:32] - majority
- Added a dedicated, reusable Fig. 6 computational-complexity benchmark path for the paper's `A3/B3` scaling study
- Extended the method-agnostic evaluator so `scores.json` can include the complexity experiment alongside the already reproduced main benchmark
- Preparing a CPU submission for the remaining paper reference experiment; milestone stays `majority` until the new job finishes

### [2026-04-09 12:32] - majority
- Reviewed job `6cc72205-3b7`: the real paper methods completed the full 100-rotation benchmark on the released dataset after auto-resuming through scheduler restarts
- Reproduced the paper's two main scored experiments end-to-end: overall robust alignment and the high-outlier subset, both with canonical `scores.json` and validation passing
- The remaining unmeasured reference experiment is the separate computational-complexity scaling study, so the workspace now clears the `majority` threshold

### [2026-04-09 12:23] - core_claim
- Reviewed successful continuation job `9141a59a-c99`: the real paper methods completed all 35 pattern/config groups for the 20-rotation slice on the released dataset and produced canonical `scoring/scores.json`
- The reproduced results support the central claim: `spmc_frs` reached 0.586° median error overall and 0.626° on the high-outlier subset while remaining under 0.30s median runtime
- Promoted the workspace to `core_claim` and reset `scripts/run.sh` to resume the full 100-rotation paper protocol from the saved checkpoint

### [2026-04-09 12:06] - method_runs
- Reviewed job `768b2584-16c`: the real paper methods completed and checkpointed all 21 `A1`-`A3` pattern/config groups for the 20-rotation slice before the Ray worker was orphaned
- Confirmed `scoring/raw_results.json` now contains 420 compute-side evaluations from the released paper dataset, but the job died before the final standalone aggregation step
- Patched the run path to resume from the saved raw checkpoint, skip completed configs, and rewrite canonical `scoring/scores.json` after every per-config checkpoint so partial progress remains usable

### [2026-04-09 11:11] - method_runs
- Reviewed job `24712a1a-0f8`: the method launched successfully, passed the NumPy smoke test, and reached 1000/3500 evaluations before the Ray worker died and the job was orphaned
- Confirmed the blocker is queue/runtime fragility rather than algorithm correctness
- Reworked the evaluation path to support rotation slices and incremental raw-result checkpoints so shorter CPU jobs can still produce canonical scores

### [2026-04-09 11:03] - method_runs
- The setup overlay build failed before submission because `/usr/local` is not writable in this fakeroot environment, so `uv pip install --system numpy` could not complete
- Reworked Python dependency installation to use `/opt/python-packages` inside the overlay and exported that path from `scripts/run.sh`
- Kept the next job as the same full offline CPU evaluation; the only change is the environment install target

### [2026-04-09 10:59] - method_runs
- Reviewed failed CPU job `62d88eed-373`: the run exited immediately with `ModuleNotFoundError: No module named 'numpy'`
- Identified the packaging bug: `environment/setup.sh` had installed NumPy under `/home/user`, but the job bind-mount hides that path at runtime
- Fixed the environment to install NumPy with `uv pip install --system` and added a startup dependency smoke test to `scripts/run.sh` before the full evaluation

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

Stopped at `majority` because the workspace is already usable as a research gym: the paper's released method is reproduced on the main scored benchmark, the problem/evaluation split is clean, and the remaining gap is the separate complexity-scaling study rather than a failure of the core environment.
