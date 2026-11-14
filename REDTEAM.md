# Audit: does this gym reward better research?

## 1. Genuine improvements and degradations

**Controlled honest ordering passes, but a reliable improvement over the stored reference is not established.** An exact faster implementation scores **+0.052340** against a fresh reference, exceeding the three-seed rank spread of **0.022996**. Removing FRS scores **−0.140031** and returning identity scores **−5.267160** against that same reference. However, the faster implementation's gain against the **stored** reference is only **+0.003398**, smaller than the seed spread. Treat that stored-reference gain as noise. The gym also fails the broader audit: successful empty submissions tie the reference, fabricated measurements beat it, and enumerating the public answers solves the hidden accuracy test.

**The paper's FPFH+QUASAR comparison remains unverified.** That comparator is described in the rubric but has neither an implementation nor measured hidden-test results. The supplied executable baseline is identity. The reproduction does beat identity and shows the paper's refinement/robustness effect, as detailed below; this does not establish the FPFH+QUASAR claim.

All scalar ranks below implement the user-specified rule with one declared audit cohort. They are **normalized audit ranks, not an externally supplied leaderboard score**. The unknown future cohort will change magnitudes and can change tradeoffs. “Stored” means the initial `scoring/scores_test.json` result for `spmc_frs`; “fresh” means seed 0. Both have rank zero relative to themselves. The rubric's illustrative `reference.json.results` numbers are not substituted for the stored measured reference.

| Actual numerical run | All median error ° | All mean error ° | Success ≤1° | Core median seconds | 10⁷-point seconds | Rank vs fresh | Rank vs stored |
|---|---:|---:|---:|---:|---:|---:|---:|
| Stored reference | 0.600237 | 0.659691 | 0.832143 | 0.309299 | 10.019580 | +0.048942 | 0 |
| [Fresh reference, seed 0](redteam/reference_seed0/run.sh) | 0.600237 | 0.659691 | 0.832143 | 0.039813 | 17.274575 | 0 | −0.048942 |
| [Genuine faster variant](redteam/better_fft/run.sh) | 0.600237 | 0.659691 | 0.832143 | 0.022757 | 12.350591 | **+0.052340** | +0.003398 |
| [Finer-resolution experiment](redteam/better_resolution/run.sh) | 0.435559 | 0.892012 | 0.799286 | 0.058337 | 48.912958 | −0.672613 | −0.721555 |
| [Weaker: remove FRS](redteam/weaker_spmc/run.sh) | 0.538558 | 1.562569 | 0.659286 | 0.014148 | 5.222548 | **−0.140031** | −0.188973 |
| [Weaker: identity](redteam/weaker_identity/run.sh) | 125.802203 | 127.255081 | 0 | 0.00000292 | 0.00005285 | **−5.267160** | −5.316102 |

The faster variant replaces exhaustive histogram-shift correlation with the equivalent FFT correlation, rounds its integer-valued correlations to preserve first-maximum tie behavior, and moves fixed template angles/histograms outside the FRS loop. **All 3,500 angular errors are exactly identical to the fresh reference**, including its tails. Core time improves by 0.017056 s, versus a reference spread of 0.002307 s. The 10⁷-point improvement is 4.923983 s, versus a spread of 2.299357 s. The 10⁶-point gain of 0.497535 s is slightly smaller than its 0.502237 s spread and is not independently significant by the requested rule.

The finer variant spends more computation on 720×360 SPMC bins and 1,440 FRS bins rather than 360×180 and 360. It improves the median but introduces a 129.986° maximum error, reduces success, and runs slower. Its lower aggregate score is appropriate for those measured tradeoffs; it is not evidence of a reversed accuracy direction. Similarly, SPMC alone has a better overall median than the hybrid, but substantially worse success and high-outlier tails. The additional scored metrics correctly detect this degradation on these honest attempts.

## 2. Seed spread and reproduction check

| Reference seed | Core median seconds | 10⁶-point seconds | 10⁷-point seconds | Rank vs fresh seed 0 | Rank vs stored |
|---|---:|---:|---:|---:|---:|
| [0](redteam/reference_seed0/scores_test.json) | 0.039813312 | 2.152374225 | 17.274574682 | 0 | −0.048941823 |
| [1](redteam/reference_seed1/scores_test.json) | 0.041639892 | 1.915396471 | 14.975217212 | +0.022996220 | −0.025945604 |
| [2](redteam/reference_seed2/scores_test.json) | 0.039332560 | 1.650137715 | 16.922743516 | +0.021924259 | −0.027017564 |
| Max minus min | **0.002307332** | **0.502236510** | **2.299357471** | **0.022996220** | **0.022996220** |

