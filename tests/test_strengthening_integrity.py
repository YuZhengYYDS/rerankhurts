"""Tiny complete artifacts exercise the offline verifier without model files."""
import csv
import gzip
import json
from pathlib import Path

import pytest

from scripts import check_strengthening_files as check


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, sort_keys=True).encode()
    path.write_bytes(gzip.compress(payload, mtime=0) if path.suffix == ".gz" else payload)


def jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def table(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def artifact(tmp_path):
    root = tmp_path / "repo"
    source = root / "experiments/strengthening"
    data, run = source / "data/strengthening_v1", root / "experiments/runs/strengthening_v1"
    results = source / "results/strengthening_v1"
    source.mkdir(parents=True)
    for name in ("generate.py", "audit_data.py", "backend.py", "protocol.py", "evaluate.py", "downstream.py", "timing.py", "analyze.py", "figures.py"):
        (source / name).write_text(f"# fixture {name}\n", encoding="utf-8")
    plan = {"population": {"independent_worlds": 2, "paired_variants_per_world": 2,
                           "chunks_per_tenant_collection": 2, "generation_seeds": [7],
                           "dev_worlds_per_seed": 1, "test_worlds_per_seed": 1},
            "downstream": {"model": "example/answer", "revision": "a" * 40, "test_worlds": 1,
                           "evidence_conditions": ["a", "b", "c", "d"]},
            "online_timing": {"questions": 1, "configurations": 4,
                              "steady_repetitions_per_question_configuration": 2,
                              "warmup_requests_per_configuration": 2}}
    dump(source / "study_plan.json", plan)
    questions, corpus, metadata = [], [], []
    for index in range(4):
        qid, collection, group = f"q{index}", f"collection{index}", f"group{index // 2}"
        questions.append({"qid": qid, "collection_id": collection, "question": "Which value?", "allowed_url_prefixes": []})
        metadata.append({"qid": qid, "collection_id": collection, "group_id": group, "seed": 7,
                         "split": "dev" if index < 2 else "test"})
        corpus.extend({"chunk_id": f"{qid}-c{i}", "collection_id": collection,
                       "url": f"https://example/{qid}/{i}", "text": "alpha beta"} for i in range(2))
    rows = {"corpus.jsonl": corpus, "questions.jsonl": questions, "metadata.jsonl": metadata,
            "truth.jsonl": [{"group_id": "group0"}, {"group_id": "group1"}], "claims.jsonl": [{"claim": "fixture"}]}
    for name, values in rows.items():
        jsonl(data / name, values)
    spec = {"study_plan_snapshot": plan, "study_plan_sha256": check.sha256(source / "study_plan.json"),
            "generator_sha256": check.sha256(source / "generate.py"),
            "counts": {"worlds": 2, "tasks": 4, "chunks": 8, "collections": 4, "chunks_per_collection": 2},
            "files": {name: {"sha256": check.sha256(data / name), "rows": len(values)} for name, values in rows.items()}}
    dump(data / "specification.json", spec)
    dump(data / "audit/report.json", {"status": "PASS", "worlds": 2, "tasks": 4, "chunks": 8,
         "claims_independently_parsed": 1, "audit_code_sha256": check.sha256(source / "audit_data.py"),
         "input_sha256": {name: check.sha256(data / name) for name in check.DATA_FILES | {"specification.json"}}})
    model = {"model": "example/model", "sha": "a" * 40, "files": {"config.json": "b" * 64}}
    configs = [{"config_id": f"config{i}", "budget": 512} for i in range(4)]
    identity = {"study_plan_sha256": spec["study_plan_sha256"], "specification_sha256": check.sha256(data / "specification.json"),
                "corpus_sha256": check.sha256(data / "corpus.jsonl"), "questions_sha256": check.sha256(data / "questions.jsonl"),
                "code_sha256": {name: check.sha256(source / name) for name in ("backend.py", "protocol.py")},
                "models": {name: model for name in ("dense", "m3", "minilm", "tokenizer")}, "configurations": configs}
    identity_hash = check.digest(identity)
    dump(run / "manifest.json", {"identity": identity, "identity_hash": identity_hash, "configurations": configs,
                                 "expected_records": 16, "questions": 4, "corpus_chunks": 8, "collections": 4})
    for q in questions:
        original = next(row for row in corpus if row["collection_id"] == q["collection_id"])
        candidate = {"chunk_id": original["chunk_id"], "url": original["url"]}
        chunk = {**candidate, "char_start": 0, "char_end": 5, "text": "alpha",
                 "source_token_start": 0, "source_token_end": 1, "token_ids": [1000]}
        records = [{"qid": q["qid"], "collection_id": q["collection_id"], "configuration": config,
                    "candidate_reservoir": [candidate], "stages": {"raw": [candidate]},
                    "final_context": {"chunks": [chunk], "token_ids": [1000], "used_tokens": 1, "budget": 512, "separator_tokens": 0}}
                   for config in configs]
        dump(run / "traces" / (check.digest(q["qid"])[:24] + ".json.gz"),
             {**q, "identity_hash": identity_hash, "configurations": records})
    dump(run / "status.json", {"status": "complete", "identity_hash": identity_hash, "observed_records": 16, "expected_records": 16})
    table(results / "per_record.csv", [{"qid": q["qid"], "config_id": c["config_id"]} for q in questions for c in configs])
    table(results / "feasibility.csv", [{"qid": q["qid"], "packing": p, "budget": b} for q in questions
                                        for p in ("prefix", "whole", "window") for b in (256, 512, 1024, 2048)])
    dump(results / "status.json", {"status": "complete", "observed_tasks": 4, "expected_tasks": 4,
         "observed_records": 16, "configurations": 4, "evaluator_sha256": check.sha256(source / "evaluate.py"),
         "parser_sha256": check.sha256(source / "audit_data.py"), "run_manifest_sha256": check.sha256(run / "manifest.json"),
         "run_status_sha256": check.sha256(run / "status.json"), "run_identity_hash": identity_hash,
         "input_hashes": {name: check.sha256(data / name) for name in ("corpus.jsonl", "questions.jsonl", "metadata.jsonl", "truth.jsonl", "specification.json")},
         "trace_sha256": {p.name: check.sha256(p) for p in (run / "traces").iterdir()},
         "output_hashes": {name: check.sha256(results / name) for name in ("per_record.csv", "feasibility.csv")}})
    selected, conditions = ["q2", "q3"], {name: config for name, config in zip(("a", "b", "c", "d"), configs)}
    answer_identity = {"data": {name: check.sha256(data / name) for name in check.DATA_FILES},
                       "inference_manifest_sha256": check.sha256(run / "manifest.json"),
                       "code_sha256": {name: check.sha256(source / name) for name in ("downstream.py", "evaluate.py", "audit_data.py", "protocol.py")},
                       "model_snapshot": {**model, "model": "example/answer"}, "model": "example/answer", "revision": "a" * 40,
                       "worlds": ["group1"], "questions": selected, "conditions": conditions,
                       "input_traces_sha256": {q: check.sha256(run / "traces" / (check.digest(q)[:24] + ".json.gz")) for q in selected}}
    answer_hash = check.digest(answer_identity)
    answers = results / "answers"
    dump(answers / "manifest.json", {"identity": answer_identity, "identity_hash": answer_hash})
    response_rows = [{"qid": q, "group_id": "group1", "condition": c, "identity_hash": answer_hash,
                      "response": "unknown", "messages": [{"role": "user", "content": "Which?"}]}
                     for q in selected for c in (*conditions, "closed_book", "no_support")]
    for row in response_rows:
        dump(answers / "responses" / f"{row['qid']}__{row['condition']}.json", row)
    table(answers / "per_answer.csv", [{"qid": row["qid"], "condition": row["condition"]} for row in response_rows])
    table(answers / "summary.csv", [{"condition": c} for c in (*conditions, "closed_book", "no_support")])
    dump(answers / "status.json", {"status": "complete", "identity_hash": answer_hash, "expected_answers": 12,
         "observed_answers": 12, "independent_worlds": 1,
         "response_files": {p.name: check.sha256(p) for p in (answers / "responses").iterdir()},
         "output_hashes": {name: check.sha256(answers / name) for name in ("per_answer.csv", "summary.csv")}})
    timing = results / "timing"
    timing_identity = {"data": answer_identity["data"], "inference_manifest": check.sha256(run / "manifest.json"),
                       "backend_sha256": check.sha256(source / "backend.py"), "protocol_sha256": check.sha256(source / "protocol.py"),
                       "timing_code_sha256": check.sha256(source / "timing.py"), "downstream_code_sha256": check.sha256(source / "downstream.py"),
                       "diagnostic_trace_hashes": {"q2": check.sha256(run / "traces" / (check.digest("q2")[:24] + ".json.gz"))},
                       "qids": ["q2"], "groups": ["group1"], "configurations": conditions, "use_result_cache": False, "repetitions": 2}
    timing_hash = check.digest(timing_identity)
    dump(timing / "manifest.json", {"identity": timing_identity, "identity_hash": timing_hash})
    timing_rows = [{"qid": "q2", "group_id": "group1", "condition": c, "phase": phase, "repeat": repeat,
                    "identity_hash": timing_hash, "latency_ms": 1.0,
                    "final_delivery_sha256": check.digest([("q2-c0", 0, 1, [1000])]), "same_delivery_as_diagnostic": True,
                    "timing_provenance": {"scope": "independent_live_request", "query_cache_hit": False,
                                          "rerank_cache_hit": False, "offline_index_and_model_loading_excluded": True}}
                   for c in conditions for phase, count in (("first_pass", 1), ("steady", 2)) for repeat in range(count)]
    jsonl(timing / "requests.jsonl", timing_rows)
    table(timing / "summary.csv", [{"phase": p, "condition": c} for p in ("first_pass", "steady") for c in conditions])
    dump(timing / "status.json", {"status": "complete", "identity_hash": timing_hash, "requests": 12, "worlds": 1,
         "warmup_requests_excluded": 8, "requests_sha256": check.sha256(timing / "requests.jsonl"),
         "summary_sha256": check.sha256(timing / "summary.csv")})
    return root, source, data, run, results


def test_complete_artifact_needs_no_model_cache(artifact):
    root, _, _, _, _ = artifact
    assert not (root / ".cache").exists()
    report = check.verify(root)
    assert report["status"] == "PASS" and report["accepted"]
    assert report["verified_trace_files"] == 4 and report["expected_records"] == 16


def test_pending_is_not_complete_and_cli_default_fails(artifact, capsys):
    root, _, _, _, results = artifact
    (results / "answers/status.json").unlink()
    assert check.verify(root)["status"] == "PENDING"
    assert not check.verify(root)["accepted"]
    assert check.verify(root, allow_in_progress=True)["accepted"]
    assert check.main(["--root", str(root)]) == 1
    assert check.main(["--root", str(root), "--allow-in-progress"]) == 0
    assert '"PENDING"' in capsys.readouterr().out


@pytest.mark.parametrize("relative", ["experiments/strengthening/backend.py",
                                     "experiments/strengthening/data/strengthening_v1/corpus.jsonl",
                                     "experiments/strengthening/results/strengthening_v1/answers/summary.csv"])
def test_tampering_is_rejected(artifact, relative):
    root, *_ = artifact
    with (root / relative).open("ab") as handle:
        handle.write(b"changed")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        check.verify(root)


def test_extra_trace_and_missing_response_are_rejected(artifact):
    root, _, _, run, results = artifact
    dump(run / "traces/foreign.json.gz", {})
    with pytest.raises(ValueError, match="Unexpected trace"):
        check.verify(root)
    (run / "traces/foreign.json.gz").unlink()
    next((results / "answers/responses").iterdir()).unlink()
    with pytest.raises(ValueError, match="Missing regular file"):
        check.verify(root)


def test_rehashed_malformed_counts_still_fail(artifact):
    root, _, _, run, _ = artifact
    status = check.read_json(run / "status.json")
    status["observed_records"] = 15
    dump(run / "status.json", status)
    with pytest.raises(ValueError, match="status counts"):
        check.verify(root)


@pytest.mark.parametrize("name", ["../outside", "/absolute", "C:/absolute", "nested\\escape", "a//b", "file:stream"])
def test_unsafe_references_are_rejected(tmp_path, name):
    with pytest.raises(ValueError, match="Unsafe"):
        check.reference(tmp_path, name)


def test_model_hashes_are_format_checked_without_reading_weights(artifact):
    root, _, _, run, _ = artifact
    manifest = check.read_json(run / "manifest.json")
    manifest["identity"]["models"]["m3"]["files"]["../../secret"] = "a" * 64
    manifest["identity_hash"] = check.digest(manifest["identity"])
    dump(run / "manifest.json", manifest)
    with pytest.raises(ValueError, match="Unsafe"):
        check.verify(root)


def test_live_cache_hit_rejected_even_with_updated_file_checksum(artifact):
    root, _, _, _, results = artifact
    timing = results / "timing"
    rows = list(check.read_jsonl(timing / "requests.jsonl"))
    rows[0]["timing_provenance"]["rerank_cache_hit"] = True
    jsonl(timing / "requests.jsonl", rows)
    status = check.read_json(timing / "status.json")
    status["requests_sha256"] = check.sha256(timing / "requests.jsonl")
    dump(timing / "status.json", status)
    with pytest.raises(ValueError, match="reused a result"):
        check.verify(root)


def test_delivered_text_cannot_hide_behind_unverified_trace_hash(artifact):
    root, _, _, run, _ = artifact
    path = next((run / "traces").iterdir())
    trace = check.read_json(path)
    trace["configurations"][0]["final_context"]["chunks"][0]["text"] = "fabricated"
    dump(path, trace)
    with pytest.raises(ValueError, match="Delivered text differs"):
        check.verify(root)


def test_cli_routes_verifier_and_dry_run_is_read_only(capsys):
    from rerankhuts import cli
    assert cli.commands_for("strengthen-verify", ["--allow-in-progress"]) == [
        ["scripts/check_strengthening_files.py", "--allow-in-progress"]]
    assert cli.main(["--dry-run", "strengthen-verify", "--allow-in-progress"]) == 0
    output = capsys.readouterr().out
    assert "check_strengthening_files.py" in output and "--allow-in-progress" in output


def test_answer_model_snapshot_must_match_declared_model(artifact):
    root, _, _, _, results = artifact
    path = results / "answers/manifest.json"
    manifest = check.read_json(path)
    manifest["identity"]["model_snapshot"]["model"] = "foreign/model"
    manifest["identity_hash"] = check.digest(manifest["identity"])
    dump(path, manifest)
    status_path = results / "answers/status.json"
    status = check.read_json(status_path)
    status["identity_hash"] = manifest["identity_hash"]
    dump(status_path, status)
    with pytest.raises(ValueError, match="snapshot identity differs"):
        check.verify(root)


def test_timing_diagnostic_hash_cannot_be_stale(artifact):
    root, _, _, _, results = artifact
    path = results / "timing/manifest.json"
    manifest = check.read_json(path)
    manifest["identity"]["diagnostic_trace_hashes"]["q2"] = "0" * 64
    manifest["identity_hash"] = check.digest(manifest["identity"])
    dump(path, manifest)
    status_path = results / "timing/status.json"
    status = check.read_json(status_path)
    status["identity_hash"] = manifest["identity_hash"]
    dump(status_path, status)
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        check.verify(root)


def test_timing_delivery_agreement_is_independently_recomputed(artifact):
    root, _, _, _, results = artifact
    path = results / "timing/requests.jsonl"
    rows = list(check.read_jsonl(path))
    rows[0]["same_delivery_as_diagnostic"] = False
    jsonl(path, rows)
    status_path = results / "timing/status.json"
    status = check.read_json(status_path)
    status["requests_sha256"] = check.sha256(path)
    dump(status_path, status)
    with pytest.raises(ValueError, match="delivery comparison differs"):
        check.verify(root)


@pytest.mark.parametrize("label,field", [("answers", "per_answer_sha256"), ("timing", "requests_sha256")])
def test_stale_auxiliary_analysis_is_rejected(artifact, label, field):
    root, source, _, _, results = artifact
    dump(results / "analysis.json", {"analysis_code_sha256": check.sha256(source / "analyze.py"),
         "study_plan_sha256": check.sha256(source / "study_plan.json"),
         "evaluated_per_record_sha256": check.sha256(results / "per_record.csv"),
         "output_hashes": {}, "auxiliary_runs": {label: {"status": "complete", field: "0" * 64}}})
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        check.verify(root)
