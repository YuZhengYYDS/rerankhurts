"""Prespecified paired-world analyses; exploratory families are labeled explicitly.

Worlds, not tasks or configurations, are independent sampling units. Sign-flip
tests assume sign exchangeability of world differences under the null; they are
not a claim that deployment policies were randomly assigned. A degenerate zero
bootstrap interval does not establish population equivalence.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .evaluate import DEFAULT_OUTPUT, ROOT, dump_json, read_json, sha256, write_csv

CONFIG_FIELDS = ("retriever", "pool", "reranker", "cap", "cap_stage", "refill", "budget", "packing",
                 "score_view", "dense_view", "policy_stage", "mmr_lambda")
ENDPOINTS = ("U_sim", "G_final", "fact_coverage", "admissible_U_sim", "C_sim", "nonempty",
             "joint_compliant_U_sim", "contradiction_exposure", "obsolete_exposure", "context_tokens", "rerank_pairs")


def holm_adjust(pvalues):
    values = np.asarray(pvalues, dtype=float)
    order = np.argsort(values, kind="stable")
    result, previous = np.empty(len(values)), 0.0
    for i, index in enumerate(order):
        previous = max(previous, min(1.0, (len(values) - i) * values[index]))
        result[index] = previous
    return result.tolist()


def bh_adjust(pvalues):
    values = np.asarray(pvalues, dtype=float)
    order = np.argsort(values, kind="stable")
    result, previous = np.empty(len(values)), 1.0
    for rank in range(len(values), 0, -1):
        index = order[rank - 1]
        previous = min(previous, values[index] * len(values) / rank)
        result[index] = min(1.0, previous)
    return result.tolist()


def paired_world_values(frame, left, right, endpoint="U_sim"):
    """Left minus right, paired by qid before averaging within each world."""
    keys = ["qid", "group_id", "seed"]
    a = frame.loc[frame.config_id == left, keys + [endpoint]].rename(columns={endpoint: "left"})
    b = frame.loc[frame.config_id == right, keys + [endpoint]].rename(columns={endpoint: "right"})
    if a.duplicated(keys).any() or b.duplicated(keys).any():
        raise ValueError("Duplicate task/configuration records")
    paired = a.merge(b, on=keys, how="outer", validate="one_to_one", indicator=True)
    if paired.empty or not paired._merge.eq("both").all():
        raise ValueError("Comparison has missing or unpaired tasks")
    if paired.groupby("group_id").seed.nunique().max() != 1:
        raise ValueError("One latent world appears under multiple generation seeds")
    paired["difference"] = paired.left.astype(float) - paired.right.astype(float)
    worlds = paired.groupby(["group_id", "seed"], sort=True).agg(
        difference=("difference", "mean"), left=("left", "mean"), right=("right", "mean"),
        n_tasks=("qid", "size")).reset_index()
    return worlds, paired


def world_statistics(worlds, repeats=5000, permutation_repeats=20000, seed=20261002):
    """Equal-world estimate and seed-stratified paired bootstrap interval."""
    if worlds.empty or worlds.group_id.duplicated().any():
        raise ValueError("Statistics require one row per independent world")
    values = worlds.difference.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite world differences")
    rng = np.random.default_rng(seed)
    estimate = float(values.mean())
    samples = np.zeros(repeats)
    for _, group in worlds.groupby("seed", sort=True):
        block = group.difference.to_numpy(dtype=float)
        samples += block[rng.integers(0, len(block), size=(repeats, len(block)))].sum(axis=1)
    samples /= len(worlds)
    lo, hi = np.quantile(samples, [.025, .975])
    # Flip each whole-world contrast, preserving all its paired variants.
    extreme = 0
    for start in range(0, permutation_repeats, 1000):
        count = min(1000, permutation_repeats - start)
        signs = rng.integers(0, 2, size=(count, len(values)), dtype=np.int8) * 2 - 1
        simulated = signs @ values / len(values)
        extreme += int(np.sum(np.abs(simulated) >= abs(estimate) - 1e-12))
    pvalue = (extreme + 1) / (permutation_repeats + 1)
    zero = bool(np.all(values == 0))
    return {"n_worlds": len(worlds), "difference": estimate, "ci95_low": float(lo), "ci95_high": float(hi),
            "p_sign_flip": pvalue, "positive_worlds": int(np.sum(values > 0)),
            "negative_worlds": int(np.sum(values < 0)), "zero_worlds": int(np.sum(values == 0)),
            "all_world_differences_zero": zero, "empirical_interval_degenerate": bool(lo == hi),
            "interval_interpretation": "Empirical zero/degenerate variation; not proof of equivalence" if lo == hi
                                       else "Seed-stratified paired-world percentile bootstrap 95%",
            "p_assumption": "World-difference sign exchangeability under the null; not randomized policy assignment"}


def canonical(value):
    if pd.isna(value):
        return None
    if isinstance(value, np.generic):
        return value.item()
    return value


def config_records(frame):
    records = frame[["config_id", *CONFIG_FIELDS]].drop_duplicates()
    if records.config_id.duplicated().any():
        raise ValueError("Configuration ID maps to inconsistent settings")
    return [{key: canonical(value) for key, value in row.items()} for row in records.to_dict("records")]


def find_config(configs, **settings):
    candidates = [record for record in configs if all(record.get(key) == value for key, value in settings.items())]
    if len(candidates) != 1:
        raise ValueError(f"Expected one configuration for {settings}, found {len(candidates)}")
    return candidates[0]["config_id"]


def contrast(frame, configs, left, right, name, family, repeats, permutation_repeats, seed,
             endpoint="U_sim", subgroup="all_test", primary=False):
    worlds, pairs = paired_world_values(frame, left, right, endpoint)
    result = {"name": name, "family": family, "analysis": "prespecified_primary" if primary else "exploratory",
              "subgroup": subgroup, "endpoint": endpoint, "left_config": left, "right_config": right,
              "n_task_pairs": len(pairs), "left_world_mean": float(worlds.left.mean()),
              "right_world_mean": float(worlds.right.mean()),
              **world_statistics(worlds, repeats, permutation_repeats, seed)}
    return result


def variant_interaction(frame, left, right, name, repeats, permutation_repeats, seed):
    """Within-world high-minus-low change of the post-minus-pre contrast."""
    _, pairs = paired_world_values(frame, left, right)
    labels = frame[["qid", "variant_id"]].drop_duplicates()
    pairs = pairs.merge(labels, on="qid", validate="one_to_one")
    wide = pairs.pivot(index=["group_id", "seed"], columns="variant_id", values="difference")
    expected = {"low_concentration", "high_concentration"}
    if set(wide) != expected or wide.isna().any().any():
        raise ValueError("Variant interaction requires both paired interventions for every world")
    worlds = (wide.high_concentration - wide.low_concentration).rename("difference").reset_index()
    return {"name": name + "_concentration_interaction", "family": "concentration_interaction", "analysis": "exploratory",
            "subgroup": "all_test", "endpoint": "U_sim", "left_config": left, "right_config": right,
            "definition": "(post-pre in high concentration) minus (post-pre in low concentration), same latent world",
            **world_statistics(worlds, repeats, permutation_repeats, seed)}


def exploratory_pairs(configs):
    """One-factor matched comparisons, frozen by configuration geometry, not outcomes."""
    pairs = []
    ordering = {"cap_stage": {"off": 0, "pre": 1, "post": 2}, "packing": {"prefix": 0, "whole": 1, "window": 2},
                "reranker": {"none": 0, "m3": 1, "minilm": 2}, "retriever": {"dense": 0, "bm25": 1, "fusion": 2},
                "score_view": {"prefix128": 0, "prefix512": 1, "window512": 2},
                "dense_view": {"prefix128": 0, "prefix512": 1, "window512": 2},
                "policy_stage": {"none": 0, "pre_retrieve": 1, "post_retrieve": 2, "post_rerank": 3}}
    fields = set(CONFIG_FIELDS) - {"budget"}
    for a, b in itertools.combinations(configs, 2):
        differences = [field for field in CONFIG_FIELDS if a[field] != b[field]]
        if set(differences) == {"cap", "cap_stage"} and (a["cap"] == 0 or b["cap"] == 0) and a["budget"] in (512, 2048):
            off, active = (a, b) if a["cap"] == 0 else (b, a)
            pairs.append((active["config_id"], off["config_id"], "cap_application"))
            continue
        if len(differences) != 1 or differences[0] not in fields or a["budget"] not in (512, 2048):
            continue
        field = differences[0]
        # Every included pair differs on precisely one intervention dimension.
        key = lambda row: ordering.get(field, {}).get(row[field], str(row[field]))
        first, second = sorted((a, b), key=key)
        pairs.append((second["config_id"], first["config_id"], field))
    return pairs


def summarize(frame):
    # Average variants within a world first, then assign each world equal weight.
    columns = [column for column in ENDPOINTS if column in frame]
    worlds = frame.groupby(["split", "config_id", "group_id"], dropna=False)[columns].mean().reset_index()
    summary = worlds.groupby(["split", "config_id"])[columns].mean().reset_index()
    sizes = worlds.groupby(["split", "config_id"]).size().rename("n_worlds").reset_index()
    return summary.merge(sizes, on=["split", "config_id"])


def legacy_null_audit(path):
    """Recompute the old pilot's exact pre/post equality without editing it."""
    if not Path(path).exists():
        return {"status": "unavailable", "path": str(path)}
    old = pd.read_csv(path)
    output = []
    for pool, budget in itertools.product((16, 64), (512, 2048)):
        subset = old[(old.pool == pool) & (old.budget == budget) & (old.reranker == "m3")]
        a = subset[subset.cap == "pre"].set_index("qid")
        b = subset[subset.cap == "post"].set_index("qid").reindex(a.index)
        if b.U_sim.isna().any():
            raise ValueError("Legacy audit cannot pair pre/post tasks")
        result = {"pool": pool, "budget": budget, "task_pairs": len(a), "worlds": a.group_id.nunique(),
                  "pre_U_sum": int(a.U_sim.sum()), "post_U_sum": int(b.U_sim.sum())}
        for endpoint in ("U_sim", "G_final", "fact_coverage", "admissible_U_sim", "contradiction_exposure", "obsolete_exposure"):
            result[endpoint + "_changed_pairs"] = int((a[endpoint] != b[endpoint]).sum())
        for stage in ("raw", "pre_cap", "rerank", "post_cap", "final"):
            result["pre_" + stage + "_U_sum"] = int(a[stage + "_U_sim"].sum())
            result["post_" + stage + "_U_sum"] = int(b[stage + "_U_sim"].sum())
        output.append(result)
    return {"status": "recomputed", "input_sha256": sha256(path), "comparisons": output,
            "interpretation": "The 480 paired setting records contain 120 tasks from 60 worlds; they are not 480 independent observations."}


