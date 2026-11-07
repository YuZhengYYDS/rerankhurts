"""Independent B2048 answer follow-up; frozen experiments are never overwritten.

prepare validates original BERT intervals without Qwen weights. baseline512 and
smoke each run two isolated repeats. run creates the exact 120-by-two matrix.
analyze and verify use saved answers, never GPU inference. All model loading is
local-only; downloading is a separate handoff step.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
import copy
import csv
from datetime import datetime, timezone
import fcntl
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

from .protocol import Config, canonical_json, digest, file_hash, load_json, read_jsonl, save_json
from .downstream import MODEL, REVISION, SEED, SYSTEM, build_messages, parse_answer, score_answer, trace_path
from .evaluate import encode_corpus, parse_corpus_claims, score_evidence, verify_final_context

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "experiments/strengthening/data/strengthening_v1"
RUN = ROOT / "experiments/runs/strengthening_v1"
BASELINE = ROOT / "experiments/strengthening/results/strengthening_v1/answers/manifest.json"
WORK = ROOT / "build/answer2048_120"
OUTPUT = ROOT / "experiments/strengthening/results/strengthening_v1/answers_2048_120"
CONDITIONS = {"m3_off_prefix": Config(budget=2048),
              "m3_post_prefix": Config(budget=2048, cap=2, cap_stage="post")}
EXPECTED_CONFIG_IDS = ("dense_p64_m3_off_b2048_prefix_prefix512_dprefix512_polnone",
                       "dense_p64_m3_post2_b2048_prefix_prefix512_dprefix512_polnone")
BASELINE_CONFIG = Config(budget=512, cap=2, cap_stage="post")
DATA_NAMES = ("corpus.jsonl", "questions.jsonl", "metadata.jsonl", "truth.jsonl", "claims.jsonl")
ORIGINAL_CODE = ("downstream.py", "evaluate.py", "audit_data.py", "protocol.py")
STATISTICS = {"direction": "post_minus_off", "unit": "world", "within_world": "mean of two URL variants",
              "bootstrap_repetitions": 5000, "permutation_repetitions": 20000, "seed": SEED,
              "bootstrap_strata": "generation seed", "multiplicity": "BH within four-endpoint follow-up family",
              "endpoints": ["complete_correct", "complete_grounded_correct", "field_accuracy", "grounded_field_accuracy"]}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def unique(rows, key):
    result = {r[key]: r for r in rows}
    require(len(result) == len(rows), "Duplicate " + key)
    return result


def save_once(path, value):
    if path.exists():
        require(load_json(path) == value, "Existing frozen follow-up file differs: " + str(path))
    else:
        save_json(path, value)


def write_csv(path, rows):
    rows = list(rows)
    require(bool(rows), "Refusing to write an empty table")
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def compare_evidence_csv(path, rows):
    with path.open(encoding="utf-8", newline="") as stream:
        actual = list(csv.DictReader(stream))
    require(len(actual) == len(rows), "Evidence table denominator differs")
    for old, new in zip(actual, rows):
        require(set(old) == set(new), "Evidence schema differs")
        for key, value in new.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                require(math.isclose(float(old[key]), float(value), abs_tol=1e-12, rel_tol=1e-12), "Evidence value differs: " + key)
            else:
                require(old[key] == str(value), "Evidence metadata differs: " + key)


def validate_paths(args):
    for name in ("baseline_manifest", "data", "run", "work", "output"):
        setattr(args, name, getattr(args, name).resolve())
    for writable in (args.work, args.output):
        require(writable != ROOT and writable not in (args.data, args.run, args.baseline_manifest.parent), "Unsafe output directory")
        require(not any(writable.is_relative_to(p) for p in (args.data, args.run, args.baseline_manifest.parent, ROOT / "paper")),
                "Follow-up output would enter a protected original directory")
    require(args.work != args.output and not args.work.is_relative_to(args.output) and not args.output.is_relative_to(args.work),
            "Working checks and formal results must be separate")


@contextmanager
def writer_lock(directory):
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".writer.lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("Another writer owns " + str(directory)) from exc
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def protect_originals(args):
    """Check frozen membership as well as bytes; new modules live outside it."""
    path = args.work / "protected_originals.json"
    if not path.exists():
        source = ROOT / "MANIFEST.json"
        require(source.is_file(), "Original delivery MANIFEST is required for the protection snapshot")
        files = load_json(source)
        files["MANIFEST.json"] = {"bytes": source.stat().st_size, "sha256": file_hash(source)}
        snapshot = {"scope": "All files in the delivered original MANIFEST plus that manifest; newly added follow-up files are separate.",
                    "files": files}
        for name, entry in files.items():
            p = ROOT / name
            require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(ROOT), "Missing/unsafe frozen file: " + name)
            require(p.stat().st_size == entry["bytes"] and file_hash(p) == entry["sha256"], "Frozen original changed: " + name)
        save_once(path, snapshot)
    snapshot = load_json(path)
    for name, entry in snapshot["files"].items():
        p = ROOT / name
        require(p.is_file() and p.resolve().is_relative_to(ROOT) and not p.is_symlink(), "Missing/unsafe original: " + name)
        require(p.stat().st_size == entry["bytes"] and file_hash(p) == entry["sha256"], "Protected original changed: " + name)
    # No additional files may silently enter the original answer or main run trees.
    for directory in (args.baseline_manifest.parent, args.run):
        expected = {str(ROOT / n) for n in snapshot["files"] if (ROOT / n).is_relative_to(directory)}
        actual = {str(p) for p in directory.rglob("*") if p.is_file()}
        require(expected == actual, "Original directory membership differs: " + str(directory))
    return {"status": "PASS", "files": len(snapshot["files"]), "snapshot_sha256": file_hash(path)}


def baseline_checks(args):
    manifest = load_json(args.baseline_manifest)
    identity = manifest["identity"]
    require(digest(identity) == manifest["identity_hash"], "Original answer identity is inconsistent")
    require(identity["model"] == MODEL and identity["revision"] == REVISION and identity["seed"] == SEED, "Unexpected original answer model")
    require(identity["system_prompt"] == SYSTEM and identity["max_new_tokens"] == 256 and identity["do_sample"] is False,
            "Original answer protocol differs")
    qids, worlds = identity["questions"], identity["worlds"]
    require(len(qids) == len(set(qids)) == 120 and len(worlds) == len(set(worlds)) == 60, "Original sample size differs")
    for name, expected in identity["data"].items():
        require(name in DATA_NAMES and file_hash(args.data / name) == expected, "Original data hash differs: " + name)
    require(set(identity["data"]) == set(DATA_NAMES), "Original data file set differs")
    require(set(identity["code_sha256"]) == set(ORIGINAL_CODE), "Original answer code set differs")
    for name, expected in identity["code_sha256"].items():
        require(file_hash(Path(__file__).with_name(name)) == expected, "Original answer code differs: " + name)
    run_manifest = load_json(args.run / "manifest.json")
    require(file_hash(args.run / "manifest.json") == identity["inference_manifest_sha256"], "Original inference manifest differs")
    require(digest(run_manifest["identity"]) == run_manifest["identity_hash"], "Original inference identity is inconsistent")
    for name, expected in run_manifest["identity"]["code_sha256"].items():
        require(file_hash(Path(__file__).with_name(name)) == expected, "Original inference code differs: " + name)
    require(file_hash(Path(__file__).with_name("study_plan.json")) == run_manifest["identity"]["study_plan_sha256"], "Original study plan differs")
    old = args.baseline_manifest.parent
    status = load_json(old / "status.json")
    require(status["status"] == "complete" and status["identity_hash"] == manifest["identity_hash"] and
            status["expected_answers"] == status["observed_answers"] == 720, "Original answers are incomplete")
    expected_names = {q + "__" + c + ".json" for q in qids for c in (*identity["conditions"], "closed_book", "no_support")}
    require(set(status["response_files"]) == expected_names == {p.name for p in (old / "responses").iterdir()}, "Original response matrix differs")
    for name, expected in status["response_files"].items():
        require(file_hash(old / "responses" / name) == expected, "Original response differs: " + name)
    for name, expected in status["output_hashes"].items():
        require(file_hash(old / name) == expected, "Original answer table differs: " + name)
    return manifest, run_manifest


def load_bundle(args):
    baseline, run_manifest = baseline_checks(args)
    identity = baseline["identity"]
    metadata = unique(read_jsonl(args.data / "metadata.jsonl"), "qid")
    questions = unique(read_jsonl(args.data / "questions.jsonl"), "qid")
    truth = unique(read_jsonl(args.data / "truth.jsonl"), "group_id")
    corpus = unique(read_jsonl(args.data / "corpus.jsonl"), "chunk_id")
    qids = sorted(identity["questions"])
    tasks = [metadata[q] for q in qids]
    require(all(t["split"] == "test" for t in tasks), "Development task entered follow-up")
    require({t["group_id"] for t in tasks} == set(identity["worlds"]), "World list differs")
    require(Counter(t["seed"] for t in tasks) == {20261002: 40, 20261003: 40, 20261004: 40}, "Seed quotas differ")
    grouped = defaultdict(list)
    for task in tasks:
        grouped[task["group_id"]].append(task)
    require(all(len(g) == 2 and {t["variant_id"] for t in g} == {"low_concentration", "high_concentration"}
                for g in grouped.values()), "World has missing or duplicate URL variant")
    sample_worlds = {min(t["group_id"] for t in tasks if t["seed"] == seed) for seed in (20261002, 20261003, 20261004)}
    sample_qids = sorted(t["qid"] for t in tasks if t["group_id"] in sample_worlds)
    require(len(sample_qids) == 6, "Invalid baseline/smoke selection")
    require(tuple(c.config_id for c in CONDITIONS.values()) == EXPECTED_CONFIG_IDS, "Wrong follow-up configurations")
    finals, trace_hashes, inventory = {}, {}, []
    for task in tasks:
        qid = task["qid"]
        path = trace_path(args.run, qid)
        trace_hashes[qid] = file_hash(path)
        require(trace_hashes[qid] == identity["input_traces_sha256"][qid], "Original trace differs: " + qid)
        trace = load_json(path)
        require(trace["identity_hash"] == run_manifest["identity_hash"] and trace["qid"] == qid, "Foreign trace")
        require(all(trace[k] == v for k, v in questions[qid].items()), "Trace public question differs")
        records = unique([dict(row, id=row["configuration"]["config_id"]) for row in trace["configurations"]], "id")
        require(set(records) == {c["config_id"] for c in run_manifest["configurations"]}, "Trace configuration set differs")
        hashes = {}
        for condition, config in CONDITIONS.items():
            record = records[config.config_id]
            require(record["configuration"] == config.record() and record["qid"] == qid and
                    record["collection_id"] == task["collection_id"], "Wrong evidence configuration/task")
            final = record["final_context"]
            require(final["budget"] == 2048 and final["used_tokens"] <= 2048, "Wrong evidence budget")
            finals[qid, condition] = final
            hashes[config.config_id] = digest(final)
        if qid in sample_qids:
            record = records[BASELINE_CONFIG.config_id]
            require(record["configuration"] == BASELINE_CONFIG.record(), "Wrong baseline512 configuration")
            finals[qid, "baseline512"] = record["final_context"]
        inventory.append({**{k: task[k] for k in ("qid", "group_id", "seed", "variant_id", "scenario", "policy", "template_family")},
                          "question": questions[qid]["question"], "trace": str(path.relative_to(ROOT)),
                          "trace_sha256": trace_hashes[qid], "context_sha256": hashes})
    return {"baseline": baseline, "run_manifest": run_manifest, "qids": qids, "tasks": inventory,
            "metadata": metadata, "questions": questions, "truth": truth, "corpus": corpus,
            "finals": finals, "trace_hashes": trace_hashes, "sample_qids": sample_qids, "sample_worlds": sorted(sample_worlds)}


def model_specs(bundle):
    return {"answer": bundle["baseline"]["identity"]["model_snapshot"],
            "budget_tokenizer": bundle["run_manifest"]["identity"]["models"]["tokenizer"]}


def model_path(spec):
    return ROOT / ".cache/models" / spec["model"].replace("/", "--") / spec["sha"]


def check_snapshots(bundle):
    for role, spec in model_specs(bundle).items():
        directory = model_path(spec)
        require(directory.is_dir(), "Missing pinned snapshot: " + str(directory))
        actual_names = {p.relative_to(directory).as_posix() for p in directory.rglob("*")
                        if p.is_file() and ".cache" not in p.relative_to(directory).parts}
        require(actual_names == set(spec["files"]), "Unexpected snapshot membership: " + role)
        for name, expected in spec["files"].items():
            require(file_hash(directory / name) == expected, "Pinned model file differs: " + role + "/" + name)
    return model_specs(bundle)


def load_budget_tokenizer(bundle):
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path(model_specs(bundle)["budget_tokenizer"]), local_files_only=True, use_fast=True)
    require(tokenizer.is_fast and tokenizer.sep_token_id == 102, "Expected pinned fast BERT tokenizer")
    return tokenizer


def evidence(bundle, qid, final, cache=None):
    meta = bundle["metadata"][qid]
    corpus = {c["chunk_id"]: bundle["corpus"][c["chunk_id"]] for c in final["chunks"]}
    require(all(c["collection_id"] == meta["collection_id"] for c in corpus.values()), "Cross-collection delivery")
    if cache is not None:
        for cid, c in corpus.items():
            if cid not in cache:
                cache.update(parse_corpus_claims({cid: c}, bundle["truth"][meta["group_id"]]))
    return score_evidence(final["chunks"], corpus, bundle["truth"][meta["group_id"]],
                          dict(meta, allowed_url_prefixes=bundle["questions"][qid]["allowed_url_prefixes"]), cache)


def verify_intervals(bundle, tokenizer):
    wanted = sorted({c["chunk_id"] for final in bundle["finals"].values() for c in final["chunks"]})
    encoded = {}
    for start in range(0, len(wanted), 128):
        encoded.update(encode_corpus({cid: bundle["corpus"][cid] for cid in wanted[start:start + 128]}, tokenizer))
    for (qid, condition), final in bundle["finals"].items():
        verify_final_context(final, bundle["corpus"], encoded, tokenizer.sep_token_id)
        expected_budget = 512 if condition == "baseline512" else 2048
        require(final["budget"] == expected_budget and final["separator_tokens"] == max(0, len(final["chunks"]) - 1), "Context budget metadata differs")
        for c in final["chunks"]:
            require(c["url"] == bundle["corpus"][c["chunk_id"]]["url"] and
                    c["delivered_tokens"] == len(c["token_ids"]) == c["source_token_end"] - c["source_token_start"] and
                    c["chunk_tokens"] == len(encoded[c["chunk_id"]]["input_ids"]) and
                    c["partial"] == (c["source_token_start"] > 0 or c["source_token_end"] < c["chunk_tokens"]), "Invalid delivery metadata")
    return {"status": "PASS", "formal_contexts": 240, "baseline_contexts": 6, "encoded_original_chunks": len(encoded),
            "checks": ["original source text", "token ids", "token and character intervals", "SEP stream", "budget", "URL and tenant", "partial metadata"]}


def plan_for(args, bundle):
    return {"version": "answer2048_120_followup_v1", "scope": "Additional controlled synthetic answer experiment; original study_plan unchanged",
            "questions": bundle["qids"], "worlds": sorted(bundle["baseline"]["identity"]["worlds"]),
            "tasks": bundle["tasks"], "conditions": {k: c.record() for k, c in CONDITIONS.items()},
            "condition_order": list(CONDITIONS), "task_order": "qid ascending", "formal_answers": 240,
            "baseline_manifest_sha256": file_hash(args.baseline_manifest), "inference_manifest_sha256": file_hash(args.run / "manifest.json"),
            "data_sha256": {n: file_hash(args.data / n) for n in DATA_NAMES}, "trace_sha256": bundle["trace_hashes"],
            "model_snapshots": model_specs(bundle), "system_prompt": SYSTEM,
            "generation": {"seed": SEED, "device": "cuda", "dtype": "float16", "attention": "sdpa", "do_sample": False,
                           "max_new_tokens": 256, "batch_size": 1, "deterministic_algorithms": True, "cudnn_benchmark": False,
                           "allow_tf32": False, "pad_token": "tokenizer.eos_token_id", "add_special_tokens": False,
                           "add_generation_prompt": True, "local_files_only": True},
            "statistics": STATISTICS, "sample_rule": "Smallest group_id within each seed; retain both URL variants, without reading outcomes",
            "check_questions": bundle["sample_qids"], "check_worlds": bundle["sample_worlds"],
            "baseline_repeats": 2, "smoke_repeats": 2, "formal_repeats": 1,
            "source_paths": {"data": str(args.data), "run": str(args.run), "baseline_manifest": str(args.baseline_manifest)}}


def prepare(args, bundle):
    args.work.mkdir(parents=True, exist_ok=True)
    with writer_lock(args.work):
        protected = protect_originals(args)
        check_snapshots(bundle)
        audit = verify_intervals(bundle, load_budget_tokenizer(bundle))
        plan = plan_for(args, bundle)
        save_once(args.work / "followup_plan.json", plan)
        # The earlier handoff inventory remains a separate immutable input audit.
        save_once(args.work / "prepared_tasks_120.json", {"tasks": bundle["tasks"], "task_count": 120, "world_count": 60})
        rows, cache = [], {}
        for task in bundle["tasks"]:
            qid = task["qid"]
            for condition in CONDITIONS:
                final = bundle["finals"][qid, condition]
                scored = evidence(bundle, qid, final, cache)
                rows.append({**{k: task[k] for k in ("qid", "group_id", "seed", "variant_id", "scenario", "policy", "template_family")},
                             "condition": condition, "config_id": CONDITIONS[condition].config_id,
                             "context_tokens": final["used_tokens"], "final_context_sha256": digest(final),
                             **{k: v for k, v in scored.items() if k != "delivered_claims" and not isinstance(v, list)}})
        indexed = {(r["qid"], r["condition"]): r for r in rows}
        require(all(indexed[q, "m3_off_prefix"]["G_final"] == indexed[q, "m3_post_prefix"]["G_final"] for q in bundle["qids"]),
                "Subset designated-page outcomes differ; inspect inputs")
        evidence_path = args.work / "evidence_2048_subset.csv"
        if evidence_path.exists():
            compare_evidence_csv(evidence_path, rows)
        else:
            write_csv(evidence_path, rows)
        report = {"status": "PASS", "plan_sha256": digest(plan), "evidence_sha256": file_hash(evidence_path),
                  "interval_audit": audit, "protected_originals": protected,
                  "evidence_counts": {c: {k: sum(float(r[k]) for r in rows if r["condition"] == c)
                                          for k in ("G_final", "U_sim")} for c in CONDITIONS}}
        save_once(args.work / "prepare_audit.json", report)
        return report


def require_prepared(args, bundle):
    plan = load_json(args.work / "followup_plan.json")
    require(plan == plan_for(args, bundle) and plan["statistics"] == STATISTICS, "Prepared follow-up plan changed")
    audit = load_json(args.work / "prepare_audit.json")
    require(audit["status"] == "PASS" and audit["plan_sha256"] == digest(plan) and
            audit["evidence_sha256"] == file_hash(args.work / "evidence_2048_subset.csv"), "Prepare audit is missing/stale")
    return plan


def generation_code_hashes():
    return {name: file_hash(Path(__file__).with_name(name)) for name in (*ORIGINAL_CODE, "downstream_2048.py")}


def configure_offline():
    # Set these before importing HF/Transformers, in every new process.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")


def gpu_environment(torch):
    require(platform.python_version_tuple()[:2] == ("3", "11"), "Formal execution requires locked Python3.11")
    expected = {"torch": "2.8.0+cu128", "transformers": "4.57.1", "numpy": "2.2.6", "pandas": "2.3.3",
                "sentence-transformers": "5.1.2", "huggingface-hub": "0.36.2", "hf-xet": "1.6.0"}
    packages = {n: importlib.metadata.version(n) for n in expected}
    require(packages == expected, "Installed packages differ from the locked environment: " + str(packages))
    require(torch.cuda.is_available() and torch.cuda.device_count() == 1, "One explicitly selected CUDA GPU is required")
    require(os.environ.get("CUDA_VISIBLE_DEVICES") in ("0", "1") and os.environ.get("CUBLAS_WORKSPACE_CONFIG") == ":4096:8" and
            os.environ.get("PYTHONHASHSEED") == "20260924" and os.environ.get("TOKENIZERS_PARALLELISM") == "false", "Task environment differs")
    command = ["nvidia-smi", "--query-gpu=index,uuid,name,driver_version,compute_cap", "--format=csv,noheader,nounits"]
    lines = list(csv.reader(subprocess.check_output(command, text=True).splitlines(), skipinitialspace=True))
    selected = next((r for r in lines if r[0] == os.environ["CUDA_VISIBLE_DEVICES"]), None)
    require(selected is not None, "Selected physical GPU not found")
    return {"python": platform.python_version(), "platform": platform.platform(), "packages": packages,
            "cuda_runtime": torch.version.cuda, "cudnn_version": torch.backends.cudnn.version(),
            "gpu_name": torch.cuda.get_device_name(0), "gpu_uuid": selected[1], "driver": selected[3],
            "compute_capability": list(torch.cuda.get_device_capability(0)), "physical_gpu": selected[0],
            "CUDA_VISIBLE_DEVICES": os.environ["CUDA_VISIBLE_DEVICES"], "PYTHONHASHSEED": os.environ["PYTHONHASHSEED"],
            "CUBLAS_WORKSPACE_CONFIG": os.environ["CUBLAS_WORKSPACE_CONFIG"], "TOKENIZERS_PARALLELISM": os.environ["TOKENIZERS_PARALLELISM"],
            "HF_HUB_OFFLINE": os.environ["HF_HUB_OFFLINE"], "TRANSFORMERS_OFFLINE": os.environ["TRANSFORMERS_OFFLINE"]}


def load_runtime(bundle):
    configure_offline()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    environment = gpu_environment(torch)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_path(model_specs(bundle)["answer"]), local_files_only=True)
    tokenizer.pad_token_id = tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(model_path(model_specs(bundle)["answer"]), local_files_only=True,
                                                torch_dtype=torch.float16, attn_implementation="sdpa").to("cuda").eval()
    torch.cuda.synchronize()
    effective = copy.deepcopy(model.generation_config)
    effective.update(do_sample=False, max_new_tokens=256, pad_token_id=tokenizer.pad_token_id)
    require(model.config._attn_implementation == "sdpa", "Unexpected attention implementation")
    return {"torch": torch, "model": model, "tokenizer": tokenizer, "environment": environment,
            "generation_config": effective.to_dict(), "model_config": model.config.to_dict(),
            "load_seconds": time.perf_counter() - start}


def make_identity(args, bundle, plan, runtime, stage):
    qids = bundle["qids"] if stage == "run" else bundle["sample_qids"]
    conditions = {"m3_post_prefix": BASELINE_CONFIG.record()} if stage == "baseline512" else {k: c.record() for k, c in CONDITIONS.items()}
    contexts = {q: {c: digest(bundle["finals"][q, "baseline512" if stage == "baseline512" else c]) for c in conditions} for q in qids}
    tasks = [t for t in bundle["tasks"] if t["qid"] in qids]
    return {"kind": "answer2048_120_followup_v1", "stage": stage, "questions": qids,
            "worlds": sorted({t["group_id"] for t in tasks}), "tasks": tasks, "conditions": conditions,
            "task_order": "qid ascending", "condition_order": list(conditions), "repeats": 1 if stage == "run" else 2,
            "baseline_manifest_sha256": file_hash(args.baseline_manifest), "inference_manifest_sha256": file_hash(args.run / "manifest.json"),
            "data_sha256": plan["data_sha256"], "trace_sha256": {q: bundle["trace_hashes"][q] for q in qids},
            "context_sha256": contexts, "model": model_specs(bundle)["answer"], "budget_tokenizer": model_specs(bundle)["budget_tokenizer"],
            "system_prompt": SYSTEM, "generation": plan["generation"], "effective_generation_config": runtime["generation_config"],
            "chat_template_sha256": digest(runtime["tokenizer"].chat_template), "code_sha256": generation_code_hashes(),
            "environment": runtime["environment"], "plan_sha256": digest(plan)}


def prompt_for(bundle, qid, final, tokenizer):
    meta = bundle["metadata"][qid]
    messages = build_messages(bundle["questions"][qid]["question"], meta["expected_keys"], final["chunks"])
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    encoded = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    return messages, prompt, encoded


def evaluate_response(bundle, qid, final, response, cache=None):
    meta = bundle["metadata"][qid]
    facts = [f for f in bundle["truth"][meta["group_id"]]["facts"] if f["fact_id"] in meta["required_fact_ids"]]
    ev = evidence(bundle, qid, final, cache)
    return score_answer(response, facts, ev["delivered_claims"], len(final["chunks"]))


def input_evidence(final):
    return [{"source_index": i, **{k: c[k] for k in ("chunk_id", "url", "char_start", "char_end", "source_token_start", "source_token_end")}}
            for i, c in enumerate(final["chunks"], 1)]


def validate_response(record, identity_hash, bundle, qid, condition, final, config, repeat, tokenizer=None, cache=None):
    meta = bundle["metadata"][qid]
    require(record["identity_hash"] == identity_hash and record["qid"] == qid and record["condition"] == condition and
            record["repeat"] == repeat and record["config_id"] == config["config_id"], "Foreign answer checkpoint")
    require(all(record[k] == meta[k] for k in ("group_id", "seed", "variant_id", "scenario", "policy", "template_family")), "Answer task metadata differs")
    require(record["input_trace_sha256"] == bundle["trace_hashes"][qid] and record["final_context_sha256"] == digest(final), "Answer context identity differs")
    require(record["input_evidence"] == input_evidence(final), "Answer evidence intervals differ")
    messages = build_messages(bundle["questions"][qid]["question"], meta["expected_keys"], final["chunks"])
    require(record["messages"] == messages and record["messages_sha256"] == digest(messages), "Answer prompt messages differ")
    require(record["generated_tokens"] == len(record["generated_token_ids"]) and record["generated_tokens_sha256"] == digest(record["generated_token_ids"]), "Answer token identity differs")
    require(0 < record["generated_tokens"] <= 256 and all(type(v) is int and v >= 0 for v in record["generated_token_ids"]),
            "Invalid generated token stream")
    require(record["hit_max_new_tokens"] == (record["generated_tokens"] == 256), "Generation length diagnostic differs")
    require(record["prompt_tokens"] == len(record["prompt_token_ids"]) and record["prompt_tokens_sha256"] == digest(record["prompt_token_ids"]), "Prompt token identity differs")
    require(record["parsed_json_object"] == (parse_answer(record["response"]) is not None), "JSON diagnostic differs")
    require(record["evaluation"] == evaluate_response(bundle, qid, final, record["response"], cache), "Saved answer score differs from original evaluator")
    require(isinstance(record["generation_ms"], (int, float)) and 0 <= record["generation_ms"] < float("inf"), "Invalid generation timing")
    if tokenizer is not None:
        _, prompt, encoded = prompt_for(bundle, qid, final, tokenizer)
        require(record["prompt_sha256"] == digest(prompt) and encoded["input_ids"][0].tolist() == record["prompt_token_ids"], "Actual prompt tokenization differs")
        require(tokenizer.decode(record["generated_token_ids"], skip_special_tokens=True) == record["response"], "Saved response differs from generated token IDs")
    return True


def response_location(directory, qid, condition):
    return directory / "responses" / f"{qid}__{condition}.json"


def checkpoint(path, identity_hash, produce, validate):
    """Validate before skipping or publishing; never regenerate a valid checkpoint."""
    if path.exists():
        record = load_json(path)
        require(record.get("identity_hash") == identity_hash, "Checkpoint belongs to a different generation identity")
        validate(record)
        return record, False
    record = produce()
    require(record.get("identity_hash") == identity_hash, "Producer returned a foreign identity")
    validate(record)
    save_json(path, record)
    return record, True


def stage_directory(args, stage):
    return args.output if stage == "run" else args.work / ("baseline512" if stage == "baseline512" else "smoke2048")


def selected_final(bundle, stage, qid, condition):
    return bundle["finals"][qid, "baseline512" if stage == "baseline512" else condition]


def collect_records(directory, manifest, bundle, tokenizer=None, allow_partial=False):
    identity = manifest["identity"]
    qids, conditions = identity["questions"], identity["conditions"]
    require(digest(identity) == manifest["identity_hash"], "Saved generation identity digest differs")
    expected_names = {f"{q}__{c}.json" for q in qids for c in conditions}
    records, cache = [], {}
    for repeat in range(identity["repeats"]):
        target = directory if identity["stage"] == "run" else directory / f"repeat_{repeat + 1}"
        response_dir = target / "responses"
        paths = sorted(response_dir.iterdir()) if response_dir.exists() else []
        if allow_partial:
            paths = [p for p in paths if not (p.name.endswith(".json.tmp") and p.name[:-4] in expected_names
                                              and p.is_file() and not p.is_symlink())]
        require(all(p.is_file() and not p.is_symlink() and p.name in expected_names for p in paths), "Unexpected response file")
        if not allow_partial:
            require({p.name for p in paths} == expected_names, "Incomplete exact response matrix")
        for path in paths:
            record = load_json(path)
            qid, condition = record["qid"], record["condition"]
            require(path.name == f"{qid}__{condition}.json" and qid in qids and condition in conditions, "Wrong response filename/identity")
            final = selected_final(bundle, identity["stage"], qid, condition)
            validate_response(record, manifest["identity_hash"], bundle, qid, condition, final,
                              conditions[condition], repeat, tokenizer, cache)
            records.append(record)
    require(len(records) == len({(r["qid"], r["condition"], r["repeat"]) for r in records}), "Duplicate response records")
    return records


def compare_repeats(records, identity):
    indexed = {(r["repeat"], r["qid"], r["condition"]): r for r in records}
    require(len(records) == len(identity["questions"]) * len(identity["conditions"]) * 2, "Incomplete repeat matrix")
    differences = []
    fields = ("messages", "prompt_sha256", "prompt_token_ids", "generated_token_ids", "response", "evaluation")
    for qid in identity["questions"]:
        for condition in identity["conditions"]:
            a, b = indexed[0, qid, condition], indexed[1, qid, condition]
            different = [key for key in fields if a[key] != b[key]]
            if different:
                differences.append({"qid": qid, "condition": condition, "fields": different})
    require(not differences, "Same-machine repeatability failed: " + json.dumps(differences))
    return {"status": "PASS", "same_machine_identical": True, "task_condition_pairs": len(records) // 2,
            "generations": len(records), "compared": list(fields), "timing_compared": False}


def check_stage_gate(args, stage):
    for gate in (("baseline512",) if stage == "smoke" else ("baseline512", "smoke2048") if stage == "run" else ()):
        directory = args.work / gate
        status, manifest, comparison = (load_json(directory / name) for name in ("status.json", "manifest.json", "comparison.json"))
        require(status["status"] == "complete" and comparison["status"] == "PASS", "Repeatability gate incomplete: " + gate)
        require(status["identity_hash"] == manifest["identity_hash"] and manifest["identity"]["code_sha256"] == generation_code_hashes(),
                "Repeatability gate belongs to different generation code")
        require(manifest["identity"]["plan_sha256"] == digest(load_json(args.work / "followup_plan.json")), "Repeatability plan differs")
        require(status["comparison_sha256"] == file_hash(directory / "comparison.json"), "Repeatability report changed")
        for name, expected in status["response_sha256"].items():
            require(file_hash(directory / name) == expected, "Gate response changed: " + name)


def require_gate_environment(args, identity, stage):
    gates = ("baseline512",) if stage == "smoke" else ("baseline512", "smoke2048") if stage == "run" else ()
    for gate in gates:
        prior = load_json(args.work / gate / "manifest.json")["identity"]
        require(prior["environment"] == identity["environment"] and
                prior["effective_generation_config"] == identity["effective_generation_config"] and
                prior["chat_template_sha256"] == identity["chat_template_sha256"],
                "Engineering checks used a different hardware/environment/generation configuration")


def generate_one(runtime, bundle, qid, condition, final, config, identity_hash, repeat, cache):
    torch, model, tokenizer = runtime["torch"], runtime["model"], runtime["tokenizer"]
    messages, prompt, encoded = prompt_for(bundle, qid, final, tokenizer)
    prompt_ids = encoded["input_ids"][0].tolist()
    require(len(prompt_ids) + 256 <= model.config.max_position_embeddings, "Prompt would exceed pinned model context length")
    encoded = encoded.to("cuda")
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    start = time.perf_counter()
    with torch.inference_mode():
        generated = model.generate(**encoded, do_sample=False, max_new_tokens=256, pad_token_id=tokenizer.pad_token_id)
    torch.cuda.synchronize()
    elapsed = (time.perf_counter() - start) * 1000
    ids = generated[0, encoded["input_ids"].shape[-1]:].tolist()
    response = tokenizer.decode(ids, skip_special_tokens=True)
    eos = runtime["generation_config"]["eos_token_id"]
    eos = eos if isinstance(eos, list) else [eos]
    meta = bundle["metadata"][qid]
    return {"identity_hash": identity_hash, **{k: meta[k] for k in ("qid", "group_id", "seed", "variant_id", "scenario", "policy", "template_family")},
            "condition": condition, "config_id": config["config_id"], "repeat": repeat,
            "input_trace_sha256": bundle["trace_hashes"][qid], "final_context_sha256": digest(final),
            "messages": messages, "messages_sha256": digest(messages), "prompt_sha256": digest(prompt),
            "prompt_tokens": len(prompt_ids), "prompt_token_ids": prompt_ids, "prompt_tokens_sha256": digest(prompt_ids),
            "response": response, "generated_tokens": len(ids), "generated_token_ids": ids, "generated_tokens_sha256": digest(ids),
            "generation_ms": elapsed, "peak_cuda_allocated_bytes": torch.cuda.max_memory_allocated(),
            "hit_max_new_tokens": len(ids) >= 256, "truncated_output": len(ids) >= 256 and bool(ids) and ids[-1] not in eos,
            "parsed_json_object": parse_answer(response) is not None, "input_evidence": input_evidence(final),
            "evaluation": evaluate_response(bundle, qid, final, response, cache), "generated_at_utc": now()}


def basic_tables(directory, records):
    # Generation summaries are derived only from raw saved responses. Inferential
    # tables are written later by the separately versioned analysis module.
    rows = []
    for r in records:
        row = {k: r[k] for k in ("qid", "group_id", "seed", "variant_id", "scenario", "policy", "template_family", "condition",
                                 "config_id", "prompt_tokens", "generated_tokens", "generation_ms", "hit_max_new_tokens", "truncated_output")}
        row.update({k: v for k, v in r["evaluation"].items() if k != "fields"})
        row["parsed_json_object"] = r["parsed_json_object"]
        rows.append(row)
    write_csv(directory / "per_answer.csv", rows)
    summaries = []
    for condition in CONDITIONS:
        values = [r for r in records if r["condition"] == condition]
        summaries.append({"condition": condition, "answers": len(values), "worlds": len({r["group_id"] for r in values}),
                          "complete_correct": sum(r["evaluation"]["complete_correct"] for r in values),
                          "complete_grounded_correct": sum(r["evaluation"]["complete_grounded_correct"] for r in values),
                          "invalid_json_outputs": sum(not r["parsed_json_object"] for r in values)})
    write_csv(directory / "generation_summary.csv", summaries)


def run_generation(args, bundle, stage):
    configure_offline()
    plan = require_prepared(args, bundle)
    check_stage_gate(args, stage)
    check_snapshots(bundle)
    protect_originals(args)
    directory = stage_directory(args, stage)
    started_at, start = now(), time.perf_counter()
    with writer_lock(directory):
        runtime = load_runtime(bundle)
        identity = make_identity(args, bundle, plan, runtime, stage)
        require_gate_environment(args, identity, stage)
        manifest = {"identity_hash": digest(identity), "identity": identity}
        manifest_path = directory / "manifest.json"
        save_once(manifest_path, manifest)
        # A new process may resume only under exactly the same static identity.
        existing = collect_records(directory, manifest, bundle, runtime["tokenizer"], allow_partial=True)
        expected = len(identity["questions"]) * len(identity["conditions"]) * identity["repeats"]
        status_path = directory / "status.json"
        previous = load_json(status_path) if status_path.exists() else {}
        sessions = previous.get("sessions", [])
        save_json(status_path, {"status": "running", "identity_hash": manifest["identity_hash"], "expected_answers": expected,
                               "observed_answers": len(existing), "started_at_utc": started_at, "sessions": sessions})
        try:
            cache, completed = {}, len(existing)
            for repeat in range(identity["repeats"]):
                target = directory if stage == "run" else directory / f"repeat_{repeat + 1}"
                for qid in identity["questions"]:
                    for condition, config in identity["conditions"].items():
                        path = response_location(target, qid, condition)
                        final = selected_final(bundle, stage, qid, condition)
                        record, is_new = checkpoint(path, manifest["identity_hash"],
                            lambda: generate_one(runtime, bundle, qid, condition, final, config, manifest["identity_hash"], repeat, cache),
                            lambda r: validate_response(r, manifest["identity_hash"], bundle, qid, condition, final,
                                                         config, repeat, runtime["tokenizer"], cache))
                        if not is_new:
                            continue
                        completed += 1
                        save_json(status_path, {"status": "running", "identity_hash": manifest["identity_hash"], "expected_answers": expected,
                                               "observed_answers": completed, "started_at_utc": started_at, "sessions": sessions})
                        print(json.dumps({"stage": stage, "completed": completed, "expected": expected, "repeat": repeat + 1,
                                          "qid": qid, "condition": condition, "generated_tokens": record["generated_tokens"],
                                          "generation_ms": round(record["generation_ms"], 2)}, ensure_ascii=False), flush=True)
            records = collect_records(directory, manifest, bundle, runtime["tokenizer"])
            response_files = {str(p.relative_to(directory)): file_hash(p) for p in sorted(directory.rglob("responses/*.json"))}
            result = {"status": "complete", "identity_hash": manifest["identity_hash"], "expected_answers": expected,
                      "observed_answers": len(records), "independent_worlds": len(identity["worlds"]),
                      "response_sha256": response_files, "generation_code_sha256": identity["code_sha256"],
                      "started_at_utc": previous.get("started_at_utc", started_at), "finished_at_utc": now(),
                      "model_load_seconds": runtime["load_seconds"], "peak_cuda_allocated_bytes": runtime["torch"].cuda.max_memory_allocated(),
                      "sessions": sessions + [{"started_at_utc": started_at, "finished_at_utc": now(), "wall_seconds": time.perf_counter() - start,
                                               "resumed_answers": len(existing), "generated_answers": len(records) - len(existing)}],
                      "protected_originals": protect_originals(args)}
            if stage != "run":
                comparison = compare_repeats(records, identity)
                if stage == "baseline512":
                    differences = []
                    for record in records:
                        if record["repeat"]:
                            continue
                        old = load_json(args.baseline_manifest.parent / "responses" / f"{record['qid']}__m3_post_prefix.json")
                        require(record["messages"] == old["messages"] and record["prompt_tokens"] == old["prompt_tokens"], "512 baseline input differs from original")
                        differences.append({"qid": record["qid"], "response_same": record["response"] == old["response"],
                                            "evaluation_same": record["evaluation"] == old["evaluation"],
                                            "old_evaluation": old["evaluation"], "new_evaluation": record["evaluation"]})
                    comparison.update(old_machine_comparisons=differences,
                                      old_response_differences=sum(not r["response_same"] for r in differences),
                                      old_evaluation_differences=sum(not r["evaluation_same"] for r in differences),
                                      original_generated_token_ids_available=False,
                                      migration_interpretation="Identical pinned inputs/protocol and stable new-machine repeats. Old-machine differences, if any, are disclosed; no parameter tuning.")
                save_json(directory / "comparison.json", comparison)
                result["comparison_sha256"] = file_hash(directory / "comparison.json")
            else:
                require(len(records) == 240, "Wrong formal denominator")
                basic_tables(directory, records)
                evidence_source = args.work / "evidence_2048_subset.csv"
                destination = directory / "evidence_2048_subset.csv"
                if destination.exists():
                    require(file_hash(destination) == file_hash(evidence_source), "Formal evidence table differs")
                else:
                    destination.write_bytes(evidence_source.read_bytes())
            save_json(status_path, result)
            save_json(directory / "environment_provenance.json", {"collected_at_utc": now(), "environment": identity["environment"],
                       "effective_generation_config": runtime["generation_config"], "model_config": runtime["model_config"],
                       "executable": sys.executable, "model_load_seconds": runtime["load_seconds"]})
            return result
        except BaseException as error:
            save_json(status_path, {"status": "failed", "identity_hash": manifest["identity_hash"], "expected_answers": expected,
                                   "error_type": type(error).__name__, "error": str(error), "failed_at_utc": now(), "sessions": sessions})
            raise


def offline_tokenizer(bundle):
    configure_offline()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path(model_specs(bundle)["answer"]), local_files_only=True)
    tokenizer.pad_token_id = tokenizer.eos_token_id
    return tokenizer


def verify_formal(args, bundle, verify_statistics=True):
    plan = require_prepared(args, bundle)
    protected = protect_originals(args)
    check_snapshots(bundle)
    manifest, status = load_json(args.output / "manifest.json"), load_json(args.output / "status.json")
    identity = manifest["identity"]
    require(identity["stage"] == "run" and identity["questions"] == plan["questions"] and identity["tasks"] == plan["tasks"] and
            identity["conditions"] == plan["conditions"] and identity["repeats"] == 1 and identity["plan_sha256"] == digest(plan), "Formal identity differs from frozen plan")
    require(identity["code_sha256"] == generation_code_hashes(), "Generation/scoring code changed after execution")
    require(status["status"] == "complete" and status["identity_hash"] == manifest["identity_hash"] and
            status["expected_answers"] == status["observed_answers"] == 240, "Formal run is not complete")
    check_stage_gate(args, "run")
    for gate in ("baseline512", "smoke2048"):
        gate_manifest = load_json(args.work / gate / "manifest.json")
        require(gate_manifest["identity"]["environment"] == identity["environment"] and
                gate_manifest["identity"]["effective_generation_config"] == identity["effective_generation_config"], "Engineering checks used a different environment/protocol")
    intervals = verify_intervals(bundle, load_budget_tokenizer(bundle))
    tokenizer = offline_tokenizer(bundle)
    records = collect_records(args.output, manifest, bundle, tokenizer)
    eos = identity["effective_generation_config"]["eos_token_id"]
    eos = eos if isinstance(eos, list) else [eos]
    max_context = load_json(model_path(model_specs(bundle)["answer"]) / "config.json")["max_position_embeddings"]
    for record in records:
        require(record["truncated_output"] == (record["generated_tokens"] == 256 and record["generated_token_ids"][-1] not in eos),
                "Truncated-output diagnostic differs")
        require(record["prompt_tokens"] + 256 <= max_context, "Saved prompt exceeds model context limit")
    expected_files = {"responses/" + r["qid"] + "__" + r["condition"] + ".json" for r in records}
    require(set(status["response_sha256"]) == expected_files, "Formal response hash set differs")
    for name, expected in status["response_sha256"].items():
        require(file_hash(args.output / name) == expected, "Formal raw answer hash differs: " + name)
    require(file_hash(args.output / "evidence_2048_subset.csv") == file_hash(args.work / "evidence_2048_subset.csv"), "Formal evidence metrics differ from prepare")
    # Recompute saved evidence metrics, not only the file checksums.
    evidence_rows, cache = [], {}
    with (args.work / "evidence_2048_subset.csv").open(encoding="utf-8", newline="") as stream:
        stored = list(csv.DictReader(stream))
    require(len(stored) == 240, "Evidence denominator differs")
    for row in stored:
        qid, condition = row["qid"], row["condition"]
        final = bundle["finals"][qid, condition]
        value = evidence(bundle, qid, final, cache)
        for key in ("G_final", "U_sim", "fact_coverage", "admissible_U_sim", "contradiction_exposure", "obsolete_exposure"):
            require(math.isclose(float(row[key]), float(value[key]), abs_tol=1e-12), "Recomputed evidence metric differs")
        evidence_rows.append((qid, condition))
    require(len(set(evidence_rows)) == 240, "Duplicate evidence metric row")
    analysis = None
    if verify_statistics:
        from .analyze_answers_2048 import verify_analysis
        analysis = verify_analysis(args.output, args.work, records)
    return {"status": "PASS", "generation_identity_hash": manifest["identity_hash"], "answers_rescored": len(records),
            "task_pairs": 120, "worlds": 60, "interval_audit": intervals, "protected_originals": protected,
            "same_machine_checks": "PASS", "analysis": analysis, "gpu_generation_performed": False,
            "scope": "Exact frozen matrix, authentic saved source intervals/prompts/tokens, original scoring, paired analysis and protected original files"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("prepare", "baseline512", "smoke", "run", "analyze", "verify"), required=True)
    parser.add_argument("--baseline-manifest", type=Path, default=BASELINE)
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--run", type=Path, default=RUN)
    parser.add_argument("--work", type=Path, default=WORK)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--device", choices=("cuda",), default="cuda")
    args = parser.parse_args(argv)
    validate_paths(args)
    if args.stage in ("baseline512", "smoke", "run"):
        configure_offline()
    args.work.mkdir(parents=True, exist_ok=True)
    command = {"started_at_utc": now(), "argv": [sys.executable, "-m", "experiments.strengthening.downstream_2048", *(sys.argv[1:] if argv is None else argv)],
               "cwd": str(Path.cwd()), "stage": args.stage}
    with (args.work / "commands.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(command, ensure_ascii=False) + "\n")
    bundle = load_bundle(args)
    if args.stage == "prepare":
        result = prepare(args, bundle)
    elif args.stage in ("baseline512", "smoke", "run"):
        result = run_generation(args, bundle, args.stage)
    elif args.stage == "analyze":
        verify_formal(args, bundle, verify_statistics=False)
        from .analyze_answers_2048 import analyze
        with writer_lock(args.output):
            calculated = analyze(args.output, args.work)
        result = {"status": "complete", "contrasts": calculated["contrasts"]}
    else:
        result = verify_formal(args, bundle)
        save_json(args.output / "verification.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
