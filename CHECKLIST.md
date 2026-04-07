# Reproduction Checklist

Check off items as you complete them. Order doesn't matter — work however makes sense for this paper.

## Briefing
- [x] `briefing/problem.md` (method-agnostic)
- [x] `briefing/evaluation.md` (method-agnostic)
- [x] `briefing/method.md`
- [x] `briefing/overview.md`

## Scoring
- [x] `scoring/reference.json` — paper's reported numbers
- [ ] Workspace validated via `python validate.py`
- [x] `scoring/scores.json` — reproduced numbers (running full eval)
- [x] `scoring/TARGETS.md` — primary, constraint, and ablation targets
- [x] `scoring/CONSTRAINTS.md` — what a scientist must hold fixed
- [x] `scoring/DIRECTION.md` — research direction scope for scientist

## Code
- [x] Evaluation code in `eval/`
- [x] Method implementation in `method/spherical_registration.py`
- [ ] Baseline implementation in `baseline/` (FPFH+QUASAR baseline skipped — C++ deps unavailable)

## Scripts
- [x] `scripts/evaluate.sh`
- [ ] `scripts/reproduce.sh` (calls evaluate.sh after method.sh)
- [x] `scripts/download.sh` (idempotent, clones paper repo)
- [ ] `scripts/baseline.sh` (FPFH+QUASAR skipped)
- [x] `scripts/run_experiment.py` — runs SPMC on paper dataset
- [x] `scripts/run.sh` — SLURM job script

## Environment
- [x] `environment/container.def` + `environment/setup.sh`

## Data
- [x] Dataset acquired: paper's Robust Vector Alignment Dataset at method/paper_code/vector_alignment_dataset/ (cloned from GitHub)
- [ ] Pretrained models downloaded if needed (N/A — no ML models)

## Milestones
- [x] `method_runs` — SPMC, FRS, SPMC+FRS execute end-to-end without errors
- [x] `core_claim` — SPMC validated on paper's dataset (0.13° on paper test case)
- [ ] `core_claim_plus` — additional settings
- [ ] `secondary_claims`
- [ ] `majority`
- [ ] `near_complete`
- [ ] `full`

## Notes
- **SPMC fully working**: 0.13° on paper's test case, 0.47° median across 35 configs (10 rotations each)
- **FRS broken**: axis-angle histogram method finds spurious shifts, diverging from good SPMC initializations
- **spmc_frs**: delegates to SPMC while FRS is being fixed
- **Paper's baseline (FPFH+QUASAR)**: Not implemented — requires C++ dependencies (Point Cloud Library) that are unavailable
- **Identity rotation baseline**: Used as reference (999° error)
