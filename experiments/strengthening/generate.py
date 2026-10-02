"""Generate the frozen strengthening workload without inspecting model outcomes.

Public schemas (the backend reads only these two files):
  corpus.jsonl: chunk_id, collection_id, url, text
  questions.jsonl: qid, collection_id, question, allowed_url_prefixes
Evaluation-only schemas:
  truth.jsonl: one latent world, its dated functional facts and values
  metadata.jsonl: qid/group/seed/split/template/variant/policy and factor labels
  claims.jsonl: complete claim spans and generator assertions for independent audit
  specification.json: frozen dimensions, file hashes and generation provenance

The two collections of a world have identical ordered texts and questions. Only
URL grouping of twelve same-publisher chunks changes. Text duplication is a
separate between-world factor. No model, ranking, metric or previous run is read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

DEFAULT_SEEDS = (20261002, 20261003, 20261004)
SCENARIOS = ("single_chunk", "same_url_complementary", "cross_url_complementary",
             "equivalent_support", "temporal_conflict", "position")
LABELS = {"route": "service route", "review_days": "file review interval",
          "release_code": "release authorization code", "retention_days": "archival retention period"}
VARIANTS = ("low_concentration", "high_concentration")
FILLER = (
    "The desk records the arrival of correspondence and preserves the accompanying cover sheet.",
    "Index headings help readers locate memoranda but do not themselves establish an operative instruction.",
    "A clerk records each administrative handoff in the correspondence ledger for later inspection.",
    "The document directory includes editorial notices and references to archived workflow records.",
    "Copies with missing pages are returned to the records desk for clarification before filing.",
    "This invented service administration exercise does not describe a real organization or clinical procedure.",
)


def identifier(*parts):
    return hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:28]


def jsonl_bytes(rows):
    return b"".join((json.dumps(r, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8") for r in rows)


def statement(subject, version, key, value, family):
    label = LABELS[key]
    if family == "prose":
        return f"For entity {subject} in revision {version}, the {label} is {value}."
    if family == "list":
        return f"- Entity {subject}; revision {version}; {label}: {value}."
    if family == "qa":
        return f"Q: Under revision {version}, what is the {label} for entity {subject}?\nA: {value}."
    raise ValueError(f"Unknown rendering family: {family}")


def filler(rng, words):
    pieces = []
    while sum(len(x.split()) for x in pieces) < words:
        pieces.append(rng.choice(FILLER))
    return " ".join(pieces)


def make_world(seed, split, index, family, regime, policy, scenario, fact_count, duplicate_count):
    group = identifier("world", seed, split, index)
    rng = random.Random(int(group, 16))
    entity = "Veloria-" + group[:8].upper()
    version_number = rng.randint(3, 9)
    value_draws = {
        "route": lambda: rng.choice(("Aster", "Cobalt", "Juniper", "Willow")) + f"-{rng.randint(10, 88)}",
        "review_days": lambda: f"{rng.choice((3, 5, 7, 11, 14, 21))} working days",
        "release_code": lambda: f"Permit-{rng.choice('KMRV')}{rng.randint(10, 88)}",
        "retention_days": lambda: f"{rng.choice((30, 60, 90, 120, 180))} calendar days",
    }
    # The same value distributions generate both versions: no fixed word,
    # number range or permit prefix gives away which statement is incorrect.
    all_facts = {}
    for key, draw in value_draws.items():
        current_value, old_value = draw(), draw()
        while old_value == current_value:
            old_value = draw()
        all_facts[key] = (current_value, old_value)
    keys = rng.sample(list(LABELS), fact_count)
    facts = [{"fact_id": identifier(group, key), "key": key, "value": all_facts[key][0],
              "old_value": all_facts[key][1], "exclusive": True} for key in keys]
    current, old = f"R{version_number}", f"R{version_number - 1}"
    world = {"group_id": group, "entity": entity, "current_version": current,
             "obsolete_version": old, "as_of": "2035-06-01",
             "versions": {old: {"valid_from": "2033-01-01", "valid_to": "2035-01-01"},
                          current: {"valid_from": "2035-01-01", "valid_to": "2037-01-01"}},
             "facts": facts, "required_fact_ids": [f["fact_id"] for f in facts],
             "expected_keys": keys, "seed": seed, "split": split, "test_regime": regime,
             "template_family": family, "policy": policy, "scenario": scenario,
             "duplicate_count": duplicate_count}
    return world, rng


def render_chunk(world, rng, claims, prefix_words, suffix_words):
    subject = claims[0]["subject"] if claims else world["entity"]
    parts = [f"Service administration record\nEntity: {subject}\nPublisher: the fictional local records office.\n\n"]
    if prefix_words:
        parts.append(filler(rng, prefix_words) + "\n\n")
    spans = []
    for assertion in claims:
        sentence = statement(assertion["subject"], assertion["version"], assertion["key"], assertion["value"], world["template_family"])
        start = sum(map(len, parts))
        parts.append(sentence)
        spans.append({**assertion, "start_char": start, "end_char": start + len(sentence)})
        parts.append("\n\n")
    parts.append(filler(rng, suffix_words))
    return "".join(parts), spans


def world_documents(world, rng):
    """Construct one semantic collection before choosing either URL intervention."""
    group = world["group_id"]
    registry = f"https://{group[:12]}.registry.invalid/"
    external = f"https://{group[:12]}.consortium.invalid/"
    designated = registry + "operative-record"
    family, scenario = world["template_family"], world["scenario"]
    long_position = scenario == "position"
    length_words = rng.randint(180, 900) if long_position else rng.randint(60, 360)
    position_fraction = rng.uniform(.05, .95)
    prefix_words = int(length_words * position_fraction)
    suffix_words = max(10, length_words - prefix_words)
    documents = []
    primary_slots = []
    equivalent_sets = []

    def assertion(fact, status="valid", near=False):
        return {"fact_id": None if near else fact["fact_id"], "key": fact["key"],
                "subject": world["entity"] + "-Annex" if near else world["entity"],
                "version": world["obsolete_version"] if status == "obsolete" else world["current_version"],
                "value": fact["value"] if status == "valid" else fact["old_value"],
                "status": "irrelevant" if near else status}

    def add(url, claims, prefix=None, suffix=None):
        text, spans = render_chunk(world, rng, claims,
                                  prefix_words if prefix is None else prefix,
                                  suffix_words if suffix is None else suffix)
        documents.append({"url": url, "text": text, "spans": spans})
        return len(documents) - 1

    if scenario == "single_chunk":
        primary_slots.append(add(designated, [assertion(f) for f in world["facts"]]))
    else:
        for i, fact in enumerate(world["facts"]):
            same_page = scenario in {"same_url_complementary", "temporal_conflict", "position"}
            url = designated if i == 0 or same_page else registry + f"operative-part-{i}"
            primary_slots.append(add(url, [assertion(fact)]))
    equivalent_sets.append(primary_slots.copy())
    if scenario == "equivalent_support":
        equivalent_sets.append([add(registry + "independent-current", [assertion(f) for f in world["facts"]])])
        add(external + "complete-current", [assertion(f) for f in world["facts"]])
    # Old statements match the old truth, while a current wrong functional value
    # is a direct contradiction. These are distinct temporal/semantic conditions.
    old_facts = world["facts"] if scenario == "temporal_conflict" else world["facts"][:1]
    add(registry + "archive", [assertion(f, "obsolete") for f in old_facts])
    add(external + "disputed", [assertion(f, "contradictory") for f in old_facts])
    for i in range(3):
        add(registry + f"annex-{i}", [assertion(world["facts"][i % len(world["facts"])], near=True)], prefix=rng.randint(0, 100), suffix=40)
    concentrated_slots = []
    for i in range(world["duplicate_count"]):
        source = documents[primary_slots[0]]
        documents.append({"url": registry + f"replica-{i}", "text": source["text"],
                          "spans": [dict(s) for s in source["spans"]]})
        concentrated_slots.append(len(documents) - 1)
    while len(concentrated_slots) < 12:
        concentrated_slots.append(add(registry + f"navigation-{len(concentrated_slots)}", [], prefix=rng.randint(0, 100), suffix=40))
    while len(documents) < 80:
        i = len(documents)
        host = external if i % 4 == 0 else registry
        add(host + f"background-{i}", [], prefix=rng.randint(0, 100), suffix=rng.randint(15, 80))
    if len(documents) != 80:
        raise ValueError("Document plan exceeds the fixed 80-chunk collection")
    order = list(range(80))
    rng.shuffle(order)
    factors = {"support_structure": scenario, "required_fact_count": len(world["facts"]),
               "duplicate_chunks": world["duplicate_count"], "target_length_words": length_words,
               "target_support_position_fraction": position_fraction,
               "support_prefix_words": prefix_words, "concentration_changed_slots": len(concentrated_slots)}
    return documents, order, set(concentrated_slots), designated, registry, equivalent_sets, factors


def build(seed_values=DEFAULT_SEEDS, dev_per_seed=20, test_per_seed=100):
    if dev_per_seed < 1 or test_per_seed < 1 or not seed_values or len(set(seed_values)) != len(seed_values):
        raise ValueError("Positive split sizes and unique generation seeds are required")
    corpus, questions, metadata, truth, claims = [], [], [], [], []
    for seed in seed_values:
        design = random.Random(seed)
        for split, count in (("dev", dev_per_seed), ("test", test_per_seed)):
            families = ["prose" if i % 2 == 0 else "list" for i in range(count)]
            if split == "test":
                families = ["qa" if i < count // 2 else ("prose" if i % 2 == 0 else "list") for i in range(count)]
            policies = ["open" if i % 2 == 0 else "constrained" for i in range(count)]
            offset = 0 if split == "dev" else dev_per_seed
            scenarios = [SCENARIOS[(i + offset) % len(SCENARIOS)] for i in range(count)]
            fact_counts = [2 + (i + offset) % 3 for i in range(count)]
            duplicates = [(0, 4, 12)[(i + offset) % 3] for i in range(count)]
            for values in (families, policies, scenarios, fact_counts, duplicates):
                design.shuffle(values)
            for index in range(count):
                family = families[index]
                regime = "heldout_template" if family == "qa" else ("development" if split == "dev" else "seen_template")
                world, rng = make_world(seed, split, index, family, regime, policies[index], scenarios[index], fact_counts[index], duplicates[index])
                documents, order, slots, designated, registry, covers, factors = world_documents(world, rng)
                truth.append(world)
                question_labels = {"route": "routing destination", "review_days": "time until record review",
                                   "release_code": "permit identifier for release", "retention_days": "duration of archival retention"}
                requested = ", ".join(question_labels[k] for k in world["expected_keys"])
                question = (f"As of {world['as_of']}, use revision {world['current_version']} for fictional entity {world['entity']}. "
                            f"Report its {requested}. Return unknown for any field not supported by the supplied records.")
                allowed = [registry] if world["policy"] == "constrained" else []
                if allowed:
                    question += f" Only material at {registry} is an allowed source."
                for variant in VARIANTS:
                    collection = identifier(world["group_id"], variant, "collection")
                    qid = identifier(world["group_id"], variant, "question")
                    ids = {i: identifier(collection, "chunk", i) for i in range(80)}
                    urls = []
                    for i in order:
                        doc = documents[i]
                        url = designated if variant == "high_concentration" and i in slots else doc["url"]
                        urls.append(url)
                        corpus.append({"chunk_id": ids[i], "collection_id": collection, "url": url, "text": doc["text"]})
                        for j, span in enumerate(doc["spans"]):
                            claims.append({"claim_id": identifier(ids[i], j), "collection_id": collection,
                                           "chunk_id": ids[i], **span})
                    questions.append({"qid": qid, "collection_id": collection, "question": question, "allowed_url_prefixes": allowed})
                    metadata.append({"qid": qid, "group_id": world["group_id"], "collection_id": collection,
                        "seed": seed, "split": split, "test_regime": regime, "template_family": family,
                        "scenario": world["scenario"], "variant_id": variant, "policy": world["policy"],
                        "gold_urls": [designated], "required_fact_ids": world["required_fact_ids"],
                        "expected_keys": world["expected_keys"],
                        "equivalent_support_sets": [[ids[i] for i in cover] for cover in covers],
                        "factors": {**factors, "max_chunks_per_url": max(Counter(urls).values()),
                                    "source_concentration": variant}})
    return corpus, questions, metadata, truth, claims


def write_dataset(output, seeds=DEFAULT_SEEDS, dev_per_seed=20, test_per_seed=100):
    rows = build(tuple(seeds), dev_per_seed, test_per_seed)
    names = ("corpus.jsonl", "questions.jsonl", "metadata.jsonl", "truth.jsonl", "claims.jsonl")
    payloads = {name: jsonl_bytes(value) for name, value in zip(names, rows)}
    plan_path = Path(__file__).with_name("study_plan.json")
    plan_bytes = plan_path.read_bytes()
    spec = {"schema_version": "strengthening-v1", "annotation_source": "synthetic_oracle",
        "status": "generated_requires_independent_audit", "seeds": list(seeds),
        "dev_per_seed": dev_per_seed, "test_per_seed": test_per_seed,
        "counts": {"worlds": len(rows[3]), "tasks": len(rows[1]), "collections": len(rows[1]),
                   "chunks_per_collection": 80, "chunks": len(rows[0])},
        "public_files": ["corpus.jsonl", "questions.jsonl"],
        "evaluation_only_files": ["truth.jsonl", "metadata.jsonl", "claims.jsonl"],
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "study_plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
        "study_plan_snapshot": json.loads(plan_bytes),
        "files": {name: {"sha256": hashlib.sha256(payload).hexdigest(), "rows": len(value)}
                  for name, payload, value in zip(names, payloads.values(), rows)},
        "design": {"independent_unit": "latent world; both variants remain in one group",
            "collection_scope": "Independent 80-chunk tenant collection; no other variant or world is searchable",
            "paired_intervention": "Only source URL concentration changes; ordered document texts, questions, hosts and facts are identical",
            "duplicate_chunks_between_worlds": [0, 4, 12], "facts_per_world": [2, 3, 4],
            "support_position": "Independent continuous fraction Uniform(0.05,0.95), rendered with full sentences; actual token visibility is measured later",
            "target_words": {"ordinary": [60, 360], "position_pressure": [180, 900]},
            "range_rationale": "Finite mechanism stress ranges spanning short/long contexts; no empirical deployment-frequency claim",
            "templates": {"dev": ["prose", "list"], "test_seen": ["prose", "list"], "test_heldout": ["qa"]},
            "heldout_fraction": "floor(test_per_seed/2) worlds per seed; heldout grammar receives structural audit but no model tuning",
            "policy_assignment": "Balanced synthetic design assignment within each seed/split; not a real-world frequency estimate",
            "acceptance": "No model-score, effect-size, significance or nonzero-gap acceptance criterion",
            "human_audit_status": "not_completed", "human_E2_completed": False}}
    payloads["specification.json"] = (json.dumps(spec, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    output = Path(output)
    for name, data in payloads.items():
        target = output / name
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f"Refusing to replace frozen data: {target}; use a new directory")
    output.mkdir(parents=True, exist_ok=True)
    for name, data in payloads.items():
        (output / name).write_bytes(data)
    return spec


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("experiments/strengthening/data/strengthening_v1"))
    p.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    p.add_argument("--dev-per-seed", type=int, default=20)
    p.add_argument("--test-per-seed", type=int, default=100)
    a = p.parse_args()
    print(json.dumps(write_dataset(a.output, a.seeds, a.dev_per_seed, a.test_per_seed)["counts"], indent=2))


if __name__ == "__main__":
    main()
