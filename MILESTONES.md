# Reproduction Milestones

**Current: method_runs**

## Progress Log

### [2026-04-08 00:36] - method_runs
- Audited the local implementation against the paper's released `vector_alignment_utils.py`
- Fixed FRS to match the paper's source-to-source final SVD estimate instead of aligning to the template
- Implemented the actual hybrid `SPMC+FRS` path instead of delegating to SPMC alone
- Restored the paper's default non-FFT circular shift search and corrected shift-to-degree scaling
- Updated the evaluation harness and run scripts to score `spmc`, `frs`, and `spmc_frs` offline on compute nodes

## Stop Justification
