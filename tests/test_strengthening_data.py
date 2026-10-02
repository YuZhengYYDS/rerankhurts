import hashlib
import json
from pathlib import Path

import pytest

from experiments.strengthening.audit_data import audit_dataset, classify, parse_claims, read_rows
from experiments.strengthening.generate import write_dataset


def truth():
    return {"entity": "Veloria-ABC", "current_version": "R4", "obsolete_version": "R3", "as_of": "2035-06-01",
            "versions": {"R3": {"valid_from": "2033-01-01", "valid_to": "2035-01-01"},
                         "R4": {"valid_from": "2035-01-01", "valid_to": "2037-01-01"}},
            "facts": [{"fact_id": "route-fact", "key": "route", "value": "Aster-42", "old_value": "Willow-53", "exclusive": True}]}


@pytest.mark.parametrize("text", [
    "For entity Veloria-ABC in revision R4, the service route is Aster-42.",
    "- Entity Veloria-ABC; revision R4; service route: Aster-42.",
    "Q: Under revision R4, what is the service route for entity Veloria-ABC?\nA: Aster-42.",
])
def test_independent_parser_recovers_three_complete_structures(text):
    original = "Context before.\n" + text + "\nContext after."
    result = parse_claims(original)
    assert len(result) == 1
    assert original[result[0]["start_char"]:result[0]["end_char"]] == text
    assert classify(truth(), result[0]) == {"fact_id": "route-fact", "status": "valid"}


def test_semantic_status_distinguishes_subject_time_and_direct_conflict():
    base = {"subject": "Veloria-ABC", "version": "R4", "key": "route", "value": "Aster-42"}
    assert classify(truth(), {**base, "value": "Willow-53"})["status"] == "contradictory"
    assert classify(truth(), {**base, "version": "R3", "value": "Willow-53"})["status"] == "obsolete"
    assert classify(truth(), {**base, "subject": "Veloria-ABC-Annex"}) == {"fact_id": None, "status": "irrelevant"}
    with pytest.raises(ValueError, match="historical truth"):
        classify(truth(), {**base, "version": "R3"})
    with pytest.raises(ValueError, match="Unknown document revision"):
        classify(truth(), {**base, "version": "R9"})
    unqualified = truth()
    unqualified["facts"][0]["exclusive"] = False
    with pytest.raises(ValueError, match="single-valued"):
        classify(unqualified, base)


def test_parser_rejects_truncated_and_unrecognized_assertions():
    for text in ("For entity Veloria-ABC in revision R4, the service route is",
                 "For entity Veloria-ABC in revision R4, the secret objective is Aster-42.",
                 "Q: Under revision R4, what is the service route for entity Veloria-ABC?\nA:"):
        with pytest.raises(ValueError):
            parse_claims(text)


def test_generation_determinism_pairing_and_independent_full_audit(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    for directory in (first, second):
        write_dataset(directory, seeds=(20261002, 20261003, 20261004), dev_per_seed=2, test_per_seed=4)
    assert {p.name: p.read_bytes() for p in first.iterdir()} == {p.name: p.read_bytes() for p in second.iterdir()}
    report = audit_dataset(first, tmp_path / "audit")
    assert report["status"] == "PASS"
    assert report["worlds"] == 18 and report["tasks"] == 36 and report["chunks"] == 2880
    assert report["paired_URL_only_interventions_verified"] == 18
    assert not report["human_audit_completed"] and not report["human_E2_completed"]
    assert report["template_worlds"]["qa"] == 6
    assert all(r["human_review_status"] == "pending" for r in read_rows(tmp_path / "audit/human_audit_packet.jsonl"))
    assert all(set(r) == {"chunk_id", "collection_id", "url", "text"} for r in read_rows(first / "corpus.jsonl"))
    with pytest.raises(ValueError, match="Refusing to replace"):
        write_dataset(first, seeds=(20261002,), dev_per_seed=1, test_per_seed=1)


@pytest.fixture
def dataset(tmp_path):
    target = tmp_path / "dataset"
    write_dataset(target, seeds=(20261002,), dev_per_seed=2, test_per_seed=4)
    return target


def replace_rows(directory, name, rows, update_hash=True):
    payload = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows).encode()
    (directory / name).write_bytes(payload)
    if update_hash:
        p = directory / "specification.json"
        spec = json.loads(p.read_text())
        spec["files"][name] = {"sha256": hashlib.sha256(payload).hexdigest(), "rows": len(rows)}
        p.write_text(json.dumps(spec), encoding="utf-8")


def test_manifest_rejects_edited_data(dataset):
    rows = read_rows(dataset / "questions.jsonl")
    rows[0]["question"] += " Extra text."
    replace_rows(dataset, "questions.jsonl", rows, update_hash=False)
    with pytest.raises(ValueError, match="hash mismatch"):
        audit_dataset(dataset)


def test_semantic_audit_does_not_trust_regenerated_claim_label_hash(dataset):
    claims = read_rows(dataset / "claims.jsonl")
    record = next(c for c in claims if c["status"] == "contradictory")
    record["status"] = "valid"
    replace_rows(dataset, "claims.jsonl", claims)
    with pytest.raises(ValueError, match="independently parsed truth"):
        audit_dataset(dataset)


def test_span_boundary_corruption_is_rejected(dataset):
    claims = read_rows(dataset / "claims.jsonl")
    claims[0]["start_char"] += 1
    replace_rows(dataset, "claims.jsonl", claims)
    with pytest.raises(ValueError, match="missing from generator annotation"):
        audit_dataset(dataset)


def test_answer_value_leakage_in_question_is_rejected(dataset):
    questions = read_rows(dataset / "questions.jsonl")
    metadata = {r["qid"]: r for r in read_rows(dataset / "metadata.jsonl")}
    worlds = {r["group_id"]: r for r in read_rows(dataset / "truth.jsonl")}
    value = worlds[metadata[questions[0]["qid"]]["group_id"]]["facts"][0]["value"]
    questions[0]["question"] += " Hint: " + value
    replace_rows(dataset, "questions.jsonl", questions)
    with pytest.raises(ValueError, match="Answer leaked"):
        audit_dataset(dataset)


def test_paired_source_policy_confounds_are_rejected(dataset):
    corpus = read_rows(dataset / "corpus.jsonl")
    corpus[0]["url"] = "https://different.registry.invalid/another-record"
    replace_rows(dataset, "corpus.jsonl", corpus)
    with pytest.raises(ValueError, match="publisher/admissibility|multiplicity|Designated URL"):
        audit_dataset(dataset)


def test_cross_collection_claims_are_rejected(dataset):
    claims = read_rows(dataset / "claims.jsonl")
    claims[0]["collection_id"] = "unrelated-collection"
    replace_rows(dataset, "claims.jsonl", claims)
    with pytest.raises(ValueError, match="collection boundary"):
        audit_dataset(dataset)
