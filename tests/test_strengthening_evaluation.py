"""Meaningful oracle-authenticity and world-level inference regression checks."""
import copy
import json

import pandas as pd
import pytest

from experiments.strengthening.evaluate import (
    feasibility_bound, mask_cost_bound, score_evidence, stage_flow, verify_final_context, STAGES,
)
from experiments.strengthening.analyze import bh_adjust, holm_adjust, paired_world_values, world_statistics


@pytest.fixture
def evidence():
    corpus = {
        "a": {"chunk_id": "a", "url": "https://allowed.invalid/a", "text": "A current route X. A current days 7."},
        "b": {"chunk_id": "b", "url": "https://other.invalid/b", "text": "A current route X. A current days 7."},
        "c": {"chunk_id": "c", "url": "https://allowed.invalid/c", "text": "A old route Y. A current route Z."},
    }
    truth = {"required_fact_ids": ["route", "days"]}
    meta = {"required_fact_ids": ["route", "days"], "gold_urls": [corpus["a"]["url"]],
            "allowed_url_prefixes": ["https://allowed.invalid/"]}
    parsed = {cid: [
        {"chunk_id": cid, "fact_id": "route", "status": "valid", "start_char": 0, "end_char": 18},
        {"chunk_id": cid, "fact_id": "days", "status": "valid", "start_char": 19, "end_char": 36},
    ] for cid in ("a", "b")}
    parsed["c"] = [
        {"chunk_id": "c", "fact_id": "route", "status": "obsolete", "start_char": 0, "end_char": 14},
        {"chunk_id": "c", "fact_id": "route", "status": "contradictory", "start_char": 15, "end_char": 33},
    ]
    # Use actual punctuation boundaries to keep this fixture internally valid.
    for cid in parsed:
        ends = [i + 1 for i, char in enumerate(corpus[cid]["text"]) if char == "."]
        for index, claim in enumerate(parsed[cid]):
            claim["start_char"] = 0 if index == 0 else ends[index - 1] + 1
            claim["end_char"] = ends[index]
    return corpus, truth, meta, parsed


def test_exact_coverage_and_policy_are_separate(evidence):
    corpus, truth, meta, parsed = evidence
    result = score_evidence([{"chunk_id": "b"}], corpus, truth, meta, parsed)
    assert result["U_sim"] == 1 and result["admissible_U_sim"] == 0
    assert result["C_sim"] == 0 and result["nonempty"] == 1 and result["G_final"] == 0
    empty = score_evidence([], corpus, truth, meta, parsed)
    assert empty["C_sim"] == empty["U_sim"] == empty["nonempty"] == 0


def test_partial_statement_does_not_receive_support(evidence):
    corpus, truth, meta, parsed = evidence
    end = parsed["a"][1]["end_char"] - 1
    result = score_evidence([{"chunk_id": "a", "char_start": 0, "char_end": end,
                              "text": corpus["a"]["text"][:end]}], corpus, truth, meta, parsed)
    assert result["G_final"] == 1 and result["U_sim"] == 0 and result["fact_coverage"] == .5
    assert [claim["fact_id"] for claim in result["delivered_claims"]] == ["route"]


def test_obsolete_and_conflict_exposures_are_not_positive_support(evidence):
    corpus, truth, meta, parsed = evidence
    result = score_evidence([{"chunk_id": "c"}], corpus, truth, meta, parsed)
    assert result["U_sim"] == 0 and result["fact_coverage"] == 0
    assert result["obsolete_exposure"] == result["contradiction_exposure"] == 1


def test_adjacent_source_intervals_jointly_cover_claim_without_single_source_credit(evidence):
    corpus, truth, meta, parsed = evidence
    fragments = [{"chunk_id": "a", "char_start": 0, "char_end": 8},
                 {"chunk_id": "a", "char_start": 8, "char_end": 18}]
    result = score_evidence(fragments, corpus, truth, meta, parsed)
    assert result["supported_fact_count"] == 1
    claim = result["delivered_claims"][0]
    assert claim["source_indices"] == [1, 2] and claim["source_index"] is None
    assert not claim["intact_single_source"]
    fragments[1]["char_start"] = 11
    assert score_evidence(fragments, corpus, truth, meta, parsed)["supported_fact_count"] == 0


