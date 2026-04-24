# Reproduction Milestones

**Current: full**

## Progress Log

### [2026-04-24 00:05] - full
- Reviewed successful split-evaluation job `9610560c-51f`: `scripts/run.sh` regenerated the raw complexity benchmark, refreshed canonical `scoring/scores.json`, wrote `scoring/scores_train.json` and `scoring/scores_test.json`, and passed `validate.py --compare`
- Closed the last remaining reproduction gap by measuring the paper's computational-complexity experiment alongside the already reproduced robust-alignment benchmarks, so all three reference experiments are now backed by real run artifacts
- Promoted the workspace to `full`; train/test complexity metrics now come from disjoint fixed halves of the 20-rotation timing benchmark so the primary ranking metric differentiates across slices without changing the underlying scientific quantity

### [2026-04-13 18:59] - majority
- Final verification confirmed the claimed `majority` milestone is justified by the checked-in results and scoring artifacts
- Rechecked folder structure, method/eval separation, method-agnostic scientist docs, and the scoring rubric for the experiments actually present in `scores.json`
- Closed the workspace for gym use at `majority`; the remaining limitation is still the unreproduced reference `computational_complexity` experiment

### [2026-04-13 10:35] - majority
- Final verification confirmed the claimed `majority` milestone remains justified by the reproduced released benchmark and reusable scoring artifacts
- Fixed the remaining environment-packaging issue by removing Python package installation from `environment/container.def`, leaving `setup.sh` as the single Python dependency entrypoint
- Closed the workspace for gym use at `majority`; the only remaining gap is the unreproduced reference computational-complexity experiment

### [2026-04-13 10:20] - majority
- Reopened the control file from a stale permanent `done` state so the remaining Fig. 6 complexity benchmark can actually be scheduled
- Rechecked the released SPMC/FRS implementation, fixed a small FRS timing-path mismatch, and confirmed the local submission still follows the paper's `A3/B3` scaling protocol rather than changing the algorithm
- Prepared a fresh CPU submission for the unreproduced `computational_complexity` experiment; milestone remains `majority` until that run lands

### [2026-04-12 23:52] - majority
- Completed final gym verification and confirmed the existing `majority` milestone is justified by the reproduced released benchmark results
- Removed benchmark-facing method leakage from scientist documents, cleaned the container/setup split, and tightened the end-to-end reproduction script preflight
- No new experiment was required for verification; the remaining limitation is still the unreproduced computational-complexity study

### [2026-04-12 23:48] - majority
- Reopened the workspace from an incorrect permanent `done` state because the paper's Fig. 6 computational-complexity experiment is still unmeasured
- Fixed a stale evaluator-call regression in `scripts/run_experiment.py` so `scripts/method.sh` and `scripts/reproduce.sh` are executable again
- Fixed the complexity scoring contract to emit only the metric names declared in `scoring/reference.json` and tightened `scripts/run.sh` to preflight the actual `A3/B3` assets before a fresh CPU submission

### [2026-04-09 14:10] - majority
- Finalized the benchmark-facing wrap-up documents so the scored targets, experiments, constraints, and direction are consistent with the checked-in `scores.json`
- Confirmed `python validate.py` still passes after the final documentation cleanup
- Closed the workspace at `majority`; the only remaining unreproduced reference item is the separate computational-complexity study

### [2026-04-09 14:01] - majority
- Ran final gym verification on folder structure, method/eval separation, briefing files, scoring files, and reusable scripts
- Fixed the remaining scoring-rubric issue by aligning `scoring/TARGETS.md` to the experiments actually present in `scoring/scores.json`
- Rebalanced reference experiment weights so the current scored gym emphasizes the full benchmark more than the overlapping high-outlier subset; milestone remains `majority`

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

### [2026-04-23 23:55] - method_runs
- Ran the first split-evaluation compute job `fd93407b-db0`; the container and setup both succeeded, but `scripts/run.sh` failed immediately when `scripts/run_complexity_experiment.py` could not import the repo-root `data` package
- Fixed the shell entrypoints to prepend `/home/user` to `PYTHONPATH` before invoking any repository Python scripts, so direct `python3 scripts/*.py` execution resolves `data/`, `method/`, and `eval/` consistently on compute nodes
- Kept the milestone at `method_runs` pending a successful split-evaluation rerun that writes fresh `scores_train.json` and `scores_test.json`

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
- Completed at milestone `full`.
