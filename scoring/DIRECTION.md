# Research Direction

## Scope
This gym is about correspondence-free rotation estimation for spherical point patterns. A scientist should try to improve rotation accuracy and robustness on the released benchmark while preserving the problem definition and evaluation protocol.

## What Good Progress Looks Like
- Lower median rotation error on the full benchmark
- Better robustness on the hardest outlier settings
- Faster runtime without sacrificing the accuracy gains above
- Runtime scaling that remains close to linear on the dedicated complexity study

## Valid Research Space
Scientists may explore geometric, statistical, optimization-based, or learned approaches, as long as they still solve the same benchmarked task: estimate the rotation directly from the two unordered spherical point sets without using benchmark-specific correspondences.

## Out of Bounds
- Switching to a different task, dataset, or output representation
- Using privileged correspondences or labels that are unavailable at evaluation time
- Improving scores only by scaling compute or changing the benchmark protocol instead of improving the method

## Practical Guidance
Work should stay focused on methods that operate on the released spherical point-set benchmark and produce comparable rotation matrices under the existing evaluator. Improvements should be measured through the canonical `scripts/evaluate.sh` interface.