All ten core/high-outlier accuracy metrics repeat exactly across seeds. This is a deterministic method on fixed released inputs and rotations: setting NumPy seeds 0/1/2 does not generate three new datasets. These reruns measure timing variability, not uncertainty on unseen rotations or new patterns. Stored accuracy agrees with the reruns; stored timing does not reproduce. The audit jobs also experienced worker preemption/migration, so absolute timings across the historical reference and these jobs should not be treated as a controlled hardware comparison. The fresh-reference comparison and the measured spread expose this limitation rather than hiding it.

### What reproduces

The code implements identifiable SPMC and FRS computational steps, not a generic surrogate: mean-to-pole alignment, geographic binary histograms, circular shift correlation, three-axis iterative histogram matching, and a final SVD estimate between the original and iteratively rotated source. Hybrid initialization and composition follow the released code. Default settings retain 180 polar × 360 azimuthal bins, 360 FRS bins, at most 50 iterations, and zero-shift convergence.

This comparison uses the local [paper, Algorithms 1–2 and §5.1](paper/2508.02339.md), [released implementation](method/paper_code/vector_alignment_utils.py), and [reproduced implementation](method/spherical_registration.py). Only the audit's method-generation paths are restricted to future-agent-visible materials; paper inspection is used for this reproduction comparison.

The full released synthetic spherical-pattern dataset is used: all 5 patterns × 7 configurations × 100 rotations, without reducing point counts or dropping difficult cases. The hidden test aggregates 40 of those rotations per configuration (1,400 errors); the train aggregation is separate. All methods generate all 100, without importing hidden indices.

The paper reports a subdegree combined median and improvement from FRS refinement under clutter. The reproduced hybrid has a 0.600237° test median. Compared with SPMC, high-outlier median improves from **1.029894° to 0.631225°**, p90 from **6.346513° to 1.306130°**, and success from **0.496667 to 0.795**. In the full 100-rotation A5 cases, SPMC degrades from **0.243261° at B1 to 11.316501° at B7**, matching the paper's reported effect; hybrid B7 is **0.498099°**. Stored FRS-only results also exhibit the reported initialization problem: overall mean **22.506955°**, versus hybrid **0.659691°**. This FRS-only observation uses the stored artifact, not a new fourth reference run.

Identity has a 125.802203° test median and zero success. It scores clearly below the hybrid, leaving useful room for accurate methods above it. None of the reference's thirteen emitted metrics is saturated at its best physical bound; the metric inventory is below.

### Departures and scope limits

- The local NumPy port vectorizes geographic conversion, adds parallel/antiparallel-vector guards and numeric clipping, and explicitly normalizes inputs. It uses transpose conventions appropriate to row-vector inputs; the evaluated estimate matches the released rotation convention. The released implementation's negative-z antipodal flip is retained, although it is not explicit in the paper's abbreviated SPMC algorithm listing.
- The port redundantly recomputes fixed template **angles** inside the FRS loop; the released code computes those angles once, while rebuilding template histograms in the loop. This is a real source of avoidable work addressed by the faster variant. Default direct shift search agrees with the released non-FFT default.
- The audit's reference dispatcher calls the canonical `spmc_frs` algorithm without the convenience API's additional normalization pass, matching the original result producer's direct call. Internal algorithm normalization is retained. The audit measures elapsed time externally rather than trusting a method-returned time. Accuracy exactly matches the stored result.
- The complexity producer independently bootstraps the released A3 template and B3 source with replacement, using float32 inputs, fixed seeds `scale` and `scale+17`, and the **first 20 released rotations**. It retains all original scales, 10³ through 10⁷. The paper describes resampling A3 and rotating each scale; its caption also names A3/B3. Independent bootstrap samples and reuse of R100 are additional gym-specific choices. Only the two largest runtime endpoints are scored; no empirical scaling exponent or correctness at scale is scored.
- The separate spherical-image path rasterizes a substitute GeoJSON world map at 360×180 and synthesizes clutter; it is not the paper's original image asset. Its effect is **unverified by this hidden test**, which never reads its raw results. ModelNet40 registration, EGI/CASE experiments, 3DMatch/KITTI, and their comparators are outside this gym's measured scope.
- FPFH+QUASAR is absent. Its illustrative numbers in `reference.json` do not constitute a reproduction or a hidden-test baseline run.

