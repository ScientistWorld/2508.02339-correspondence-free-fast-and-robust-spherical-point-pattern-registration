# Reproduction Milestones

**Current: method_runs**

## Progress Log

### [2026-04-06 09:30] - method_runs
- Container build troubleshooting: switch base image to Red Hat UBI (registry.access.redhat.com/ubi9/python-311)
  - mirror.gcr.io: returned corrupted JSON during blob pull
  - Docker Hub: unauthenticated rate-limited
  - GHCR: requires authentication
  - Red Hat UBI: publicly accessible (HTTP 200, no auth)
- Removed paper PDF (35MB) to free filesystem quota
- Full reproduction code ready: SPMC, FRS, SPMC+FRS on synthetic spherical dataset
- Job resubmitted with fixed container image

### [2026-04-05 14:00] - method_runs
- Implemented SPMC (Spherical Pattern Matching by Correlation) algorithm
- Implemented FRS (Fast Rotation Search) algorithm
- Implemented SPMC+FRS hybrid algorithm
- Created synthetic spherical dataset generator matching paper's "Robust Vector Alignment Dataset"
- Implemented evaluation pipeline with angular error and timing metrics
- Created baseline (identity rotation) for reference
- Job submitted to compute cluster to validate end-to-end execution

### [2026-04-05 12:00] - none
- Read the paper thoroughly
- Identified core algorithms: SPMC, FRS, SPMC+FRS
- Filled in briefing files (problem.md, evaluation.md, method.md, overview.md)
- Created reference.json with paper's reported numbers
- Created scoring documentation (TARGETS.md, CONSTRAINTS.md, DIRECTION.md)
