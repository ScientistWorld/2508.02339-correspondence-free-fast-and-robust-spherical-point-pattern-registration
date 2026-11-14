> **Superseded:** this report describes the pre-hardening gym (raw-result aggregation). The current evaluation design and its verification are in `HARDENING.md`.

# Verification Report

## Initial Assessment
The workspace started in a mostly good `secondary_claims` state: the released spherical-pattern benchmark and the separate complexity study were already reproduced, `validate.py --compare` passed, and the problem/method separation was intact. The main issue I found was narrower and important for gym use: the canonical top-level scorer in `eval/evaluate.py` was not emitting all of the robust-alignment constraint metrics that `scoring/reference.json` and the train/test slices already declared.

## Issues Found
- Minor: `scoring/scores.json` under-reported the robust-alignment rubric. The main scorer emitted only median/mean/runtime for `robust_alignment_all` and only median/p90 for `robust_alignment_high_outliers`, while `reference.json` and `scores_{train,test}.json` already included success-rate and error-tail constraints.
- Cosmetic: `scoring/EXPERIMENTS.md`, `PROGRESS.md`, `CHECKLIST.md`, `MILESTONES.md`, and `action.yaml` reflected an in-progress submission state instead of the final verified close-out.

## Fixes Applied
- Updated `eval/evaluate.py` so the canonical evaluator now writes `success_rate_1deg`, `std_rotation_error_deg`, `p95_rotation_error_deg`, and `max_rotation_error_deg` for `robust_alignment_all`, plus `success_rate_1deg` and `std_rotation_error_deg` for `robust_alignment_high_outliers`.
- Regenerated `scoring/scores.json` from the existing raw artifacts with `bash scripts/evaluate.sh`.
- Updated `scoring/EXPERIMENTS.md` so the documented metric lists match the actual scored outputs.
- Re-ran `python3 validate.py --compare` and confirmed the workspace still passes structural and scoring checks.
- Verified `scripts/download.sh` remains portable: no `shared/` references in committed code, and both external URLs resolve successfully with `curl -I -L`.
- Updated the milestone/progress/checklist records and switched the control file to a final `done` state at `secondary_claims`.

## Final Judgment
This workspace is ready to serve as a gym for the packaged scope. From-scratch agents can use the method-agnostic `briefing/`, `data/`, `eval/`, and scoring docs without learning the paper's implementation, and improve-mode agents can build on the shipped method and raw artifacts through the same reusable evaluator. The milestone should remain `secondary_claims`: the released spherical-pattern benchmark and the dedicated complexity study are reproduced, while the point-cloud experiment is still absent and the newly added spherical-image path still lacks a fresh scored artifact.

- Milestone: secondary_claims
- Ready for gym use: yes
- Confidence: high
- Key limitation: The gym is strong for the released spherical-pattern benchmark and complexity study, but it still lacks a scored spherical-image artifact and does not package the paper's point-cloud-registration experiment.