def test_forged_text_and_url_rejected(evidence):
    corpus, truth, meta, parsed = evidence
    with pytest.raises(ValueError, match="text differs"):
        score_evidence([{"chunk_id": "a", "text": "forged"}], corpus, truth, meta, parsed)
    with pytest.raises(ValueError, match="URL differs"):
        score_evidence([{"chunk_id": "b", "url": corpus["a"]["url"]}], corpus, truth, meta, parsed)


@pytest.fixture
def token_evidence():
    corpus = {"a": {"text": "abc def ghi", "url": "u"}}
    encoded = {"a": {"input_ids": [10, 11, 12], "offset_mapping": [(0, 3), (4, 7), (8, 11)]}}
    final = {"chunks": [{"chunk_id": "a", "source_token_start": 1, "source_token_end": 3,
                          "char_start": 4, "char_end": 11, "text": "def ghi", "token_ids": [11, 12]}],
             "token_ids": [11, 12], "used_tokens": 2, "budget": 2}
    return corpus, encoded, final


def test_token_and_character_delivery_verified(token_evidence):
    corpus, encoded, final = token_evidence
    assert verify_final_context(final, corpus, encoded, 102)
    forged = copy.deepcopy(final)
    forged["chunks"][0]["token_ids"][0] = 999
    with pytest.raises(ValueError, match="token IDs differ"):
        verify_final_context(forged, corpus, encoded, 102)


def test_unbudgeted_text_and_overlap_rejected(token_evidence):
    corpus, encoded, final = token_evidence
    forged = copy.deepcopy(final)
    forged["chunks"][0].update(char_start=0, text="abc def ghi")
    with pytest.raises(ValueError, match="unbudgeted"):
        verify_final_context(forged, corpus, encoded, 102)
    forged = copy.deepcopy(final)
    forged["chunks"] *= 2
    with pytest.raises(ValueError, match="Overlapping"):
        verify_final_context(forged, corpus, encoded, 102)


def test_separator_and_budget_cannot_be_forged(token_evidence):
    corpus, encoded, final = token_evidence
    forged = copy.deepcopy(final)
    forged["token_ids"] += [102]
    with pytest.raises(ValueError, match="token stream"):
        verify_final_context(forged, corpus, encoded, 102)
    forged = copy.deepcopy(final)
    forged["budget"] = 1
    with pytest.raises(ValueError, match="Budget"):
        verify_final_context(forged, corpus, encoded, 102)


def test_cover_bound_costs_separators_and_alternative_support():
    assert mask_cost_bound([(1, 3), (2, 5)], 2) == 9
    assert mask_cost_bound([(1, 3), (2, 5), (3, 7)], 2) == 7
    assert mask_cost_bound([(1, 3)], 2) is None


def test_window_bound_allows_final_prefix_and_does_not_inherit_prefix_infeasibility():
    text = " ".join(["x"] * 10)
    corpus = {"c": {"text": text, "url": "u"}}
    encoded = {"c": {"input_ids": list(range(10)), "offset_mapping": [(2 * i, 2 * i + 1) for i in range(10)]}}
    parsed = {"c": [{"status": "valid", "fact_id": "f", "start_char": 8, "end_char": 9}]}
    meta = {"required_fact_ids": ["f"], "allowed_url_prefixes": []}
    prefix = feasibility_bound(corpus, parsed, encoded, meta, "prefix")
    window = feasibility_bound(corpus, parsed, encoded, meta, "window", window_tokens=4)
    whole = feasibility_bound(corpus, parsed, encoded, meta, "whole")
    assert prefix["minimum_relaxed_tokens"] == 5
    assert window["minimum_relaxed_tokens"] == 1
    assert whole["minimum_relaxed_tokens"] == 10


def test_pure_reranking_cannot_delete_support():
    scores = {stage: {"supported_fact_ids": ["f"], "U_sim": 1} for stage in (*STAGES, "final")}
    rows = {stage: [{"chunk_id": "a"}] for stage in STAGES}
    assert stage_flow(scores, rows)["budget_full_coverage_loss"] == 0
    rows["rerank"] = []
    with pytest.raises(ValueError, match="Pure reranking"):
        stage_flow(scores, rows)


def test_world_weighting_not_task_pseudoreplication():
    rows = []
    for group, variants, effect in (("w1", 2, 1), ("w2", 1, 0)):
        for index in range(variants):
            for config, value in (("a", effect), ("b", 0)):
                rows.append({"qid": f"{group}-{index}", "group_id": group, "seed": 1,
                             "config_id": config, "U_sim": value})
    worlds, pairs = paired_world_values(pd.DataFrame(rows), "a", "b")
    assert len(pairs) == 3 and len(worlds) == 2 and worlds.difference.mean() == .5
    result = world_statistics(worlds, repeats=100, permutation_repeats=100, seed=9)
    assert result["difference"] == .5 and result["n_worlds"] == 2


