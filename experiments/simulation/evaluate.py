"""Independent synthetic span oracle and frozen development/test selection pilot.

This module never emits human U labels or calls the human-only E2 evaluator.
No retrieval or model inference is performed. Only complete oracle spans in
verified, actually delivered budget-tokenizer prefixes receive support credit.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, urlunsplit

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ANNOTATION_SOURCE = "synthetic_oracle"
SEED = 20260928
REPEATS = 5000
SCENARIOS = {"aligned", "distributed", "alternative_source", "stale_version", "near_match", "late_evidence"}
PINNED_MODELS = {
    "dense": ("BAAI/bge-small-en-v1.5", "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"),
    "reranker": ("BAAI/bge-reranker-v2-m3", "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e"),
    "tokenizer": ("google-bert/bert-base-uncased", "86b5e0934494bd15c9632b12f734a8a67f723594"),
}


def fail_unless(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith(".gz") else raw)


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def unique_index(rows, key, label):
    result = {}
    for row in rows:
        value = row.get(key)
        fail_unless(isinstance(value, str) and value, f"{label}: missing/invalid {key}")
        fail_unless(value not in result, f"{label}: duplicate {key}: {value}")
        result[value] = row
    return result


def normalize_url(value):
    parsed = urlsplit(str(value).strip())
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), parsed.query, ""))


def configurations():
    return [{"pool": pool, "cap": cap, "reranker": ranker, "budget": budget,
             "config_id": f"p{pool}_{cap}_{ranker}_b{budget}"}
            for pool in (16, 64) for ranker in ("none", "m3")
            for cap in (("off", "pre") if ranker == "none" else ("off", "pre", "post"))
            for budget in (512, 2048)]


def structural_order(config):
    return (config["reranker"] != "none", config["pool"], {"off": 0, "pre": 1, "post": 2}[config["cap"]], config["config_id"])


def verify_file_manifest(data, specification):
    files = specification.get("files", {})
    for name in ("corpus.jsonl", "questions.jsonl", "oracle.jsonl"):
        fail_unless(name in files, f"Specification is missing a hash for {name}")
        fail_unless(files[name].get("sha256") == sha256(data / name), f"Data hash mismatch: {name}")


def validate_data(corpus_rows, question_rows, oracle_rows, specification):
    corpus = unique_index(corpus_rows, "chunk_id", "corpus")
    questions = unique_index(question_rows, "qid", "questions")
    oracle = unique_index(oracle_rows, "qid", "oracle")
    fail_unless(len(questions) == 120 and set(questions) == set(oracle), "Pilot requires exactly 120 matched question/oracle IDs")
    fail_unless(specification.get("status") == "complete" and specification.get("annotation_source") == ANNOTATION_SOURCE,
                "Specification must be complete and explicitly synthetic_oracle")
    fail_unless(specification.get("generation_seed") == SEED, "Unexpected frozen generation seed")
    for name, rows in (("corpus.jsonl", corpus_rows), ("questions.jsonl", question_rows), ("oracle.jsonl", oracle_rows)):
        fail_unless(specification["files"][name].get("rows") == len(rows), f"Specification row count mismatch: {name}")
    for chunk in corpus.values():
        fail_unless(set(chunk) == {"chunk_id", "url", "text"}, "System-visible corpus must contain only chunk_id/url/text")
        fail_unless(isinstance(chunk["text"], str) and chunk["text"].strip(), "Empty corpus text")
        fail_unless((urlsplit(chunk["url"]).hostname or "").endswith(".invalid"), "Synthetic corpus URL must use a fictional .invalid domain")
    groups = defaultdict(list)
    claim_chunk_groups = defaultdict(set)
    for qid, question in questions.items():
        reference = oracle[qid]
        fail_unless(question.get("construction_source") == "synthetic_information_need", "Question must declare synthetic construction")
        for field in ("group_id", "split", "policy", "scenario"):
            fail_unless(question.get(field) == reference.get(field), f"Question/oracle metadata mismatch: {qid}/{field}")
        fail_unless(question["split"] in {"dev", "test"} and question["policy"] in {"open", "constrained"}, "Invalid split or policy")
        fail_unless(question["scenario"] in SCENARIOS, "Unknown scenario")
        fail_unless(isinstance(question.get("question"), str) and question["question"].strip(), "Missing question text")
        fail_unless(isinstance(question.get("gold_urls"), list) and question["gold_urls"], "Missing designated gold pages")
        required = reference.get("required_fact_ids")
        fail_unless(isinstance(required, list) and required and len(required) == len(set(required))
                    and all(isinstance(fact, str) and fact for fact in required), f"Invalid required facts: {qid}")
        allowed = reference.get("allowed_url_prefixes")
        fail_unless(isinstance(allowed, list) and all(isinstance(prefix, str) and prefix for prefix in allowed), "Invalid source policy prefixes")
        fail_unless(bool(allowed) == (question["policy"] == "constrained"), "Only constrained questions must supply source prefixes")
        fail_unless(isinstance(reference.get("claims"), list), "Oracle claims must be a list")
        supported, admissible_supported = set(), set()
        for claim in reference["claims"]:
            cid = claim.get("chunk_id")
            fail_unless(cid in corpus, f"Unknown oracle chunk ID: {cid}")
            fail_unless(claim.get("fact_id") in required, f"Claim references unknown required fact: {qid}")
            fail_unless(claim.get("status") in {"valid", "contradictory", "obsolete"}, "Unknown claim status")
            text = corpus[cid]["text"]
            start, end = claim.get("start_char"), claim.get("end_char")
            fail_unless(type(start) is int and type(end) is int and 0 <= start < end <= len(text)
                        and text[start:end].strip(), f"Invalid claim character span: {qid}/{cid}")
            admissible = question["policy"] == "open" or any(corpus[cid]["url"].startswith(prefix) for prefix in allowed)
            fail_unless(type(claim.get("admissible")) is bool and claim["admissible"] == admissible, "Claim admissibility disagrees with frozen source policy")
            claim_chunk_groups[cid].add(question["group_id"])
            if claim["status"] == "valid":
                supported.add(claim["fact_id"])
                if claim["admissible"]:
                    admissible_supported.add(claim["fact_id"])
        fail_unless(supported == set(required) and admissible_supported == set(required), f"Oracle has no complete valid admissible corpus support: {qid}")
        groups[question["group_id"]].append(question)
    fail_unless(len(groups) == 60, "Expected 60 independent world groups")
    for group, pair in groups.items():
        fail_unless(len(pair) == 2 and {q["policy"] for q in pair} == {"open", "constrained"}, f"Group lacks exactly two policy versions: {group}")
        fail_unless(len({q["split"] for q in pair}) == len({q["scenario"] for q in pair}) == 1, "Policy pair crosses split/scenario")
        fail_unless(set(oracle[pair[0]["qid"]]["required_fact_ids"]) == set(oracle[pair[1]["qid"]]["required_fact_ids"]), "Policy versions do not share one information need")
    fail_unless(all(len(values) == 1 for values in claim_chunk_groups.values()), "Oracle support documents cross world groups")
    split_groups = {split: {gid for gid, pair in groups.items() if pair[0]["split"] == split} for split in ("dev", "test")}
    fail_unless(len(split_groups["dev"]) == 20 and len(split_groups["test"]) == 40, "Expected 20 development and 40 test groups")
    totals = Counter(pair[0]["scenario"] for pair in groups.values())
    fail_unless(set(totals) == SCENARIOS and set(totals.values()) == {10}, "Expected ten worlds in each of six scenarios")
    for split in ("dev", "test"):
        balance = Counter(pair[0]["scenario"] for pair in groups.values() if pair[0]["split"] == split)
        fail_unless(set(balance) == SCENARIOS and max(balance.values()) - min(balance.values()) <= 1, "Scenario split is not balanced")
    selection = specification.get("selection", {})
    fail_unless(selection.get("frozen_before_model_execution") is True, "Selection must be frozen before model execution")
    for split in ("dev", "test"):
        fail_unless(set(selection.get(f"{split}_groups", [])) == split_groups[split], "Frozen selection split differs from questions")
    fail_unless(selection.get("primary_policy") == "open" and selection.get("primary_budget") == 512
                and selection.get("secondary_budget") == 2048, "Unexpected frozen primary/secondary selection protocol")
    fail_unless(selection.get("bootstrap_repetitions") == REPEATS and selection.get("bootstrap_seed") == SEED, "Unexpected bootstrap specification")
    primary_order = [c["config_id"] for c in sorted((c for c in configurations() if c["budget"] == 512), key=structural_order)]
    fail_unless(selection.get("configs") == primary_order and selection.get("tie_order") == primary_order,
                "Frozen configuration set or structural tie order differs from contract")
    fail_unless(selection.get("primary_endpoint") == "U_sim" and selection.get("primary_G") == "G_final"
                and selection.get("weighting") == "equal_information_needs", "Frozen selector endpoint/weighting differs from contract")
    for key, (model_name, revision) in PINNED_MODELS.items():
        entry = specification.get("models", {}).get(key, {})
        fail_unless(entry.get("model") == model_name and entry.get("sha") == revision, "Specification changes frozen model/tokenizer")
    return corpus, questions, oracle, groups


def span_token_end(text, offsets, start, end):
    """Minimum prefix length containing all tokens intersecting a complete span."""
    fail_unless(type(start) is int and type(end) is int and 0 <= start < end <= len(text), "Invalid span bounds")
    overlapping = [(i, left, right) for i, (left, right) in enumerate(offsets) if right > start and left < end and right > left]
    fail_unless(bool(overlapping), "Claim has no budget-tokenizer representation")
    first, last = overlapping[0], overlapping[-1]
    fail_unless(not text[start:max(start, first[1])].strip() and not text[min(end, last[2]):end].strip(),
                "Tokenizer offsets do not cover complete claim boundaries")
    return last[0] + 1


def compile_claims(oracle, corpus, tokenized):
    compiled = {}
    for qid, reference in oracle.items():
        claims = []
        for claim in reference["claims"]:
            cid = claim["chunk_id"]
            claims.append({**claim, "complete_at_token": span_token_end(corpus[cid]["text"], tokenized[cid]["offset_mapping"], claim["start_char"], claim["end_char"])})
        compiled[qid] = claims
    return compiled


def structural_budget_feasibility(questions, oracle, compiled):
    """Necessary per-fact prefix bound, computed independently of model rankings.

    A complete span that alone requires more than B chunk-prefix tokens can
    never fit under this prefix-packing protocol. Satisfying this bound for
    every fact does NOT prove that their supporting chunks fit jointly.
    """
    rows = []
    for qid, question in sorted(questions.items()):
        for budget in (512, 2048):
            required = oracle[qid]["required_fact_ids"]
            valid_minima, admissible_minima = {}, {}
            for fact in required:
                claims = [claim for claim in compiled[qid] if claim["fact_id"] == fact and claim["status"] == "valid"]
                valid_minima[fact] = min((claim["complete_at_token"] for claim in claims), default=None)
                admissible_minima[fact] = min((claim["complete_at_token"] for claim in claims if claim["admissible"]), default=None)
            missing = [fact for fact, minimum in valid_minima.items() if minimum is None or minimum > budget]
            missing_admissible = [fact for fact, minimum in admissible_minima.items() if minimum is None or minimum > budget]
            constrained = question["policy"] == "constrained"
            rows.append({"qid": qid, "group_id": question["group_id"], "split": question["split"], "scenario": question["scenario"],
                         "policy": question["policy"], "budget": budget, "required_fact_ids": required,
                         "minimum_valid_span_prefix_tokens": valid_minima,
                         "facts_without_any_budget_feasible_valid_span": missing,
                         "necessary_condition_for_U_sim_satisfied": not missing,
                         "minimum_admissible_valid_span_prefix_tokens": admissible_minima if constrained else None,
                         "facts_without_any_budget_feasible_admissible_span": missing_admissible if constrained else None,
                         "necessary_condition_for_admissible_U_sim_satisfied": not missing_admissible if constrained else None})
    grouped = defaultdict(list)
    for row in rows:
        for scenario in ("all", row["scenario"]):
            grouped[(row["split"], row["policy"], row["budget"], scenario)].append(row)
    summary = []
    for (split, policy, budget, scenario), group in sorted(grouped.items()):
        infeasible = sum(not row["necessary_condition_for_U_sim_satisfied"] for row in group)
        admissible_infeasible = sum(not row["necessary_condition_for_admissible_U_sim_satisfied"] for row in group) if policy == "constrained" else None
        summary.append({"split": split, "policy": policy, "budget": budget, "scenario": scenario,
                        "n_information_needs": len(group), "individually_infeasible_information_needs": infeasible,
                        "U_sim_mean_upper_bound": 1 - infeasible / len(group),
                        "admissible_individually_infeasible_information_needs": admissible_infeasible,
                        "admissible_U_sim_mean_upper_bound": 1 - admissible_infeasible / len(group) if admissible_infeasible is not None else None})
    return {"annotation_source": ANNOTATION_SOURCE, "model_rankings_used": False,
            "method": "For each required fact, take the smallest complete-span token-prefix length among valid oracle spans in the entire corpus. If that minimum exceeds the evidence budget (or no valid span exists), full coverage is impossible. The bound ignores joint packing, separators and retrieval; passing it is necessary, not sufficient.",
            "interpretation": "This diagnoses structural budget infeasibility, not a model error. It does not change the frozen endpoint, denominator, configuration set or selection protocol.",
            "per_task_budget": rows, "summary": summary}


def score_support(reference, claims, delivered_lengths, corpus):
    """Count unique supported facts, never duplicate spans, pages or chunks."""
    required = set(reference["required_fact_ids"])
    valid, admissible, contradictory, obsolete = set(), set(), set(), set()
    for claim in claims:
        if delivered_lengths.get(claim["chunk_id"], 0) < claim["complete_at_token"]:
            continue
        fact = claim["fact_id"]
        if claim["status"] == "valid":
            valid.add(fact)
            if claim["admissible"]:
                admissible.add(fact)
        elif claim["status"] == "contradictory":
            contradictory.add(fact)
        elif claim["status"] == "obsolete":
            obsolete.add(fact)
    constrained = reference["policy"] == "constrained"
    context_ids = [cid for cid, count in delivered_lengths.items() if count > 0]
    compliant = bool(context_ids) and all(any(corpus[cid]["url"].startswith(prefix) for prefix in reference["allowed_url_prefixes"]) for cid in context_ids)
    return {
        "U_sim": int(required <= valid), "fact_coverage": len(required & valid) / len(required),
        "supported_fact_count": len(required & valid), "required_fact_count": len(required),
        "supported_fact_ids": sorted(required & valid),
        "contradiction_exposure": int(bool(contradictory)), "obsolete_exposure": int(bool(obsolete)),
        "contradictory_fact_count": len(contradictory), "obsolete_fact_count": len(obsolete),
        "admissible_U_sim": int(required <= admissible) if constrained else None,
        "admissible_fact_coverage": len(required & admissible) / len(required) if constrained else None,
        "C_sim": int(compliant) if constrained else None,
    }


def first_support_loss(stage_scores, key="U_sim"):
    for stage in ("raw", "pre_cap", "rerank", "post_cap", "final"):
        if stage_scores[stage][key] == 0:
            return {"raw": "candidate_not_covered", "rerank": "rerank_membership", "final": "budget"}.get(stage, stage)
    return "retained"


def cap_two(rows):
    counts, retained = Counter(), []
    for row in rows:
        url = normalize_url(row["url"])
        if counts[url] < 2:
            retained.append(row)
            counts[url] += 1
    return retained


def check_final_context(final, post, corpus, tokenized, tokenizer, budget):
    expected_ids, expected_lengths, expected_stream = [], [], []
    for row in post:
        cid = row["chunk_id"]
        tokens = tokenized[cid]["input_ids"]
        if not tokens:
            continue
        remaining = budget - len(expected_stream) - int(bool(expected_ids))
        if remaining <= 0:
            break
        take = tokens[:remaining]
        if expected_ids:
            expected_stream.append(tokenizer.sep_token_id)
        expected_stream.extend(take)
        expected_ids.append(cid)
        expected_lengths.append(len(take))
        if len(take) < len(tokens):
            break
    chunks = final.get("chunks", [])
    fail_unless([c["chunk_id"] for c in chunks] == expected_ids, "Final context is not the actual budget prefix of post-cap ranking")
    fail_unless(final.get("budget") == budget and final.get("token_ids") == expected_stream
                and final.get("used_tokens") == len(expected_stream) <= budget, "Final evidence token stream/budget mismatch")
    fail_unless(final.get("separator_tokens") == max(len(chunks) - 1, 0), "Final separator count mismatch")
    delivered = {}
    for chunk, count in zip(chunks, expected_lengths):
        cid = chunk["chunk_id"]
        fail_unless(cid in corpus and chunk["url"] == corpus[cid]["url"], "Unknown/mismatched final chunk")
        full = tokenized[cid]["input_ids"]
        fail_unless(chunk.get("token_ids") == full[:count] and chunk.get("delivered_tokens") == count,
                    "Saved final tokens are not the pinned tokenizer's original chunk prefix")
        fail_unless(chunk.get("chunk_tokens") == len(full) and chunk.get("partial") == (count < len(full)), "Wrong final token count/partial flag")
        expected_text = tokenizer.decode(full[:count], skip_special_tokens=False, clean_up_tokenization_spaces=False)
        fail_unless(chunk.get("text") == expected_text, "Saved final text differs from decoded delivered token IDs")
        delivered[cid] = count
    return delivered


def validate_manifest(data, run, corpus, questions):
    manifest, status = read_json(run / "manifest.json"), read_json(run / "status.json")
    fail_unless(status.get("status") == "complete" and status.get("observed_records") == 2400
                and status.get("expected_records") == 2400, "Requires a complete 120 x 20 simulation run")
    fail_unless(manifest.get("questions") == 120 and manifest.get("expected_records") == 2400
                and manifest.get("corpus_chunks") == len(corpus), "Run count mismatch")
    identity = manifest["identity"]
    identity_hash = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    fail_unless(manifest.get("identity_hash") == identity_hash, "Run identity hash mismatch")
    for key, name in (("corpus_sha256", "corpus.jsonl"), ("questions_sha256", "questions.jsonl"), ("specification_sha256", "specification.json")):
        fail_unless(identity.get(key) == sha256(data / name), f"Run data hash mismatch: {name}")
    for key, (name, revision) in PINNED_MODELS.items():
        actual = identity.get("models", {}).get(key, {})
        fail_unless(actual.get("model") == name and actual.get("sha") == revision, f"Model/tokenizer revision differs from frozen pilot: {key}")
    expected = {c["config_id"]: c for c in configurations()}
    actual = unique_index(manifest.get("configurations", []), "config_id", "manifest configurations")
    fail_unless(actual == expected, "Run does not contain the frozen 20 configurations")
    return manifest


def load_pinned_tokenizer(run, manifest):
    from transformers import AutoTokenizer
    model = manifest["identity"]["models"]["tokenizer"]
    directory = ROOT / ".cache/models" / model["model"].replace("/", "--") / model["sha"]
    file_manifest = read_json(run / "model_files" / (model["model"].replace("/", "--") + ".json"))
    fail_unless(file_manifest.get("model") == model["model"] and file_manifest.get("sha") == model["sha"], "Tokenizer file manifest mismatch")
    fail_unless(file_manifest.get("tokenizer_only") is True, "Evaluator accepts tokenizer-only download manifests")
    # Frozen Windows manifests may use backslashes even when reanalyzed on Linux.
    expected_files = {}
    for stored_name, expected_hash in file_manifest["files"].items():
        name = stored_name.replace("\\", "/")
        path = PurePosixPath(name)
        fail_unless(not path.is_absolute() and ".." not in path.parts and ":" not in name,
                    "Unsafe tokenizer manifest path")
        fail_unless(path.suffix.lower() in {".json", ".txt", ".model"}, "Tokenizer manifest unexpectedly contains model weights")
        expected_files[name] = expected_hash
    missing = [name for name in expected_files if not (directory / name).is_file()]
    if missing:
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id=model["model"], revision=model["sha"], local_dir=directory,
                          allow_patterns=missing)
    for name, expected_hash in expected_files.items():
        path = directory / name
        fail_unless(path.is_file() and sha256(path) == expected_hash, f"Pinned tokenizer file bytes differ: {name}")
    tokenizer = AutoTokenizer.from_pretrained(str(directory), local_files_only=True, use_fast=True)
    fail_unless(tokenizer.is_fast and tokenizer.sep_token_id is not None, "Fast pinned BERT tokenizer with offsets and SEP is required")
    return tokenizer, file_manifest


def evaluate_traces(run, corpus, questions, oracle, compiled, tokenized, tokenizer, manifest):
    rows, seen_queries, hashes = [], set(), {}
    expected = {c["config_id"]: c for c in configurations()}
    known_gold = {qid: {normalize_url(url) for url in q["gold_urls"]} for qid, q in questions.items()}
    paths = sorted((run / "traces").glob("*.json.gz"))
    fail_unless(len(paths) == 120, "Requires exactly 120 trace files")
    get_ids = lambda stage: [row["chunk_id"] for row in stage]
    for path in paths:
        trace = read_json(path)
        qid = trace.get("qid")
        fail_unless(qid in questions and qid not in seen_queries, "Unknown or duplicate query trace")
        seen_queries.add(qid)
        hashes[path.name] = sha256(path)
        question = questions[qid]
        fail_unless(trace.get("identity_hash") == manifest["identity_hash"], "Trace belongs to a different run")
        for field in ("question", "group_id", "topic", "construction_source"):
            fail_unless(trace.get(field) == question[field], f"Trace question metadata mismatch: {qid}/{field}")
        fail_unless(set(trace.get("gold_urls", [])) == known_gold[qid], "Trace designated pages differ from questions")
        records = trace.get("configurations", [])
        ids = [row["configuration"]["config_id"] for row in records]
        fail_unless(len(ids) == len(set(ids)) == 20 and set(ids) == set(expected), "Missing/duplicate/unknown configuration trace")
        raw_max = trace.get("raw_max", [])
        fail_unless(len(raw_max) == 64 and len(set(get_ids(raw_max))) == 64, "Invalid shared raw pool")
        for record in records:
            conf = record["configuration"]
            cid = conf["config_id"]
            fail_unless(conf == expected[cid], "Trace configuration differs from frozen configuration")
            stages = record.get("stages", {})
            fail_unless(set(stages) == {"raw", "pre_cap", "rerank", "post_cap"}, "Invalid trace stages")
            for stage in (raw_max, *stages.values()):
                fail_unless(len(get_ids(stage)) == len(set(get_ids(stage))), "Duplicate chunk ID within stage")
                for chunk in stage:
                    chunk_id = chunk.get("chunk_id")
                    fail_unless(chunk_id in corpus and chunk.get("url") == corpus[chunk_id]["url"], "Unknown chunk ID or URL mismatch")
                    fail_unless(chunk.get("chunk_tokens") == len(tokenized[chunk_id]["input_ids"]), "Stage token count differs from pinned tokenizer")
            raw, pre, ordered, post = (stages[key] for key in ("raw", "pre_cap", "rerank", "post_cap"))
            fail_unless(get_ids(raw) == get_ids(raw_max[:conf["pool"]]), "Configurations do not share raw candidates")
            fail_unless(get_ids(pre) == get_ids(cap_two(raw) if conf["cap"] == "pre" else raw), "Pre-cap membership mismatch")
            fail_unless(set(get_ids(ordered)) == set(get_ids(pre)) and len(ordered) == len(pre), "Reranker changes candidate membership")
            if conf["reranker"] == "none":
                fail_unless(get_ids(ordered) == get_ids(pre), "Non-reranked order changed")
            else:
                fail_unless(all(isinstance(x.get("rerank_score"), (int, float)) and math.isfinite(x["rerank_score"]) for x in ordered), "Invalid reranker score")
                fail_unless(get_ids(ordered) == get_ids(sorted(ordered, key=lambda x: (-x["rerank_score"], x["raw_rank"]))), "Reranked order differs from scores")
            fail_unless(get_ids(post) == get_ids(cap_two(ordered) if conf["cap"] == "post" else ordered), "Post-cap membership mismatch")
            delivered = check_final_context(record["final_context"], post, corpus, tokenized, tokenizer, conf["budget"])
            scores = {name: score_support(oracle[qid], compiled[qid], {r["chunk_id"]: len(tokenized[r["chunk_id"]]["input_ids"]) for r in stage}, corpus)
                      for name, stage in stages.items()}
            scores["final"] = score_support(oracle[qid], compiled[qid], delivered, corpus)
            observed_g = int(any(normalize_url(corpus[chunk_id]["url"]) in known_gold[qid] for chunk_id, count in delivered.items() if count > 0))
            fail_unless(record.get("metrics", {}).get("G_final") == observed_g, "Saved G does not match actual final context")
            row = {"qid": qid, "group_id": question["group_id"], "split": question["split"], "policy": question["policy"],
                   "scenario": question["scenario"], **conf, "annotation_source": ANNOTATION_SOURCE,
                   "valid_for_human_eval_claim": False, "G_final": observed_g, **scores["final"],
                   "context_tokens": record["final_context"]["used_tokens"],
                   "first_support_loss_stage": first_support_loss(scores),
                   "first_admissible_support_loss_stage": first_support_loss(scores, "admissible_U_sim") if question["policy"] == "constrained" else None}
            for name, values in scores.items():
                for metric_name, value in values.items():
                    row[f"{name}_{metric_name}"] = value
            rows.append(row)
    fail_unless(seen_queries == set(questions) and len(rows) == 2400, "Incomplete 120 x 20 evaluator output")
    return rows, hashes


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[("overall", "all", row["split"], row["policy"], row["config_id"])].append(row)
        groups[("scenario", row["scenario"], row["split"], row["policy"], row["config_id"])].append(row)
    metrics = ("G_final", "U_sim", "fact_coverage", "contradiction_exposure", "obsolete_exposure", "admissible_U_sim", "admissible_fact_coverage", "C_sim", "context_tokens")
    summary = []
    for (scope, scenario, split, policy, cid), records in sorted(groups.items()):
        fail_unless(len({r["group_id"] for r in records}) == len(records), "Summary would double-weight an information need")
        summary.append({"scope": scope, "scenario": scenario, "split": split, "policy": policy, "config_id": cid,
                        "n_information_needs": len(records), "annotation_source": ANNOTATION_SOURCE,
                        **{key: float(np.mean([r[key] for r in records])) if all(r[key] is not None for r in records) else None for key in metrics},
                        "support_loss_stage_counts": dict(Counter(r["first_support_loss_stage"] for r in records))})
    return summary


def select_config(scores, ordered_ids):
    highest = max(scores.values())
    ties = [cid for cid in ordered_ids if scores[cid] == highest]
    return ties[0], ties


def selection_analysis(rows, specification, budget):
    configs = sorted((c for c in configurations() if c["budget"] == budget), key=structural_order)
    ordered = [c["config_id"] for c in configs]
    chosen_rows = [r for r in rows if r["policy"] == "open" and r["budget"] == budget]
    indexed = {(r["split"], r["group_id"], r["config_id"]): r for r in chosen_rows}
    fail_unless(len(indexed) == len(chosen_rows), "Duplicate information need/configuration in selector")
    dev = sorted(specification["selection"]["dev_groups"])
    test = sorted(specification["selection"]["test_groups"])
    fail_unless(len(dev) == 20 and len(test) == 40 and not set(dev) & set(test), "Invalid development/test selector groups")
    for split, groups in (("dev", dev), ("test", test)):
        fail_unless(all((split, gid, cid) in indexed for gid in groups for cid in ordered), "Unpaired or incomplete selection inputs")
    matrices = {metric: np.asarray([[indexed[("dev", gid, cid)][metric] for cid in ordered] for gid in dev], dtype=float)
                for metric in ("G_final", "U_sim")}
    selected, ties, means = {}, {}, {}
    for metric, matrix in matrices.items():
        totals = dict(zip(ordered, matrix.sum(axis=0).tolist()))
        selected[metric], ties[metric] = select_config(totals, ordered)
        means[metric] = {cid: total / len(dev) for cid, total in totals.items()}
    g_config, u_config = selected["G_final"], selected["U_sim"]
    differences = np.asarray([indexed[("test", gid, u_config)]["U_sim"] - indexed[("test", gid, g_config)]["U_sim"] for gid in test], dtype=float)
    test_rng = np.random.default_rng(SEED)
    test_draws = test_rng.integers(0, len(test), (REPEATS, len(test)))
    interval = np.quantile(differences[test_draws].mean(axis=1), [.025, .975]).tolist()
    dev_rng = np.random.default_rng(SEED)
    dev_draws = dev_rng.integers(0, len(dev), (REPEATS, len(dev)))
    frequencies, tie_frequencies = {}, {}
    for metric, matrix in matrices.items():
        totals = matrix[dev_draws].sum(axis=1)
        winners = totals.argmax(axis=1)  # Config columns have the frozen structural tie order.
        counts = np.bincount(winners, minlength=len(ordered))
        frequencies[metric] = {cid: {"count": int(count), "frequency": float(count / REPEATS)} for cid, count in zip(ordered, counts)}
        tied = totals == totals.max(axis=1, keepdims=True)
        tie_frequencies[metric] = {cid: float(frequency) for cid, frequency in zip(ordered, tied.mean(axis=0))}
    return {
        "status": "complete", "analysis": "primary" if budget == 512 else "exploratory_secondary",
        "annotation_source": ANNOTATION_SOURCE, "policy": "open", "budget": budget,
        "n_dev_information_needs": len(dev), "n_test_information_needs": len(test), "configuration_tie_order": ordered,
        "dev_selected_by_G": g_config, "dev_selected_by_U_sim": u_config, "dev_all_ties": ties, "dev_means": means,
        "test_selected_config_means": {selector: {metric: float(np.mean([indexed[("test", gid, cid)][metric] for gid in test]))
                                                   for metric in ("G_final", "U_sim", "fact_coverage", "contradiction_exposure", "obsolete_exposure")}
                                       for selector, cid in (("G", g_config), ("U_sim", u_config))},
        "test_U_sim_delta_U_selected_minus_G_selected": float(differences.mean()), "paired_test_group_bootstrap_95ci": interval,
        "bootstrap_repetitions": REPEATS, "bootstrap_seed": SEED,
        "interval_estimand": "Test-group sampling variation conditional on the fixed development-selected pair; development selection is not reoptimized inside this interval.",
        "development_bootstrap_selection_frequencies": frequencies,
        "development_bootstrap_tie_membership_frequencies": tie_frequencies,
        "selection_uncertainty_note": "Development frequencies are a separate instability diagnostic, not an end-to-end selection interval.",
        "test_group_differences": [{"group_id": gid, "difference": int(delta)} for gid, delta in zip(test, differences)],
        "constrained_policy": "descriptive_only_no_source_feasible_selector",
        "interpretation": "A zero or reversed gap is retained. Synthetic complete-fact coverage is not adjudicated human utility or clinical sufficiency.",
    }


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(value, sort_keys=True) if isinstance(value, (list, dict)) else value for key, value in row.items()})
    return stream.getvalue().encode("utf-8")


def evaluate(data, run, output):
    fail_unless(output not in {data, run}, "Output must be separate from frozen input data and model traces")
    spec = read_json(data / "specification.json")
    verify_file_manifest(data, spec)
    corpus, questions, oracle, groups = validate_data(read_jsonl(data / "corpus.jsonl"), read_jsonl(data / "questions.jsonl"), read_jsonl(data / "oracle.jsonl"), spec)
    manifest = validate_manifest(data, run, corpus, questions)
    tokenizer, tokenizer_files = load_pinned_tokenizer(run, manifest)
    chunk_ids = list(corpus)
    encoded = tokenizer([corpus[cid]["text"] for cid in chunk_ids], add_special_tokens=False, truncation=False,
                        return_offsets_mapping=True, verbose=False)
    tokenized = {cid: {"input_ids": encoded["input_ids"][i], "offset_mapping": encoded["offset_mapping"][i]} for i, cid in enumerate(chunk_ids)}
    compiled = compile_claims(oracle, corpus, tokenized)
    feasibility = structural_budget_feasibility(questions, oracle, compiled)
    rows, trace_hashes = evaluate_traces(run, corpus, questions, oracle, compiled, tokenized, tokenizer, manifest)
    primary, secondary = selection_analysis(rows, spec, 512), selection_analysis(rows, spec, 2048)
    provenance = {
        "input_files": {name: sha256(data / name) for name in ("corpus.jsonl", "questions.jsonl", "oracle.jsonl", "specification.json")},
        "run_manifest_sha256": sha256(run / "manifest.json"), "run_status_sha256": sha256(run / "status.json"),
        "run_identity": manifest["identity_hash"], "model_snapshots": manifest["identity"]["models"],
        "inference_code_sha256": manifest["identity"].get("code_sha256", {}),
        "generator_code_sha256": spec.get("code_sha256"), "evaluator_code_sha256": sha256(__file__),
        "tokenizer_file_manifest": tokenizer_files, "trace_sha256": trace_hashes,
    }
    selection = {"annotation_source": ANNOTATION_SOURCE, "valid_for_human_eval_claim": False,
                 "primary": primary, "exploratory_2048": secondary, "provenance": provenance}
    status = {
        "status": "complete", "annotation_source": ANNOTATION_SOURCE, "valid_for_human_eval_claim": False,
        "observed_records": len(rows), "expected_records": 2400, "worlds": len(groups), "tasks": len(questions),
        "scenario_world_counts": dict(sorted(Counter(pair[0]["scenario"] for pair in groups.values()).items())),
        "split_world_counts": dict(sorted(Counter(pair[0]["split"] for pair in groups.values()).items())),
        "generation_seed": SEED, "human_U_available": False, "human_E2_complete": False,
        "U_sim_available": True, "C_sim_available_for_constrained_tasks": True, "answer_A_available": False,
        "scoring": "Complete character spans mapped to pinned BERT offsets; every saved final token stream is verified against the original chunk token prefix. Full-text stage membership is scored separately.",
        "scope": "Controlled fictional simulation; no human labels, medical validity or independent real-world transfer claim.",
        "provenance": provenance,
    }
    payloads = {"per_record.csv": csv_bytes(rows), "summary.csv": csv_bytes(summarize(rows)),
                "selection.json": (json.dumps(selection, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
                "budget_feasibility.json": (json.dumps({**feasibility, "provenance": provenance}, indent=2, ensure_ascii=False) + "\n").encode("utf-8")}
    status["output_sha256"] = {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()}
    payloads["status.json"] = (json.dumps(status, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    output.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        temporary = output / (name + ".tmp")
        temporary.write_bytes(payload)
        temporary.replace(output / name)
    print(json.dumps({"status": "complete", "records": len(rows), "primary_G_choice": primary["dev_selected_by_G"],
                      "primary_U_sim_choice": primary["dev_selected_by_U_sim"], "primary_test_delta": primary["test_U_sim_delta_U_selected_minus_G_selected"],
                      "primary_95ci": primary["paired_test_group_bootstrap_95ci"], "human_E2_complete": False}, indent=2))
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "experiments/simulation/data/pilot_v2")
    parser.add_argument("--run", type=Path, default=ROOT / "experiments/runs/simulation_pilot_v2")
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/simulation/results/pilot_v2")
    args = parser.parse_args()
    evaluate(args.data.resolve(), args.run.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