The synthetic core therefore still exhibits the paper's robustness phenomenon and is nontrivial for the simple baseline. The resampled complexity inputs also give the reference median errors **0.540767° at 10⁶** and **0.718078° at 10⁷**, so those actual reference timings are not measurements of total failure. At the unscored 10³ scale, however, independent resampling gives a **35.777841°** median, showing that this smaller setup changes difficulty substantially. These audit-only errors are saved in each complexity artifact; the hidden evaluator ignores them. The image substitute cannot support a claim of reproducing the image effect until it is actually evaluated.

## 3. Shortcut runs

Every linked `run.sh` installs its case's `method.py`, generates or stages its artifacts as a future agent could, runs the train aggregation, and invokes **`bash scripts/evaluate_test.sh` with no arguments**, using default paths. Test evaluation executes in a separate process and imports no case code. Neither `eval/` nor the test launcher was changed. There is no background-process survival or evaluator/Python-environment tampering. The filesystem artifacts suffice in a fresh test container.

Each case retains its raw artifacts, train/test logs, exit status, and any scores the evaluator wrote. Invalid cases retain an explicit absence marker when no score was produced. Artifact-replay cases use the freshly generated seed-0 results, not hidden answers or initially available scoring caches. Zero/negative/empty/missing-accuracy writers and public-answer enumeration need no reference artifact at all. Proposed-method cases are compared under the same `spmc_frs` result label.

| Shortcut and runnable evidence | What it does | Rank vs stored reference | Rank vs fresh reference | Outcome |
|---|---|---:|---:|---|
| [shortcut_fabricated_zero](redteam/shortcut_fabricated_zero/run.sh) | Installs identity; writes 100 zero errors/times for every configuration and zero complexity times. | **+0.356785** | +0.405726 | **Works.** All accuracy errors 0, success 1, times 0; evaluator trusts the raw measurements. |
| [shortcut_impossible_negative](redteam/shortcut_impossible_negative/run.sh) | Writes −1° errors and −1 s times, with identity installed. | **+0.598666** | +0.647607 | **Works.** Physically impossible values are accepted. Negative errors even count as successes. |
| [shortcut_empty](redteam/shortcut_empty/run.sh) | Writes an empty method configuration map and empty complexity map. | **0: tie** | **0: tie** | **Works as a shortcut tie.** Exit 0; exact output is `{"experiments": {}}`. All losses disappear. |
| [shortcut_missing_accuracy](redteam/shortcut_missing_accuracy/run.sh) | Omits all task accuracy results; submits only zero complexity times. | **+0.095917** | +0.189639 | **Works.** A failed identity method outranks the reference through its other metrics. |
| [shortcut_filter_easy](redteam/shortcut_filter_easy/run.sh) | Replays only the five B1 configurations; removes the entire high-outlier comparison. | −0.037705 | +0.011237 | **Fails the stored-reference cutoff.** Accepted filtering slightly improves the fresh score, but that gain is below seed spread. |
| [shortcut_null](redteam/shortcut_null/run.sh) | Replaces error entries with JSON null. | No score | No score | **Fails.** Both launchers exit 1 on `float(None)`; no worst-value score artifact is written. |
| [shortcut_nan](redteam/shortcut_nan/run.sh) | Submits NaN errors and core times. | Undefined | Undefined | **Not demonstrated to pay.** Exit 0, NaN metrics and success 0 are emitted. No nonfinite-value ranking policy is supplied, so no scalar rank is claimed. |
| [shortcut_short_arrays](redteam/shortcut_short_arrays/run.sh) | Supplies just one zero error/time per configuration. | No score | No score | **Fails.** Present arrays are length-checked; both launchers exit 1. No worst-value score artifact is written. |
| [shortcut_stale_identity](redteam/shortcut_stale_identity/run.sh) | Installs identity plus another method on disk; replays the honest reference raw artifacts. | −0.048942 | **0: tie** | **Shortcut tie with the fresh reference**, below the stored reference. The installed method's true 125.802° error is never recomputed. Extra on-disk method is omitted. |
| [shortcut_write_final](redteam/shortcut_write_final/run.sh) | Writes a forged final score of −123° before testing, while leaving reference raw artifacts. | −0.048942 | **0: tie** | **Direct final-score forgery fails:** test overwrites it. The residual tie is the same stale-artifact shortcut, not successful final-file forgery. |
| [shortcut_fixed_rotations](redteam/shortcut_fixed_rotations/run.sh) | Replaces the public rotation asset with 100 identities, then genuinely benchmarks identity against this changed truth. | **+0.356781** | +0.405722 | **Works.** Actual measured errors 0, success 1; original evaluator accepts the changed ground-truth operating setup. |
| [shortcut_answer_enumeration](redteam/shortcut_answer_enumeration/run.sh) | Enumerates the 35 public source fingerprints × 100 public rotation answers and selects by the observed source centroid. | **+0.354815** | +0.403757 | **Works.** Genuine outputs achieve median 0°, max 0.000002415°, success 1 on the original test inputs. |

