"""Independent text-to-truth audit; never imports the workload generator.

Public evaluator API: parse_claims(text) returns semantic statements with exact
character spans; classify(truth, claim) derives fact_id/status from the dated
functional fact table. Generator labels are only checked against these results.
This is automated semantic/structural quality control, not human annotation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

LABEL_TO_KEY = {"service route": "route", "file review interval": "review_days",
                "release authorization code": "release_code", "archival retention period": "retention_days"}
SUBJECT = r"(?P<subject>[A-Za-z0-9-]+)"
VERSION = r"(?P<version>R\d+)"
LABEL = r"(?P<label>[a-z -]+)"
VALUE = r"(?P<value>[^.\n]+)"
GRAMMARS = {
    "prose": re.compile(r"For entity " + SUBJECT + r" in revision " + VERSION + r", the " + LABEL + r" is " + VALUE + r"\."),
    "list": re.compile(r"- Entity " + SUBJECT + r"; revision " + VERSION + r"; " + LABEL + r": " + VALUE + r"\."),
    "qa": re.compile(r"Q: Under revision " + VERSION + r", what is the " + LABEL + r" for entity " + SUBJECT + r"\?\nA: " + VALUE + r"\."),
}
VALUE_GRAMMARS = {"route": re.compile(r"[A-Z][a-z]+-\d{2}"), "review_days": re.compile(r"[1-9]\d* working days"),
                  "release_code": re.compile(r"Permit-[A-Z]\d{2}"), "retention_days": re.compile(r"[1-9]\d* calendar days")}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def unique(rows, key):
    result = {}
    for row in rows:
        value = row.get(key)
        require(isinstance(value, str) and value and value not in result, f"Missing or duplicate {key}: {value}")
        result[value] = row
    return result


def parse_claims(text):
    """Parse complete prose/list/QA statements without generator metadata."""
    require(isinstance(text, str), "Document text must be a string")
    result = []
    for family, pattern in GRAMMARS.items():
        for match in pattern.finditer(text):
            fields = match.groupdict()
            require(fields["label"] in LABEL_TO_KEY, "Unknown functional predicate in document")
            key = LABEL_TO_KEY[fields["label"]]
            value = fields["value"].strip()
            require(VALUE_GRAMMARS[key].fullmatch(value) is not None, f"Malformed value for {key}")
            result.append({"start_char": match.start(), "end_char": match.end(),
                           "subject": fields["subject"], "version": fields["version"],
                           "key": key, "value": value, "template_family": family})
    result.sort(key=lambda c: c["start_char"])
    require(all(a["end_char"] <= b["start_char"] for a, b in zip(result, result[1:])), "Overlapping parsed statements")
    markers = list(re.finditer(r"For entity |(?m:^- Entity )|(?m:^Q: Under revision )", text))
    require(len(markers) == len(result), "Incomplete or unrecognized statement grammar")
    return result


def classify(truth, claim):
    """Classify a functional assertion using truth, subject and validity dates."""
    if claim["subject"] != truth["entity"]:
        return {"fact_id": None, "status": "irrelevant"}
    facts = {f["key"]: f for f in truth["facts"]}
    require(claim["key"] in facts, "Claim predicate is not required by this world")
    fact = facts[claim["key"]]
    require(fact.get("exclusive") is True, "Contradiction requires an explicitly single-valued predicate")
    require(claim["version"] in truth["versions"], "Unknown document revision")
    interval = truth["versions"][claim["version"]]
    start, end, as_of = (date.fromisoformat(v) for v in (interval["valid_from"], interval["valid_to"], truth["as_of"]))
    require(start < end, "Invalid version validity interval")
    if start <= as_of < end:
        require(claim["version"] == truth["current_version"], "Truth has inconsistent current revision")
        status = "valid" if claim["value"] == fact["value"] else "contradictory"
    else:
        require(claim["version"] == truth["obsolete_version"] and end <= as_of,
                "Only current or superseded revisions are defined")
        require(claim["value"] == fact["old_value"], "Superseded statement disagrees with the historical truth")
        status = "obsolete"
    return {"fact_id": fact["fact_id"], "status": status}


def audit_dataset(data, output=None, human_sample_worlds=60):
    data = Path(data)
    spec = json.loads((data / "specification.json").read_text(encoding="utf-8"))
    require(spec.get("schema_version") == "strengthening-v1" and spec.get("annotation_source") == "synthetic_oracle", "Unexpected dataset schema/scope")
    names = ("corpus.jsonl", "questions.jsonl", "metadata.jsonl", "truth.jsonl", "claims.jsonl")
    loaded = {}
    for name in names:
        raw = (data / name).read_bytes()
        loaded[name] = read_rows(data / name)
        require(hashlib.sha256(raw).hexdigest() == spec["files"][name]["sha256"], f"Data hash mismatch: {name}")
        require(len(loaded[name]) == spec["files"][name]["rows"], f"Data row count mismatch: {name}")
    corpus = unique(loaded["corpus.jsonl"], "chunk_id")
    questions = unique(loaded["questions.jsonl"], "qid")
    metadata = unique(loaded["metadata.jsonl"], "qid")
    truth = unique(loaded["truth.jsonl"], "group_id")
    claims = unique(loaded["claims.jsonl"], "claim_id")
    require(set(questions) == set(metadata), "Question/metadata IDs differ")
    collections, collection_meta, groups = defaultdict(list), {}, defaultdict(list)
    for c in corpus.values():
        require(set(c) == {"chunk_id", "collection_id", "url", "text"}, "Corpus exposes unexpected fields")
        require(isinstance(c["text"], str) and c["text"].strip(), "Empty document")
        require((urlsplit(c["url"]).hostname or "").endswith(".invalid"), "Expected fictional source host")
        collections[c["collection_id"]].append(c)
    for qid, q in questions.items():
        require(set(q) == {"qid", "collection_id", "question", "allowed_url_prefixes"}, "Questions expose unexpected fields")
        m = metadata[qid]
        require(q["collection_id"] == m["collection_id"] and m["collection_id"] not in collection_meta, "Collection task mapping is not one-to-one")
        require(m["group_id"] in truth, "Unknown world")
        w = truth[m["group_id"]]
        for key in ("seed", "split", "test_regime", "template_family", "scenario", "policy", "required_fact_ids", "expected_keys"):
            require(m[key] == w[key], f"World/task mismatch: {key}")
        require(set(w["expected_keys"]) == {f["key"] for f in w["facts"]}, "Expected field schema differs from truth")
        require(set(w["required_fact_ids"]) == {f["fact_id"] for f in w["facts"]} and len(w["facts"]) in {2, 3, 4}, "Invalid required fact table")
        require(bool(q["allowed_url_prefixes"]) == (m["policy"] == "constrained"), "Policy projection mismatch")
        require(w["entity"] in q["question"] and w["current_version"] in q["question"], "Question lacks its subject/version")
        for fact in w["facts"]:
            require(fact["value"] != fact["old_value"], "Current and obsolete values must differ")
            require(fact["value"] not in q["question"] and fact["old_value"] not in q["question"], "Answer leaked into question")
        require(len(collections[m["collection_id"]]) == 80, "Every task requires exactly 80 isolated chunks")
        collection_meta[m["collection_id"]] = m
        groups[m["group_id"]].append(qid)
    require(set(collections) == set(collection_meta), "Unassigned collection or missing collection")
    require(set(groups) == set(truth), "Unassigned latent world")
    provided = {}
    for claim in claims.values():
        require(claim["chunk_id"] in corpus and corpus[claim["chunk_id"]]["collection_id"] == claim["collection_id"], "Claim crosses collection boundary")
        key = (claim["chunk_id"], claim["start_char"], claim["end_char"])
        require(key not in provided, "Duplicate annotated span")
        provided[key] = claim
    reparsed, observed = [], set()
    valid_by_chunk, status_counts = defaultdict(set), Counter()
    fields = ("subject", "version", "key", "value", "fact_id", "status")
    for cid, c in corpus.items():
        m = collection_meta[c["collection_id"]]
        w = truth[m["group_id"]]
        for semantic in parse_claims(c["text"]):
            require(semantic["template_family"] == m["template_family"], "Document grammar differs from declared family")
            assertion = {**semantic, **classify(w, semantic)}
            key = (cid, assertion["start_char"], assertion["end_char"])
            require(key in provided, "Text assertion is missing from generator annotation")
            expected = provided[key]
            require(all(assertion[k] == expected[k] for k in fields), "Generator annotation disagrees with independently parsed truth")
            observed.add(key)
            status_counts[assertion["status"]] += 1
            reparsed.append({"claim_id": expected["claim_id"], "collection_id": c["collection_id"], "chunk_id": cid, **assertion})
            if assertion["status"] == "valid":
                valid_by_chunk[cid].add(assertion["fact_id"])
    require(observed == set(provided), "Generator has annotations with no matching complete text assertion")
    support_diagnostics = []
    for qid, m in metadata.items():
        required = set(m["required_fact_ids"])
        chunks = collections[m["collection_id"]]
        supported = set().union(*(valid_by_chunk[c["chunk_id"]] for c in chunks))
        q = questions[qid]
        admissible = set().union(*(valid_by_chunk[c["chunk_id"]] for c in chunks
                                 if not q["allowed_url_prefixes"] or any(c["url"].startswith(p) for p in q["allowed_url_prefixes"])))
        require(supported == required and admissible == required, "World lacks complete valid/admissible corpus support")
        require(m["gold_urls"] and set(m["gold_urls"]) <= {c["url"] for c in chunks}, "Designated URL absent from its collection")
        for cover in m["equivalent_support_sets"]:
            require(cover and all(cid in corpus and corpus[cid]["collection_id"] == m["collection_id"] for cid in cover), "Support set crosses collections")
            require(set().union(*(valid_by_chunk[cid] for cid in cover)) == required, "Declared support set is not a full independently verified cover")
        if m["scenario"] == "equivalent_support":
            require(len(m["equivalent_support_sets"]) >= 2 and not set(m["equivalent_support_sets"][0]) & set(m["equivalent_support_sets"][1]), "Equivalent covers must be distinct complete sets")
        max_per_url = max(Counter(c["url"] for c in chunks).values())
        require(max_per_url == m["factors"]["max_chunks_per_url"], "Incorrect source multiplicity factor")
        support_diagnostics.append({"qid": qid, "supporting_chunks_per_fact": {f: sum(f in valid_by_chunk[c["chunk_id"]] for c in chunks) for f in sorted(required)},
                                    "max_chunks_per_url": max_per_url,
                                    "cap_structurally_inactive": {str(cap): max_per_url <= cap for cap in (1, 2, 4)}})
    pair_count = 0
    for gid, qids in groups.items():
        require(len(qids) == 2, "Each independent world must have exactly two variants")
        by_variant = {metadata[q]["variant_id"]: q for q in qids}
        require(set(by_variant) == {"low_concentration", "high_concentration"}, "Missing paired intervention")
        low, high = (questions[by_variant[k]] for k in ("low_concentration", "high_concentration"))
        require(low["question"] == high["question"] and low["allowed_url_prefixes"] == high["allowed_url_prefixes"], "Paired task changes question/policy")
        a, b = collections[low["collection_id"]], collections[high["collection_id"]]
        require([x["text"] for x in a] == [x["text"] for x in b], "Paired intervention changes text or candidate order")
        require(all(urlsplit(x["url"]).netloc == urlsplit(y["url"]).netloc for x, y in zip(a, b)), "Paired URL intervention changes publisher/admissibility")
        require(sum(x["url"] != y["url"] for x, y in zip(a, b)) == 12, "Expected exactly twelve URL grouping interventions")
        pair_count += 1
    for seed in spec["seeds"]:
        for split, expected_n in (("dev", spec["dev_per_seed"]), ("test", spec["test_per_seed"])):
            part = [w for w in truth.values() if w["seed"] == seed and w["split"] == split]
            require(len(part) == expected_n, "Seed/split counts differ from specification")
            policies = Counter(w["policy"] for w in part)
            require(abs(policies["open"] - policies["constrained"]) <= 1, "Unbalanced synthetic policy design")
            require(all(w["template_family"] != "qa" for w in part) if split == "dev"
                    else sum(w["template_family"] == "qa" for w in part) == expected_n // 2,
                    "Heldout template allocation differs from frozen design")
    report = {"status": "PASS", "annotation_source": "synthetic_oracle", "human_audit_completed": False,
              "human_E2_completed": False, "model_outputs_read": False,
              "worlds": len(truth), "tasks": len(questions), "chunks": len(corpus),
              "claims_independently_parsed": len(reparsed), "claim_status_counts": dict(status_counts),
              "paired_URL_only_interventions_verified": pair_count,
              "seed_split_worlds": dict(Counter(f"{w['seed']}/{w['split']}" for w in truth.values())),
              "template_worlds": dict(Counter(w["template_family"] for w in truth.values())),
              "scenario_worlds": dict(Counter(w["scenario"] for w in truth.values())),
              "support_diagnostics": support_diagnostics,
              "input_sha256": {name: hashlib.sha256((data / name).read_bytes()).hexdigest() for name in (*names, "specification.json")},
              "audit_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if output is not None:
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (output / "claims_reparsed.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in reparsed), encoding="utf-8")
        # Round-robin template/scenario strata within equal seed quotas. The
        # sampling key is fixed before inference and never refers to winners.
        sample_limit = min(max(0, human_sample_worlds), len(truth))
        seed_values = sorted({w["seed"] for w in truth.values()})
        selected = []
        for seed_index, seed in enumerate(seed_values):
            quota = sample_limit // len(seed_values) + int(seed_index < sample_limit % len(seed_values))
            buckets = defaultdict(list)
            for gid, world in truth.items():
                if world["seed"] == seed:
                    buckets[(world["template_family"], world["scenario"])].append(gid)
            for values in buckets.values():
                values.sort(key=lambda gid: hashlib.sha256(("audit-sample-20261002|" + gid).encode()).hexdigest())
            chosen = []
            while len(chosen) < quota and any(buckets.values()):
                for key in sorted(buckets):
                    if buckets[key] and len(chosen) < quota:
                        chosen.append(buckets[key].pop(0))
            selected.extend(chosen)
        packet = [{"group_id": gid, "truth": truth[gid], "qids": groups[gid],
                   "collection_ids": [questions[q]["collection_id"] for q in groups[gid]],
                   "documents_file": "../corpus.jsonl", "instructions": "Compare the text with the fact table; inspect full subject/version/value statements and source rules. No model outcomes or configurations are provided.",
                   "human_review_status": "pending"} for gid in selected]
        (output / "human_audit_packet.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in packet), encoding="utf-8")
        with (output / "human_audit_template.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["group_id", "reviewer_slot", "reviewer_id", "text_truth_consistent", "complete_claim_spans", "temporal_status_correct", "source_policy_correct", "comments", "completed_at"])
            writer.writeheader()
            writer.writerows({"group_id": gid, "reviewer_slot": slot} for gid in selected for slot in ("A", "B"))
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, default=Path("experiments/strengthening/data/strengthening_v1"))
    p.add_argument("--output", type=Path)
    p.add_argument("--human-sample-worlds", type=int, default=60)
    args = p.parse_args()
    report = audit_dataset(args.data, args.output or args.data / "audit", args.human_sample_worlds)
    print(json.dumps({k: v for k, v in report.items() if k not in {"support_diagnostics", "input_sha256"}}, indent=2))


if __name__ == "__main__":
    main()
