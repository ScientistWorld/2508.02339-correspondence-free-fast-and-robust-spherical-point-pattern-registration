# Progress

## What Works
- **SPMC algorithm** fully implemented and previously validated on the paper dataset
- **Paper's dataset**: Robust Vector Alignment Dataset fully loaded and verified (35 pickle files + 100 rotations)
- **Evaluation pipeline**: rotation error computation, timing, aggregation, scores.json output
- **scripts/evaluate.sh**: method-agnostic aggregation path that reads raw results and writes scores.json
- **data access**: baseline and method runs now share the same method-agnostic loader in `data/dataset.py`
- **scripts/download.sh**: idempotent, clones paper repo from GitHub
- **Container**: Red Hat UBI image with numpy installed via setup.sh
- **Implementation fidelity audit**: local method code was compared against the paper's released reference implementation and corrected where it diverged
- **Audit conclusion**: the workspace contains a real implementation of the paper's SPMC, FRS, and hybrid pipeline, not a surrogate model
- **End-to-end local smoke test**: `scripts/method.sh -> scripts/evaluate.sh -> validate.py --compare` completed successfully on the real dataset with `N_ROTATIONS=1`
- **Submission state**: offline scripts were cleaned up and pushed; the pending job uses the audited algorithm path without further method changes
- **Scoring integrity fix**: canonical evaluation no longer fabricates a computational-complexity experiment by extrapolating runtime from the main benchmark
- **Single-writer scoring path**: `scripts/run_experiment.py` now writes only `scoring/raw_results.json`; canonical `scoring/scores.json` is left exclusively to `eval/evaluate.py`
- **Environment fix prepared**: NumPy installation was moved from a bind-mounted workspace path to system site-packages inside the setup overlay
- **Environment fix revised**: the scheduler's fakeroot overlay cannot write to `/usr/local`, so NumPy is now targeted to `/opt/python-packages` and exposed via `PYTHONPATH` in `scripts/run.sh`
- **Chunked evaluation path**: `scripts/run_experiment.py` now supports rotation slices and incremental checkpoints, so partial CPU runs still leave usable raw results and scores
- **Resume-safe continuation path**: the evaluator now reloads `scoring/raw_results.json`, skips already completed pattern/config groups, and rewrites canonical `scoring/scores.json` after each checkpoint so interrupted jobs can continue rather than restart
- **Fresh compute-side core-claim evidence**: job `9141a59a-c99` completed all 35 pattern/config groups for the 20-rotation slice, validated the canonical scoring artifacts, and confirmed the released algorithm path on the real paper dataset
- **Full benchmark reproduction**: job `6cc72205-3b7` extended every config from 20 to 100 rotations, auto-resumed across worker restarts, and completed the paper's full main benchmark with validated canonical scores
- **Complexity benchmark path**: added `scripts/run_complexity_experiment.py` and `scripts/complexity.sh` for the paper's separate Fig. 6 runtime-scaling study on `A3/B3`
- **Evaluator extension**: `eval/evaluate.py` and `scripts/evaluate.sh` now aggregate both the main benchmark raw results and optional complexity raw results into one canonical `scoring/scores.json`
- **Final gym verification**: method-agnostic briefing and scoring docs were reviewed and rewritten where needed so future from-scratch agents can understand the task without seeing the paper's implementation choices
- **Dataset separation fix**: the canonical released dataset now lives under `data/vector_alignment_dataset`, and the shared loader in `data/dataset.py` no longer depends on assets inside `method/`

## Results Achieved
- **SPMC on paper's test case (A1/B3/r5)**: 0.13° error — **exact match** with paper's reported 0.13°
- **1-rotation end-to-end smoke test** (35 evaluations on the paper dataset through the submitted script path):
  - Overall SPMC median: **0.50°**
  - Overall FRS median: **1.09°**
  - Overall SPMC+FRS median: **0.52°**
  - High-outlier SPMC+FRS median: **0.74°**
  - `validate.py --compare` passed on the generated artifacts
