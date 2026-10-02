import math

import pytest

from experiments.protocol import (configurations, digest, first_url_loss, freeze_manifest, identify_corpus,
                                  load_json, normalize_url, pack_prefix, require_human_utility,
                                  rerank, save_json, stage, url_cap, url_metrics)


def chunk(cid, url, rank, ids=(1, 2, 3)):
    return {"chunk_id": cid, "url": url, "raw_rank": rank,
            "token_ids": list(ids), "retrieval_score": 1 / rank}


def test_exactly_twenty_unique_cells_and_equivalent_none_cap_merged():
    cells = configurations()
    assert len(cells) == len({c.config_id for c in cells}) == 20
    assert all(c.cap != "post" for c in cells if c.reranker == "none")


def test_cap_preserves_order_and_never_replenishes_from_outside_pool():
    raw = [chunk(str(i), "https://example.org/a/" if i < 4 else "https://example.org/b", i + 1)
           for i in range(6)]
    assert [x["chunk_id"] for x in url_cap(raw[:4])] == ["0", "1"]
    assert [x["chunk_id"] for x in url_cap(raw)] == ["0", "1", "4", "5"]


def test_normalization_does_not_discard_version_query():
    assert normalize_url("HTTPS://EXAMPLE.org/a/#fragment") == "https://example.org/a"
    assert normalize_url("https://example.org/a?version=1") != normalize_url("https://example.org/a?version=2")


def test_pack_counts_separator_and_truncates_last_chunk_without_skipping():
    raw = [chunk("a", "u1", 1, range(4)), chunk("b", "u2", 2, range(10, 20)), chunk("c", "u3", 3)]
    result = pack_prefix(raw, 8, 99, lambda ids: ",".join(map(str, ids)))
    assert result["token_ids"] == [0, 1, 2, 3, 99, 10, 11, 12]
    assert result["used_tokens"] == 8
    assert [x["chunk_id"] for x in result["chunks"]] == ["a", "b"]
    assert result["chunks"][1]["partial"]
    assert result["chunks"][1]["text"] == "10,11,12"


def test_pack_never_adds_trailing_separator_or_zero_token_chunk():
    raw = [chunk("a", "a", 1), chunk("b", "b", 2)]
    result = pack_prefix(raw, 4, 99, str)
    assert result["used_tokens"] == 3
    assert len(result["chunks"]) == 1
    assert not result["chunks"][0]["partial"]


def test_rerank_ties_keep_first_stage_order():
    raw = [chunk("a", "a", 1), chunk("b", "b", 2), chunk("c", "c", 3)]
    assert [x["chunk_id"] for x in rerank(raw, {"a": 0, "b": 1, "c": 1})] == ["b", "c", "a"]


def test_cap_and_rerank_can_change_membership_not_just_order():
    raw = [chunk("a", "x", 1), chunk("b", "x", 2), chunk("c", "x", 3), chunk("d", "y", 4)]
    scores = {"a": 0, "b": 1, "c": 4, "d": 2}
    pre = rerank(url_cap(raw), scores)
    post = url_cap(rerank(raw, scores))
    assert "c" not in {r["chunk_id"] for r in pre}
    assert "c" in {r["chunk_id"] for r in post}


def test_url_ndcg_collapses_duplicate_chunks_and_full_gold_idcg():
    raw = [chunk("a", "g1", 1), chunk("b", "g1", 2), chunk("c", "wrong", 3)]
    result = url_metrics(raw, ["g1", "g2"])
    assert result["url_ndcg_at_10"] == pytest.approx(1 / (1 + 1 / math.log2(3)))
    assert result["gold_url_recall"] == 0.5
    assert result["G"] == 1


def test_first_loss_is_mutually_exclusive_and_url_diagnostic():
    raw = [chunk("a", "gold", 1), chunk("b", "other", 2)]
    assert first_url_loss(raw, raw, raw, raw, [], ["gold"]) == "budget"
    assert first_url_loss(raw, [], [], [], [], ["gold"]) == "pre_cap"
    assert first_url_loss([], [], [], [], [], ["gold"]) == "candidate_not_covered"


def test_trace_stage_has_identity_url_rank_and_token_count():
    row = stage([chunk("a", "https://a", 12, (1, 2))], {"a": 0.5})[0]
    assert (row["chunk_id"], row["url"], row["rank"], row["raw_rank"], row["chunk_tokens"]) == ("a", "https://a", 1, 12, 2)
    assert row["rerank_score"] == 0.5


