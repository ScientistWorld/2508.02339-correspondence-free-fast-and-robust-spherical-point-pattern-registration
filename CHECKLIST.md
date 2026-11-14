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
- [x] Baseline implementation in `baseline/` (identity + principal-axes moment matching; the paper's FPFH+QUASAR comparator is still unavailable)

## Scripts
- [x] `scripts/evaluate.sh` — self-contained evaluation pipeline
- [x] `scripts/reproduce.sh` — calls evaluate.sh
- [x] `scripts/download.sh` — idempotent, clones paper repo
- [x] `scripts/baseline.sh` — identity sanity baseline on the released dataset
- [x] `scripts/run_complexity_experiment.py` — runs the paper's A3/B3 runtime-scaling benchmark
- [x] `eval/train` + `eval/test` run every registered method (pattern, image and sparse experiments); see `HARDENING.md`
- [x] `scripts/run.sh` — latest verified Ray job script

## Environment
- [x] `environment/container.def` + `environment/setup.sh`

## Data
- [x] Dataset acquired: paper's Robust Vector Alignment Dataset at `data/downloads/vector_alignment_dataset/` (copied from the paper's released repo)
- [x] Pretrained models downloaded if needed (N/A — no ML models used)

## Milestones
- [x] `method_runs` — SPMC, FRS, SPMC+FRS execute end-to-end without errors
- [x] `core_claim` — the released robust-alignment benchmark is reproduced on the real dataset with validated canonical scores
- [x] `core_claim_plus` — the main benchmark is reproduced across the full 100-rotation released protocol
- [x] `secondary_claims` — the separate computational-complexity study is also reproduced and scored
- [ ] `majority`
- [ ] `near_complete`
- [ ] `full`

## Notes
- **SPMC fully working**: exact agreement with the released code on audited spot checks
- **FRS fixed in code**: final source-to-source SVD step now matches the released implementation
- **spmc_frs fixed in code**: the hybrid now uses the actual SPMC initialization plus FRS refinement path
- **Current limitation**: the packaged gym still does not reproduce the paper's point-cloud-registration experiment, and the new spherical-image adaptation benchmark still needs a fresh compute-side result before it counts toward a higher milestone
- **Current verification state**: the workspace is gym-ready for the released spherical-pattern benchmark and the complexity study, which supports `secondary_claims` but not `majority`
- **Scoring alignment**: top-level `scores.json` now includes the same robust-alignment constraint metrics already declared in `reference.json` and the train/test slices
- **Paper's baseline (FPFH+QUASAR)**: Not implemented — requires C++ dependencies (Point Cloud Library) that are unavailable
- **Identity rotation baseline**: Used as reference (999° error)