- **10-rotation full evaluation** (5 patterns × 7 configs = 350 evals):
  - Overall SPMC median: **0.51°** (vs paper's 1.5° for SPMC, 0.8° for hybrid)
  - Overall SPMC mean: 1.56°
  - High-outlier (B5-B7) median: 0.93°, p90: 6.42°
  - Median time: 0.77s per evaluation
- **Per-config SPMC medians**:
  - B1-B2 (0-5% outliers): 0.13-0.25° — excellent
  - B3-B4 (10-20% outliers): 0.17-3.05° — good
  - B5-B7 (50-90% outliers): 0.35-11.44° — reasonable
- **Compute-side partial 20-rotation run** (`768b2584-16c`, actual paper dataset and algorithm):
  - Completed all 21 configs for patterns `A1`-`A3` before infrastructure loss
  - Preserved **420** evaluated rotations in `scoring/raw_results.json`
  - This is fresh compute-node evidence from the released benchmark, not a local smoke test
- **Compute-side full 20-rotation benchmark** (`9141a59a-c99`, actual paper dataset and algorithm):
  - Completed all **5 patterns × 7 configs × 20 rotations = 700 evaluations**
  - Canonical `validate.py --compare` passed on the produced `scoring/scores.json`
  - `spmc_frs`: **0.586°** median overall, **0.645°** mean overall, **0.294s** median runtime
  - `spmc_frs` high-outlier subset (B5-B7): **0.626°** median, **1.277°** p90
  - `spmc`: **0.536°** median overall, **0.918°** median on high outliers
  - `frs`: **0.840°** median overall, but unstable tail behavior at high outliers (`p90 = 150.129°`)
- **Compute-side full 100-rotation benchmark** (`6cc72205-3b7`, actual paper dataset and algorithm):
  - Completed all **5 patterns × 7 configs × 100 rotations = 3500 evaluations**
  - Survived scheduler restarts by resuming from the saved raw checkpoint and still finished with validated canonical outputs
  - `spmc_frs`: **0.597°** median overall vs. **0.8°** in the paper, **0.659°** mean overall vs. **2.1°**, **0.307s** median runtime vs. **0.9s**
  - `spmc_frs` high-outlier subset (B5-B7): **0.621°** median vs. **1.1°**, **1.317°** p90 vs. **6.2°**
  - `spmc`: **0.545°** median overall, **1.033°** median on high outliers
  - `frs`: **0.836°** median overall, but still a heavy high-outlier tail (`p90 = 150.259°`)
- Our SPMC outperforms the paper's reported results (both SPMC and hybrid)
- **Local post-audit spot checks** against the paper code now agree on representative cases for:
  - `spmc`: exact numerical agreement on tested cases
  - `frs`: exact agreement on easy and hard spot checks after the source-to-source SVD correction
  - `spmc_frs`: no longer falls back to pure SPMC; improves difficult cases such as `A5/B7/r1` to 0.83°

## What Remains
- Compute-side execution of the computational complexity scaling test with varying point counts
- Optional FPFH+QUASAR baseline reimplementation (requires Point Cloud Library C++ stack that is currently unavailable here)

## Issues Encountered
- **Failed CPU job `62d88eed-373`**: compute-side import failed before evaluation started: `ModuleNotFoundError: No module named 'numpy'`
- **Root cause**: `environment/setup.sh` had installed NumPy under `/home/user/python-packages`, but `/home/user` is bind-mounted at runtime, hiding that installation from the container
- **Mitigation**: switched to `uv pip install --system numpy` and added an explicit import smoke test in `scripts/run.sh`
- **Setup overlay failure before resubmission**: the environment build reported `/usr/local/lib/python3.10/dist-packages/...: Invalid argument`, so the system-site install target is not usable under fakeroot here
- **Mitigation revised**: install NumPy into `/opt/python-packages` with `python3 -m pip --target` and export that path in `scripts/run.sh`
- **Interrupted CPU job `24712a1a-0f8`**: the actual method ran, but the Ray worker died after ~1000/3500 evaluations and the restarted attempt was orphaned before any final artifact was written
- **Mitigation**: shortened the default job to a 20-rotation slice and added per-config raw-result checkpoints so future runs survive partial interruption
- **Interrupted CPU job `768b2584-16c`**: the 20-rotation slice progressed farther and checkpointed through `A3_B7`, but the worker was orphaned again before the final evaluator step
- **Mitigation**: `scripts/run_experiment.py` now reloads existing raw checkpoints, skips finished configs, and writes `scores.json` at every per-config checkpoint so future interruptions still leave canonical scoring artifacts
- **Successful continuation job `9141a59a-c99`**: resume-from-checkpoint worked as intended, finished the remaining `A4`-`A5` configs, and left a validated canonical score artifact
- **Successful full-benchmark job `6cc72205-3b7`**: the Ray scheduler restarted the task twice, but the checkpoint/resume path preserved progress and completed the 100-rotation benchmark anyway
- **Cancelled CPU submission**: the prior queued CPU job did not produce results, so a fresh submission is still required
- **Previous FRS mismatch**: The earlier reproduction estimated the final FRS rotation against the template and bypassed the paper's source-to-source SVD finalization. That has now been corrected.
- **Previous hybrid mismatch**: `spmc_frs` had been delegating to SPMC alone. The actual hybrid composition from the paper is now implemented.
- **Rotation convention bug in hybrid**: `spmc_frs` was feeding FRS with `source @ R_spmc.T` instead of the paper-equivalent aligned source `source @ R_spmc`. This was the last correctness bug found during the audit.
- **Login-node limitation**: the login node still lacks NumPy, so Python-side spot checks must rely on compute jobs until the refreshed setup overlay is built
- **Current complexity-path limitation**: the new Fig. 6 scripts parse cleanly via `py_compile`, but they cannot be executed on the login node because NumPy is only available inside the compute overlay
- **Stale score artifact**: `scripts/run_experiment.py` had still been writing a summary `scoring/scores.json`, which allowed non-canonical score blocks to persist even after the evaluator was cleaned. That path has now been removed.
- **Gym-verification issue**: several benchmark-facing markdown files still leaked paper-specific method details and the canonical dataset path still pointed into `method/`. Those issues are now fixed, and the workspace passed a fresh `python validate.py --compare` check afterward.

## Deviations from Paper
- **Baseline**: FPFH+QUASAR baseline not implemented (requires Point Cloud Library C++ deps).
  Identity rotation used as reference — not scored in scoring/scores.json.
- **Scoring scope**: the canonical `scores.json` now reports only experiments actually measured on a run. The paper's separate computational-complexity study remains in `reference.json` but is not claimed in reproduced scores until it is explicitly run.
- **Evaluation status**: the workspace now has validated compute-side results for the paper's two main scored experiments on the full 100-rotation benchmark. The remaining gap is the separate complexity-scaling study.
- **Dataset**: Using paper's actual dataset (not synthetic) — improvement over the paper's
  evaluation methodology.
- **Current run protocol**: `scripts/run.sh`, `scripts/method.sh`, `scripts/evaluate.sh`, and `scripts/reproduce.sh` all export the overlay Python path directly, so they now work standalone inside the container rather than only through `run.sh`.
- **Baseline packaging**: the shipped baseline is an identity-rotation sanity check on the released dataset, not the paper's FPFH+QUASAR baseline.

## Final Status
- Workspace verified as gym-ready at milestone `majority`
- Main limitation: the separate computational-complexity scaling study remains documented in `reference.json` but is not yet reproduced in `scores.json`