def test_resume_rejects_changed_protocol_and_atomic_gzip_roundtrip(tmp_path):
    path = tmp_path / "manifest.json"
    freeze_manifest(path, {"identity_hash": digest({"a": 1})})
    freeze_manifest(path, {"identity_hash": digest({"a": 1})})
    with pytest.raises(ValueError, match="different"):
        freeze_manifest(path, {"identity_hash": digest({"a": 2})})
    compressed = tmp_path / "trace.json.gz"
    save_json(compressed, {"value": [1, "中文"]})
    assert load_json(compressed) == {"value": [1, "中文"]}
    assert not compressed.with_name(compressed.name + ".tmp").exists()


def test_e2_rejects_missing_and_automatic_utility():
    with pytest.raises(ValueError, match="independent human"):
        require_human_utility([])
    with pytest.raises(ValueError, match="cannot substitute"):
        require_human_utility([{"G": 1, "U": 2, "annotation_source": "llm_judge"}])
    require_human_utility([{"U": 2, "annotation_source": "human_adjudicated"}])


def test_duplicate_legacy_ids_keep_every_row_with_auditable_identity():
    original = [{"chunk_id": "a", "url": "u", "text": text} for text in ("first", "second", "first")]
    rows, audit = identify_corpus(original)
    assert len(rows) == len({r["chunk_id"] for r in rows}) == 3
    assert [r["text"] for r in rows] == ["first", "second", "first"]
    assert all(r["original_chunk_id"] == "a" for r in rows)
    assert audit["colliding_legacy_ids"] == 1
    assert audit["exact_duplicate_extra_rows"] == 1
    assert rows == identify_corpus(original)[0]


def test_e2_group_integrity_completeness_and_independence():
    from experiments.analyze_selection import validate
    spec = {"dev_groups": ["d"], "test_groups": ["t"], "configs": ["a", "b"],
            "tie_order": ["a", "b"], "primary_metric": "G", "token_budget": 512,
            "frozen_before_test_inspection": True}
    rows = [{"qid": q, "information_need_id": q, "group_id": group, "config_id": config, "token_budget": 512,
             "U": 2, "G": 1, "url_ndcg_at_10": 1, "source_policy": "open",
             "construction_source": "independent_information_need", "annotation_source": "human_adjudicated"}
            for q, group in (("q1", "d"), ("q2", "t")) for config in ("a", "b")]
    assert validate(rows, spec) == {"q1": "d", "q2": "t"}
    with pytest.raises(ValueError, match="all frozen configurations"):
        validate(rows[:-1], spec)
    with pytest.raises(ValueError, match="disjoint"):
        validate(rows, {**spec, "test_groups": ["d"]})
    with pytest.raises(ValueError, match="independently proposed"):
        validate([{**r, "construction_source": "legacy_page_informed"} for r in rows], spec)
    with pytest.raises(ValueError, match="token budget"):
        validate([{**r, "token_budget": 2048} for r in rows], spec)
    with pytest.raises(ValueError, match="group lists must be unique"):
        validate(rows, {**spec, "dev_groups": ["d", "d"]})
    with pytest.raises(ValueError, match="complete deterministic tie order"):
        validate(rows, {**spec, "configs": ["a", "b", "b"], "tie_order": ["a", "b", "b"]})
    with pytest.raises(ValueError, match="share an information need"):
        validate([{**r, "information_need_id": "same_need"} for r in rows], spec)
    with pytest.raises(ValueError, match="binary"):
        validate([{**r, "G": 0.5} for r in rows], spec)
    with pytest.raises(ValueError, match="ordinal integer"):
        validate([{**r, "U": True} for r in rows], spec)


def test_annotation_export_requires_frozen_human_fact_rubric(tmp_path):
    from experiments.annotation import export, write_jsonl
    rubric = tmp_path / "rubric.jsonl"
    write_jsonl(rubric, [{"qid": "q1", "necessary_facts": [], "rubric_author": "",
                          "frozen_before_system_output": False}])
    with pytest.raises(ValueError, match="domain-expert"):
        export(tmp_path / "run", rubric, tmp_path / "packet", 42)