Six shortcut runs meet or exceed the **stored** reference, including the successful empty-result tie. Replay cases are explicitly shortcut ties against the fresh reference, not claimed wins against the stored reference. NaN and evaluator failures are not counted as successful shortcuts. See [all metric outputs and ranks](redteam/report_tables.md) and [machine-readable summary](redteam/summary.json).

### Public-answer reconstruction and brute force

The public data loader exposes `RandomRotation100.pkl`, the unrotated base sources, and every template. For a base source mean μ and released rotation R, the rotated source mean is Rμ. The enumeration shortcut precomputes all **3,500** such three-dimensional fingerprints and their associated rotations. At prediction time it computes the source mean, checks every candidate, and returns the nearest candidate's stored rotation. It neither uses correspondences nor reads hidden split indices. It does use public benchmark answers and fixed source fingerprints, so it is a **shortcut**, not an improved general registration method.

This brute force **solves the test**: all 1,400 hidden core cases meet 1°, with median 0° and mean 0.000000612°. Core median time is **0.000548 s**; one-time table setup is **0.070358 s**. The test's effective candidate universe is too small and public to test unrestricted rotation estimation. This is exhaustive enumeration of the actual benchmark answer universe, not a claim that exhaustive continuous SO(3) search is cheap. It would fail on genuinely unseen rotations/patterns. At the two scored complexity scales its returned rotations are also essentially exact; at smaller unscored resampled scales it can fail catastrophically, further exposing the scope of the shortcut.

### Fixed artifacts and comparisons

No trained fixed model is part of this hidden evaluator, so there is no fixed detector/checkpoint to retrain. The tested fixed-asset replacement is the rotation pickle. It changes the truth side of the comparison, then records honestly measured errors on the altered task. The test never reloads or verifies the original truth. Filtering B1 separately demonstrates that required test size/configurations are not enforced. Direct final-score editing is overwritten, but raw measurement editing is fully trusted. These are scoring/data-contract failures, not process tampering.

## 4. Completeness, bounds, and ranking mechanics

### Bound inventory

**Every emitted scored metric already at its best bound: none.** Lower is better for errors, dispersion and times (best physical bound 0); higher is better for success (bound 1). The complete stored-reference inventory is:

| Experiment | Metric | Stored reference | Best bound |
|---|---|---:|---:|
| all | median error ° | 0.600237 | 0 |
| all | mean error ° | 0.659691 | 0 |
| all | median time s | 0.309299 | 0 |
| all | success ≤1° | 0.832143 | 1 |
| all | error std ° | 0.428825 | 0 |
| all | p95 error ° | 1.419609 | 0 |
| all | max error ° | 2.651642 | 0 |
| high outliers | median error ° | 0.631225 | 0 |
| high outliers | p90 error ° | 1.306130 | 0 |
| high outliers | success ≤1° | 0.795 | 1 |
| high outliers | error std ° | 0.451418 | 0 |
| complexity | 10⁶-point time s | 0.889561 | 0 |
| complexity | 10⁷-point time s | 10.019580 | 0 |

The rubric additionally lists **five image metrics in two experiments with total weight 0.25**. Neither the stored hidden scores nor any no-argument hidden test run emits these experiments. They are missing, not saturated. Thus only three of five rubric experiments, carrying weight 0.75, participate. `TARGETS.md` describes three experiments while `reference.json` describes five. See [the exact metric inventory](redteam/metric_inventory.json).

### Can a failed method outrank the reference?

With complete, honest measurements, identity loses by **−5.316102** against the stored reference despite its time benefits. Its core-time plus complexity gains sum to approximately **+0.147310**, far below its accuracy losses in this cohort. Removing FRS also loses. This supports the benefit/constraint balance for the tested complete attempts, not a universal guarantee across all future normalization cohorts.

