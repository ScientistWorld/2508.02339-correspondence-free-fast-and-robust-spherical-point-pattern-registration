# Scoring audit

All case `run.sh` scripts install their `method.py`, generate or stage visible raw
artifacts, call the untouched train launcher and then the untouched hidden test
launcher with **no arguments**, and save both score files plus exit status here.
Each launcher executes in a separate process; there is no background process or
Python environment manipulation. Temporary method/data/scoring changes are
restored in `finally`. The evaluator and its launcher are never modified.

Run the CPU bundle with `bash redteam/run_all.sh` inside the gym container.
The three reference seeds and genuine variants use all 5×7×100 input cases,
and the original 10³–10⁷ scaling protocol over 20 rotations. No hidden rotation
indices are used in generation. Audit normalization is computed afterwards in
`summarize.py`; it is not an input to any method or shortcut.

`reference_method.py` is a snapshot of the visible improve-mode implementation.
`ranking_reference.json` and `reference_scores_test.json` are audit-only snapshots
of the rubric and checked-in scores; no shortcut reads either. The raw-artifact
shortcuts reuse freshly generated `reference_seed0` outputs, which a future
improve-mode agent can produce itself, rather than depending on unavailable
checked-in raw scoring files. From-scratch shortcuts such as fabricated zeros,
missing accuracy, and public-answer enumeration do not require reference values.

Every shortcut is explicitly named `shortcut_*`. Known-invalid artifacts are
retained as evidence, not recommendations. Full results and limitations are in
`/home/user/REDTEAM.md`. `summarize.py` uses the specified coefficient/direction
rule and a declared finite audit cohort; the future ranking cohort is unknown.
The accepted NaN artifact is left unranked because no nonfinite-value ranking
policy is supplied. Completed `status.json` files are skipped by `run_all.sh`;
to repeat a case, use its `run.sh` directly. It regenerates scores from saved raw
checkpoints; remove that case's raw JSON files first to remeasure the method.
