"""Build manuscript tables from complete, hashed strengthening core results.

This stdlib-only builder checks saved identities and independently recomputes
equal-world U_sim means. It does not run models or regenerate statistical tests.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))
DEFAULT_RESULTS = ROOT / "experiments/strengthening/results/strengthening_v1"
DEFAULT_RUN = ROOT / "experiments/runs/strengthening_v1"
DEFAULT_DATA = ROOT / "experiments/strengthening/data/strengthening_v1"
CONFIG_FIELDS = ("retriever", "dense_view", "pool", "reranker", "cap", "cap_stage",
                 "refill", "budget", "packing", "score_view", "policy_stage", "mmr_lambda")
BASE = dict(retriever="dense", dense_view="prefix512", pool=64, reranker="m3",
            cap=0, cap_stage="off", refill=False, packing="prefix",
            score_view="prefix512", policy_stage="none", mmr_lambda=None)
METHODS = (
    ("Dense", "Prefix", dict(reranker="none")),
    ("Dense+M3 off", "Prefix", {}),
    ("Dense+M3 pre-2", "Prefix", dict(cap=2, cap_stage="pre")),
    ("Dense+M3 post-2", "Prefix", dict(cap=2, cap_stage="post")),
    ("Dense+M3 post-2", "Whole", dict(cap=2, cap_stage="post", packing="whole")),
    ("Dense+M3 post-2", "Window", dict(cap=2, cap_stage="post", packing="window")),
    ("Dense+MiniLM post-2", "Prefix", dict(reranker="minilm", cap=2, cap_stage="post")),
    ("BM25+M3 post-2", "Prefix", dict(retriever="bm25", cap=2, cap_stage="post")),
    ("Fusion+M3 post-2", "Prefix", dict(retriever="fusion", cap=2, cap_stage="post")),
    ("Dense+MMR", "Prefix", dict(reranker="none", mmr_lambda=0.5)),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream)


def check_hash(path, expected):
    require(isinstance(expected, str) and sha(path) == expected, f"SHA-256 mismatch: {path}")


def near(a, b, message):
    require(math.isfinite(float(a)) and math.isfinite(float(b))
            and abs(float(a) - float(b)) <= 1e-12, message)


def matched_config(configs, budget, **changes):
    target = {**BASE, "budget": budget, **changes}
    matches = [c for c in configs.values() if all(c[k] == target[k] for k in CONFIG_FIELDS)]
    require(len(matches) <= 1, f"Ambiguous exact configuration: {target}")
    return matches[0]["config_id"] if matches else None


def csv_config_value(text, value):
    if value is None:
        return text == ""
    if isinstance(value, bool):
        return text == str(value)
    if isinstance(value, (int, float)):
        return math.isfinite(float(text)) and float(text) == value
    return text == value


def validated_inputs(source, run, data):
    status, analysis = read_json(source / "status.json"), read_json(source / "analysis.json")
    require(status.get("status") == analysis.get("status") == "complete", "Complete evaluation and analysis required")
    require((status.get("observed_tasks"), status.get("expected_tasks"), status.get("observed_records"),
             status.get("configurations")) == (720, 720, 89280, 124), "Full strengthening population required")
    require(status.get("annotation_source") == "independent_synthetic_text_parser"
            and (status.get("scoring_method") == "deterministic_exact_fact_coverage"
                 or status.get("human_audit_complete") is False), "Synthetic endpoint identity changed")
    for name in ("per_record.csv", "feasibility.csv"):
        check_hash(source / name, status["output_hashes"][name])
    check_hash(source / "per_record.csv", analysis["evaluated_per_record_sha256"])
    for name in ("summary.csv", "primary_contrasts.csv"):
        check_hash(source / name, analysis["output_hashes"][name])
    for name in ("manifest.json", "status.json"):
        check_hash(run / name, status["run_" + name.replace(".json", "") + "_sha256"])
    manifest, run_status = read_json(run / "manifest.json"), read_json(run / "status.json")
    require(run_status.get("status") == "complete" and run_status.get("observed_records") == 89280
            and run_status.get("expected_records") == 89280, "Complete inference required")
    identity = hashlib.sha256(json.dumps(manifest["identity"], sort_keys=True, ensure_ascii=False,
                                         separators=(",", ":")).encode()).hexdigest()
    require(identity == manifest["identity_hash"] == run_status["identity_hash"] == status["run_identity_hash"],
            "Inference/evaluation identity mismatch")
    require(manifest["configurations"] == manifest["identity"]["configurations"], "Configuration manifest mismatch")
    configs = {c["config_id"]: c for c in manifest["configurations"]}
    require(len(configs) == len(manifest["configurations"]) == 124, "Duplicate/missing configurations")
    for name, expected in status["input_hashes"].items():
        require(Path(name).name == name, "Unexpected data reference")
        if name == "specification.json":
            from scripts.check_strengthening_files import recorded_specification
            check_hash(recorded_specification(data, expected), expected)
        else:
            check_hash(data / name, expected)
    for key, filename in (("evaluator_sha256", "evaluate.py"), ("parser_sha256", "audit_data.py")):
        from scripts.check_strengthening_files import recorded_source
        check_hash(recorded_source(ROOT / "experiments/strengthening", filename, status[key]), status[key])
    check_hash(ROOT / "experiments/strengthening/analyze.py", analysis["analysis_code_sha256"])
    plan_path = ROOT / "experiments/strengthening/study_plan.json"
    for payload in (status, analysis):
        check_hash(recorded_source(plan_path.parent, plan_path.name, payload["study_plan_sha256"]), payload["study_plan_sha256"])
    stats = analysis["statistics"]
    require(stats["unit"] == "world" and stats["within_world"] == "equal paired-variant mean"
            and stats["bootstrap"] == "generation-seed stratified"
            and (stats["repetitions"], stats["sign_flip_repetitions"], stats["seed"]) == (5000, 20000, 20261002),
            "Statistical protocol changed")
    metadata = [json.loads(line) for line in (data / "metadata.jsonl").read_text(encoding="utf-8").splitlines()]
    tasks = {m["qid"]: m for m in metadata}
    require(len(tasks) == len(metadata) == 720, "Duplicate/missing metadata tasks")
    groups = defaultdict(list)
    for row in metadata:
        groups[row["group_id"]].append(row)
    require(len(groups) == 360, "Expected 360 worlds")
    for rows in groups.values():
        require(len(rows) == 2 and {r["variant_id"] for r in rows} == {"low_concentration", "high_concentration"}
                and len({(r["split"], r["seed"]) for r in rows}) == 1, "Invalid paired world")
    require(Counter((rows[0]["seed"], rows[0]["split"]) for rows in groups.values())
            == Counter({(seed, split): count for seed in (20261002, 20261003, 20261004)
                        for split, count in (("dev", 20), ("test", 100))}), "Unexpected world splits")
    # Recompute every summary from paired task outcomes, never treating configurations as samples.
    seen, world_sums = set(), defaultdict(float)
    for row in read_csv(source / "per_record.csv"):
        qid, cid = row["qid"], row["config_id"]
        require(qid in tasks and cid in configs and (qid, cid) not in seen, "Unknown or duplicate task/configuration")
        seen.add((qid, cid))
        meta = tasks[qid]
        require(all(row[k] == str(meta[k]) for k in ("group_id", "collection_id", "seed", "split", "variant_id")),
                "Task metadata mismatch")
        require(all(csv_config_value(row[k], configs[cid][k]) for k in CONFIG_FIELDS), "Configuration fields mismatch")
        value = float(row["U_sim"])
        require(value in (0.0, 1.0), "U_sim must be binary")
        world_sums[(meta["split"], cid, meta["group_id"])] += value
    require(len(seen) == 89280, "Incomplete task/configuration matrix")
    recomputed = defaultdict(list)
    for (split, cid, _), value in world_sums.items():
        recomputed[(split, cid)].append(value / 2)
    summaries = {}
    for row in read_csv(source / "summary.csv"):
        key = (row["split"], row["config_id"])
        require(key in recomputed and key not in summaries, "Unknown or duplicate summary")
        expected = 300 if row["split"] == "test" else 60
        require(int(row["n_worlds"]) == len(recomputed[key]) == expected, "Summary world denominator mismatch")
        near(row["U_sim"], sum(recomputed[key]) / expected, "Summary differs from equal-world U_sim")
        summaries[key] = row
    require(len(summaries) == 248, "Expected all development/test configuration summaries")
    primary = list(read_csv(source / "primary_contrasts.csv"))
    require(len(primary) == 2 and {r["name"] for r in primary} == {"cap_order_512", "cap_order_2048"}, "Primary family changed")
    announced = {r["name"]: r for r in analysis["primary"]}
    require(set(announced) == {r["name"] for r in primary} and len(analysis["primary"]) == 2, "Analysis primary family mismatch")
    for row in primary:
        budget = int(row["name"].rsplit("_", 1)[1])
        for key, stage in (("left_config", "post"), ("right_config", "pre")):
            require(row[key] == matched_config(configs, budget, cap=2, cap_stage=stage), "Primary configuration mismatch")
        require(row["analysis"] == "prespecified_primary" and row["endpoint"] == "U_sim" and row["subgroup"] == "all_test"
                and int(row["n_worlds"]) == 300 and int(row["n_task_pairs"]) == 600, "Primary population/endpoint mismatch")
        for key in ("left_world_mean", "right_world_mean", "difference", "ci95_low", "ci95_high", "p_sign_flip", "p_holm"):
            near(row[key], announced[row["name"]][key], "Primary CSV differs from analysis JSON")
        near(row["left_world_mean"], summaries[("test", row["left_config"])]["U_sim"], "Post mean mismatch")
        near(row["right_world_mean"], summaries[("test", row["right_config"])]["U_sim"], "Pre mean mismatch")
        near(row["difference"], float(row["left_world_mean"]) - float(row["right_world_mean"]), "Contrast direction mismatch")
        require(-1 <= float(row["ci95_low"]) <= float(row["ci95_high"]) <= 1
                and 0 <= float(row["p_sign_flip"]) <= float(row["p_holm"]) <= 1, "Invalid interval/p-value")
    previous = 0.0
    for i, row in enumerate(sorted(primary, key=lambda r: float(r["p_sign_flip"]))):
        previous = max(previous, min(1.0, (2 - i) * float(row["p_sign_flip"])))
        near(row["p_holm"], previous, "Holm correction mismatch")
    return status, analysis, configs, summaries, sorted(primary, key=lambda r: int(r["name"].rsplit("_", 1)[1]))


def build(source=DEFAULT_RESULTS, run=DEFAULT_RUN, data=DEFAULT_DATA, output=None):
    source, run, data = Path(source).resolve(), Path(run).resolve(), Path(data).resolve()
    output = Path(output).resolve() if output else ROOT / "build/reanalysis/tables/strengthening"
    status, analysis, configs, summaries, primary = validated_inputs(source, run, data)
    lines = ["% Generated from complete, SHA-verified strengthening core results; do not edit numerical cells.",
        r"\begin{table*}[t]", r"\centering",
        r"\caption{Prespecified cap-order comparisons on 300 test worlds, averaging both variants within each world. Dense pool 64, M3, cap 2, prefix512 scoring views and prefix packing are fixed, with no refill or source filter. Coverage and differences are fractions. Intervals use 5,000 seed-stratified world bootstrap replicates; sign-flip $p$-values are Holm-adjusted across the two comparisons.}",
        r"\label{tab:strengthening-primary}", r"\begin{tabular}{rrrrcr}", r"\toprule",
        r"Budget & Pre-cap $U_{\mathrm{sim}}$ & Post-cap $U_{\mathrm{sim}}$ & $\Delta$ (post--pre) & World 95\% CI & Holm $p$ \\", r"\midrule"]
    for row in primary:
        lines.append(" & ".join((row["name"].rsplit("_", 1)[1], f"{float(row['right_world_mean']):.4f}",
            f"{float(row['left_world_mean']):.4f}", f"{float(row['difference']):.4f}",
            f"[{float(row['ci95_low']):.4f}, {float(row['ci95_high']):.4f}]", f"{float(row['p_holm']):.4f}")) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}", "", r"\begin{table}[t]", r"\centering",
        r"\caption{Complete fact coverage for fixed method and packing configurations on the same 300 test worlds. Pool 64 and prefix512 model views are fixed, with no refill or source filter. Off and Dense/MMR rows use no cap; pre/post-2 denotes cap 2 placement. MMR uses $\lambda=0.5$.}",
        r"\label{tab:strengthening-methods}", r"\begin{tabular}{@{}llrr@{}}", r"\toprule",
        r"Method & Packing & $B=512$ & $B=2048$ \\", r"\midrule"]
    cells = []
    for method, packing, settings in METHODS:
        values = []
        for budget in (512, 2048):
            cid = matched_config(configs, budget, **settings)
            value = float(summaries[("test", cid)]["U_sim"]) if cid else None
            values.append("--" if value is None else f"{value:.3f}")
            cells.append({"method": method, "packing": packing, "budget": budget, "config_id": cid,
                          "U_sim": value, "n_worlds": 300 if cid else None, "settings": {**BASE, "budget": budget, **settings}})
        lines.append(" & ".join((method, packing, *values)) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    output.mkdir(parents=True, exist_ok=True)
    tex = output / "strengthening_table.tex"
    tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
    provenance = {"kind": "complete_strengthening_core_tables", "annotation_source": status["annotation_source"],
        "valid_for_human_eval_claim": False, "run_identity_hash": status["run_identity_hash"],
        "worlds": 360, "test_worlds": 300, "tasks": 720, "configuration_records": 89280,
        "aggregation": "Equal paired-variant means within each world, then equal world means; independently recomputed from all per_record rows",
        "table_labels": ["tab:strengthening-primary", "tab:strengthening-methods"],
        "statistics": analysis["statistics"], "primary_rows": primary, "method_cells": cells,
        "source_sha256": {name: sha(source / name) for name in
                          ("status.json", "analysis.json", "per_record.csv", "feasibility.csv", "summary.csv", "primary_contrasts.csv")},
        "run_sha256": {name: sha(run / name) for name in ("manifest.json", "status.json")},
        "data_sha256": status["input_hashes"], "study_plan_sha256": status["study_plan_sha256"],
        "builder_sha256": sha(Path(__file__).resolve()), "generated_tex_sha256": sha(tex)}
    (output / "strengthening_table_manifest.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    return provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="?", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(args.results, args.run, args.data, args.output)
    print(json.dumps({"status": "complete", "test_worlds": result["test_worlds"],
                      "table_labels": result["table_labels"], "generated_tex_sha256": result["generated_tex_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
