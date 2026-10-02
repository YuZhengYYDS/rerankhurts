"""Independent text-and-span evaluation of the strengthening experiment.

The parser is implemented in audit_data and never imports the generator. Saved
claim labels are not used to award credit. Only complete assertions present in
the actual delivered source intervals count as evidence. No human labels are
created, and fictional exact fact coverage is not semantic clinical utility.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "experiments/strengthening/data/strengthening_v1"
DEFAULT_RUN = ROOT / "experiments/runs/strengthening_v1"
DEFAULT_OUTPUT = ROOT / "experiments/strengthening/results/strengthening_v1"
TOKENIZER = ROOT / ".cache/models/google-bert--bert-base-uncased/86b5e0934494bd15c9632b12f734a8a67f723594"
STAGES = ("raw", "after_retrieval_policy", "pre_cap", "rerank", "post_cap", "post_policy")
METRICS = ("G_final", "U_sim", "fact_coverage", "supported_fact_count", "admissible_U_sim",
           "admissible_fact_coverage", "contradiction_exposure", "obsolete_exposure", "C_sim", "nonempty")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith(".gz") else data)


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def unique_index(rows, key):
    result = {}
    for row in rows:
        require(row.get(key) and row[key] not in result, f"Missing or duplicate {key}: {row.get(key)}")
        result[row[key]] = row
    return result


def dump_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, rows):
    rows = list(rows)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list, tuple)) else value
                             for key, value in row.items()})


def permitted(url, metadata):
    prefixes = metadata.get("allowed_url_prefixes", [])
    return not prefixes or any(url.startswith(prefix) for prefix in prefixes)


def parse_corpus_claims(corpus, truth):
    """Classify independently parsed text against the latent world fact table."""
    from .audit_data import classify, parse_claims
    parsed = {}
    for cid, chunk in corpus.items():
        values = []
        for claim in parse_claims(chunk["text"]):
            value = dict(claim)
            value.update(classify(truth, claim))
            value["chunk_id"] = cid
            values.append(value)
        parsed[cid] = values
    return parsed


def score_evidence(chunks, corpus, truth, metadata, parsed_claims=None):
    """Score full source texts or verified delivery fragments.

    Public interface also used by downstream answer scoring. Each fragment has
    chunk_id and optional char_start/char_end (otherwise full text). Actual source
    intervals may jointly cover an assertion across a window boundary. Missing
    non-whitespace characters prevent support. source_indices are one-based S1,
    S2, ... labels; source_index is populated only for a single intact fragment.
    This function verifies character text. Token authenticity is additionally
    checked by verify_final_context for saved model-run traces.
    """
    parsed_claims = parsed_claims if parsed_claims is not None else parse_corpus_claims(corpus, truth)
    required = set(metadata.get("required_fact_ids", truth["required_fact_ids"]))
    require(bool(required), "At least one required fact is necessary")
    support, admissible, contradictory, obsolete = set(), set(), set(), set()
    delivered_claims, delivered_urls, intervals = [], [], defaultdict(list)
    for source_index, fragment in enumerate(chunks, 1):
        cid = fragment["chunk_id"]
        require(cid in corpus, f"Unknown chunk: {cid}")
        source = corpus[cid]
        start, end = fragment.get("char_start", 0), fragment.get("char_end", len(source["text"]))
        require(type(start) is int and type(end) is int and 0 <= start < end <= len(source["text"]),
                f"Invalid source interval: {cid}/{start}:{end}")
        if "text" in fragment:
            require(fragment["text"] == source["text"][start:end], f"Delivered text differs from source: {cid}")
        if "url" in fragment:
            require(fragment["url"] == source["url"], f"Delivered URL differs from source: {cid}")
        delivered_urls.append(source["url"])
        intervals[cid].append((start, end, source_index))
    for cid, ranges in intervals.items():
        source = corpus[cid]
        allowed = permitted(source["url"], metadata)
        for claim in parsed_claims[cid]:
            left, right = claim["start_char"], claim["end_char"]
            cursor, contributors = left, []
            intact = [index for start, end, index in ranges if start <= left and right <= end]
            for start, end, index in sorted(ranges):
                if end <= cursor or start >= right:
                    continue
                if start > cursor and source["text"][cursor:min(start, right)].strip():
                    break
                contributors.append(index)
                cursor = max(cursor, end)
                if cursor >= right:
                    break
            if cursor >= right:
                record = dict(claim, source_index=intact[0] if intact else None,
                              source_indices=[intact[0]] if intact else sorted(contributors),
                              intact_single_source=bool(intact), admissible=allowed)
                delivered_claims.append(record)
                fid, status = claim.get("fact_id"), claim["status"]
                if fid not in required:
                    continue
                if status == "valid":
                    support.add(fid)
                    if allowed:
                        admissible.add(fid)
                elif status == "contradictory":
                    contradictory.add(fid)
                elif status == "obsolete":
                    obsolete.add(fid)
    nonempty = bool(delivered_urls)
    compliance = nonempty and all(permitted(url, metadata) for url in delivered_urls)
    return {"G_final": int(bool(set(delivered_urls) & set(metadata.get("gold_urls", [])))),
            "U_sim": int(support == required), "fact_coverage": len(support) / len(required),
            "supported_fact_count": len(support), "required_fact_count": len(required),
            "supported_fact_ids": sorted(support), "admissible_fact_ids": sorted(admissible),
            "admissible_U_sim": int(admissible == required), "admissible_fact_coverage": len(admissible) / len(required),
            "contradiction_exposure": int(bool(contradictory)), "obsolete_exposure": int(bool(obsolete)),
            "contradictory_fact_count": len(contradictory), "obsolete_fact_count": len(obsolete),
            "C_sim": int(compliance), "nonempty": int(nonempty),
            "joint_compliant_U_sim": int(compliance and admissible == required),
            "delivered_claims": delivered_claims}


def encode_corpus(corpus, tokenizer):
    ids = list(corpus)
    encoded = tokenizer([corpus[cid]["text"] for cid in ids], add_special_tokens=False,
                        return_offsets_mapping=True, truncation=False, verbose=False)
    return {cid: {"input_ids": encoded["input_ids"][i], "offset_mapping": encoded["offset_mapping"][i]}
            for i, cid in enumerate(ids)}


def verify_final_context(final, corpus, encoded, sep_token_id):
    """Verify every token interval and its exact source text before assigning credit."""
    chunks, stream, seen = final.get("chunks", []), [], defaultdict(list)
    for fragment in chunks:
        cid = fragment["chunk_id"]
        require(cid in corpus and cid in encoded, f"Unknown delivered chunk: {cid}")
        ids, offsets = encoded[cid]["input_ids"], encoded[cid]["offset_mapping"]
        start, end = fragment["source_token_start"], fragment["source_token_end"]
        require(type(start) is int and type(end) is int and 0 <= start < end <= len(ids), f"Invalid token interval: {cid}")
        require(fragment["token_ids"] == ids[start:end], f"Delivered token IDs differ: {cid}")
        left, right = fragment["char_start"], fragment["char_end"]
        text = corpus[cid]["text"]
        require(0 <= left <= offsets[start][0] and offsets[end - 1][1] <= right <= len(text),
                f"Character/token intervals disagree: {cid}")
        require(not text[left:offsets[start][0]].strip() and not text[offsets[end - 1][1]:right].strip(),
                f"Character interval includes unbudgeted text: {cid}")
        require(fragment["text"] == text[left:right], f"Delivered character text differs: {cid}")
        require(not any(start < other_end and other_start < end for other_start, other_end in seen[cid]),
                f"Overlapping duplicate delivery intervals: {cid}")
        seen[cid].append((start, end))
        if stream:
            stream.append(sep_token_id)
        stream.extend(fragment["token_ids"])
    require(final["token_ids"] == stream, "Final token stream is not the recorded chunks plus one SEP")
    require(final["used_tokens"] == len(stream) <= final["budget"], "Budget or token accounting mismatch")
    return True


def mask_cost_bound(units, required_count):
    """Exact minimum cost in a relaxed set-cover problem (<=4 facts).

    Units are (fact_bitmask, token_cost) and may be selected in arbitrary order.
    Duplicate/overlapping units are allowed in the relaxation, so its feasibility
    is a necessary condition, never a claim that the deployed ranker can achieve
    the resulting coverage. One separator is charged between selected units.
    """
    target = (1 << required_count) - 1
    cheapest = {}
    for mask, cost in units:
        if mask:
            cheapest[mask] = min(cheapest.get(mask, float("inf")), cost + 1)
    dp = [float("inf")] * (target + 1)
    dp[0] = 0
    for state in range(target + 1):
        for mask, cost in cheapest.items():
            combined = state | mask
            dp[combined] = min(dp[combined], dp[state] + cost)
    return None if dp[target] == float("inf") else int(dp[target] - 1)


def feasibility_bound(corpus, parsed, encoded, metadata, packing, window_tokens=192, window_stride=None):
    """Oracle relaxation for this packer's deliverable unit geometry.

    Prefix: any prefix up to a complete assertion. Whole: entire source chunk.
    Window: the backend's fixed token windows. The relaxation ignores ranking,
    overlap restrictions and cap order, and is explicitly an upper bound on U.
    """
    required = list(metadata["required_fact_ids"])
    bits = {fid: 1 << i for i, fid in enumerate(required)}
    units, admissible_units = [], []
    for cid, chunk in corpus.items():
        ids, offsets = encoded[cid]["input_ids"], encoded[cid]["offset_mapping"]
        claims = [claim for claim in parsed[cid] if claim["status"] == "valid" and claim.get("fact_id") in bits]
        if not ids or not claims:
            continue
        if packing == "whole":
            ranges = [(0, len(ids))]
        elif packing == "prefix":
            ends = {next((i + 1 for i, (_, right) in enumerate(offsets) if right >= claim["end_char"]), len(ids))
                    for claim in claims}
            ranges = [(0, end) for end in ends]
        elif packing == "window":
            require(window_stride in (None, window_tokens), "This bound implements nonoverlapping backend windows")
            # Build macro-units from every subset of facts in this source. A
            # macro can join adjacent windows to cover a boundary-spanning
            # assertion. Any prefix of every window is allowed in the relaxation
            # (the deployed packer may truncate only its final delivered unit).
            by_fact = defaultdict(list)
            for claim in claims:
                first = next(i for i, (_, right) in enumerate(offsets) if right > claim["start_char"])
                last = next(i + 1 for i, (_, right) in enumerate(offsets) if right >= claim["end_char"])
                by_fact[claim["fact_id"]].append((first, last))
            choices = [[None, *by_fact[fid]] for fid in required]
            for combination in itertools.product(*choices):
                mask, windows = 0, {}
                for fid, interval in zip(required, combination):
                    if interval is None:
                        continue
                    mask |= bits[fid]
                    first, last = interval
                    for left in range((first // window_tokens) * window_tokens, last, window_tokens):
                        windows[left] = max(windows.get(left, left), min(left + window_tokens, last))
                if mask:
                    cost = sum(right - left for left, right in windows.items()) + len(windows) - 1
                    units.append((mask, cost))
                    if permitted(chunk["url"], metadata):
                        admissible_units.append((mask, cost))
            continue
        else:
            raise ValueError(f"Unknown packing geometry: {packing}")
        for left, right in ranges:
            char_start, char_end = offsets[left][0], offsets[right - 1][1]
            mask = 0
            for claim in claims:
                if char_start <= claim["start_char"] and claim["end_char"] <= char_end:
                    mask |= bits[claim["fact_id"]]
            units.append((mask, right - left))
            if permitted(chunk["url"], metadata):
                admissible_units.append((mask, right - left))
    return {"packing": packing, "bound_type": "necessary_condition_from_oracle_relaxation",
            "minimum_relaxed_tokens": mask_cost_bound(units, len(required)),
            "minimum_admissible_relaxed_tokens": mask_cost_bound(admissible_units, len(required)),
            "interpretation": "Failure proves infeasibility under these units; passing does not establish deployed-packer reachability."}


def stage_flow(stage_scores, stage_rows):
    """Separate removed candidates from lost last valid support for required facts."""
    result = {}
    for before, after in zip(STAGES, STAGES[1:]):
        a, b = stage_scores[before], stage_scores[after]
        old = {row["chunk_id"] for row in stage_rows[before]}
        new = {row["chunk_id"] for row in stage_rows[after]}
        lost = set(a["supported_fact_ids"]) - set(b["supported_fact_ids"])
        key = f"{before}_to_{after}"
        result[key + "_deleted_candidates"] = len(old - new)
        result[key + "_deleted_candidate_fraction"] = len(old - new) / len(old) if old else 0.0
        result[key + "_added_candidates"] = len(new - old)
        result[key + "_lost_last_support_count"] = len(lost)
        result[key + "_lost_last_support_ids"] = sorted(lost)
        admissible_lost = set(a.get("admissible_fact_ids", [])) - set(b.get("admissible_fact_ids", []))
        result[key + "_lost_admissible_support_count"] = len(admissible_lost)
        result[key + "_full_coverage_loss"] = int(a["U_sim"] > b["U_sim"])
        if after == "rerank":
            require(old == new and not lost, "Pure reranking changed full-set membership/support")
    before, after = stage_scores["post_policy"], stage_scores["final"]
    result["budget_lost_last_support_ids"] = sorted(set(before["supported_fact_ids"]) - set(after["supported_fact_ids"]))
    result["budget_lost_last_support_count"] = len(result["budget_lost_last_support_ids"])
    result["budget_full_coverage_loss"] = int(before["U_sim"] > after["U_sim"])
    first = "retained" if after["U_sim"] else "candidate_not_covered"
    if stage_scores["raw"]["U_sim"] and not after["U_sim"]:
        first = next((stage for stage in STAGES[1:] if not stage_scores[stage]["U_sim"]), "budget")
    result["first_support_loss_stage"] = first
    return result


def evaluate(data, run, output, tokenizer, allow_partial=False):
    data, run, output = Path(data), Path(run), Path(output)
    corpus_all = unique_index(read_jsonl(data / "corpus.jsonl"), "chunk_id")
    questions = unique_index(read_jsonl(data / "questions.jsonl"), "qid")
    metadata = unique_index(read_jsonl(data / "metadata.jsonl"), "qid")
    truths = unique_index(read_jsonl(data / "truth.jsonl"), "group_id")
    require(set(questions) == set(metadata), "Question/metadata IDs differ")
    collections = defaultdict(dict)
    for cid, chunk in corpus_all.items():
        collections[chunk["collection_id"]][cid] = chunk
    run_status = read_json(run / "status.json") if (run / "status.json").exists() else {}
    manifest = read_json(run / "manifest.json")
    identity = manifest["identity"]
    require(identity["corpus_sha256"] == sha256(data / "corpus.jsonl") and
            identity["questions_sha256"] == sha256(data / "questions.jsonl"), "Run manifest input hashes differ")
    specification = read_json(data / "specification.json")
    require(identity.get("specification_sha256") == sha256(data / "specification.json"),
            "Dataset specification differs from the pre-inference run identity")
    for name, entry in specification["files"].items():
        require(Path(name).name == name, "Invalid dataset file path")
        require(sha256(data / name) == entry["sha256"], f"Frozen data hash mismatch: {name}")
    frozen_configs = {record["config_id"]: record for record in manifest["configurations"]}
    require(allow_partial or run_status.get("status") == "complete", "Run is not complete")
    rows, feasibility, trace_hashes, seen, config_sets = [], [], {}, set(), []
    for trace_path in sorted((run / "traces").glob("*.json.gz")):
        trace = read_json(trace_path)
        require(trace.get("identity_hash") == manifest["identity_hash"], "Foreign model trace identity")
        qid = trace["qid"]
        require(qid in questions and qid not in seen, f"Unexpected/duplicate trace qid: {qid}")
        seen.add(qid)
        trace_hashes[trace_path.name] = sha256(trace_path)
        question = questions[qid]
        meta = dict(metadata[qid], allowed_url_prefixes=question.get("allowed_url_prefixes", []))
        require(trace["question"] == question["question"] and trace["collection_id"] == question["collection_id"],
                f"Trace differs from public input: {qid}")
        require(trace.get("allowed_url_prefixes", []) == meta["allowed_url_prefixes"], f"Policy differs: {qid}")
        corpus = collections[question["collection_id"]]
        truth = truths[meta["group_id"]]
        parsed, encoded = parse_corpus_claims(corpus, truth), encode_corpus(corpus, tokenizer)
        bound_cache, ids_seen = {}, set()
        for record in trace["configurations"]:
            config = record["configuration"]
            require(config == frozen_configs.get(config["config_id"]), "Trace configuration differs from frozen manifest")
            require(config["config_id"] not in ids_seen, f"Duplicate configuration: {qid}")
            ids_seen.add(config["config_id"])
            final, stage_rows = record["final_context"], record["stages"]
            require(final["budget"] == config["budget"], "Configuration and delivered budget differ")
            verify_final_context(final, corpus, encoded, tokenizer.sep_token_id)
            stage_scores = {stage: score_evidence(stage_rows[stage], corpus, truth, meta, parsed) for stage in STAGES}
            stage_scores["final"] = score_evidence(final["chunks"], corpus, truth, meta, parsed)
            row = {key: meta.get(key) for key in ("qid", "group_id", "collection_id", "seed", "split", "test_regime",
                                                 "template_family", "scenario", "variant_id", "policy")}
            row.update(config)
            row.update({"factor_" + key: value for key, value in meta.get("factors", {}).items()
                        if not isinstance(value, (list, dict))})
            row.update({key: value for key, value in stage_scores["final"].items() if key != "delivered_claims"})
            for stage, scores in stage_scores.items():
                row.update({f"{stage}_{key}": scores[key] for key in METRICS})
                row[f"{stage}_n_source_fragments"] = len(final["chunks"] if stage == "final" else stage_rows[stage])
            row.update(stage_flow(stage_scores, stage_rows))
            row.update(context_tokens=final["used_tokens"], rerank_pairs=record.get("rerank_pairs"),
                       annotation_source="independent_synthetic_text_parser", valid_for_human_eval_claim=False)
            if record.get("score_visibility"):
                visible = [{"chunk_id": cid, "char_start": span["char_start"], "char_end": span["char_end"]}
                           for cid, spans in record["score_visibility"].items() for span in spans]
                visibility = score_evidence(visible, corpus, truth, meta, parsed)
                row["score_visible_U_sim"] = visibility["U_sim"]
                row["score_visible_fact_coverage"] = visibility["fact_coverage"]
                intact = {claim["fact_id"] for claim in visibility["delivered_claims"]
                          if claim["status"] == "valid" and claim["intact_single_source"]
                          and claim.get("fact_id") in set(meta["required_fact_ids"])}
                row["score_single_call_visible_U_sim"] = int(intact == set(meta["required_fact_ids"]))
                row["score_single_call_visible_fact_coverage"] = len(intact) / len(meta["required_fact_ids"])
            row["raw_max_chunks_per_source"] = max(Counter(item["url"] for item in stage_rows["raw"]).values(), default=0)
            row["final_delivery_sha256"] = hashlib.sha256(json.dumps(
                [(item["chunk_id"], item["source_token_start"], item["source_token_end"], item["token_ids"])
                 for item in final["chunks"]], separators=(",", ":")).encode()).hexdigest()
            key = (config["packing"], tuple(sorted(item["chunk_id"] for item in stage_rows["post_policy"])))
            if key not in bound_cache:
                subcorpus = {cid: corpus[cid] for cid in key[1]}
                bound_cache[key] = feasibility_bound(subcorpus, parsed, encoded, meta, config["packing"])
            bound = bound_cache[key]
            minimum = bound["minimum_relaxed_tokens"]
            row["necessary_feasibility_pass"] = int(minimum is not None and minimum <= config["budget"])
            require(not row["U_sim"] or row["necessary_feasibility_pass"], "Observed coverage exceeds proposed oracle upper bound")
            rows.append(row)
        config_sets.append(ids_seen)
        require(ids_seen == set(frozen_configs), "Task is missing frozen configurations")
        for packing in ("prefix", "whole", "window"):
            bound = feasibility_bound(corpus, parsed, encoded, meta, packing)
            for budget in (256, 512, 1024, 2048):
                minimum = bound["minimum_relaxed_tokens"]
                feasibility.append({"qid": qid, "group_id": meta["group_id"], "split": meta["split"], "budget": budget,
                                    "corpus_U_upper_bound": int(minimum is not None and minimum <= budget), **bound})
    require(bool(rows), "No traces to evaluate")
    require(all(values == config_sets[0] for values in config_sets), "Configuration matrix differs across tasks")
    complete = seen == set(questions) and run_status.get("status") == "complete"
    require(allow_partial or complete, "Missing task traces")
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "per_record.csv", rows)
    write_csv(output / "feasibility.csv", feasibility)
    status = {"status": "complete" if complete else "partial", "observed_tasks": len(seen), "expected_tasks": len(questions),
              "observed_records": len(rows), "configurations": len(config_sets[0]),
              "annotation_source": "independent_synthetic_text_parser", "human_audit_complete": False,
              "scope": "Fictional administrative exact fact coverage; no human utility or clinical generalization claim.",
              "evaluator_sha256": sha256(__file__), "parser_sha256": sha256(Path(__file__).with_name("audit_data.py")),
              "run_manifest_sha256": sha256(run / "manifest.json"), "run_status_sha256": sha256(run / "status.json"),
              "run_identity_hash": manifest["identity_hash"],
              "study_plan_sha256": identity["study_plan_sha256"],
              "input_hashes": {name: sha256(data / name) for name in ("corpus.jsonl", "questions.jsonl", "metadata.jsonl", "truth.jsonl", "specification.json")},
              "trace_sha256": trace_hashes,
              "output_hashes": {name: sha256(output / name) for name in ("per_record.csv", "feasibility.csv")}}
    dump_json(output / "status.json", status)
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tokenizer", type=Path, default=TOKENIZER)
    parser.add_argument("--allow-partial", action="store_true", help="Smoke verification only; output remains explicitly partial")
    args = parser.parse_args(argv)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, use_fast=True)
    require(tokenizer.is_fast and tokenizer.sep_token_id is not None, "Pinned fast tokenizer with SEP required")
    result = evaluate(args.data, args.run, args.output, tokenizer, args.allow_partial)
    print(json.dumps({key: result[key] for key in ("status", "observed_tasks", "expected_tasks", "observed_records",
                                                  "configurations", "human_audit_complete")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
