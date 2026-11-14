#!/usr/bin/env python3
"""Hardening analysis: ranks, paired-bootstrap noise, determinism, train/test.

Rank of attempt a against the reference r (spmc_frs), as specified for this gym:
    S(a) = sum_e w_e sum_m |c_em| * d_em * (x_a,em - x_r,em) / sigma_em
d = +1 if higher_is_better else -1; sigma = population std of the metric over
the attempt cohort (two cohorts reported: valid attempts only, and all
attempts including failed runs, which carry worst values).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "notes" / "hardening" / "results"
REF = json.loads((ROOT / "scoring" / "reference.json").read_text())["experiments"]
REFERENCE = "spmc_frs"

SPEC = {  # experiment -> (group, subset)
    "robust_alignment_all": ("robust", None),
    "robust_alignment_high_outliers": ("robust", {"B5", "B6", "B7"}),
    "spherical_image_alignment_all": ("images", None),
    "spherical_image_alignment_high_clutter": ("images", {"Img5"}),
    "sparse_alignment": ("sparse", None),
}


def stat(metric: str, e: np.ndarray) -> float:
    if metric.startswith("median"):
        return float(np.median(e))
    if metric.startswith("mean"):
        return float(np.mean(e))
    if metric.startswith("p95"):
        return float(np.percentile(e, 95))
    if metric.startswith("p90"):
        return float(np.percentile(e, 90))
    if metric.startswith("max"):
        return float(np.max(e))
    if metric == "success_rate_1deg":
        return float(np.mean(e <= 1.0))
    if metric == "success_rate_5deg":
        return float(np.mean(e <= 5.0))
    raise ValueError(metric)


def load_scores(path: Path, tag: str, rows: dict, status: dict) -> None:
    if not path.is_file():
        return
    data = json.loads(path.read_text())
    for exp, block in data["experiments"].items():
        for method, values in block["results"].items():
            rows.setdefault(f"{tag}:{method}", {})[exp] = values
    for method, info in data.get("_diagnostics", {}).get("methods", {}).items():
        status[f"{tag}:{method}"] = info


def sigmas(rows: dict, keys: list) -> dict:
    out = {}
    for exp, spec in REF.items():
        for metric in spec["metrics"]:
            vals = [rows[k][exp][metric] for k in keys if exp in rows[k] and metric in rows[k][exp]]
            vals = [v for v in vals if np.isfinite(v)]
            sd = float(np.std(vals)) if len(vals) > 1 else 0.0
            out[(exp, metric)] = sd
    return out


def rank(values: dict, ref_values: dict, sig: dict) -> float:
    total = 0.0
    for exp, spec in REF.items():
        for metric, mdef in spec["metrics"].items():
            sd = sig.get((exp, metric), 0.0)
            if sd <= 0 or exp not in values or metric not in values[exp]:
                continue
            d = 1.0 if mdef["higher_is_better"] else -1.0
            total += spec["weight"] * abs(mdef["coefficient"]) * d * (values[exp][metric] - ref_values[exp][metric]) / sd
    return total


def metrics_from_instances(inst: dict, idx: dict | None = None) -> dict:
    out = {}
    for exp, (group, subset) in SPEC.items():
        labels = np.array(inst[group]["labels"])
        errors = np.array(inst[group]["errors"], dtype=float)
        if idx is not None:
            labels, errors = labels[idx[group]], errors[idx[group]]
        if subset is not None:
            errors = errors[np.isin(labels, list(subset))]
        out[exp] = {m: stat(m, errors) for m in REF[exp]["metrics"]}
    return out


def main() -> None:
    rows, status = {}, {}
    load_scores(ROOT / "scoring" / "scores_test.json", "reference", rows, status)
    for path in sorted(RES.glob("*_scores_test.json")):
        tag = path.name.replace("_scores_test.json", "")
        if tag == "reference_rerun":
            continue
        load_scores(path, tag, rows, status)
    ref_key = f"reference:{REFERENCE}"
    ref_vals = rows[ref_key]
    scenario = ("stale_artifacts:", "tamper_rotations:", "tamper_template:")
    cohort = [k for k in rows if not k.startswith(scenario)]  # scenario reruns would double-count
    valid = [k for k in cohort if status.get(k, {}).get("status", "ok") == "ok"]
    sig_valid = sigmas(rows, valid)
    sig_all = sigmas(rows, cohort)
    table = []
    for key in rows:
        table.append({
            "attempt": key,
            "status": status.get(key, {}).get("status", "ok"),
            "failure": status.get(key, {}).get("failure", "")[:160],
            "cpu_seconds": status.get(key, {}).get("cpu_seconds", {}),
            "rank_valid_cohort": rank(rows[key], ref_vals, sig_valid),
            "rank_all_cohort": rank(rows[key], ref_vals, sig_all),
            "metrics": rows[key],
        })
    table.sort(key=lambda r: -r["rank_valid_cohort"])

    # Paired bootstrap (identical instances for every method).
    boot = {}
    ref_inst_path = RES / "reference_test_instances.json"
    if ref_inst_path.is_file():
        ref_inst = json.loads(ref_inst_path.read_text())[REFERENCE]
        rng = np.random.default_rng(0)
        sizes = {g: len(ref_inst[g]["errors"]) for g in ref_inst}
        draws = [{g: rng.integers(0, n, n) for g, n in sizes.items()} for _ in range(1000)]
        ref_full = metrics_from_instances(ref_inst)
        self_noise = [rank(metrics_from_instances(ref_inst, d), ref_full, sig_valid) for d in draws]
        boot["reference_self_rank_95pct_halfwidth"] = float(np.percentile(np.abs(self_noise), 95))
        for path in sorted(RES.glob("*_test_instances.json")):
            data = json.loads(path.read_text())
            for method, inst in data.items():
                if path.name.startswith("reference") and method == REFERENCE:
                    continue
                if any(len(inst[g]["errors"]) != sizes[g] for g in sizes):
                    continue
                full = rank(metrics_from_instances(inst), ref_full, sig_valid)
                diffs = [rank(metrics_from_instances(inst, d), metrics_from_instances(ref_inst, d), sig_valid)
                         for d in draws]
                boot[f"{path.name.split('_test_instances')[0]}:{method}"] = {
                    "rank_vs_reference": full,
                    "paired_bootstrap_95ci": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))],
                }

    # Determinism of the stored reference.
    determinism = None
    rerun = RES / "reference_rerun_scores_test.json"
    if rerun.is_file():
        a = json.loads((ROOT / "scoring" / "scores_test.json").read_text())["experiments"]
        b = json.loads(rerun.read_text())["experiments"]
        determinism = a == b

    # Train vs test for the shipped methods.
    train_test = {}
    train_path = ROOT / "scoring" / "scores_train.json"
    if train_path.is_file():
        tr = json.loads(train_path.read_text())["experiments"]
        te = json.loads((ROOT / "scoring" / "scores_test.json").read_text())["experiments"]
        for exp in te:
            for method in te[exp]["results"]:
                primary = REF[exp]["primary_metric"]
                train_test.setdefault(method, {})[exp] = {
                    "train": tr.get(exp, {}).get("results", {}).get(method, {}).get(primary),
                    "test": te[exp]["results"][method][primary],
                }
    for path in sorted(RES.glob("*_scores_train.json")):
        tag = path.name.replace("_scores_train.json", "")
        tr = json.loads(path.read_text())["experiments"]
        te_path = RES / f"{tag}_scores_test.json"
        if not te_path.is_file():
            continue
        te = json.loads(te_path.read_text())["experiments"]
        for exp in te:
            for method in te[exp]["results"]:
                primary = REF[exp]["primary_metric"]
                train_test.setdefault(f"{tag}:{method}", {})[exp] = {
                    "train": tr.get(exp, {}).get("results", {}).get(method, {}).get(primary),
                    "test": te[exp]["results"][method][primary],
                }

    marker = RES / "read_hidden_marker.txt"
    summary = {
        "reference": REFERENCE,
        "sigma_valid_cohort": {f"{e}.{m}": s for (e, m), s in sig_valid.items()},
        "table": table,
        "paired_bootstrap": boot,
        "reference_rerun_identical": determinism,
        "train_vs_test_primary": train_test,
        "read_hidden_marker": marker.read_text() if marker.is_file() else None,
    }
    (RES / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    lines = ["| attempt | status | robust med | robust succ1 | robust p95 | high med | img med | sparse med | sparse succ5 | rank (valid σ) | rank (all σ) |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in table:
        m = r["metrics"]
        lines.append("| {} | {} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:+.3f} | {:+.3f} |".format(
            r["attempt"], r["status"],
            m["robust_alignment_all"]["median_rotation_error_deg"], m["robust_alignment_all"]["success_rate_1deg"],
            m["robust_alignment_all"]["p95_rotation_error_deg"], m["robust_alignment_high_outliers"]["median_rotation_error_deg"],
            m["spherical_image_alignment_all"]["median_rotation_error_deg"], m["sparse_alignment"]["median_rotation_error_deg"],
            m["sparse_alignment"]["success_rate_5deg"], r["rank_valid_cohort"], r["rank_all_cohort"]))
    lines.append("")
    lines.append(f"Reference rerun identical: {determinism}")
    lines.append(f"Paired bootstrap: {json.dumps(boot, indent=1)}")
    (RES / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
