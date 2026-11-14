# Research Direction

## Scope
Correspondence-free rotation estimation for spherical point patterns, scored
on fresh hidden instances by the evaluators in `eval/`.

## What good progress looks like
- Lower median error on the pattern benchmark without more gross failures
  (watch success rate, p95 and max as well as the median)
- Robustness when most source points are outliers
- Robust image registration under structured clutter
- Reliable registration of sparse, independently sampled point sets (the
  current reference fails grossly on about a quarter of them)
- All within about a CPU-second per registration

## Known weak points of the reference
The reference's 1-degree histograms limit precision (median ~0.6 deg even
without noise); its mean-direction initialisation is unstable when patterns
cover the whole sphere or are sparsely sampled; fine-resolution histograms
alone become noisy and alias on pixel-grid images.

## Out of bounds
Changing the task, the data, the thresholds or the evaluator; exploiting
anything other than the two point sets given per instance.
