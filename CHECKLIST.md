# Reproduction Checklist

Check off items as you complete them. Order doesn't matter — work however makes sense for this paper.

## Briefing
- [x] `briefing/problem.md` (method-agnostic)
- [x] `briefing/evaluation.md` (method-agnostic)
- [x] `briefing/method.md`
- [x] `briefing/overview.md`

## Scoring
- [x] `scoring/reference.json` — paper's reported / paper-derived comparison targets
- [x] Workspace validated via `python validate.py` — all checks pass
- [x] `scoring/scores.json` — local smoke-test numbers exist
- [x] Canonical scorer reports only directly measured experiments (no extrapolated complexity claims)
- [x] `scoring/TARGETS.md` — primary, constraint, and ablation targets
- [x] `scoring/CONSTRAINTS.md` — what a scientist must hold fixed
- [x] `scoring/DIRECTION.md` — research direction scope for scientist

## Code
- [x] Evaluation code in `eval/` — method-agnostic rotation error computation
- [x] Method implementation in `method/spherical_registration.py`
- [ ] Baseline implementation in `baseline/` (paper baseline still unavailable; `scripts/baseline.sh` provides only an identity sanity check)

## Scripts
- [x] `scripts/evaluate.sh` — self-contained evaluation pipeline
- [x] `scripts/reproduce.sh` — calls evaluate.sh
- [x] `scripts/download.sh` — idempotent, clones paper repo
- [x] `scripts/baseline.sh` — identity sanity baseline on the released dataset
- [x] `scripts/run_experiment.py` — runs SPMC, FRS, and SPMC+FRS on the paper dataset
- [x] `scripts/run_complexity_experiment.py` — runs the paper's A3/B3 runtime-scaling benchmark
- [x] `scripts/run.sh` — Ray job script for the remaining resume-safe CPU complexity benchmark

## Environment
- [x] `environment/container.def` + `environment/setup.sh`

## Data
- [x] Dataset acquired: paper's Robust Vector Alignment Dataset at data/vector_alignment_dataset/ (copied from the paper's released repo)
- [x] Pretrained models downloaded if needed (N/A — no ML models used)

## Milestones
- [x] `method_runs` — SPMC, FRS, SPMC+FRS execute end-to-end without errors
- [x] `core_claim` — compute-side results support the released method on all 5 patterns × 7 configs
- [x] `core_claim_plus` — full 100-rotation benchmark completed on compute with validated scores
- [ ] `secondary_claims`
- [x] `majority` — 2 of 3 scored reference experiments reproduced (main benchmark + high-outlier subset)
- [ ] `near_complete` — pending the compute-side complexity benchmark
- [ ] `full`

## Notes
- **SPMC fully working**: exact agreement with the released code on audited spot checks
- **FRS fixed in code**: final source-to-source SVD step now matches the released implementation
- **spmc_frs fixed in code**: the hybrid now uses the actual SPMC initialization plus FRS refinement path
- **Current limitation**: the separate complexity-scaling study remains in `reference.json` but is not part of the verified scored gym because it has not been reproduced yet
- **Current submission state**: the workspace remains open at `majority` and the next queued step is a CPU submission for the remaining complexity-scaling study
- **Paper's baseline (FPFH+QUASAR)**: Not implemented — requires C++ dependencies (Point Cloud Library) that are unavailable
- **Identity rotation baseline**: Used as reference (999° error)
