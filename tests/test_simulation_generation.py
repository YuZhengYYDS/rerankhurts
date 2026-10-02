"""Structural tests for fictional generated data; no model outcomes are asserted."""
from collections import Counter, defaultdict
import json
import re

import pytest

from experiments.protocol import require_human_utility
from experiments.simulation.generate import (
    SCENARIOS, SEED, claim_sentence, generate, jsonl_bytes, latent_worlds, sha256, write_dataset,
)


@pytest.fixture(scope="module")
def dataset():
    return generate(SEED)


def test_counts_policy_pairs_and_whole_world_split(dataset):
    corpus, questions, oracle, spec = dataset
    assert len(corpus) == 780
    assert len(questions) == len(oracle) == 120
    pairs = defaultdict(list)
    for question in questions:
        pairs[question["group_id"]].append(question)
    assert len(pairs) == 60
    assert Counter(rows[0]["split"] for rows in pairs.values()) == {"dev": 20, "test": 40}
    assert Counter(rows[0]["scenario"] for rows in pairs.values()) == {s: 10 for s in SCENARIOS}
    for rows in pairs.values():
        assert len(rows) == 2
        assert {r["policy"] for r in rows} == {"open", "constrained"}
        assert len({r["split"] for r in rows}) == 1
        assert len({r["scenario"] for r in rows}) == 1
    assert set(spec["selection"]["dev_groups"]).isdisjoint(spec["selection"]["test_groups"])


def test_schema_keeps_oracle_out_of_model_input_records(dataset):
    corpus, questions, oracle, spec = dataset
    for chunk in corpus:
        assert set(chunk) == {"chunk_id", "url", "text"}
        assert re.fullmatch(r"[0-9a-f]{32}", chunk["chunk_id"])
        assert ".invalid/" in chunk["url"]
        assert not re.search(r"\b[0-9a-f]{32}\b", chunk["text"])
    for question in questions:
        assert set(question) == {"qid", "question", "group_id", "topic", "gold_urls", "construction_source", "split", "policy", "scenario"}
        assert question["construction_source"] == "synthetic_information_need"
    assert {r["qid"] for r in oracle} == {r["qid"] for r in questions}
    assert spec["model_input_whitelist"] == {"question": "question", "document": "text"}
    assert spec["annotation_source"] == "synthetic_oracle"


def test_exact_full_subject_value_version_spans_and_counterclaims(dataset):
    corpus, _, oracle, _ = dataset
    by_chunk = {c["chunk_id"]: c for c in corpus}
    worlds, _ = latent_worlds(SEED)
    by_world = {w["group_id"]: w for w in worlds}
    seen_status = set()
    for task in oracle:
        world = by_world[task["group_id"]]
        indices = {f["fact_id"]: i for i, f in enumerate(world["facts"])}
        assert len(set(task["required_fact_ids"])) == 3
        for claim in task["claims"]:
            assert set(claim) == {"chunk_id", "fact_id", "start_char", "end_char", "status", "admissible"}
            text = by_chunk[claim["chunk_id"]]["text"]
            assert 0 <= claim["start_char"] < claim["end_char"] <= len(text)
            span = text[claim["start_char"]:claim["end_char"]]
            assert span == claim_sentence(world, indices[claim["fact_id"]], claim["status"])
            assert world["name"] in span
            assert (world["old_version"] if claim["status"] == "obsolete" else world["version"]) in span
            seen_status.add(claim["status"])
    assert seen_status == {"valid", "contradictory", "obsolete"}


def test_release_counterstatement_negates_each_exact_world_requirement():
    worlds, _ = latent_worlds(SEED)
    assert len({w["facts"][2]["value"] for w in worlds}) == 5
    for world in worlds:
        requirement = world["facts"][2]["value"]
        valid = claim_sentence(world, 2, "valid")
        assert requirement in valid and "does not require" not in valid
        for status in ("contradictory", "obsolete"):
            sentence = claim_sentence(world, 2, status)
            assert f"does not require {requirement}" in sentence
            assert world["name"] in sentence
            assert (world["version"] if status == "contradictory" else world["old_version"]) in sentence


def test_every_task_has_complete_admissible_support_but_gold_is_not_oracle(dataset):
    corpus, questions, oracle, _ = dataset
    by_chunk = {c["chunk_id"]: c for c in corpus}
    by_qid = {q["qid"]: q for q in questions}
    imperfect_gold = 0
    for task in oracle:
        support = set()
        gold_support = set()
        for claim in task["claims"]:
            allowed = task["policy"] == "open" or any(by_chunk[claim["chunk_id"]]["url"].startswith(prefix) for prefix in task["allowed_url_prefixes"])
            assert claim["admissible"] == allowed
            if claim["status"] == "valid" and allowed:
                support.add(claim["fact_id"])
                if by_chunk[claim["chunk_id"]]["url"] in by_qid[task["qid"]]["gold_urls"]:
                    gold_support.add(claim["fact_id"])
        assert support == set(task["required_fact_ids"])
        imperfect_gold += gold_support != set(task["required_fact_ids"])
        assert bool(task["allowed_url_prefixes"]) == (task["policy"] == "constrained")
    assert imperfect_gold > 0