def test_missing_pairs_and_duplicate_rows_rejected():
    frame = pd.DataFrame([{"qid": "q", "group_id": "w", "seed": 1, "config_id": "a", "U_sim": 1}])
    with pytest.raises(ValueError, match="unpaired"):
        paired_world_values(frame, "a", "b")
    with pytest.raises(ValueError, match="Duplicate"):
        paired_world_values(pd.concat([frame, frame]), "a", "b")


def test_null_statistics_do_not_claim_equivalence():
    worlds = pd.DataFrame({"group_id": ["a", "b", "c"], "seed": [1, 1, 2], "difference": [0., 0., 0.]})
    result = world_statistics(worlds, repeats=100, permutation_repeats=100)
    assert result["difference"] == result["ci95_low"] == result["ci95_high"] == 0
    assert result["p_sign_flip"] == 1 and result["all_world_differences_zero"]
    assert "not proof of equivalence" in result["interval_interpretation"]


def test_multiplicity_adjustment_families():
    assert holm_adjust([.01, .04]) == pytest.approx([.02, .04])
    assert holm_adjust([.04, .01, .03]) == pytest.approx([.06, .03, .06])
    assert bh_adjust([.01, .04, .03]) == pytest.approx([.03, .04, .04])


def test_full_analysis_writes_world_primary_and_control_reports(tmp_path):
    from experiments.strengthening.protocol import Config
    from experiments.strengthening.analyze import ENDPOINTS, analyze
    configurations = [Config(cap=2, cap_stage=stage, budget=budget) for stage in ("pre", "post") for budget in (512, 2048)]
    rows = []
    for group in ("w1", "w2"):
        for variant in ("low_concentration", "high_concentration"):
            for configuration in configurations:
                row = {"qid": group + variant, "group_id": group, "seed": 1, "split": "test", "template_family": "qa",
                       "test_regime": "heldout_template", "scenario": "single_chunk", "variant_id": variant,
                       "policy": "constrained", "raw_max_chunks_per_source": 1, "final_delivery_sha256": "same",
                       "factor_duplicate_chunks": 0, "raw_U_sim": 0, "post_cap_U_sim": 0,
                       "budget_full_coverage_loss": 0, **configuration.record(), **{key: 0 for key in ENDPOINTS}}
                rows.append(row)
    pd.DataFrame(rows).to_csv(tmp_path / "per_record.csv", index=False)
    (tmp_path / "status.json").write_text('{"status":"complete"}', encoding="utf-8")
    plan = {"statistics": {"bootstrap_repetitions": 40, "permutation_repetitions": 40, "bootstrap_seed": 5},
            "primary_comparisons": [{"name": f"cap_order_{budget}", "retriever": "dense", "pool": 64,
                "reranker": "m3", "cap": 2, "budget": budget, "packing": "prefix", "score_view": "prefix512",
                "dense_view": "prefix512", "policy_stage": "none", "endpoint": "U_sim"} for budget in (512, 2048)]}
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")
    report = analyze(tmp_path, path, exploratory=True)
    assert report["status"] == "complete" and len(report["primary"]) == 2
    assert all(row["n_worlds"] == 2 and row["p_holm"] == 1 for row in report["primary"])
    assert (tmp_path / "exploratory_contrasts.csv").exists()
    assert json.loads((tmp_path / "controls.json").read_text())[0]["different_delivery_no_op_tasks"] == 0


def test_cross_window_claim_bound_covers_both_adjacent_fragments():
    text = " ".join(["x"] * 10)
    corpus = {"c": {"text": text, "url": "u"}}
    encoded = {"c": {"input_ids": list(range(10)), "offset_mapping": [(2 * i, 2 * i + 1) for i in range(10)]}}
    parsed = {"c": [{"status": "valid", "fact_id": "f", "start_char": 6, "end_char": 11}]}
    meta = {"required_fact_ids": ["f"], "allowed_url_prefixes": []}
    # Fact spans tokens 3..5: first four-token window + two tokens of the
    # second window + one separator. It must not be marked impossible.
    result = feasibility_bound(corpus, parsed, encoded, meta, "window", window_tokens=4)
    assert result["minimum_relaxed_tokens"] == 7
