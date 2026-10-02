"""E2 grouped dev-selection/test-utility analysis; refuses fabricated or missing U.

Input CSV: qid,information_need_id,group_id,config_id,token_budget,
construction_source,source_policy,G,url_ndcg_at_10,U,annotation_source,
adjudication_record_id. U=0/1/2; primary utility is U==2.
Specification JSON freezes dev_groups, test_groups, configs, primary_metric (G or
url_ndcg_at_10), tie_order (full config list), delta, seed, bootstrap_repetitions.
Each config must have equal token budgets (declare token_budget in specification).
Only an independently designed open-evidence cohort is accepted for formal E2.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import numpy as np

from .protocol import file_hash, load_json, read_jsonl, require_human_utility, save_json


def validate(rows, spec, allow_legacy=False):
    require_human_utility(rows)
    dev, test = set(spec["dev_groups"]), set(spec["test_groups"])
    configs = list(spec["configs"])
    if len(dev) != len(spec["dev_groups"]) or len(test) != len(spec["test_groups"]):
        raise ValueError("Frozen group lists must be unique; duplicates would reweight bootstrap samples.")
    if not dev or not test or dev & test:
        raise ValueError("Nonempty, disjoint development/test groups are required.")
    if len(configs) < 2 or len(set(configs)) != len(configs) or set(spec["tie_order"]) != set(configs) or len(spec["tie_order"]) != len(configs):
        raise ValueError("Freeze at least two configurations and a complete deterministic tie order.")
    if spec["primary_metric"] not in ("G", "url_ndcg_at_10"):
        raise ValueError("Freeze G or URL nDCG as the primary selection metric.")
    if type(spec.get("token_budget")) is not int or spec["token_budget"] <= 0 or spec.get("frozen_before_test_inspection") is not True:
        raise ValueError("Freeze a common token budget and specification before inspecting test outcomes.")
    if any(r["source_policy"] != "open" for r in rows):
        raise ValueError("This entry point implements open evidence only; predeclare a feasibility rule before constrained-task selection.")
    if not allow_legacy and any(r["construction_source"] != "independent_information_need" for r in rows):
        raise ValueError("Formal E2 requires independently proposed information needs; use --allow-legacy-diagnostic only for a labelled diagnostic.")
    seen, question_groups, needs, question_needs = set(), {}, {}, {}
    for r in rows:
        if type(r.get("U")) is not int:
            raise ValueError("U must be an explicit ordinal integer, not an inferred probability or boolean.")
        need = r.get("information_need_id")
        if not isinstance(need, str) or not need.strip():
            raise ValueError("Every question requires an information_need_id to guard against version leakage.")
        if need in needs and needs[need] != r["qid"]:
            raise ValueError("Multiple question versions share an information need; use one open-evidence instance per need.")
        if r["qid"] in question_needs and question_needs[r["qid"]] != need:
            raise ValueError("One question has inconsistent information_need_id values.")
        needs[need], question_needs[r["qid"]] = r["qid"], need
        if int(r.get("token_budget", -1)) != spec["token_budget"]:
            raise ValueError("All compared configurations must use the frozen token budget.")
        if r["group_id"] not in dev | test or r["config_id"] not in configs:
            raise ValueError("Labels outside frozen groups/configurations found.")
        key = (r["qid"], r["config_id"])
        if key in seen:
            raise ValueError("Duplicate question/configuration labels.")
        seen.add(key)
        if r["qid"] in question_groups and question_groups[r["qid"]] != r["group_id"]:
            raise ValueError("Same question appears in different groups.")
        question_groups[r["qid"]] = r["group_id"]
        for metric in ("G", "url_ndcg_at_10"):
            if not np.isfinite(r[metric]) or not 0 <= r[metric] <= 1:
                raise ValueError(f"Invalid {metric}.")
        if r["G"] not in (0, 1):
            raise ValueError("G must be binary designated-page retention.")
    if len(seen) != len(question_groups) * len(configs):
        raise ValueError("Every question must have adjudicated labels for all frozen configurations; no imputation is permitted.")
    if set(question_groups.values()) != dev | test:
        raise ValueError("At least one frozen group has no labels.")
    return question_groups


def verify_provenance(rows, provenance_path):
    """Verify archived annotation records, without claiming to authenticate humans.

    A source-name string alone is insufficient. The command-line entry point
    requires a hashed fact rubric, question-construction manifest and original
    two-annotator/adjudication records that agree with every CSV row.
    """
    provenance = load_json(provenance_path)
    if provenance.get("kind") != "human_adjudication":
        raise ValueError("Annotation provenance must describe human adjudication, not automatic judgments.")
    annotators = provenance.get("annotator_ids", [])
    if len(set(annotators)) < 2 or any(not isinstance(a, str) or not a.strip() for a in annotators):
        raise ValueError("Record at least two named independent human annotators.")
    adjudicator = provenance.get("adjudicator_id")
    if not isinstance(adjudicator, str) or not adjudicator.strip():
        raise ValueError("A named human adjudicator is required.")
    archives = {}
    for key in ("rubric", "construction_manifest", "adjudication_records"):
        path = Path(provenance[key + "_file"])
        if not path.is_absolute():
            path = provenance_path.parent / path
        if file_hash(path) != provenance[key + "_sha256"]:
            raise ValueError(f"{key} provenance hash does not match the archived file.")
        archives[key] = read_jsonl(path)

    def unique_index(values, key):
        index = {v[key]: v for v in values}
        if len(index) != len(values):
            raise ValueError(f"Duplicate {key} in annotation provenance.")
        return index

    rubric = unique_index(archives["rubric"], "qid")
    construction = unique_index(archives["construction_manifest"], "qid")
    records = unique_index(archives["adjudication_records"], "adjudication_record_id")
    for row in rows:
        qid = row["qid"]
        facts = rubric.get(qid, {})
        if not facts.get("necessary_facts") or facts.get("frozen_before_system_output") is not True or not facts.get("rubric_author"):
            raise ValueError("All questions require an archived, expert-authored, pre-output fact rubric.")
        source = construction.get(qid, {})
        if any(source.get(k) != row[k] for k in ("information_need_id", "group_id", "construction_source")):
            raise ValueError("CSV question identity/construction does not match the archived construction manifest.")
        record = records.get(row.get("adjudication_record_id"), {})
        if type(record.get("U")) is not int or any(record.get(k) != row[k] for k in ("qid", "config_id", "U")) or record.get("adjudicator_id") != adjudicator:
            raise ValueError("CSV U does not match its archived human adjudication record.")
        ratings = record.get("annotator_ratings", [])
        rating_ids = [r.get("annotator_id") for r in ratings]
        if len(set(rating_ids)) < 2 or len(set(rating_ids)) != len(rating_ids) or not set(rating_ids) <= set(annotators):
            raise ValueError("Each selected evidence bundle requires two independent archived human ratings.")
        if any(type(r.get("U")) is not int or r["U"] not in (0, 1, 2) for r in ratings):
            raise ValueError("Archived human ratings must be explicit ordinal U labels.")
    return {"provenance_sha256": file_hash(provenance_path),
            "archival_integrity": "verified against supplied archived files",
            "human_authenticity": "User-attested; code cannot authenticate human authorship or a chronological preregistration."}


def evaluate(rows, spec, allow_legacy=False):
    question_groups = validate(rows, spec, allow_legacy)
    config_ids = spec["configs"]
    dev_q = sorted(q for q, g in question_groups.items() if g in spec["dev_groups"])
    test_q = sorted(q for q, g in question_groups.items() if g in spec["test_groups"])
    lookup = {(r["qid"], r["config_id"]): r for r in rows}
    tie = {c: i for i, c in enumerate(spec["tie_order"])}

    def score(qids, config, metric):
        return float(np.mean([int(lookup[q, config]["U"] == 2) if metric == "U" else lookup[q, config][metric] for q in qids]))

    def select(qids, metric):
        return min(config_ids, key=lambda c: (-score(qids, c, metric), tie[c]))

    c_g, c_u = select(dev_q, spec["primary_metric"]), select(dev_q, "U")
    delta = score(test_q, c_u, "U") - score(test_q, c_g, "U")
    rng = np.random.default_rng(spec["seed"])
    repetitions = spec.get("bootstrap_repetitions", 10000)
    if type(repetitions) is not int or repetitions < 1000:
        raise ValueError("Use at least 1000 predeclared bootstrap repetitions.")
    if min(len(spec["dev_groups"]), len(spec["test_groups"])) < 2:
        raise ValueError("Grouped bootstrap needs at least two development and two test groups; even two gives fragile uncertainty.")
    if isinstance(spec.get("delta"), bool) or not isinstance(spec.get("delta"), (float, int)) or not 0 <= spec["delta"] <= 1:
        raise ValueError("Freeze a practical utility difference delta in [0,1].")

    def sample(groups):
        # Sample groups; include all member questions with multiplicity. Each
        # information need must have one row, never duplicate open/closed versions.
        drawn = rng.choice(groups, size=len(groups), replace=True)
        return [q for g in drawn for q in question_groups if question_groups[q] == g]

    boot = []
    selection_counts = {"G": Counter(), "U": Counter()}
    for _ in range(repetitions):
        sampled_test = sample(spec["test_groups"])
        boot.append(score(sampled_test, c_u, "U") - score(sampled_test, c_g, "U"))
        sampled_dev = sample(spec["dev_groups"])
        selection_counts["G"][select(sampled_dev, spec["primary_metric"])] += 1
        selection_counts["U"][select(sampled_dev, "U")] += 1
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"analysis_scope": "legacy diagnostic" if allow_legacy else "independent human-labelled E2",
            "c_G": c_g, "c_U": c_u, "test_U_difference": delta,
            "paired_group_bootstrap_95CI": [float(lo), float(hi)], "practical_delta": spec["delta"],
            "CI_excludes_zero": bool(lo > 0 or hi < 0), "CI_lower_bound_exceeds_delta": bool(lo >= spec["delta"]),
            "test_questions": len(test_q), "dev_questions": len(dev_q),
            "dev_groups": len(spec["dev_groups"]), "test_groups": len(spec["test_groups"]),
            "dev_selection_frequencies": {metric: {c: counts[c] / repetitions for c in config_ids}
                                         for metric, counts in selection_counts.items()},
            "configuration_summary": [{"config_id": c, "dev_G_metric": score(dev_q, c, spec["primary_metric"]),
                                       "dev_U": score(dev_q, c, "U"), "test_U": score(test_q, c, "U")} for c in config_ids],
            "uncertainty": "Paired percentile bootstrap resamples whole predefined groups; intervals with few independent groups are fragile. Failure to exclude zero does not establish equivalence.",
            "utility_definition": "Proportion of adjudicated evidence bundles rated sufficient (U=2); no U inferred from URL identity."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--provenance", type=Path, required=True,
                   help="Manifest of named annotators and hashed human records, fact rubric and question construction.")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--allow-legacy-diagnostic", action="store_true")
    args = p.parse_args()
    with args.labels.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        try:
            r["U"] = int(r["U"])
            r["G"] = float(r["G"])
            r["url_ndcg_at_10"] = float(r["url_ndcg_at_10"])
        except (KeyError, ValueError):
            raise ValueError("Missing or invalid U/G/nDCG; blanks cannot be treated as zero.") from None
    spec = load_json(args.spec)
    validate(rows, spec, args.allow_legacy_diagnostic)
    provenance = verify_provenance(rows, args.provenance)
    result = evaluate(rows, spec, args.allow_legacy_diagnostic)
    result.update({"labels_sha256": file_hash(args.labels), "spec_sha256": file_hash(args.spec),
                   "analysis_code_sha256": file_hash(__file__), "specification": spec,
                   "annotation_provenance": provenance})
    save_json(args.output, result)
    print(f"Saved E2 analysis to {args.output}")


if __name__ == "__main__":
    main()
