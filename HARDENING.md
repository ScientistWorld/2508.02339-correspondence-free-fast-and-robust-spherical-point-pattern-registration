# Hardening report (final iteration)

Paper: *Correspondence-Free Fast and Robust Spherical Point Pattern Registration* (2508.02339).
Inputs: `REDTEAM.md` (no `REVIEW.md` existed). All numbers below are measured by
the job runs in `jobs/` and saved under `notes/hardening/results/` (`summary.md`,
`summary.json`, per-method score files, per-instance errors). Ranks use the
specified rule: Σ_e w_e Σ_m |c_em| · d_em · (x − x_ref)/σ_em against the stored
reference `spmc_frs`, σ = population std of each metric over the attempts I ran
("valid cohort": every non-failed run; an "honest cohort" of methods that really
register, robust median < 20°, is reported as a sensitivity check). Noise is a
1,000-draw paired bootstrap over test instances (every method sees the same
instances).

## 1. What was wrong and what changed

| REDTEAM finding | Fix |
|---|---|
| The hidden test aggregated raw errors/times **written by the method** (fabricated zeros, negative errors, NaN accepted) | `eval/test/evaluate.py` now **runs every registered method itself** (`METHODS` dicts in `method/*.py`), one subprocess per (method, instance group), streaming only (template, source) point sets over a pipe (`eval/test/runner.py`). Ground truth stays in the evaluator process; every number is recomputed from the returned 3×3 matrices. |
| Test = 40 of the **public** R100 rotations applied to the **public** source sets → enumerating 35 public fingerprints × 100 public answers solved it | Hidden instances are generated in memory from a secret seed that lives only in `eval/test/hidden_seed.txt`: fresh rotations **and** fresh noise/outlier realisations (verified to match the released protocol exactly: B1 = template shuffled, B2+ = isotropic N(0, 0.01²) then renormalised, B3–B7 add ⌊r·N⌋ uniform-sphere outliers), fresh image clutter, fresh sparse subsamples. The seed file is `chmod 0` while method code runs (restored afterwards and at start-up). |
| Empty / partial / missing-accuracy submissions tied or won (rank skips missing values) | A failed run — exception, invalid output (non-finite, not orthonormal within 1e-4, det ≠ +1, wrong shape), import error, empty registry, process death, CPU budget exceeded — gets the **worst value of every metric of every experiment** (180° errors, 0 success). A `method/` with no registry yields a worst-valued `no_registered_method` entry. Instance set and size are fixed by `eval/`. |
| Replacing `RandomRotation100.pkl` changed the truth side | The hidden test never reads the public rotations; every asset it reads (templates, world map) is SHA-256-verified **before unpickling**; a mismatch fails every method. The train evaluator verifies all 41 released files the same way. `scripts/download.sh` now pins both upstream commits and checks hashes. |
| Wall-clock metrics (core time, 10⁶/10⁷-point time) depended on load; stored reference timing did not reproduce | **No metric depends on wall-clock time.** The paper's speed claim ("< 1 s per case", O(n)) is enforced as a constraint: 1 CPU-second per instance (+60 s start-up) per instance group, measured by the kernel (`RLIMIT_CPU` + `RUSAGE_CHILDREN`, BLAS threads pinned to 1). The reference (SPMC+FRS) uses 5–15 % of it per group (FRS ablation ≤ 21 %), so its scores cannot depend on load. Runtime scaling is an unscored diagnostic (`scripts/complexity.sh`). |
| Two image experiments (weight 0.25) were in the rubric but never scored | Implemented in both evaluators (world-map substitute, five clutter levels, SphImg2SphPoints at threshold 0.21 done by the evaluator). |
| No experiment where the method falls short | Added `sparse_alignment`: template and source are **independent** 1,000/3,000-point samples of a pattern (the low-density end of the paper's Fig. 6 study) with noise and 10 % outliers. The reference fails grossly (> 5°) on 26 % of them. |
| `std` metrics reward uniformly bad methods | Removed (non-monotone). Tails are covered by p90/p95/max/mean/success. |
| Train/test shared the same public instances (index split) | Train = the paper's released dataset (Experiment 1 exactly), one public clutter realisation per image level, public-seed sparse samples; test = same generators, secret realisations. `eval/train` and `eval/test` share no code; same interface, metrics and rules; no method name is hard-coded. |

The reproduced method itself is unchanged (it already matches the released code and the paper's Fig. 4: A1 SPMC+FRS medians 0.67/0.26/0.28/0.46/0.36/0.82/0.31° identical; A5 SPMC 0.24 → 11.32°). It only gained a `METHODS` registry.

## 2. Do better results now score higher?

Hidden test (fresh secret instances), rank vs the stored reference, paired-bootstrap 95 % CI:

| Method | robust median / success ≤1° / p95 | high-outlier median | image median | sparse median / success ≤5° | Rank (valid σ) [95 % CI] | Rank (honest σ) [95 % CI] |
|---|---|---|---|---|---|---|
| **dual-init FRS + smoothed polish** (better) | 0.157° / 1.000 / 0.34° | 0.184° | 1.212° | 1.117° / 0.780 | **+0.119** [+0.105, +0.179] | **+0.337** [+0.298, +0.408] |
| **SPMC+FRS + smoothed polish** (better) | 0.165° / 0.993 / 0.35° | 0.185° | 1.226° | 1.282° / 0.738 | **+0.095** [+0.083, +0.106] | **+0.264** [+0.240, +0.283] |
| **dual-init FRS** (better) | 0.416° / 0.883 / 1.14° | 0.524° | 0.746° | 1.341° / 0.780 | **+0.095** [+0.083, +0.154] | **+0.214** [+0.178, +0.290] |
| SPMC+FRS (reference) | 0.587° / 0.821 / 1.38° | 0.636° | 0.869° | 1.677° / 0.738 | 0 (self-noise ±0.049) | 0 (self-noise ±0.082) |
| SPMC+FRS + plain 0.25° FRS (weaker) | 0.420° / 0.812 / 1.69° | 0.505° | 1.646° | 2.933° / 0.586 | −0.248 [−0.302, −0.158] | −0.474 |
| principal axes (closed-form baseline) | 0.349° / 0.801 / 2.12° | 0.787° | 21.1° | 3.758° / 0.570 | −0.275 [−0.328, −0.241] | −0.950 |
| SPMC alone (paper ablation) | 0.572° / 0.660 / 7.68° | 1.103° | 9.32° | 5.674° / 0.480 | −0.403 [−0.451, −0.371] | −1.129 |
| FRS alone (paper ablation) | 0.837° / 0.612 / 166° | 0.822° | 0.976° | 3.052° / 0.584 | −1.015 [−1.073, −0.879] | −1.862 |
| identity | 132° / 0 | 131° | 132° | 131° / 0 | −4.78 | −48.1 |

*Better* variants (`notes/hardening/cases/variants/polish.py`): "smoothed polish" re-runs FRS on 0.25° bins whose histograms are smoothed by a 1° Gaussian (Fourier-domain correlation), inside a 2° trust region; "dual-init" also runs FRS from a principal-axes start and keeps the solution whose aligned source lies on more template density. Every genuinely better variant beats the reference by more than the paired noise and more than the reference's own bootstrap spread; every weaker one (including the paper's own SPMC and FRS ablations, i.e. the paper's hybrid effect) scores lower beyond noise. The plain fine-bin refinement improves the core median but aliases on pixel-grid images, degrades sparse inputs and adds a 123° failure, and the test ranks it below the reference, as it should.

**Before** (REDTEAM, old evaluator): the only "better" variant, an FFT speed-up with identical errors, scored +0.003 vs the stored reference — below the 0.023 seed spread — because the gain was pure wall-clock time; removing FRS scored −0.140/−0.189, identity −5.3.

The paper's claim reproduces in the paper's direction on the hidden test: SPMC+FRS < 1° median overall (0.587°), stays sub-degree at 50–90 % outliers (0.636°) where SPMC degrades (1.10°, p90 8.2°), and fixes FRS's initialisation failures (FRS p95 166°).

## 3. Major shortcuts: before → after

| REDTEAM shortcut | Before (rank vs stored ref) | Fix | After (hidden test) |
|---|---|---|---|
| fabricated zero errors/times | **+0.357** (works) | method outputs are matrices; errors recomputed | not expressible; analogous invalid outputs (`zero_matrix`, `scaled_identity`) → **failed, −6.02** |
| impossible negative values | **+0.599** (works) | same | not expressible; `reflection` (det −1) → **failed, −6.02** |
| NaN errors | undefined | finite-SO(3) check | `nan_matrix` → **failed, −6.02** |
| null / short arrays | evaluator crashed, no score | worst-value failure path | `wrong_shape` → **failed, −6.02** |
| empty submission | **0 (tie)** | empty registry / import failure scored as failed | `empty_registry`, `import_error` → **failed, −6.02** |
| missing accuracy (timing only) | **+0.096** (failed method outranks) | evaluator runs every experiment; no timing metric | `skip_hard_instances` (solves easy instances, refuses the 90 %-outlier ones) → **failed, −6.02** |
| filter easy configurations | −0.038 / +0.011 | instance set fixed by `eval/` | same `skip_hard_instances` → **failed** |
| stale reference artifacts / forged final score | 0 tie (fresh ref) | raw files never read; output always overwritten | forged `scores_test.json` + fake `raw_results.json` left on disk: identity still scored at its true 132° (−4.78) |
| replace public rotations with identities | **+0.357** (works) | test never reads them; hashes verified | test unaffected (identity 132°); train run → integrity failure, all methods worst |
| (new) replace a public template | — | hash verified before unpickling | all methods **failed** on the test |
| public-answer enumeration | **+0.355** (solves test: 0° median) | secret fresh rotations and realisations | **97.3° median, −4.07** on test (still 0.0° on train, which uses the public answers by design and is not ranked) |
| (new) read the hidden seed during the run | — | seed file unreadable while methods run | probe logged `DENIED (PermissionError)` in the test (`READABLE` in train, where nothing is secret) |
| (new) unlimited compute | — | 1 CPU-s/instance budget | `cpu_hog_3s` killed at the 560 CPU-s group budget → **failed, −6.02** |
| brute force over SO(3) | — | — | 4,000-rotation density-correlation grid: 10.1° median, **−1.57** |

## 4. Shortcuts left (and why)

- **Hidden seed in git history.** `eval/test/hidden_seed.txt` is committed (the hidden test must run from a clone). If the hidden-test container contains `.git` with that history, a method could read it via git objects; locking `.git` during the run would risk corrupting the repository. Left to the grader (it requires reading evaluator files, an explicit violation).
- **Undoing the lock.** A method running as the same user could `chmod` the seed file back before reading it. Explicit tampering; left to the grader.
- **Escaping CPU accounting** with daemonised, never-reaped grandchildren (forked workers that are reaped *are* counted). Left to the grader; the gym brief says not to defend against leftover processes.
- **Wall-clock hang guard.** Kills a method process only after 2 × its CPU budget + 300 s of wall time (stops methods that sleep without using CPU). The reference needs < 1/20 of that, so stored scores do not depend on load.
- **Public templates.** The hidden test uses the paper's five public template patterns (the template is an input anyway); a method may precompute per-template tables. This is legitimate amortisation, not answer leakage: rotations, noise, outliers, clutter and subsamples are all fresh.
- **Moment methods on the paper's own protocol.** Uniform-sphere outliers are isotropic, so a closed-form principal-axes estimate is competitive on the core benchmark (median 0.35° vs 0.59°). It stays below the reference overall (−0.275, CI excludes 0; −0.95 under honest σ) because images and sparse inputs break it, and below every genuine improvement. The core protocol was kept as the paper's.

## 5. Reference score before and after

| | Before (old evaluator: public rotations 40-index slice, method-written errors) | After (hidden test: fresh secret instances, evaluator-computed) |
|---|---|---|
| robust median / mean / success ≤1° / p95 / max | 0.600° / 0.660° / 0.832 / 1.420° / 2.652° | 0.587° / 0.654° / 0.821 / 1.377° / 2.652° |
| high-outlier median / p90 / success | 0.631° / 1.306° / 0.795 | 0.636° / 1.217° / 0.808 |
| images median / mean / success (Img5 median / max) | not scored | 0.869° / 2.252° / 0.602 (1.191° / 140.2°) |
| sparse median / mean / success ≤5° | — | 1.677° / 23.70° / 0.738 |
| timing (core median s, 10⁶ s, 10⁷ s) | 0.309 / 0.890 / 10.02 (not reproducible) | not scored; CPU use 0.074 s/instance vs 1 s budget |

The stored reference is deterministic: a second hidden-test run reproduced every SPMC+FRS metric bit-for-bit (`reference_rerun_identical: true`). Train vs test agree (SPMC+FRS robust median 0.597° vs 0.587°, high 0.621° vs 0.636°, images 0.694° vs 0.869°, sparse 1.468° vs 1.677°; the polish variant 0.159° vs 0.165°), so an honest method scores alike while the train-tuned enumeration collapses (0.0° → 97.3°). Image numbers sit on the paper's scale (paper 0.89° overall, Img5 1.32°/peak 2.96°; train Img5 1.34°/2.74°), so they stay as paper results in `reference.json`.

## 6. Headroom

- The reference sits at the bound of **no** scored metric (best: robust success 0.821, max 2.65°; sparse fails grossly on 26 %).
- Three variants score above it beyond noise (§2), and brute force does not.
- One metric saturates for the strongest variant: `success_rate_1deg` reaches 1.000 on both robust experiments for dual-init + polish. Medians (0.157° vs a noise floor far below), p95, the image experiments (where the polish variants are *worse* than the reference) and sparse (22 % still > 5°) keep headroom.
- Baselines make sense: identity −4.78 (132°), principal axes −0.275, both clearly below the reference, with room above it.

## 7. Weights (changed, with reasons)

| Experiment | Before | After | Why |
|---|---|---|---|
| robust_alignment_all | 0.45 | 0.45 | paper's main claim (Exp. 1) |
| robust_alignment_high_outliers | 0.15 | 0.20 | the paper's robustness claim is what distinguishes the hybrid from SPMC/FRS |
| computational_complexity | 0.15 | removed | wall-clock only; the speed claim is now a CPU-budget constraint |
| spherical_image_alignment_all / _high_clutter | 0.15 / 0.10 (never scored) | 0.10 / 0.05 | now actually scored; substitute image, an application rather than the core claim |
| sparse_alignment | — | 0.20 | where the method falls short; real headroom |

Metric changes: removed `median_time_s`, `std_rotation_error_deg` (both experiments) and the timing experiment; added `success_rate_1deg` to the image experiment and the sparse metrics. Coefficients of retained metrics are unchanged. The paper-reported numbers are unchanged; values that were in removed time metrics moved to `reference.json → _paper_reported_unscored`, together with the paper's textual claims and the Fig. 4 A1 medians. The aggregate robust-alignment `results` values (e.g. SPMC+FRS 0.8°) are not printed in the paper; they are earlier approximations, kept unchanged and annotated.

## 8. Not fixed / stated plainly

- **FPFH+QUASAR** (the paper's comparator) is still not implemented; its numbers remain paper-only baselines in `reference.json`. The point-cloud registration experiments (ModelNet40, 3DMatch, KITTI) are not part of the gym.
- **Runtime/O(n) scaling** is not a ranked quantity; only the CPU budget enforces speed. A method 10× slower than the reference but within 1 CPU-s/instance is not penalised.
- **Image experiment** uses a public GeoJSON world map and synthetic rectangle/ellipse clutter instead of the paper's unreleased image and coloured clutter.
- **σ normalisation** in my ranks uses my own attempt cohort; the real cohort will differ. The ordering better > reference > weaker > shortcuts holds under both cohorts I tried.
- **`max_rotation_error_deg`** (robust 0.15, Img5 0.4 coefficients) depends on single instances; it widens bootstrap intervals for methods that add rare failures (e.g. the plain fine-bin variant) but did not reverse any ordering.
- **Compute nodes were drained every ~25 min** during this iteration; the hidden test of the three shipped methods takes ~23 min, so a hidden-test job may need a restart (results are deterministic, so a restart reproduces them exactly).

## 9. Files

- Evaluators: `eval/test/{evaluate,runner}.py` + `eval/test/hidden_seed.txt` (secret), `eval/train/{evaluate,runner}.py`; launchers `scripts/evaluate_{train,test}.sh` (no arguments; every registered method on disk).
- Reference: `method/spherical_registration.py` (`METHODS`: `spmc`, `frs`, `spmc_frs`); baselines `baseline/baselines.py` (`scripts/baseline.sh`).
- Stored reference scores: `scoring/scores_test.json`, `scoring/scores_train.json` (= `scores.json`), from the shipped `method/` alone.
- Verification bundle: `notes/hardening/run_cases.sh`, `cases/`, `scenarios.py`, `analyze.py`, `results/`.
- Reproduce the reference: `bash scripts/download.sh` (online) then `bash scripts/run.sh` / `scripts/reproduce.sh` (offline CPU).
