# Design Notes (current gym)

Superseded design: the earlier rotation-index train/test split over a raw
results file written by the method was replaced in the hardening iteration
(see `HARDENING.md` for the reasons and evidence).

## Current design
- **Interface:** `METHODS = {name: fn(template, source) -> R}` in any `method/*.py`; every entry on disk is scored.
- **Evaluators run the methods** (`eval/{train,test}/evaluate.py` + `runner.py`, separate copies, no shared code): one subprocess per (method, instance group), point sets streamed over a pipe, ground truth only in the evaluator process, every metric recomputed from the returned matrices.
- **Train** = the paper's released dataset (5 templates x 7 released source sets x released R100), one public clutter realisation per image level, public-seed sparse samples. **Hidden test** = the same generators with fresh realisations and rotations from a secret seed in `eval/test/hidden_seed.txt` (made unreadable while methods run).
- **Failure = worst values everywhere** (invalid/non-SO(3) output, exception, import error, empty registry, CPU budget > 1 s/instance).
- **Assets** are SHA-256-verified before unpickling; `scripts/download.sh` pins upstream commits.
- **No wall-clock metric**; compute is a kernel-measured CPU budget.
- Experiments and weights: `scoring/reference.json`, `scoring/EXPERIMENTS.md`.
