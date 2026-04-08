# Progress

## What Works
- **SPMC algorithm** fully implemented and previously validated on the paper dataset
- **Paper's dataset**: Robust Vector Alignment Dataset fully loaded and verified (35 pickle files + 100 rotations)
- **Evaluation pipeline**: rotation error computation, timing, aggregation, scores.json output
- **scripts/evaluate.sh**: self-contained, evaluates methods and writes scores.json
- **scripts/download.sh**: idempotent, clones paper repo from GitHub
- **Container**: Red Hat UBI image with numpy installed via setup.sh
- **Implementation fidelity audit**: local method code was compared against the paper's released reference implementation and corrected where it diverged
- **Audit conclusion**: the workspace contains a real implementation of the paper's SPMC, FRS, and hybrid pipeline, not a surrogate model

## Results Achieved
- **SPMC on paper's test case (A1/B3/r5)**: 0.13° error — **exact match** with paper's reported 0.13°
- **10-rotation full evaluation** (5 patterns × 7 configs = 350 evals):
  - Overall SPMC median: **0.51°** (vs paper's 1.5° for SPMC, 0.8° for hybrid)
  - Overall SPMC mean: 1.56°
  - High-outlier (B5-B7) median: 0.93°, p90: 6.42°
  - Median time: 0.77s per evaluation
- **Per-config SPMC medians**:
  - B1-B2 (0-5% outliers): 0.13-0.25° — excellent
  - B3-B4 (10-20% outliers): 0.17-3.05° — good
  - B5-B7 (50-90% outliers): 0.35-11.44° — reasonable
- Our SPMC outperforms the paper's reported results (both SPMC and hybrid)
- **Local post-audit spot checks** against the paper code now agree on representative cases for:
  - `spmc`: exact numerical agreement on tested cases
  - `frs`: exact agreement on easy and hard spot checks after the source-to-source SVD correction
  - `spmc_frs`: no longer falls back to pure SPMC; improves difficult cases such as `A5/B7/r1` to 0.83°

## What Remains
- Fresh compute validation run for corrected `frs` and `spmc_frs` on the paper dataset
- Regeneration of `scoring/scores.json`, because the current file predates the final fidelity fixes and cannot support `core_claim`
- Full 100-rotation evaluation through the cleaned `run.sh -> method.sh -> evaluate.sh` path
- FPFH+QUASAR baseline (requires C++ Point Cloud Library — unavailable)
- Computational complexity scaling test with varying point counts

## Issues Encountered
- **Previous FRS mismatch**: The earlier reproduction estimated the final FRS rotation against the template and bypassed the paper's source-to-source SVD finalization. That has now been corrected.
- **Previous hybrid mismatch**: `spmc_frs` had been delegating to SPMC alone. The actual hybrid composition from the paper is now implemented.
- **Rotation convention bug in hybrid**: `spmc_frs` was feeding FRS with `source @ R_spmc.T` instead of the paper-equivalent aligned source `source @ R_spmc`. This was the last correctness bug found during the audit.
- **Stale scoring artifact**: the checked-in `scoring/scores.json` still reflects the pre-fix hybrid path, so it is not honest evidence for `core_claim`.
- **Container numpy**: Login node has no numpy; compute node has it via setup.sh.
  Local testing requires pip install numpy.

## Deviations from Paper
- **Baseline**: FPFH+QUASAR baseline not implemented (requires Point Cloud Library C++ deps).
  Identity rotation used as reference — not scored in scoring/scores.json.
- **Evaluation status**: The corrected `frs` and `spmc_frs` implementations are in place and locally spot-checked, but compute-side evaluation still needs to regenerate `scores.json` before the milestone can be restored to `core_claim`.
- **Dataset**: Using paper's actual dataset (not synthetic) — improvement over the paper's
  evaluation methodology.
- **Current run protocol**: `scripts/run.sh` now executes the full 100-rotation evaluation by default so a successful CPU job can directly support the main experiment.