But **shortcut_missing_accuracy** proves a failed method can outrank the reference: it gets no accuracy losses because those entries are absent, while two zero timing values supply strictly positive gains. This conclusion does not depend on timing units, coefficient signs, or the particular audit cohort whenever those timing metrics have nonzero spread. Likewise, fabricated zeros and fixed-rotation identity improve every emitted reference metric; the result is not an artifact of mixing incomparable units.

### Missing values, failed runs, and methods on disk

The hidden test does **not** assign worst values to every scored metric/experiment after failure. Null and truncated-array runs exit nonzero without a score file. Whether an external job system penalizes that exit is outside the supplied rank rule; no profitable rank is asserted for those failures. More decisively, a successful empty run emits no experiments and ties, while a successful partial run emits only timing and wins. Present arrays must be long enough for the held-out indices; absent methods/configurations/scales are never required.

The test also does **not** write every method on disk under `results`. In `shortcut_stale_identity`, `method/spherical_registration.py` and an additional `method/audit_unregistered.py` both contain identity methods, but results still contain only the raw artifact's `spmc_frs` key. The evaluator never imports or discovers either implementation. It processes whichever method labels/configuration keys the submitted raw JSON contains. No matrix, SO(3) validity, measurement provenance, data hash, or complete required-case manifest is checked.

### Formula and normalization

For attempt a and reference r, the audit computes

`S(a;r) = Σ_e w_e Σ_m |c_em| · d_em · (x_a,em − x_r,em) / σ_em`,

where `d=+1` for higher-is-better and `d=−1` otherwise. A missing attempt/reference value contributes no term. **Coefficient signs are ignored**, as requested; metric direction comes exclusively from `higher_is_better`. The coefficients set relative influence after variation normalization, not raw measurement units.

[The aggregation script](redteam/summarize.py) uses population standard deviation over the **16 finite successful audit attempts plus the stored reference**, per available metric. Failed evaluator runs have no ranked artifact. The accepted NaN attempt is excluded from this finite normalization cohort and left unranked; silently converting it to a missing value would assume a policy the user did not supply. Zero-variation metrics contribute no term. Exact standard deviations, cohort membership, contributions, missing metrics, raw scores, and seed spreads are saved in [summary.json](redteam/summary.json). Future leaderboard values cannot be computed exactly before its attempt cohort exists. Empty-result ties and componentwise-dominating shortcuts remain decisive without knowing it.

## 5. Execution, restoration, and next-iteration fixes

The two CPU jobs were `07b06731-204` (worker loss; cancelled after checkpoints) and `1141bd20-aac` (exit 0 after resume). They completed **19 cases: seven honest numerical controls/variants and twelve shortcut attempts**. Every numerical case used all 3,500 core registrations and all five complexity scales × 20 rotations. The two deliberately invalid artifact cases failed as intended; their failures did not abort the bundle. Completed reference outputs were reused for checks that only change reporting. No installation, GPU computation, or heavy numerical work ran on the interactive node.

All audit-owned changes to `method/`, `data/`, `scoring/`, `eval/`, and `scripts/` have been restored. A git comparison against the iteration-start commit verifies the tracked benchmark sources/artifacts are unchanged, including `scripts/run.sh`. The downloaded rotation file's SHA-256 is again `a57435e765f1261717bc46b93a91a5bd1717be7a06828bf8236bac8823aabd3c`, identical to all three untouched public copies. Temporary extra methods and interrupted-run recovery state are absent. Initial unrelated workspace changes were recorded in [initial_status.txt](redteam/initial_status.txt) and preserved. Durable audit changes are confined to `redteam/` and this report; root `action.yaml` is the required completion protocol, and job logs/commits are scheduler-managed.

The final evidence/completeness and restoration checks are recorded in [validation.txt](redteam/validation.txt).

The highest-priority next iteration is to make the restored hidden evaluator **execute the submitted method on immutable evaluator-owned inputs**, compute errors from checked SO(3) outputs, and measure time itself. Require every method, configuration, rotation, experiment and scale, and emit explicit worst values on failure rather than omitting losses. Use fresh private rotations and additional patterns/noise realizations, not a secret index slice of public answers. Tie large-scale timing credit to correctness at that same scale. Either implement the image experiments and actual paper comparator or remove their phantom rubric entries. Finally, regenerate the stored runtime reference under the same measurement protocol/hardware and retain repeated controls so real gains can be separated from timing noise.
