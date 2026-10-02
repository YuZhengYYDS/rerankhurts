"""Generate a frozen fictional workflow corpus and a separate exact-span oracle.

This is a controlled simulator, not clinical advice or independent human data.
All latent facts are fixed before any document is rendered. Generation never
reads model scores, run outputs, or selected configurations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

SEED = 20260928
SCENARIOS = ("aligned", "distributed", "alternative_source", "stale_version", "near_match", "late_evidence")
MODEL_SNAPSHOTS = {
    "dense": {"model": "BAAI/bge-small-en-v1.5", "sha": "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"},
    "reranker": {"model": "BAAI/bge-reranker-v2-m3", "sha": "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e"},
    "tokenizer": {"model": "google-bert/bert-base-uncased", "sha": "86b5e0934494bd15c9632b12f734a8a67f723594"},
}


def opaque(rng):
    return f"{rng.getrandbits(128):032x}"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def jsonl_bytes(rows):
    return b"".join(json_bytes(row) for row in rows)


def latent_worlds(seed):
    """Build all requirements and group assignments before rendering any text."""
    rng = random.Random(seed)
    extra_dev = set(rng.sample(list(SCENARIOS), 2))
    worlds = []
    name_starts = ("Vel", "Or", "Tal", "Mir", "Sen", "Ar", "Cor", "Pel", "Ner", "Zel", "Lum", "Dor")
    name_ends = ("avia", "oria", "elion", "amara", "uvia", "erion", "alune", "ivara", "esara", "omira")
    used_names = set()
    for scenario in SCENARIOS:
        splits = ["dev"] * (4 if scenario in extra_dev else 3)
        splits += ["test"] * (10 - len(splits))
        rng.shuffle(splits)
        for split in splits:
            while True:
                name = rng.choice(name_starts) + rng.choice(name_ends) + "-" + str(rng.randint(21, 98))
                if name not in used_names:
                    used_names.add(name)
                    break
            revision = rng.randint(3, 8)
            edition = rng.choice(("K", "R", "V", "M", "T"))
            prefix = opaque(rng)[:12]
            route = rng.choice(("Aster", "Cobalt", "Juniper", "Saffron", "Willow", "Tamarind")) + "-" + str(rng.randint(11, 89))
            day = rng.choice((3, 5, 7, 9, 11, 13, 15))
            rule = rng.choice((
                "two matching registry identifiers before record release",
                "a second clerk's countersignature before record release",
                "a matched intake form and routing receipt before record release",
                "a completed duplicate-record check before record release",
                "a verified cohort code and an independent reviewer sign-off before record release",
            ))
            worlds.append({"group_id": opaque(rng), "scenario": scenario, "split": split,
                "name": name, "version": f"{edition}-{revision}", "old_version": f"{edition}-{revision - 1}",
                "facts": [{"fact_id": opaque(rng), "kind": "route", "value": route, "wrong_value": "Cinder-" + str(rng.randint(91, 99))},
                          {"fact_id": opaque(rng), "kind": "checkpoint", "value": f"{day} working days after intake", "wrong_value": f"{day + 4} working days after intake"},
                          {"fact_id": opaque(rng), "kind": "release", "value": rule, "wrong_value": f"does not require {rule}"}],
                "prefixes": {"registry": f"https://{prefix}.registry.invalid/", "consortium": f"https://{prefix}.consortium.invalid/",
                             "methods": f"https://{prefix}.methods.invalid/"},
                "qids": {policy: opaque(rng) for policy in ("open", "constrained")}})
    return worlds, rng


def claim_sentence(world, index, status, subject=None):
    """A full sentence always includes subject, value, and version context."""
    fact = world["facts"][index]
    subject = subject or world["name"]
    value = fact["value"] if status == "valid" else fact["wrong_value"]
    if status == "obsolete":
        context = f"the superseded revision {world['old_version']}"
    else:
        context = f"current revision {world['version']}"
    if fact["kind"] == "release" and status != "valid":
        # Directly negate this world's exact requirement. A generic lack of
        # identity checks need not contradict a different receipt/check rule.
        if world["split"] == "dev":
            return (f"For the fictional {subject} oncology registry cohort under {context}, "
                    f"the release safeguard does not require {fact['value']}.")
        return (f"In {context}, the fictional oncology registry cohort {subject} "
                f"does not require {fact['value']} as its clearance condition.")
    if world["split"] == "dev":
        templates = {
            "route": "For the fictional {subject} oncology registry cohort under {context}, the handling route is {value}.",
            "checkpoint": "For the fictional {subject} oncology registry cohort under {context}, the record-review checkpoint is {value}.",
            "release": "For the fictional {subject} oncology registry cohort under {context}, the release safeguard requires {value}.",
        }
    else:
        templates = {
            "route": "The fictional oncology registry cohort {subject} is assigned to the {value} processing track in {context}.",
            "checkpoint": "The fictional oncology registry cohort {subject} reaches its file-verification checkpoint {value} according to {context}.",
            "release": "The fictional oncology registry cohort {subject} uses this clearance condition in {context}: {value}.",
        }
    return templates[fact["kind"]].format(subject=subject, context=context, value=value)


def filler(world, rng, minimum_words):
    """Operational prose without statements of any required fact or clinical rule."""
    if world["split"] == "dev":
        sentences = (
            "The coordination desk keeps a dated routing receipt with the intake cover sheet so later administrative queries can be traced to their originating packet.",
            "Staff use the document directory to locate the relevant workflow note; the directory heading itself does not certify that a particular record is ready for processing.",
            "The local change log preserves editorial amendments, access notes and copies of previously circulated notices for review by the records team.",
            "A transfer between clerks is recorded as an administrative handover, with the original packet retained alongside the subsequent correspondence.",
            "This fictional exercise concerns record coordination only and provides no diagnosis, treatment recommendation, drug regimen or patient-care instruction.",
            "When a copied page is difficult to read, the desk requests another copy rather than interpreting missing words as a completed instruction.",
            "The appendix describes indexing practice, page continuity and storage conventions; the operative instructions appear separately in the workflow statement.",
            "An editorial note can explain why a page was circulated without replacing the cohort-specific instructions issued in the applicable revision.",
        )
    else:
        sentences = (
            "Administrative handoffs are documented in a correspondence ledger, allowing a subsequent reviewer to reconstruct which packet was available when a clerical query arose.",
            "The file directory points readers to the relevant processing memorandum, while its index terms serve only to support navigation through the exercise materials.",
            "Earlier circulation notices remain attached to the history of the file so the distinction between editorial changes and operative instructions can be examined.",
            "An unclear photocopy is returned for clarification; incomplete wording must not be reconstructed as if it were an instruction authorized by the publisher.",
            "No statement in this invented administrative setting is intended as a clinical assessment, a therapeutic recommendation or guidance for managing a real patient.",
            "The storage appendix records the sequence of pages and the manner of attaching correspondence, leaving substantive cohort instructions to the designated statement.",
            "Correspondence from another office may describe the history of a packet, but a historical explanation does not by itself establish the applicable processing instruction.",
            "Reviewers retain the original notice together with later memoranda to make changes in the fictional documentation exercise inspectable.",
        )
    parts, count = [], 0
    while count < minimum_words:
        sentence = rng.choice(sentences)
        parts.append(sentence)
        count += len(sentence.split())
    return " ".join(parts)


def document_plans(world, rng):
    """Declare claim placement before rendering; plans are evaluator-internal."""
    scenario = world["scenario"]
    urls = {slot: world["prefixes"][family] + opaque(rng)
            for slot, family in (("designated", "registry"), ("supplement", "registry"), ("current", "registry"),
                                 ("archive", "registry"), ("disputed", "registry"), ("near", "registry"),
                                 ("alternative", "consortium"), ("methods", "methods"))}
    if scenario == "distributed":
        gold_claims = [[(i, "valid")] for i in range(3)]
    elif scenario == "alternative_source":
        gold_claims = [[(0, "valid")], [], []]
    elif scenario == "stale_version":
        gold_claims = [[(i, "obsolete") for i in range(3)], [(0, "contradictory")], [(1, "valid")]]
    elif scenario == "near_match":
        gold_claims = [[(0, "valid")], [], [(1, "valid")]]
    else:
        gold_claims = [[(i, "valid") for i in range(3)], [], [(0, "valid")]]
    plans = []

    def add(slot, family, claims, late=False, near=False):
        plans.append({"chunk_id": opaque(rng), "url": urls[slot], "family": family,
                      "claims": claims, "prefix_words": rng.randint(650, 880) if late else rng.choice((0, 15, 35, 65, 95, 130)),
                      "suffix_words": rng.choice((10, 25, 50, 100, 180)), "near": near})

    for i, claims in enumerate(gold_claims):
        add("designated", "registry", claims, late=scenario == "late_evidence" and i == 0)
    for i in range(3):
        claims = [(j, "valid") for j in range(3)] if i == 0 and scenario in ("aligned", "stale_version", "near_match") else [(i, "valid")]
        add("supplement" if i < 2 else "current", "registry", claims, late=scenario == "late_evidence" and i == 2)
    alt = [0, 1] if scenario in ("distributed", "late_evidence") else [0, 1, 2]
    add("alternative", "consortium", [(i, "valid") for i in alt])
    add("alternative", "consortium", [(0 if scenario == "late_evidence" else 2, "valid")])
    add("methods", "methods", [(1 if scenario == "late_evidence" else 2, "valid")])
    add("archive", "registry", [(i, "obsolete") for i in range(3)])
    add("disputed", "registry", [(rng.randrange(3), "contradictory")])
    add("near", "registry", [(i, "valid") for i in range(3)], near=True)
    add("designated", "registry", [])
    return plans, urls["designated"]


def render_document(world, plan, rng):
    publishers = {"registry": f"Fictional {world['name']} Registry", "consortium": f"Fictional {world['name']} Documentation Consortium",
                  "methods": f"Fictional {world['name']} Methods Board"}
    subject = world["name"] + " auxiliary cohort" if plan["near"] else world["name"]
    heading = rng.choice(("Record coordination memorandum", "Cohort workflow note", "Operational documentation excerpt", "Registry processing bulletin"))
    pieces = [f"{heading}\nPublisher: {publishers[plan['family']]}\nSubject: {subject}\nThis document belongs to a fictional administrative simulation.\n\n"]
    if plan["prefix_words"]:
        pieces.append(filler(world, rng, plan["prefix_words"]) + "\n\n")
    if plan["near"]:
        pieces.append("The auxiliary cohort is a separate record population; instructions below do not apply to the primary cohort.\n\n")
    claim_spans = []
    claim_plans = list(plan["claims"])
    rng.shuffle(claim_plans)
    for index, status in claim_plans:
        sentence = claim_sentence(world, index, status, subject=subject)
        start = sum(map(len, pieces))
        pieces.append(sentence)
        if not plan["near"]:
            claim_spans.append({"chunk_id": plan["chunk_id"], "fact_id": world["facts"][index]["fact_id"],
                                "start_char": start, "end_char": start + len(sentence), "status": status})
        pieces.append("\n\n")
    if not claim_plans:
        pieces.append("This excerpt supplies navigation and correspondence context; the operative cohort instructions are recorded in the companion memoranda.\n\n")
    pieces.append(filler(world, rng, plan["suffix_words"]))
    return {"chunk_id": plan["chunk_id"], "url": plan["url"], "text": "".join(pieces)}, claim_spans


def selection_contract(worlds):
    from experiments.protocol import configurations
    cells = configurations("m3")
    order = lambda c: (c.reranker != "none", c.pool, {"off": 0, "pre": 1, "post": 2}[c.cap], c.config_id)
    primary = sorted((c for c in cells if c.budget == 512), key=order)
    return {"primary_policy": "open", "primary_budget": 512, "secondary_budget": 2048,
        "primary_endpoint": "U_sim", "primary_G": "G_final", "weighting": "equal_information_needs",
        "dev_groups": sorted(w["group_id"] for w in worlds if w["split"] == "dev"),
        "test_groups": sorted(w["group_id"] for w in worlds if w["split"] == "test"),
        "configs": [c.config_id for c in primary], "tie_order": [c.config_id for c in primary],
        "tie_rule": "ascending reranker flag (none first), pool, cap order off/pre/post, config_id; structural, not measured cost",
        "report_all_ties": True, "bootstrap_repetitions": 5000, "bootstrap_seed": SEED,
        "interval": "paired whole-group percentile bootstrap 95%",
        "delta_definition": "test mean U_sim of the dev-selected U_sim configuration minus test mean U_sim of the dev-selected G_final configuration",
        "development_selection_frequencies": True,
        "practical_delta": None, "practical_delta_note": "No application-calibrated meaningful-effect threshold is claimed in this synthetic pilot.",
        "secondary_analysis": "2048-token contrast is exploratory",
        "constrained_selection": "descriptive_only_no_source_feasible_selector",
        "null_or_reversed_gap": "retain_and_report_without_regeneration",
        "frozen_before_model_execution": True, "configurations": [c.record() for c in cells]}


def generate(seed=SEED):
    worlds, rng = latent_worlds(seed)
    corpus, questions, oracle = [], [], []
    for world in worlds:
        plans, designated = document_plans(world, rng)
        claims = []
        for plan in plans:
            row, spans = render_document(world, plan, rng)
            corpus.append(row)
            claims.extend(spans)
        by_id = {p["chunk_id"]: p for p in plans}
        if world["split"] == "dev":
            base_question = (f"For the fictional {world['name']} oncology registry cohort under current revision {world['version']}, "
                             "what handling route, record-review checkpoint timing, and release safeguard apply?")
        else:
            base_question = (f"Which processing track, file-verification checkpoint timing, and clearance condition apply to "
                             f"the fictional oncology registry cohort {world['name']} in current revision {world['version']}?")
        for policy in ("open", "constrained"):
            allowed = [world["prefixes"]["registry"]] if policy == "constrained" else []
            question = base_question
            if policy == "constrained":
                question += (f" Use only evidence published by the Fictional {world['name']} Registry "
                             f"at {world['prefixes']['registry']}; material from other publishers is not permitted.")
            questions.append({"qid": world["qids"][policy], "question": question, "group_id": world["group_id"],
                "topic": "fictional_oncology_registry_workflow", "gold_urls": [designated],
                "construction_source": "synthetic_information_need", "split": world["split"], "policy": policy, "scenario": world["scenario"]})
            oracle.append({"qid": world["qids"][policy], "group_id": world["group_id"], "split": world["split"],
                "policy": policy, "scenario": world["scenario"], "required_fact_ids": [f["fact_id"] for f in world["facts"]],
                "allowed_url_prefixes": allowed, "claims": [{**c, "admissible": policy == "open" or any(by_id[c["chunk_id"]]["url"].startswith(p) for p in allowed)} for c in claims]})
    # Neither original generation order nor a type-specific block provides a tie cue.
    rng.shuffle(corpus)
    rng.shuffle(questions)
    rng.shuffle(oracle)
    counts = Counter(w["scenario"] for w in worlds)
    specification = {"schema_version": "controlled-simulation-v1", "dataset_revision": 2, "status": "complete",
        "validity_correction": "Revision 2 makes each nonvalid release statement explicitly negate that world's exact required safeguard. World IDs, split, seed and document placement plans are unchanged. Revision 1 is excluded from substantive analysis because its generic release counterstatement was not always contradictory.",
        "scope": "Controlled fictional administrative evidence environment; not human judgments, clinical advice or independent real-world replication.",
        "annotation_source": "synthetic_oracle", "generation_seed": seed,
        "generation_order": ["latent requirements and world/group split", "document claim/placement plans", "text rendering and exact spans", "corpus/task/oracle row shuffle"],
        "model_input_whitelist": {"question": "question", "document": "text"},
        "evaluation_only_files": ["oracle.jsonl", "specification.json"],
        "models": MODEL_SNAPSHOTS,
        "counts": {"worlds": len(worlds), "tasks": len(questions), "corpus_chunks": len(corpus),
                   "dev_groups": sum(w["split"] == "dev" for w in worlds), "test_groups": sum(w["split"] == "test" for w in worlds),
                   "scenario_worlds": dict(counts), "scenario_split_worlds": {s: {split: sum(w["scenario"] == s and w["split"] == split for w in worlds) for split in ("dev", "test")} for s in SCENARIOS}},
        "rendering_families": {"dev": "handling-route / record-review / release-safeguard; subject-version-value sentence order",
                               "test": "processing-track / file-verification / clearance-condition; subject-value-version sentence order"},
        "design_notes": ["All 60 worlds have three required facts and 13 corpus chunks, with distinct entities and URLs across worlds.",
                         "Each world has valid support for every fact within its allowed registry source, including facts beyond 512 tokens in the late-evidence condition.",
                         "A designated URL can carry partial, historical or conflicting material and is not itself the support oracle.",
                         "Open tasks allow all sources. Constrained tasks declare their publisher/domain rule in the question before retrieval.",
                         "Obsolete and contradictory claims share the relevant subject; auxiliary-cohort distractors have no oracle claims for the primary cohort.",
                         "Repeated document structure and explicit sentences limit realism. This pilot has no clinical-validity or external-transfer claim.",
                         "No outcome-dependent regeneration, choice of winning configuration, or test-result tuning is permitted."],
        "selection": selection_contract(worlds)}
    return corpus, questions, oracle, specification


def write_dataset(output, seed=SEED):
    corpus, questions, oracle, spec = generate(seed)
    by_id = {c["chunk_id"]: c for c in corpus}
    if len(by_id) != len(corpus) or len({q["qid"] for q in questions}) != len(questions):
        raise ValueError("Generated record identifiers are not unique.")
    for task in oracle:
        required = set(task["required_fact_ids"])
        supported = set()
        for claim in task["claims"]:
            doc = by_id[claim["chunk_id"]]
            if not 0 <= claim["start_char"] < claim["end_char"] <= len(doc["text"]):
                raise ValueError("Invalid generated claim span.")
            if claim["fact_id"] not in required:
                raise ValueError("Claim references an unknown fact.")
            if claim["status"] == "valid" and claim["admissible"]:
                supported.add(claim["fact_id"])
        if supported != required:
            raise ValueError("A task lacks complete admissible support in the corpus.")
    payloads = {"corpus.jsonl": jsonl_bytes(corpus), "questions.jsonl": jsonl_bytes(questions), "oracle.jsonl": jsonl_bytes(oracle)}
    spec["files"] = {name: {"sha256": sha256(data), "rows": len(data.splitlines())} for name, data in payloads.items()}
    spec["code_sha256"] = {"generate.py": sha256(Path(__file__).read_bytes()),
                           "protocol.py": sha256((Path(__file__).parents[1] / "protocol.py").read_bytes())}
    spec["complete_status_definition"] = "Data generation and structural checks only; no model execution, utility experiment or human annotation is implied."
    payloads["specification.json"] = json_bytes(spec)
    output = Path(output)
    if output.exists():
        for name, data in payloads.items():
            target = output / name
            if target.exists() and target.read_bytes() != data:
                raise ValueError(f"Refusing to replace frozen generated data: {target}. Choose a new version directory.")
    output.mkdir(parents=True, exist_ok=True)
    for name, data in payloads.items():
        (output / name).write_bytes(data)
    return spec


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("experiments/simulation/data/pilot_v2"))
    p.add_argument("--seed", type=int, default=SEED)
    args = p.parse_args()
    spec = write_dataset(args.output, args.seed)
    print(json.dumps({"output": str(args.output), "counts": spec["counts"], "annotation_source": spec["annotation_source"]}, indent=2))


if __name__ == "__main__":
    main()
