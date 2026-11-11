"""Review citations must match their world as well as their source text."""
import json

import pytest

from scripts.check_world_review_records import DATA, verify


@pytest.fixture
def review_repository(tmp_path):
    data = tmp_path / DATA
    reviews = data / "audit/reviews"
    reviews.mkdir(parents=True)
    packet, corpus, claims, sections = [], [], [], []
    for index in range(60):
        world, collection = f"world{index}", f"collection{index}"
        cid, claim_id = f"chunk{index}", f"claim{index}"
        text = f"World {index} has route A."
        url = f"https://example.invalid/{index}"
        packet.append({"group_id": world, "qids": [f"q{index}a", f"q{index}b"],
                       "collection_ids": [collection],
                       "truth": {"facts": [{"fact_id": "route", "key": "route", "value": "A"}],
                                 "required_fact_ids": ["route"]}})
        corpus.append({"chunk_id": cid, "collection_id": collection, "url": url, "text": text})
        claims.append({"claim_id": claim_id, "chunk_id": cid, "start_char": 0, "end_char": len(text)})
        sections.append(
            f"## World {index + 1}: {world}\n"
            f"Question IDs: `q{index}a`, `q{index}b`\nCollection IDs: `{collection}`\n"
            "Required facts: route=A.\n"
            + "\n".join(f"**D{dimension} criterion: pass**" for dimension in range(1, 5))
            + f"\nchunk `{cid}`, claim `{claim_id}`, Character span `[0, {len(text)})`; Source `{url}`.\n> {text}\n"
        )
    for path, rows in [(data / "audit/human_audit_packet.jsonl", packet),
                       (data / "corpus.jsonl", corpus), (data / "claims.jsonl", claims)]:
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    for label in ["A", "B"]:
        (reviews / f"WORLD_REVIEW_RESULTS_{label}.md").write_text("\n".join(sections), encoding="utf-8")
    return tmp_path, sections


def test_all_review_citations_belong_to_their_world(review_repository):
    root, _ = review_repository
    result = verify(root)
    assert result["status"] == "PASS"
    assert [review["evidence_citations"] for review in result["reviews"]] == [60, 60]


def test_valid_source_citation_from_another_world_is_rejected(review_repository):
    root, sections = review_repository
    path = root / DATA / "audit/reviews/WORLD_REVIEW_RESULTS_A.md"
    first_citation = sections[0][sections[0].index("chunk `"):]
    foreign_citation = sections[1][sections[1].index("chunk `"):]
    path.write_text(path.read_text(encoding="utf-8").replace(first_citation, foreign_citation, 1), encoding="utf-8")
    with pytest.raises(ValueError, match="does not belong to world"):
        verify(root)
