# Design Notes — Iteration N (designer_stage_N)

## Summary

Reviewed the existing train/test split design. **No changes were needed** — the design is solid and covers the key anti-shortcut goals.

## What I Checked

### Split Style
- **Rotation-index split**: 40 train rotations (indices 1,3,4,5,...), 40 test rotations (8,13,15,16,...), 20 reserved
- **Complexity split**: 10 train rotations (0,2,4,6,...), 10 test rotations (1,3,5,7,...) from 20 total
- Split is appropriate: the paper's core claim is robustness across rotations, so different rotation subsets probe different aspects of the method

### Scripts
- `evaluate_train.sh` → `eval/train/evaluate.py` → `scoring/scores_train.json` ✓
- `evaluate_test.sh` → `eval/test/evaluate.py` → `scoring/scores_test.json` ✓
- No hardcoded method defaults ✓
- No cross-imports between train and test ✓

### Metrics Coverage
- **robust_alignment_all** (weight 0.6): 7 metrics — median, mean, std, p95, max error; success_rate; median time
- **robust_alignment_high_outliers** (weight 0.2): 4 metrics — median, p90, success_rate, std error
- **computational_complexity** (weight 0.2): 2 metrics — time at 1M and 10M points
- All metrics measure scientific quantities, not agreement with the paper ✓
- No forbidden metric patterns (deviation_from_paper, etc.) ✓

### Validation
- `python validate.py` passes all checks ✓
- Score stubs deleted ✓

## Potential Runtime Concerns

1. **Complexity experiment is small**: Only 20 total rotations (10 per slice). The time estimates are based on few samples, so there may be higher variance in the complexity metrics. However, since this is already a computed-benchmark (not the main robustness claim), this is acceptable.

2. **raw_complexity_results.json may not exist**: The scripts handle this gracefully by checking if the file exists. If missing, complexity scores are skipped. This is correct behavior.

3. **Methods discovered from raw_results.json**: Scripts enumerate methods from whatever keys exist in the input file, so future agents adding new methods will be automatically scored. This is the correct pattern.

## Design Strengths

1. **Multi-metric triangulation**: 7 + 4 + 2 = 13 total metrics across 3 experiments makes gaming difficult
2. **Statistical robustness metrics**: std, p95, max catch inconsistent methods
3. **Split covers the paper's claim**: The paper claims robustness up to 90% outliers; both experiments test this
4. **Complexity is split too**: Both train and test evaluate computational cost

## No Changes Made

The existing design is well-constructed. All failure modes from the prompt were checked and none were present:
- No copy-paste bugs in scripts ✓
- No hardcoded method defaults ✓
- No paper-agreement metrics ✓
- No leakage between train/test ✓
- Score stubs properly absent ✓
