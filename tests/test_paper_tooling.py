"""Historical regeneration fixtures exercise safe output routing without models."""
import csv
import hashlib
import json
from pathlib import Path
import sys

from scripts.paper import build_e3_table as e3
from scripts.paper import build_simulation_table as simulation
from scripts.paper import build_strengthening_table as strengthening
from scripts.paper import build_tables as legacy


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def snapshot_inputs(root):
    for tree in ("paper", "archive/paper_20261022"):
        path = root / tree / "unchanged.tex"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"Do not overwrite supplied or archived manuscript")
    return {path: path.read_bytes() for path in root.rglob("unchanged.tex")}


def assert_untouched(snapshot):
    assert all(path.read_bytes() == payload for path, payload in snapshot.items())


def test_e3_table_invocation_writes_scratch_table_and_figure(tmp_path, monkeypatch):
    before = snapshot_inputs(tmp_path)
    run = tmp_path / "e3_run"
    run.mkdir()
    write_json(run / "manifest.json", {"questions": 155, "identity_hash": "fixture"})
    write_json(run / "status.json", {"status": "complete", "expected_records": 3100,
                                     "observed_records": 3100})
    rows = [{"config_id": str(index), "n_questions": 155, "G_final": .5,
             "ranking_url_ndcg10": .5, "ranking_url_mrr": .5, "mean_context_tokens": 100,
             "budget": 2048, "reranker": "none", "pool": 64, "cap": "off",
             "latency_p50_ms": 1, "latency_p95_ms": 2} for index in range(20)]
    write_csv(run / "summary.csv", rows)
    (run / "G_factorial.pdf").write_bytes(b"fixture figure")
    (run / "G_contrasts.csv").write_text("fixture contrast")
    monkeypatch.setattr(e3, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["build_e3_table.py", str(run)])
    e3.main()
    output = tmp_path / "build/reanalysis/tables/e3"
    assert "0.5000" in (output / "generated/e3_results.tex").read_text()
    assert (output / "figures/G_factorial.pdf").read_bytes() == b"fixture figure"
    assert json.loads((output / "generated/e3_table_manifest.json").read_text())["questions"] == 155
    assert_untouched(before)


def test_simulation_table_invocation_writes_scratch_table_and_figure(tmp_path, monkeypatch):
    before = snapshot_inputs(tmp_path)
    source = tmp_path / "simulation_results"
    source.mkdir()
    selections, rows = {}, []
    for key, budget in (("primary", 512), ("exploratory_2048", 2048)):
        cid = f"p64_off_m3_b{budget}"
        selections[key] = {"status": "complete", "policy": "open", "budget": budget,
            "n_dev_information_needs": 20, "n_test_information_needs": 40,
            "configuration_tie_order": list(range(10)), "dev_selected_by_G": cid,
            "dev_selected_by_U_sim": cid, "test_U_sim_delta_U_selected_minus_G_selected": 0,
            "test_selected_config_means": {criterion: {"G_final": .9, "U_sim": .8}
                                           for criterion in ("G", "U_sim")}}
        rows.append({"scope": "overall", "split": "test", "policy": "open", "config_id": cid,
                     "n_information_needs": 40, "G_final": .9, "U_sim": .8})
    selections.update(annotation_source="synthetic_oracle", valid_for_human_eval_claim=False)
    write_json(source / "selection.json", selections)
    write_csv(source / "summary.csv", rows)
    write_json(source / "budget_feasibility.json", {})
    (source / "selection_comparison.pdf").write_bytes(b"fixture figure")
    write_json(source / "status.json", {"status": "complete", "observed_records": 2400,
        "expected_records": 2400, "worlds": 60, "tasks": 120,
        "split_world_counts": {"dev": 20, "test": 40}, "annotation_source": "synthetic_oracle",
        "valid_for_human_eval_claim": False,
        "output_sha256": {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                          for name in ("selection.json", "summary.csv", "budget_feasibility.json")},
        "provenance": {"run_identity": "fixture", "input_files": {}}})
    monkeypatch.setattr(simulation, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["build_simulation_table.py", str(source)])
    simulation.main()
    output = tmp_path / "build/reanalysis/tables/simulation"
    assert "0.800" in (output / "generated/simulation_results.tex").read_text()
    assert (output / "figures/selection_comparison.pdf").read_bytes() == b"fixture figure"
    assert_untouched(before)


def test_strengthening_default_output_uses_scratch_with_validated_input_fixture(tmp_path, monkeypatch):
    before = snapshot_inputs(tmp_path)
    source, run, data = [tmp_path / name for name in ("results", "run", "data")]
    for directory in (source, run, data):
        directory.mkdir()
    for name in ("status.json", "analysis.json", "per_record.csv", "feasibility.csv", "summary.csv", "primary_contrasts.csv"):
        (source / name).write_text("validated fixture")
    for name in ("manifest.json", "status.json"):
        (run / name).write_text("validated fixture")
    status = {"annotation_source": "synthetic_oracle", "run_identity_hash": "fixture",
              "input_hashes": {}, "study_plan_sha256": "fixture"}
    primary = [{"name": f"contrast_{budget}", "right_world_mean": .25, "left_world_mean": .5,
                "difference": .25, "ci95_low": .1, "ci95_high": .4, "p_holm": .03}
               for budget in (512, 2048)]
    monkeypatch.setattr(strengthening, "ROOT", tmp_path)
    monkeypatch.setattr(strengthening, "METHODS", [])
    monkeypatch.setattr(strengthening, "validated_inputs", lambda *args: (status, {"statistics": {}}, {}, {}, primary))
    strengthening.build(source, run, data)
    output = tmp_path / "build/reanalysis/tables/strengthening"
    assert "0.2500" in (output / "strengthening_table.tex").read_text()
    assert (output / "strengthening_table_manifest.json").is_file()
    assert_untouched(before)


def test_legacy_table_invocation_uses_scratch_output(tmp_path, monkeypatch):
    before = snapshot_inputs(tmp_path)
    tables = tmp_path / "results/tables"
    tables.mkdir(parents=True)
    methods = ["None (dense Base)", "MiniLM-L6", "bge-reranker-base", "MedCPT-Cross-Encoder",
               "LLM listwise (DeepSeek)", "bge-reranker-v2-m3", "MiniLM-L6 + NCI source prior"]
    write_csv(tables / "rev_table_rerankers.csv", [{"method": method, "orig78_ndcg": .5,
              "orig78_hit": .5, "exp155_ndcg": .5, "exp155_hit": .5} for method in methods])
    modes = ["baseline", "rerank", "rerank_bge_base", "rerank_bge_m3", "rerank_medcpt", "rrf_hybrid", "rerank_source_aware"]
    write_csv(tables / "rev_table_judge.csv", [{"mode": mode, "judge": judge,
        "valid_for_human_eval_claim": "false", "composite_mean": 3, "distinct_source_mean_relevance": 1}
        for mode in modes for judge in ("answer_quality_1to5", "graded_relevance_0to2")])
    output = tmp_path / "build/reanalysis/tables/legacy"
    monkeypatch.setattr(legacy, "ROOT", tmp_path)
    monkeypatch.setattr(legacy, "TABLES", tables)
    monkeypatch.setattr(legacy, "GENERATED", output)
    legacy.main()
    assert "0.5000" in (output / "legacy_results.tex").read_text()
    assert (output / "judge_results.tex").is_file()
    assert_untouched(before)