def test_alternate_support_and_explicit_policy_are_distinct(dataset):
    corpus, questions, oracle, _ = dataset
    by_chunk = {c["chunk_id"]: c for c in corpus}
    by_group = defaultdict(dict)
    question_group = defaultdict(dict)
    for task in oracle:
        by_group[task["group_id"]][task["policy"]] = task
    for question in questions:
        question_group[question["group_id"]][question["policy"]] = question
    for gid, tasks in by_group.items():
        open_task, constrained = tasks["open"], tasks["constrained"]
        assert open_task["required_fact_ids"] == constrained["required_fact_ids"]
        assert all(c["admissible"] for c in open_task["claims"])
        assert any(not c["admissible"] and c["status"] == "valid" for c in constrained["claims"])
        oq, cq = question_group[gid]["open"], question_group[gid]["constrained"]
        assert cq["question"].startswith(oq["question"])
        assert "Use only evidence published by" in cq["question"]
        if open_task["scenario"] == "alternative_source":
            foreign = {c["fact_id"] for c in constrained["claims"] if not c["admissible"] and c["status"] == "valid"}
            assert foreign == set(constrained["required_fact_ids"])


def test_late_support_requires_full_span_not_chunk_membership(dataset):
    corpus, _, oracle, _ = dataset
    by_chunk = {c["chunk_id"]: c for c in corpus}
    late_claims = 0
    for task in oracle:
        if task["scenario"] != "late_evidence" or task["policy"] != "open":
            continue
        for claim in task["claims"]:
            if claim["status"] != "valid":
                continue
            text = by_chunk[claim["chunk_id"]]["text"]
            # These ASCII prose words each require at least one WordPiece token;
            # 650+ preceding words conservatively place the fact beyond token512.
            if len(text[:claim["start_char"]].split()) >= 650:
                late_claims += 1
                prefix = text[:claim["end_char"] - 1]
                assert text[claim["start_char"]:claim["end_char"]] not in prefix
                assert claim["end_char"] > len(prefix)
    assert late_claims >= 40
    assert max(len(c["text"].split()) for c in corpus) > 800
    assert min(len(c["text"].split()) for c in corpus) < 150


def test_unique_records_repeated_urls_and_near_match_not_support(dataset):
    corpus, questions, oracle, _ = dataset
    assert len({c["chunk_id"] for c in corpus}) == len(corpus)
    assert len({q["qid"] for q in questions}) == len(questions)
    counts = Counter(c["url"] for c in corpus)
    assert max(counts.values()) >= 4
    claimed = {claim["chunk_id"] for task in oracle for claim in task["claims"]}
    near = [c for c in corpus if "The auxiliary cohort is a separate record population" in c["text"]]
    assert len(near) == 60
    assert not claimed.intersection(c["chunk_id"] for c in near)
    assert sum("fictional" in c["text"].lower() for c in corpus) == len(corpus)


def test_world_entities_and_documents_do_not_cross_splits(dataset):
    corpus, questions, oracle, _ = dataset
    worlds, _ = latent_worlds(SEED)
    assert len({w["name"] for w in worlds}) == 60
    owner = {}
    for world in worlds:
        docs = [c for c in corpus if any(c["url"].startswith(p) for p in world["prefixes"].values())]
        assert len(docs) == 13
        for doc in docs:
            assert doc["chunk_id"] not in owner
            owner[doc["chunk_id"]] = world["group_id"]
            assert world["name"] in doc["text"]
    for task in oracle:
        assert all(owner[c["chunk_id"]] == task["group_id"] for c in task["claims"])
    assert all(("handling route" in q["question"]) == (q["split"] == "dev") for q in questions)


def test_frozen_selection_contract_and_human_only_gate(dataset):
    _, _, _, spec = dataset
    selection = spec["selection"]
    assert selection["primary_policy"] == "open" and selection["primary_budget"] == 512
    assert len(selection["configs"]) == len(set(selection["configs"])) == 10
    assert all(c.endswith("b512") for c in selection["configs"])
    assert selection["tie_order"][:4] == ["p16_off_none_b512", "p16_pre_none_b512", "p64_off_none_b512", "p64_pre_none_b512"]
    assert selection["bootstrap_repetitions"] == 5000 and selection["bootstrap_seed"] == SEED
    assert selection["frozen_before_model_execution"] is True
    with pytest.raises(ValueError, match="cannot substitute"):
        require_human_utility([{"U": 2, "annotation_source": "synthetic_oracle"}])


def test_generation_is_deterministic_and_writes_verified_hashes(tmp_path, dataset):
    second = generate(SEED)
    assert all(first == repeated for first, repeated in zip(dataset, second))
    spec = write_dataset(tmp_path)
    for name, metadata in spec["files"].items():
        data = (tmp_path / name).read_bytes()
        assert sha256(data) == metadata["sha256"]
        assert len(data.splitlines()) == metadata["rows"]
    before = (tmp_path / "specification.json").read_bytes()
    assert write_dataset(tmp_path) == spec
    assert (tmp_path / "specification.json").read_bytes() == before
    (tmp_path / "corpus.jsonl").write_bytes(b"changed\n")
    with pytest.raises(ValueError, match="Refusing to replace frozen"):
        write_dataset(tmp_path)
