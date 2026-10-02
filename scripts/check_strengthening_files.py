"""Offline strengthening-artifact integrity verification (Python stdlib only).

No models, tokenizers, CUDA, network access, or local model-cache files are used.
This verifies recorded identities, exact file/record sets and source references;
it does not substitute for scientific evaluation or independent human review.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = {"corpus.jsonl", "questions.jsonl", "metadata.jsonl", "truth.jsonl", "claims.jsonl"}
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def sha256(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), f"Missing regular file: {path}")
    payload = path.read_bytes()
    return json.loads(gzip.decompress(payload) if path.suffix == ".gz" else payload,
                      object_pairs_hook=unique_object)


def read_jsonl(path):
    with Path(path).open(encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line, object_pairs_hook=unique_object)


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def safe_relative(name):
    require(isinstance(name, str) and name and not any(c in name for c in '\\:<>"|?*'),
            f"Unsafe referenced path: {name!r}")
    require(not any(ord(c) < 32 or ord(c) == 127 for c in name), f"Unsafe referenced path: {name!r}")
    require(all(part not in {"", ".", ".."} and not part.endswith((".", " ")) for part in name.split("/")),
            f"Unsafe referenced path: {name!r}")
    return name


def reference(base, name):
    safe_relative(name)
    base = Path(base).resolve()
    path = base / name
    require(path.resolve().is_relative_to(base), f"Reference escapes artifact directory: {name}")
    cursor = path
    while cursor != base:
        require(not cursor.is_symlink(), f"Linked artifact reference: {name}")
        cursor = cursor.parent
    return path


def valid_hash(value):
    return isinstance(value, str) and bool(HASH_PATTERN.fullmatch(value))


def check_hash(path, expected):
    require(valid_hash(expected), f"Invalid SHA-256 for {path}")
    require(Path(path).is_file() and not Path(path).is_symlink(), f"Missing regular file: {path}")
    require(sha256(path) == expected, f"SHA-256 mismatch: {path}")


def check_hash_map(base, mapping, exact=None):
    require(isinstance(mapping, dict), "File hashes must be an object")
    require(len({name.casefold() for name in mapping}) == len(mapping), "Aliased hash-map filenames")
    if exact is not None:
        require(set(mapping) == set(exact), f"Recorded file set differs: {base}")
    for name, expected in mapping.items():
        check_hash(reference(base, name), expected)


def check_model_identity(model):
    require(isinstance(model.get("model"), str) and model["model"], "Missing model identifier")
    require(isinstance(model.get("sha"), str) and REVISION_PATTERN.fullmatch(model["sha"]), "Model revision is not an immutable SHA")
    files = model.get("files")
    require(isinstance(files, dict) and bool(files), "Missing recorded model file hashes")
    for name, value in files.items():
        safe_relative(name)
        require(valid_hash(value), "Invalid recorded model file hash")


def unique_rows(rows, key, label):
    result = {}
    for row in rows:
        value = row[key]
        require(isinstance(value, str) and value and value not in result, f"Duplicate/invalid {label} ID")
        result[value] = row
    return result


def exact_pairs(rows, fields, expected, label):
    actual = [tuple(row[field] for field in fields) for row in rows]
    require(len(actual) == len(set(actual)) and set(actual) == set(expected), f"{label} record set differs")


def check_identity(manifest):
    require(valid_hash(manifest.get("identity_hash")) and digest(manifest["identity"]) == manifest["identity_hash"],
            "Manifest identity digest mismatch")
    return manifest["identity"]


def check_dataset(root, data, source):
    specification = read_json(data / "specification.json")
    plan = read_json(source / "study_plan.json")
    require(specification["study_plan_snapshot"] == plan, "Dataset study-plan snapshot differs")
    check_hash(source / "study_plan.json", specification["study_plan_sha256"])
    check_hash(source / "generate.py", specification["generator_sha256"])
    require(set(specification["files"]) == DATA_FILES, "Unexpected dataset file set")
    require({path.name for path in data.glob("*.jsonl")} == DATA_FILES, "Unrecorded dataset JSONL files")
    loaded = {}
    for name, entry in specification["files"].items():
        path = reference(data, name)
        check_hash(path, entry["sha256"])
        loaded[name] = list(read_jsonl(path))
        require(len(loaded[name]) == entry["rows"], f"Dataset row count mismatch: {name}")
    corpus = unique_rows(loaded["corpus.jsonl"], "chunk_id", "chunk")
    questions = unique_rows(loaded["questions.jsonl"], "qid", "question")
    metadata = unique_rows(loaded["metadata.jsonl"], "qid", "metadata")
    worlds = unique_rows(loaded["truth.jsonl"], "group_id", "world")
    require(set(questions) == set(metadata), "Question/metadata IDs differ")
    population, counts = plan["population"], specification["counts"]
    require(len(worlds) == counts["worlds"] == population["independent_worlds"], "Independent world count differs")
    require(len(questions) == counts["tasks"] == len(worlds) * population["paired_variants_per_world"], "Task count differs")
    require(len(corpus) == counts["chunks"] == counts["tasks"] * population["chunks_per_tenant_collection"], "Chunk count differs")
    collection_counts = Counter(row["collection_id"] for row in corpus.values())
    require(set(collection_counts) == {q["collection_id"] for q in questions.values()}, "Collection references differ")
    require(len(collection_counts) == counts["collections"] == len(questions), "Collection isolation count differs")
    require(set(collection_counts.values()) == {counts["chunks_per_collection"]} and counts["chunks_per_collection"] == population["chunks_per_tenant_collection"], "Per-collection size differs")
    groups = defaultdict(list)
    for qid, question in questions.items():
        require(set(question) == {"qid", "collection_id", "question", "allowed_url_prefixes"}, "Public question contains extra fields")
        meta = metadata[qid]
        require(meta["group_id"] in worlds and meta["collection_id"] == question["collection_id"], "Invalid task/world/collection reference")
        groups[meta["group_id"]].append(meta)
    split_counts = Counter()
    for group, variants in groups.items():
        require(len(variants) == population["paired_variants_per_world"], "Paired-world count differs")
        require(len({(row["seed"], row["split"]) for row in variants}) == 1, "World variants cross a seed/split")
        split_counts[(variants[0]["seed"], variants[0]["split"])] += 1
    expected_splits = {(seed, split): population[f"{split}_worlds_per_seed"]
                       for seed in population["generation_seeds"] for split in ("dev", "test")}
    require(dict(split_counts) == expected_splits, "Seed/world split counts differ")
    for row in corpus.values():
        require(set(row) == {"chunk_id", "collection_id", "url", "text"}, "Public corpus contains extra fields")
    audit = read_json(data / "audit/report.json")
    require(audit["status"] == "PASS", "Independent data audit did not pass")
    check_hash_map(data, audit["input_sha256"], DATA_FILES | {"specification.json"})
    check_hash(source / "audit_data.py", audit["audit_code_sha256"])
    require((audit["worlds"], audit["tasks"], audit["chunks"], audit["claims_independently_parsed"]) ==
            (len(worlds), len(questions), len(corpus), len(loaded["claims.jsonl"])), "Audit counts differ")
    return specification, plan, corpus, questions, metadata


def check_run(run, source, data, specification, corpus, questions, pending):
    if not (run / "manifest.json").exists():
        pending.append("evidence run has not started")
        return None, {}
    manifest = read_json(run / "manifest.json")
    identity = check_identity(manifest)
    check_hash(source / "study_plan.json", identity["study_plan_sha256"])
    check_hash(data / "specification.json", identity["specification_sha256"])
    for name, field in (("corpus.jsonl", "corpus_sha256"), ("questions.jsonl", "questions_sha256")):
        check_hash(data / name, identity[field])
    check_hash_map(source, identity["code_sha256"], {"backend.py", "protocol.py"})
    require(set(identity["models"]) == {"dense", "m3", "minilm", "tokenizer"}, "Model identity set differs")
    for model in identity["models"].values():
        check_model_identity(model)
    configurations = unique_rows(manifest["configurations"], "config_id", "configuration")
    require(manifest["configurations"] == identity["configurations"], "Configuration identity differs")
    expected_records = len(questions) * len(configurations)
    require(manifest["expected_records"] == expected_records and manifest["questions"] == len(questions), "Run denominator differs")
    require(manifest["corpus_chunks"] == len(corpus) and manifest["collections"] == len(questions), "Run data counts differ")
    status = read_json(run / "status.json") if (run / "status.json").exists() else {}
    complete = status.get("status") == "complete"
    expected_names = {digest(qid)[:24] + ".json.gz": qid for qid in questions}
    traces = run / "traces"
    files = sorted(traces.iterdir()) if traces.exists() else []
    files = [path for path in files if not (not complete and path.name.endswith(".tmp"))]
    require(all(path.name in expected_names and path.is_file() and not path.is_symlink() for path in files), "Unexpected trace file or path")
    if complete:
        require({path.name for path in files} == set(expected_names), "Complete run is missing traces")
    observed, hashes = 0, {}
    for path in files:
        trace = read_json(path)
        qid = expected_names[path.name]
        question = questions[qid]
        require(trace["identity_hash"] == manifest["identity_hash"] and trace["qid"] == qid, "Trace identity/qid differs")
        require(all(trace[key] == value for key, value in question.items()), "Trace public input differs")
        records = unique_rows((dict(record, config_id=record["configuration"]["config_id"]) for record in trace["configurations"]), "config_id", "trace configuration")
        require(set(records) == set(configurations), "Trace configuration set differs")
        for config_id, record in records.items():
            require(record["configuration"] == configurations[config_id], "Trace configuration fields differ")
            require(record["qid"] == qid and record["collection_id"] == question["collection_id"], "Record input reference differs")
            for rows in [record["candidate_reservoir"], *record["stages"].values()]:
                ids = [row["chunk_id"] for row in rows]
                require(len(ids) == len(set(ids)), "Duplicate candidate-stage IDs")
                for row in rows:
                    original = corpus.get(row["chunk_id"])
                    require(original is not None and original["collection_id"] == question["collection_id"] and original["url"] == row["url"], "Cross-collection or foreign stage reference")
            final = record["final_context"]
            stream, intervals = [], defaultdict(list)
            for chunk in final["chunks"]:
                original = corpus.get(chunk["chunk_id"])
                require(original is not None and original["collection_id"] == question["collection_id"] and original["url"] == chunk["url"], "Foreign delivered source")
                start, end = chunk["char_start"], chunk["char_end"]
                require(isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(original["text"]), "Invalid delivered char range")
                require(chunk["text"] == original["text"][start:end], "Delivered text differs from original source interval")
                begin_token, end_token = chunk["source_token_start"], chunk["source_token_end"]
                require(0 <= begin_token < end_token and end_token - begin_token == len(chunk["token_ids"]), "Invalid delivered token range")
                require(all(end <= left or start >= right for left, right in intervals[chunk["chunk_id"]]), "Overlapping delivered windows")
                intervals[chunk["chunk_id"]].append((start, end))
                if stream:
                    stream.append(102)  # Pinned bert-base-uncased SEP; no tokenizer installation needed.
                stream.extend(chunk["token_ids"])
            require(final["token_ids"] == stream and final["used_tokens"] == len(stream) <= configurations[config_id]["budget"], "Delivered evidence budget/stream differs")
            require(final["budget"] == configurations[config_id]["budget"] and final["separator_tokens"] == max(0, len(final["chunks"]) - 1), "Evidence budget metadata differs")
        observed += len(records)
        hashes[path.name] = sha256(path)
    if complete:
        require(status["identity_hash"] == manifest["identity_hash"] and status["observed_records"] == observed == expected_records and status["expected_records"] == expected_records, "Complete run status counts differ")
    else:
        pending.append(f"evidence run: {observed}/{expected_records} records")
    return manifest, hashes


def check_evaluation(results, run, data, source, manifest, trace_hashes, questions, pending):
    if not (results / "status.json").exists():
        pending.append("independent evidence evaluation is not complete")
        return
    status = read_json(results / "status.json")
    require(manifest is not None and status["run_identity_hash"] == manifest["identity_hash"], "Evaluation references a foreign run")
    check_hash(source / "evaluate.py", status["evaluator_sha256"])
    check_hash(source / "audit_data.py", status["parser_sha256"])
    check_hash(run / "manifest.json", status["run_manifest_sha256"])
    check_hash(run / "status.json", status["run_status_sha256"])
    check_hash_map(data, status["input_hashes"], {"corpus.jsonl", "questions.jsonl", "metadata.jsonl", "truth.jsonl", "specification.json"})
    check_hash_map(results, status["output_hashes"], {"per_record.csv", "feasibility.csv"})
    require(set(status["trace_sha256"]) <= set(trace_hashes), "Evaluation contains unknown trace references")
    for name, expected in status["trace_sha256"].items():
        safe_relative(name)
        require(trace_hashes[name] == expected, "Evaluated trace hash differs")
    evaluated_qids = {read_json(run / "traces" / name)["qid"] for name in status["trace_sha256"]}
    ids = {config["config_id"] for config in manifest["configurations"]}
    rows = list(read_csv(results / "per_record.csv"))
    exact_pairs(rows, ("qid", "config_id"), {(q, c) for q in evaluated_qids for c in ids}, "Evaluation")
    require(status["observed_records"] == len(rows) and status["observed_tasks"] == len(evaluated_qids) and status["expected_tasks"] == len(questions) and status["configurations"] == len(ids), "Evaluation denominator differs")
    feasibility = list(read_csv(results / "feasibility.csv"))
    exact_pairs(feasibility, ("qid", "packing", "budget"), {(q, p, str(b)) for q in evaluated_qids for p in ("prefix", "whole", "window") for b in (256, 512, 1024, 2048)}, "Feasibility")
    if status["status"] == "complete":
        require(status["trace_sha256"] == trace_hashes and evaluated_qids == set(questions), "Complete evaluation omits traces")
    else:
        pending.append("independent evidence evaluation is partial")


def check_auxiliary_manifest(directory, data, run, source, pending, label):
    if not (directory / "manifest.json").exists():
        pending.append(f"{label} run has not started")
        return None, None
    manifest = read_json(directory / "manifest.json")
    identity = check_identity(manifest)
    check_hash_map(data, identity["data"], DATA_FILES)
    status = read_json(directory / "status.json") if (directory / "status.json").exists() else None
    if status is None or status.get("status") != "complete":
        pending.append(f"{label} run is not complete")
    if status is not None:
        require(status["identity_hash"] == manifest["identity_hash"], f"{label} status identity differs")
    return manifest, status


def check_answers(directory, data, run, source, plan, questions, metadata, pending):
    manifest, status = check_auxiliary_manifest(directory, data, run, source, pending, "answer")
    if manifest is None:
        return
    identity = manifest["identity"]
    check_hash(run / "manifest.json", identity["inference_manifest_sha256"])
    check_hash_map(source, identity["code_sha256"], {"downstream.py", "evaluate.py", "audit_data.py", "protocol.py"})
    check_model_identity(identity["model_snapshot"])
    require(identity["model_snapshot"]["model"] == identity["model"] and
            identity["model_snapshot"]["sha"] == identity["revision"], "Answer model snapshot identity differs from its declaration")
    require(identity["model"] == plan["downstream"]["model"] and identity["revision"] == plan["downstream"]["revision"], "Answer model differs from plan")
    groups, qids = identity["worlds"], identity["questions"]
    require(len(groups) == len(set(groups)) == plan["downstream"]["test_worlds"], "Answer-world count differs")
    require(len(qids) == len(set(qids)) and set(qids) == {qid for qid, meta in metadata.items() if meta["group_id"] in groups}, "Answer questions omit world variants")
    require(all(metadata[qid]["split"] == "test" for qid in qids), "Answer selection contains development questions")
    require(set(identity["input_traces_sha256"]) == set(qids), "Answer trace set differs")
    for qid, expected in identity["input_traces_sha256"].items():
        check_hash(run / "traces" / (digest(qid)[:24] + ".json.gz"), expected)
    if status is None or status.get("status") != "complete":
        return
    conditions = set(identity["conditions"]) | {"closed_book", "no_support"}
    require(len(identity["conditions"]) == len(plan["downstream"]["evidence_conditions"]), "Answer evidence-condition count differs")
    frozen_configs = {row["config_id"]: row for row in read_json(run / "manifest.json")["configurations"]}
    require(all(frozen_configs.get(config["config_id"]) == config for config in identity["conditions"].values()), "Answer conditions differ from the frozen evidence matrix")
    expected_pairs = {(qid, condition) for qid in qids for condition in conditions}
    expected_names = {f"{qid}__{condition}.json" for qid, condition in expected_pairs}
    check_hash_map(directory / "responses", status["response_files"], expected_names)
    require({p.name for p in (directory / "responses").iterdir()} == expected_names, "Unexpected response files")
    responses = [read_json(directory / "responses" / name) for name in sorted(expected_names)]
    exact_pairs(responses, ("qid", "condition"), expected_pairs, "Answer")
    for row in responses:
        require(row["identity_hash"] == manifest["identity_hash"] and row["group_id"] == metadata[row["qid"]]["group_id"], "Answer record identity differs")
        require(isinstance(row["response"], str) and isinstance(row["messages"], list) and row["messages"], "Missing answer output/prompt")
    require(status["expected_answers"] == status["observed_answers"] == len(expected_pairs) and status["independent_worlds"] == len(groups), "Answer status denominator differs")
    check_hash_map(directory, status["output_hashes"], {"per_answer.csv", "summary.csv"})
    exact_pairs(read_csv(directory / "per_answer.csv"), ("qid", "condition"), expected_pairs, "Answer CSV")
    exact_pairs(read_csv(directory / "summary.csv"), ("condition",), {(c,) for c in conditions}, "Answer summary")


def check_timing(directory, data, run, source, plan, metadata, pending):
    manifest, status = check_auxiliary_manifest(directory, data, run, source, pending, "online timing")
    if manifest is None:
        return
    identity = manifest["identity"]
    for filename, field in (("backend.py", "backend_sha256"), ("protocol.py", "protocol_sha256"),
                            ("timing.py", "timing_code_sha256"), ("downstream.py", "downstream_code_sha256")):
        check_hash(source / filename, identity[field])
    check_hash(run / "manifest.json", identity["inference_manifest"])
    qids, groups, configurations = identity["qids"], identity["groups"], identity["configurations"]
    planned = plan["online_timing"]
    require(len(qids) == len(set(qids)) == len(groups) == len(set(groups)) == planned["questions"], "Timing selection count differs")
    require({metadata[qid]["group_id"] for qid in qids} == set(groups) and all(metadata[qid]["split"] == "test" for qid in qids), "Timing world/split references differ")
    require(len(configurations) == planned["configurations"] and identity["use_result_cache"] is False and identity["repetitions"] == planned["steady_repetitions_per_question_configuration"], "Timing protocol differs")
    frozen_configs = {row["config_id"]: row for row in read_json(run / "manifest.json")["configurations"]}
    require(all(frozen_configs.get(config["config_id"]) == config for config in configurations.values()), "Timing configurations differ from evidence matrix")
    require(set(identity["diagnostic_trace_hashes"]) == set(qids), "Timing diagnostic trace set differs")
    diagnostic_deliveries = {}
    for qid, expected_hash in identity["diagnostic_trace_hashes"].items():
        path = run / "traces" / (digest(qid)[:24] + ".json.gz")
        check_hash(path, expected_hash)
        records = {row["configuration"]["config_id"]: row for row in read_json(path)["configurations"]}
        for condition, config in configurations.items():
            chunks = records[config["config_id"]]["final_context"]["chunks"]
            diagnostic_deliveries[qid, condition] = digest([
                (chunk["chunk_id"], chunk["source_token_start"], chunk["source_token_end"], chunk["token_ids"])
                for chunk in chunks])
    if status is None or status.get("status") != "complete":
        return
    check_hash(directory / "requests.jsonl", status["requests_sha256"])
    check_hash(directory / "summary.csv", status["summary_sha256"])
    rows = list(read_jsonl(directory / "requests.jsonl"))
    expected = {(qid, condition, phase, repeat) for qid in qids for condition in configurations
                for phase, count in (("first_pass", 1), ("steady", identity["repetitions"])) for repeat in range(count)}
    exact_pairs(rows, ("qid", "condition", "phase", "repeat"), expected, "Timing request")
    require(status["requests"] == len(expected) and status["worlds"] == len(groups) and status["warmup_requests_excluded"] == len(configurations) * planned["warmup_requests_per_configuration"], "Timing status denominator differs")
    for row in rows:
        provenance = row["timing_provenance"]
        require(row["identity_hash"] == manifest["identity_hash"] and row["group_id"] == metadata[row["qid"]]["group_id"], "Timing record identity differs")
        require(provenance["scope"] == "independent_live_request" and not provenance["query_cache_hit"] and not provenance["rerank_cache_hit"] and provenance["offline_index_and_model_loading_excluded"], "Timed request reused a result or loaded a model")
        require(isinstance(row["latency_ms"], (int, float)) and math.isfinite(row["latency_ms"]) and row["latency_ms"] >= 0, "Invalid measured latency")
        require(valid_hash(row["final_delivery_sha256"]) and isinstance(row["same_delivery_as_diagnostic"], bool), "Invalid online delivery identity")
        same_delivery = row["final_delivery_sha256"] == diagnostic_deliveries[row["qid"], row["condition"]]
        require(row["same_delivery_as_diagnostic"] == same_delivery, "Online/diagnostic delivery comparison differs")
    exact_pairs(read_csv(directory / "summary.csv"), ("phase", "condition"), {(p, c) for p in ("first_pass", "steady") for c in configurations}, "Timing summary")


def check_optional_analysis(results, source):
    path = results / "analysis.json"
    if path.exists():
        report = read_json(path)
        check_hash(source / "analyze.py", report["analysis_code_sha256"])
        check_hash(source / "study_plan.json", report["study_plan_sha256"])
        check_hash(results / "per_record.csv", report["evaluated_per_record_sha256"])
        if "output_hashes" in report:
            check_hash_map(results, report["output_hashes"])
        auxiliary = report.get("auxiliary_runs", {})
        if auxiliary.get("answers", {}).get("status") == "complete":
            check_hash(results / "answers/per_answer.csv", auxiliary["answers"]["per_answer_sha256"])
        if auxiliary.get("timing", {}).get("status") == "complete":
            check_hash(results / "timing/requests.jsonl", auxiliary["timing"]["requests_sha256"])
    path = results / "figures/manifest.json"
    if path.exists():
        report = read_json(path)
        check_hash_map(results, report["source_csv_sha256"])
        check_hash_map(results / "figures", report["figure_sha256"])
        if "code_sha256" in report:
            check_hash_map(source, report["code_sha256"])
        if "figures_code_sha256" in report:
            check_hash(source / "figures.py", report["figures_code_sha256"])


def verify(root=ROOT, data=None, run=None, results=None, allow_in_progress=False):
    root = Path(root).resolve()
    source = root / "experiments/strengthening"
    data = Path(data).resolve() if data else source / "data/strengthening_v1"
    run = Path(run).resolve() if run else root / "experiments/runs/strengthening_v1"
    results = Path(results).resolve() if results else source / "results/strengthening_v1"
    pending = []
    specification, plan, corpus, questions, metadata = check_dataset(root, data, source)
    manifest, trace_hashes = check_run(run, source, data, specification, corpus, questions, pending)
    check_evaluation(results, run, data, source, manifest, trace_hashes, questions, pending)
    check_answers(results / "answers", data, run, source, plan, questions, metadata, pending)
    check_timing(results / "timing", data, run, source, plan, metadata, pending)
    check_optional_analysis(results, source)
    return {"status": "PENDING" if pending else "PASS", "accepted": not pending or allow_in_progress,
            "pending": pending, "worlds": specification["counts"]["worlds"], "questions": len(questions),
            "verified_trace_files": len(trace_hashes), "expected_records": manifest["expected_records"] if manifest else None,
            "model_cache_required": False, "human_review": "not established by this integrity check",
            "scope": "Recorded file identities, exact record sets and original-source references; not a replacement for semantic or human evaluation."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--results", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--allow-in-progress", action="store_true", help="Accept pending runs without claiming completion")
    mode.add_argument("--require-complete", action="store_true", help="Require all three runs and evaluation complete (default)")
    args = parser.parse_args(argv)
    try:
        report = verify(args.root, args.data, args.run, args.results, args.allow_in_progress)
    except (ValueError, KeyError, TypeError, OSError, gzip.BadGzipFile) as error:
        print(json.dumps({"status": "FAIL", "accepted": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