def test_e2_selects_only_on_development_and_reports_paired_test_difference():
    from experiments.analyze_selection import evaluate
    spec = {"dev_groups": ["d1", "d2"], "test_groups": ["t1", "t2"], "configs": ["a", "b"],
            "tie_order": ["a", "b"], "primary_metric": "G", "token_budget": 512,
            "frozen_before_test_inspection": True, "seed": 42, "delta": 0.05,
            "bootstrap_repetitions": 1000}
    rows = [{"qid": group, "information_need_id": group, "group_id": group, "config_id": config, "token_budget": 512,
             "U": 2 if config == "b" else 0, "G": int(config == "a"),
             "url_ndcg_at_10": int(config == "a"), "source_policy": "open",
             "construction_source": "independent_information_need", "annotation_source": "human_adjudicated"}
            for group in ("d1", "d2", "t1", "t2") for config in ("a", "b")]
    result = evaluate(rows, spec)
    assert result["c_G"] == "a" and result["c_U"] == "b"
    assert result["test_U_difference"] == 1
    assert result["paired_group_bootstrap_95CI"] == [1, 1]
    assert result["dev_selection_frequencies"]["G"]["a"] == 1


def test_human_provenance_rejects_automatic_source_and_unverified_single_rater(tmp_path):
    from experiments.analyze_selection import verify_provenance
    path = tmp_path / "provenance.json"
    save_json(path, {"kind": "llm_judge", "annotator_ids": ["auto1", "auto2"]})
    with pytest.raises(ValueError, match="not automatic judgments"):
        verify_provenance([], path)
    save_json(path, {"kind": "human_adjudication", "annotator_ids": ["one"]})
    with pytest.raises(ValueError, match="at least two named"):
        verify_provenance([], path)


def test_e2_ties_use_frozen_order_and_test_labels_do_not_choose_configs():
    from experiments.analyze_selection import evaluate
    spec = {"dev_groups": ["d1", "d2"], "test_groups": ["t1", "t2"], "configs": ["a", "b"],
            "tie_order": ["b", "a"], "primary_metric": "G", "token_budget": 512,
            "frozen_before_test_inspection": True, "seed": 42, "delta": 0.05,
            "bootstrap_repetitions": 1000}
    rows = [{"qid": group, "information_need_id": group, "group_id": group, "config_id": config, "token_budget": 512,
             "U": 2 if (group.startswith("d") or config == "a") else 0, "G": 1,
             "url_ndcg_at_10": 1, "source_policy": "open",
             "construction_source": "independent_information_need", "annotation_source": "human_adjudicated"}
            for group in ("d1", "d2", "t1", "t2") for config in ("a", "b")]
    result = evaluate(rows, spec)
    assert result["c_G"] == result["c_U"] == "b"  # a wins on test; never used for selection
    assert result["test_U_difference"] == 0


def test_archived_human_provenance_checks_hashes_and_row_level_U(tmp_path):
    from experiments.analyze_selection import verify_provenance
    from experiments.annotation import write_jsonl
    from experiments.protocol import file_hash
    # Explicit synthetic fixture only; these values are never experimental data.
    row = {"qid": "fixture_q", "information_need_id": "fixture_need", "group_id": "fixture_group",
           "construction_source": "independent_information_need", "config_id": "fixture_config",
           "U": 2, "adjudication_record_id": "fixture_record"}
    files = {
        "rubric": [{"qid": "fixture_q", "necessary_facts": ["fixture fact"],
                    "frozen_before_system_output": True, "rubric_author": "fixture_author"}],
        "construction_manifest": [{k: row[k] for k in ("qid", "information_need_id", "group_id", "construction_source")}],
        "adjudication_records": [{"qid": "fixture_q", "config_id": "fixture_config", "U": 2,
            "adjudication_record_id": "fixture_record", "adjudicator_id": "fixture_adjudicator",
            "annotator_ratings": [{"annotator_id": "fixture_a", "U": 1}, {"annotator_id": "fixture_b", "U": 2}]}]}
    provenance = {"kind": "human_adjudication", "annotator_ids": ["fixture_a", "fixture_b"],
                  "adjudicator_id": "fixture_adjudicator"}
    for key, values in files.items():
        path = tmp_path / (key + ".jsonl")
        write_jsonl(path, values)
        provenance[key + "_file"] = path.name
        provenance[key + "_sha256"] = file_hash(path)
    path = tmp_path / "provenance.json"
    save_json(path, provenance)
    assert verify_provenance([row], path)["archival_integrity"].startswith("verified")
    with pytest.raises(ValueError, match="does not match its archived"):
        verify_provenance([{**row, "U": 0}], path)
    (tmp_path / "rubric.jsonl").write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="hash does not match"):
        verify_provenance([row], path)