def plot_results(primary, summary, output):
    # Optional: caller performs its PDF-operation approval marker before --plots.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.8, 2.8), constrained_layout=True)
    for i, row in enumerate(primary):
        ax.errorbar(row["difference"], i, xerr=[[row["difference"] - row["ci95_low"]],
                                                 [row["ci95_high"] - row["difference"]]],
                    fmt="o", color="#205b83", capsize=4)
    ax.axvline(0, color="0.55", linewidth=1)
    ax.set(yticks=range(len(primary)), yticklabels=[row["name"] for row in primary],
           xlabel="Post-cap minus pre-cap full fact coverage (paired world mean)")
    ax.spines[["top", "right"]].set_visible(False)
    for extension in ("png", "pdf"):
        fig.savefig(output / f"primary_cap_order.{extension}", dpi=220)
    plt.close(fig)


def auxiliary_analyses(output, repeats=5000, permutation_repeats=20000, seed=20261002, answers=None, timing=None):
    """Analyze separate actual answer and online-request runs only if complete."""
    result = {}
    answers, timing = Path(answers or output / "answers"), Path(timing or output / "timing")
    if (answers / "status.json").exists():
        status = read_json(answers / "status.json")
        if status.get("status") != "complete":
            result["answers"] = {"status": "incomplete_not_analyzed"}
        else:
            frame = pd.read_csv(answers / "per_answer.csv").rename(columns={"condition": "config_id"})
            comparisons = [("m3_post_prefix", "m3_pre_prefix", "post_minus_pre"),
                           ("m3_post_window", "m3_post_prefix", "window_minus_prefix")]
            rows = []
            for left, right, name in comparisons:
                for endpoint in ("complete_correct", "complete_grounded_correct", "field_accuracy", "grounded_field_accuracy"):
                    rows.append(contrast(frame, [], left, right, name, "answer_quality", repeats,
                                         permutation_repeats, seed, endpoint))
            for row, qvalue in zip(rows, bh_adjust([row["p_sign_flip"] for row in rows])):
                row["q_bh_within_family"] = qvalue
                row["family_size"] = len(rows)
            write_csv(output / "answer_contrasts.csv", rows)
            endpoints = ["complete_correct", "complete_grounded_correct", "field_accuracy", "grounded_field_accuracy",
                         "schema_valid", "unsupported_fields", "unsupported_abstentions", "unsupported_answers",
                         "prompt_tokens", "generated_tokens"]
            means = frame.groupby(["config_id", "group_id"])[endpoints].mean().groupby("config_id").mean()
            means.to_csv(output / "answer_world_summary.csv")
            result["answers"] = {"status": "complete", "worlds": frame.group_id.nunique(), "comparisons": len(rows),
                                 "per_answer_sha256": sha256(answers / "per_answer.csv"),
                                 "interpretation": "Recorded model answers evaluated against exact fictional truth and source grounding as separate endpoints."}
    if (timing / "status.json").exists():
        status = read_json(timing / "status.json")
        if status.get("status") != "complete":
            result["timing"] = {"status": "incomplete_not_analyzed"}
        else:
            records = [json.loads(line) for line in (timing / "requests.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
            frame = pd.DataFrame(records)
            steady = frame[frame.phase == "steady"].copy()
            # Reduce repeated requests within each world and condition before
            # treating worlds as independent. Request quantiles remain descriptive.
            worlds = steady.groupby(["group_id", "seed", "condition"]).latency_ms.mean().reset_index()
            worlds["qid"] = worlds.group_id
            worlds = worlds.rename(columns={"condition": "config_id"})
            rows = []
            for left, right, name in (("m3_post_prefix", "m3_pre_prefix", "post_minus_pre_latency"),
                                      ("m3_post_window", "m3_post_prefix", "window_minus_prefix_latency")):
                rows.append(contrast(worlds, [], left, right, name, "online_latency", repeats,
                                     permutation_repeats, seed, "latency_ms"))
            for row, qvalue in zip(rows, bh_adjust([row["p_sign_flip"] for row in rows])):
                row["q_bh_within_family"] = qvalue
            write_csv(output / "timing_world_contrasts.csv", rows)
            result["timing"] = {"status": "complete", "worlds": steady.group_id.nunique(),
                                "requests": len(steady), "requests_sha256": sha256(timing / "requests.jsonl"),
                                "interpretation": "Request p50/p95 are descriptive actual-request quantiles; world CIs use per-world repeated-request means. Repetitions are not independent worlds."}
    return result


def analyze(output, plan_path, plots=False, exploratory=True, answers=None, timing=None):
    output, plan_path = Path(output), Path(plan_path)
    status, plan = read_json(output / "status.json"), read_json(plan_path)
    if status.get("status") != "complete":
        raise ValueError("Confirmatory analysis requires a complete independently evaluated run")
    if status.get("study_plan_sha256") and status["study_plan_sha256"] != sha256(plan_path):
        raise ValueError("Study plan differs from the plan frozen before model inference")
    frame = pd.read_csv(output / "per_record.csv")
    if frame.duplicated(["qid", "config_id"]).any():
        raise ValueError("Duplicate task/configuration rows")
    configs = config_records(frame)
    test = frame[frame.split == "test"].copy()
    stats = plan["statistics"]
    repeats, seed = stats.get("bootstrap_repetitions", 5000), stats.get("bootstrap_seed", 20261002)
    permutation_repeats = stats.get("permutation_repetitions", 20000)
    primary = []
    for specification in plan["primary_comparisons"]:
        settings = {key: specification[key] for key in CONFIG_FIELDS if key in specification}
        settings.update(refill=False, mmr_lambda=None, dense_view=specification.get("dense_view", "prefix512"))
        left, right = (find_config(configs, **settings, cap_stage=stage) for stage in ("post", "pre"))
        primary.append(contrast(test, configs, left, right, specification["name"], "primary_cap_order", repeats,
                                permutation_repeats, seed, endpoint=specification["endpoint"], primary=True))
    for row, adjusted in zip(primary, holm_adjust([row["p_sign_flip"] for row in primary])):
        row["p_holm"] = adjusted
    write_csv(output / "primary_contrasts.csv", primary)
    summary = summarize(frame)
    summary.to_csv(output / "summary.csv", index=False)
    # Prespecified descriptive views; every subgroup is exploratory.
    breakdowns = []
    for field in ("template_family", "test_regime", "seed", "scenario", "variant_id", "policy"):
        for label, subgroup in test.groupby(field, dropna=False):
            part = summarize(subgroup)
            part["stratum_field"], part["stratum_value"] = field, label
            breakdowns.append(part)
    pd.concat(breakdowns, ignore_index=True).to_csv(output / "subgroup_summary.csv", index=False)
    stages = [column for column in frame if "lost_last_support_count" in column or "full_coverage_loss" in column
              or "lost_admissible_support_count" in column or "deleted_candidate" in column or "added_candidates" in column]
    flow = frame.groupby(["split", "config_id", "group_id"])[stages].mean().groupby(["split", "config_id"]).mean()
    flow.to_csv(output / "support_flow.csv")
    four_cell = frame.groupby(["split", "config_id", "G_final", "U_sim"]).agg(
        task_records=("qid", "size"), worlds=("group_id", "nunique")).reset_index()
    four_cell.to_csv(output / "source_coverage_four_cells.csv", index=False)
    explorations = []
    if exploratory:
        for left, right, family in exploratory_pairs(configs):
            endpoints = ("U_sim", "admissible_U_sim", "C_sim", "nonempty", "joint_compliant_U_sim") if family == "policy_stage" else ("U_sim",)
            subset = test[test.policy == "constrained"] if family == "policy_stage" else test
            for endpoint in endpoints:
                explorations.append(contrast(subset, configs, left, right, f"{left}_minus_{right}", family,
                                             repeats, permutation_repeats, seed, endpoint,
                                             subgroup="constrained_test" if family == "policy_stage" else "all_test"))
        for primary_row in primary:
            explorations.append(variant_interaction(test, primary_row["left_config"], primary_row["right_config"],
                                                     primary_row["name"], repeats, permutation_repeats, seed))
            for field in ("template_family", "test_regime", "seed", "scenario", "variant_id", "policy"):
                for label, subgroup in test.groupby(field, dropna=False):
                    explorations.append(contrast(subgroup, configs, primary_row["left_config"], primary_row["right_config"],
                                                 primary_row["name"], "subgroup_" + field, repeats,
                                                 permutation_repeats, seed, subgroup=f"{field}={label}"))
        families = sorted({row["family"] for row in explorations})
        for family in families:
            members = [row for row in explorations if row["family"] == family]
            for row, adjusted in zip(members, bh_adjust([row["p_sign_flip"] for row in members])):
                row["q_bh_within_family"] = adjusted
                row["family_size"] = len(members)
        write_csv(output / "exploratory_contrasts.csv", explorations)
    controls = []
    for left, right, family in exploratory_pairs(configs):
        if family != "cap_stage":
            continue
        a, b = frame[frame.config_id == left].set_index("qid"), frame[frame.config_id == right].set_index("qid")
        b = b.reindex(a.index)
        eligible = (a.raw_max_chunks_per_source <= a.cap) & ~a.refill.astype(bool)
        controls.append({"post": left, "pre": right, "eligible_no_op_tasks": int(eligible.sum()),
                         "different_delivery_no_op_tasks": int((a.final_delivery_sha256[eligible] != b.final_delivery_sha256[eligible]).sum()),
                         "interpretation": "Constructive no-op invariant; support-preserving redundancy is separately measured in support_flow."})
    if any(row["different_delivery_no_op_tasks"] for row in controls):
        raise ValueError("A prespecified cap-inactive control changed actual delivered evidence")
    dump_json(output / "controls.json", controls)
    # This condition is defined by generation factors, never selected by the
    # observed success of an experimental configuration. The designated source
    # contains only copies of one complete-support chunk, so a positive cap
    # cannot delete its last available full support. This is a membership
    # invariant; it does not promise that a finite budget delivers that support.
    redundant = frame[(frame.scenario == "single_chunk") & (frame.variant_id == "high_concentration") &
                      (frame.factor_duplicate_chunks == 12) & (frame.policy_stage == "none") & ~frame.refill.astype(bool)]
    violations = redundant[(redundant.raw_U_sim == 1) & (redundant.post_cap_U_sim != 1)]
    if len(violations):
        raise ValueError("Constructive redundant-complete-support membership control failed")
    dump_json(output / "redundant_support_control.json", {
        "task_configuration_records": len(redundant), "distinct_worlds": redundant.group_id.nunique(),
        "raw_full_support_records": int(redundant.raw_U_sim.sum()), "membership_violations": len(violations),
        "definition": "Single full-support chunk plus 12 exact copies under one URL; high-concentration variant, no source filter/refill",
        "interpretation": "Checks preservation of at least one full support in membership, not equality of budgeted final coverage."})
    old = legacy_null_audit(ROOT / "experiments/simulation/results/pilot_v2/per_record.csv")
    dump_json(output / "legacy_null_audit.json", old)
    report = {"status": "complete", "scope": "Controlled fictional administrative simulation",
              "primary": primary, "n_exploratory_contrasts": len(explorations), "study_plan_sha256": sha256(plan_path),
              "analysis_code_sha256": sha256(__file__), "evaluated_per_record_sha256": sha256(output / "per_record.csv"),
              "statistics": {"unit": "world", "within_world": "equal paired-variant mean", "bootstrap": "generation-seed stratified",
                             "repetitions": repeats, "sign_flip_repetitions": permutation_repeats, "seed": seed,
                             "primary_correction": "Holm across the two prespecified endpoints",
                             "exploratory_correction": "BH within each explicitly named family; subgroup effects are exploratory",
                             "equivalence": "No equivalence margin was prespecified; zero estimates do not establish equivalence"},
              "acceptance_mapping": {"A": "Generator and independent parser audits; sampled-world review records: data/strengthening_v1/audit/reviews/",
                                     "B": "Stage support flow, cap controls, budget geometry and packer-specific relaxed bounds",
                                     "C": "Matched configurations and per-template/model contrasts; conditional on fixed simulator families",
                                     "D": "Separate downstream answer-model report required; not inferred from U_sim",
                                     "E": "Nonempty, unconditional compliance and admissible coverage of explicit source filters",
                                     "F": "Separate actual online-request timing report required; no latency inferred from shared-cache traces"},
              "clinical_generalization_established": False}
    report["auxiliary_runs"] = auxiliary_analyses(output, repeats, permutation_repeats, seed, answers, timing)
    generated = ("primary_contrasts.csv", "summary.csv", "subgroup_summary.csv", "support_flow.csv",
                 "source_coverage_four_cells.csv", "exploratory_contrasts.csv", "controls.json",
                 "redundant_support_control.json", "legacy_null_audit.json", "answer_contrasts.csv",
                 "answer_world_summary.csv", "timing_world_contrasts.csv")
    report["output_hashes"] = {name: sha256(output / name) for name in generated if (output / name).exists()}
    dump_json(output / "analysis.json", report)
    if plots:
        plot_results(primary, summary, output)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--plan", type=Path, default=ROOT / "experiments/strengthening/study_plan.json")
    parser.add_argument("--plots", action="store_true", help="Also generate scientific PDF/PNG figure")
    parser.add_argument("--skip-exploratory", action="store_true", help="Debug only; full artifact requires exploratory families")
    parser.add_argument("--answers", type=Path, help="Actual answer run; defaults to results/answers if present")
    parser.add_argument("--timing", type=Path, help="Actual online timing run; defaults to results/timing if present")
    args = parser.parse_args(argv)
    result = analyze(args.results, args.plan, args.plots, not args.skip_exploratory, args.answers, args.timing)
    print(json.dumps({"status": result["status"], "primary_comparisons": len(result["primary"]),
                      "exploratory_contrasts": result["n_exploratory_contrasts"]}))


if __name__ == "__main__":
    main()
