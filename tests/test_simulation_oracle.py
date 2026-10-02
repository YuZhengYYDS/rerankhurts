"""Independent oracle semantics, trace-prefix validation, and selector guards."""
from copy import deepcopy
import hashlib
import json
import re
import gzip
import sys
from types import SimpleNamespace

import pytest

from experiments.simulation.evaluate import (
    PINNED_MODELS, REPEATS, ROOT, SCENARIOS, SEED, check_final_context, compile_claims,
    configurations, evaluate_traces, first_support_loss, score_support, select_config,
    selection_analysis, span_token_end, structural_order, unique_index, validate_data,
    validate_manifest, verify_file_manifest, structural_budget_feasibility, load_pinned_tokenizer,
)
from experiments.protocol import require_human_utility


def encoded(text):
    offsets = [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]
    return {"input_ids": list(range(10, 10 + len(offsets))), "offset_mapping": offsets}


def oracle(policy="open", required=("f1",), claims=None):
    return {"required_fact_ids": list(required), "policy": policy,
            "allowed_url_prefixes": [] if policy == "open" else ["https://registry.invalid/"],
            "claims": claims or []}


def claim(cid, fact="f1", status="valid", admissible=True, end=3):
    return {"chunk_id": cid, "fact_id": fact, "status": status,
            "admissible": admissible, "complete_at_token": end}


def test_partial_span_cannot_omit_subject_value_or_late_version():
    text = "Cohort Amber uses handling route Delta under CURRENT revision."
    tokens = encoded(text)
    threshold = span_token_end(text, tokens["offset_mapping"], 0, len(text))
    c = {"c": {"url": "https://registry.invalid/page", "text": text}}
    claims = [claim("c", end=threshold)]
    assert score_support(oracle(), claims, {"c": threshold - 1}, c)["U_sim"] == 0
    assert score_support(oracle(), claims, {"c": threshold}, c)["U_sim"] == 1
    with pytest.raises(ValueError, match="offsets"):
        span_token_end(text, tokens["offset_mapping"][1:], 0, len(text))


def test_late_fact_requires_prefix_through_its_complete_span():
    text = "Unrelated lead-in. Cohort Amber uses Delta under CURRENT revision."
    tokens = encoded(text)
    start = text.index("Cohort")
    assert span_token_end(text, tokens["offset_mapping"], start, len(text)) == len(tokens["input_ids"])
    assert span_token_end(text, tokens["offset_mapping"], start, len(text)) > 2


def test_alternate_url_can_support_without_designated_gold_page():
    corpus = {"alt": {"url": "https://alternate.invalid/evidence"}}
    result = score_support(oracle(), [claim("alt")], {"alt": 3}, corpus)
    assert result["U_sim"] == 1
    assert result["C_sim"] is None


def test_designated_page_membership_alone_gives_no_support():
    corpus = {"gold": {"url": "https://registry.invalid/designated"}}
    assert score_support(oracle(), [], {"gold": 400}, corpus)["U_sim"] == 0


def test_duplicate_chunks_and_spans_do_not_count_a_fact_twice():
    corpus = {cid: {"url": "https://registry.invalid/shared"} for cid in ("a", "b")}
    claims = [claim("a"), claim("a"), claim("b")]
    result = score_support(oracle(required=("f1", "f2")), claims, {"a": 3, "b": 3}, corpus)
    assert result["supported_fact_count"] == 1
    assert result["fact_coverage"] == .5
    assert result["U_sim"] == 0


def test_multiple_distinct_facts_in_one_chunk_are_credited_separately():
    corpus = {"c": {"url": "https://registry.invalid/a"}}
    claims = [claim("c", "f1", end=3), claim("c", "f2", end=6)]
    assert score_support(oracle(required=("f1", "f2")), claims, {"c": 5}, corpus)["fact_coverage"] == .5
    assert score_support(oracle(required=("f1", "f2")), claims, {"c": 6}, corpus)["U_sim"] == 1


def test_obsolete_version_is_exposure_and_never_valid_support():
    corpus = {"old": {"url": "https://registry.invalid/old"}}
    result = score_support(oracle(), [claim("old", status="obsolete")], {"old": 3}, corpus)
    assert result["obsolete_exposure"] == 1
    assert result["U_sim"] == result["supported_fact_count"] == 0


def test_contradiction_does_not_erase_or_masquerade_as_valid_coverage():
    corpus = {cid: {"url": f"https://registry.invalid/{cid}"} for cid in ("yes", "no")}
    claims = [claim("yes"), claim("no", status="contradictory")]
    result = score_support(oracle(), claims, {"yes": 3, "no": 3}, corpus)
    assert result["U_sim"] == result["contradiction_exposure"] == 1
    assert score_support(oracle(), claims, {"no": 3}, corpus)["U_sim"] == 0


def test_partial_counterclaim_and_old_version_do_not_trigger_exposure():
    corpus = {"c": {"url": "https://registry.invalid/x"}}
    claims = [claim("c", status="contradictory", end=5), claim("c", status="obsolete", end=7)]
    result = score_support(oracle(), claims, {"c": 4}, corpus)
    assert result["obsolete_exposure"] == result["contradiction_exposure"] == 0


def test_source_policy_distinguishes_content_admissibility_and_all_context_compliance():
    corpus = {"allowed": {"url": "https://registry.invalid/a"}, "alt": {"url": "https://alternate.invalid/a"}}
    claims = [claim("alt", admissible=False), claim("allowed")]
    ref = oracle("constrained")
    alternate = score_support(ref, claims, {"alt": 3}, corpus)
    assert (alternate["U_sim"], alternate["admissible_U_sim"], alternate["C_sim"]) == (1, 0, 0)
    mixed = score_support(ref, claims, {"alt": 3, "allowed": 3}, corpus)
    assert (mixed["U_sim"], mixed["admissible_U_sim"], mixed["C_sim"]) == (1, 1, 0)
    assert score_support(ref, claims, {}, corpus)["C_sim"] == 0
    assert score_support(ref, claims, {"allowed": 3}, corpus)["C_sim"] == 1


def test_full_stage_support_and_final_prefix_have_distinct_loss_labels():
    scores = {name: {"U_sim": 1} for name in ("raw", "pre_cap", "rerank", "post_cap", "final")}
    scores["final"]["U_sim"] = 0
    assert first_support_loss(scores) == "budget"
    scores["pre_cap"]["U_sim"] = 0
    assert first_support_loss(scores) == "pre_cap"
    scores["raw"]["U_sim"] = 0
    assert first_support_loss(scores) == "candidate_not_covered"


class FakeTokenizer:
    sep_token_id = 999

    def decode(self, ids, **kwargs):
        return ",".join(map(str, ids))


def context_fixture():
    corpus = {"a": {"url": "https://registry.invalid/a"}, "b": {"url": "https://registry.invalid/b"}}
    tokenized = {"a": {"input_ids": [11, 12, 13]}, "b": {"input_ids": [21, 22, 23, 24]}}
    post = [{"chunk_id": cid, "url": corpus[cid]["url"]} for cid in ("a", "b")]
    final = {"budget": 6, "used_tokens": 6, "token_ids": [11, 12, 13, 999, 21, 22], "separator_tokens": 1,
             "chunks": [{"chunk_id": "a", "url": corpus["a"]["url"], "token_ids": [11, 12, 13], "delivered_tokens": 3,
                         "chunk_tokens": 3, "partial": False, "text": "11,12,13"},
                        {"chunk_id": "b", "url": corpus["b"]["url"], "token_ids": [21, 22], "delivered_tokens": 2,
                         "chunk_tokens": 4, "partial": True, "text": "21,22"}]}
    return corpus, tokenized, post, final


def test_saved_final_prefix_is_verified_token_for_token():
    corpus, tokenized, post, final = context_fixture()
    assert check_final_context(final, post, corpus, tokenized, FakeTokenizer(), 6) == {"a": 3, "b": 2}
    final["chunks"][1]["token_ids"] = [23, 24]
    with pytest.raises(ValueError, match="original chunk prefix"):
        check_final_context(final, post, corpus, tokenized, FakeTokenizer(), 6)


def test_changed_saved_text_and_separator_are_rejected():
    corpus, tokenized, post, final = context_fixture()
    modified = deepcopy(final)
    modified["chunks"][1]["text"] = "fabricated complete proposition"
    with pytest.raises(ValueError, match="decoded"):
        check_final_context(modified, post, corpus, tokenized, FakeTokenizer(), 6)
    final["token_ids"][3] = 777
    with pytest.raises(ValueError, match="token stream"):
        check_final_context(final, post, corpus, tokenized, FakeTokenizer(), 6)


def test_unknown_ids_duplicate_ids_and_incomplete_trace_set_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="duplicate"):
        unique_index([{"qid": "q"}, {"qid": "q"}], "qid", "test")
    (tmp_path / "traces").mkdir()
    with pytest.raises(ValueError, match="120 trace"):
        evaluate_traces(tmp_path, {}, {}, {}, {}, {}, None, {})


def test_duplicate_configuration_ids_are_rejected_before_any_metric(tmp_path):
    trace_dir = tmp_path / "traces"
    trace_dir.mkdir()
    question = {"qid": "q", "question": "Fictional need", "group_id": "world", "topic": "fictional",
                "construction_source": "synthetic_information_need", "gold_urls": ["https://registry.invalid/a"]}
    trace = {**question, "identity_hash": "identity", "configurations": [{"configuration": configurations()[0]}] * 20}
    for i in range(120):
        (trace_dir / f"{i:03d}.json.gz").write_bytes(gzip.compress(json.dumps(trace).encode()))
    with pytest.raises(ValueError, match="configuration trace"):
        evaluate_traces(tmp_path, {}, {"q": question}, {}, {}, {}, None, {"identity_hash": "identity"})


def test_unknown_trace_qid_is_not_silently_dropped(tmp_path):
    trace_dir = tmp_path / "traces"
    trace_dir.mkdir()
    for i in range(120):
        (trace_dir / f"{i:03d}.json.gz").write_bytes(gzip.compress(b'{"qid":"unknown"}'))
    with pytest.raises(ValueError, match="Unknown or duplicate query"):
        evaluate_traces(tmp_path, {}, {}, {}, {}, {}, None, {})


def test_changed_data_bytes_are_rejected_before_scoring(tmp_path):
    for name in ("corpus.jsonl", "questions.jsonl", "oracle.jsonl"):
        (tmp_path / name).write_bytes(b"{}\n")
    specification = {"files": {name: {"sha256": hashlib.sha256(b"{}\n").hexdigest()} for name in ("corpus.jsonl", "questions.jsonl", "oracle.jsonl")}}
    verify_file_manifest(tmp_path, specification)
    (tmp_path / "oracle.jsonl").write_text('{"changed":true}\n')
    with pytest.raises(ValueError, match="hash mismatch"):
        verify_file_manifest(tmp_path, specification)


def test_incomplete_run_status_is_rejected(tmp_path):
    (tmp_path / "manifest.json").write_text("{}")
    (tmp_path / "status.json").write_text('{"status":"partial","observed_records":20,"expected_records":2400}')
    with pytest.raises(ValueError, match="complete 120"):
        validate_manifest(tmp_path, tmp_path, {}, {})


def selection_fixture():
    rows = []
    dev = [f"dev{i}" for i in range(20)]
    test = [f"test{i}" for i in range(40)]
    ordered = sorted((c for c in configurations() if c["budget"] == 512), key=structural_order)
    g_choice, u_choice = ordered[0]["config_id"], ordered[-1]["config_id"]
    for split, groups in (("dev", dev), ("test", test)):
        for i, gid in enumerate(groups):
            for config in ordered:
                cid = config["config_id"]
                utility = int(cid == u_choice) if split == "dev" else int(cid == g_choice)
                rows.append({"group_id": gid, "split": split, "policy": "open", **config,
                             "G_final": int(cid == g_choice), "U_sim": utility, "fact_coverage": utility,
                             "contradiction_exposure": 0, "obsolete_exposure": 0})
    return rows, {"selection": {"dev_groups": dev, "test_groups": test}}, g_choice, u_choice


def test_development_only_selection_retains_reversed_test_gap():
    rows, spec, g_choice, u_choice = selection_fixture()
    result = selection_analysis(rows, spec, 512)
    assert result["dev_selected_by_G"] == g_choice
    assert result["dev_selected_by_U_sim"] == u_choice
    assert result["test_U_sim_delta_U_selected_minus_G_selected"] == -1
    assert result["paired_test_group_bootstrap_95ci"] == [-1, -1]
    assert result["bootstrap_repetitions"] == REPEATS
    for metric in ("G_final", "U_sim"):
        assert sum(value["count"] for value in result["development_bootstrap_selection_frequencies"][metric].values()) == REPEATS


def test_all_ties_follow_structural_rule_and_null_gap_is_retained():
    rows, spec, _, _ = selection_fixture()
    for row in rows:
        row["G_final"] = row["U_sim"] = 1
    result = selection_analysis(rows, spec, 512)
    assert len(result["dev_all_ties"]["G_final"]) == len(result["dev_all_ties"]["U_sim"]) == 10
    assert result["dev_selected_by_G"] == result["dev_selected_by_U_sim"] == "p16_off_none_b512"
    assert result["test_U_sim_delta_U_selected_minus_G_selected"] == 0
    assert result["paired_test_group_bootstrap_95ci"] == [0, 0]


def test_duplicate_policy_group_or_missing_configuration_cannot_enter_selector():
    rows, spec, _, _ = selection_fixture()
    with pytest.raises(ValueError, match="Duplicate"):
        selection_analysis(rows + [rows[0]], spec, 512)
    with pytest.raises(ValueError, match="incomplete"):
        selection_analysis(rows[1:], spec, 512)


def test_synthetic_oracle_never_passes_human_e2_guard():
    with pytest.raises(ValueError):
        require_human_utility([{"U": 2, "annotation_source": "synthetic_oracle"}])


def test_structural_budget_bound_is_necessary_and_separates_admissible_spans():
    questions = {"q": {"group_id": "g", "split": "dev", "scenario": "late_evidence", "policy": "constrained"}}
    references = {"q": oracle("constrained", ("f1", "f2"))}
    claims = {"q": [claim("a", "f1", end=500), claim("b", "f2", end=600), claim("c", "f2", admissible=False, end=400)]}
    result = structural_budget_feasibility(questions, references, claims)["per_task_budget"]
    small = next(r for r in result if r["budget"] == 512)
    assert small["necessary_condition_for_U_sim_satisfied"] is True
    # Individual feasible facts can total 900 tokens; this condition does not
    # claim the evidence packs jointly into the 512-token context.
    assert small["necessary_condition_for_admissible_U_sim_satisfied"] is False
    assert small["facts_without_any_budget_feasible_admissible_span"] == ["f2"]
    large = next(r for r in result if r["budget"] == 2048)
    assert large["necessary_condition_for_admissible_U_sim_satisfied"] is True


def tokenizer_manifest_fixture(tmp_path, monkeypatch):
    import experiments.simulation.evaluate as evaluator
    monkeypatch.setattr(evaluator, "ROOT", tmp_path)
    model = {"model": "google-bert/bert-base-uncased", "sha": "f" * 40}
    run = tmp_path / "run"
    (run / "model_files").mkdir(parents=True)
    payload = b'{"test":"tokenizer"}'
    file_manifest = {**model, "tokenizer_only": True, "files": {"tokenizer.json": hashlib.sha256(payload).hexdigest()}}
    (run / "model_files/google-bert--bert-base-uncased.json").write_text(json.dumps(file_manifest))
    monkeypatch.setitem(sys.modules, "transformers", SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=lambda *a, **kw: SimpleNamespace(is_fast=True, sep_token_id=102))))
    return run, {"identity": {"models": {"tokenizer": model}}}, payload


def test_absent_tokenizer_download_is_pinned_and_only_requests_missing_files(tmp_path, monkeypatch):
    run, manifest, payload = tokenizer_manifest_fixture(tmp_path, monkeypatch)
    calls = []
    def download(**kwargs):
        calls.append(kwargs)
        kwargs["local_dir"].mkdir(parents=True, exist_ok=True)
        (kwargs["local_dir"] / "tokenizer.json").write_bytes(payload)
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=download))
    load_pinned_tokenizer(run, manifest)
    assert calls[0]["revision"] == "f" * 40
    assert calls[0]["allow_patterns"] == ["tokenizer.json"]
    load_pinned_tokenizer(run, manifest)
    assert len(calls) == 1  # No network after all recorded bytes are present.


def test_present_corrupt_tokenizer_is_rejected_not_silently_redownloaded(tmp_path, monkeypatch):
    run, manifest, _ = tokenizer_manifest_fixture(tmp_path, monkeypatch)
    local = tmp_path / ".cache/models/google-bert--bert-base-uncased" / ("f" * 40)
    local.mkdir(parents=True)
    (local / "tokenizer.json").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="bytes differ"):
        load_pinned_tokenizer(run, manifest)


def data_fixture():
    corpus, questions, references = [], [], []
    dev, test = [], []
    for si, scenario in enumerate(sorted(SCENARIOS)):
        for j in range(10):
            group = f"world_{si}_{j}"
            split = "dev" if j < 3 + int(si >= 4) else "test"
            (dev if split == "dev" else test).append(group)
            cid = f"chunk_{si}_{j}"
            url = f"https://{group}.registry.invalid/evidence"
            text = f"World {group} requires current route Delta."
            corpus.append({"chunk_id": cid, "url": url, "text": text})
            for policy in ("open", "constrained"):
                qid = f"{group}_{policy}"
                questions.append({"qid": qid, "question": f"Requirement of {group}? {policy}", "group_id": group,
                                  "split": split, "policy": policy, "scenario": scenario, "gold_urls": [url],
                                  "construction_source": "synthetic_information_need", "topic": "fictional"})
                references.append({"qid": qid, "group_id": group, "split": split, "policy": policy, "scenario": scenario,
                                   "required_fact_ids": ["f"], "allowed_url_prefixes": [url] if policy == "constrained" else [],
                                   "claims": [{"chunk_id": cid, "fact_id": "f", "start_char": 0, "end_char": len(text), "status": "valid", "admissible": True}]})
    primary = [c["config_id"] for c in sorted((c for c in configurations() if c["budget"] == 512), key=structural_order)]
    spec = {"status": "complete", "annotation_source": "synthetic_oracle", "generation_seed": SEED,
            "files": {"corpus.jsonl": {"rows": 60}, "questions.jsonl": {"rows": 120}, "oracle.jsonl": {"rows": 120}},
            "models": {key: {"model": value[0], "sha": value[1]} for key, value in PINNED_MODELS.items()},
            "selection": {"frozen_before_model_execution": True, "dev_groups": dev, "test_groups": test,
                          "primary_policy": "open", "primary_budget": 512, "secondary_budget": 2048,
                          "bootstrap_seed": SEED, "bootstrap_repetitions": REPEATS, "configs": primary, "tie_order": primary,
                          "primary_endpoint": "U_sim", "primary_G": "G_final", "weighting": "equal_information_needs"}}
    return corpus, questions, references, spec


def test_open_and_constrained_versions_cannot_cross_group_split():
    corpus, questions, references, spec = data_fixture()
    assert len(validate_data(corpus, questions, references, spec)[3]) == 60
    questions[1]["split"] = references[1]["split"] = "test"
    with pytest.raises(ValueError, match="crosses split"):
        validate_data(corpus, questions, references, spec)


def test_oracle_unknown_chunk_id_and_wrong_source_admissibility_fail():
    corpus, questions, references, spec = data_fixture()
    broken = deepcopy(references)
    broken[0]["claims"][0]["chunk_id"] = "unknown"
    with pytest.raises(ValueError, match="Unknown oracle"):
        validate_data(corpus, questions, broken, spec)
    references[1]["claims"][0]["admissible"] = False
    with pytest.raises(ValueError, match="admissibility"):
        validate_data(corpus, questions, references, spec)


def test_actual_pinned_bert_wordpiece_offset_boundary():
    transformers = pytest.importorskip("transformers")
    name, revision = PINNED_MODELS["tokenizer"]
    path = ROOT / ".cache/models" / name.replace("/", "--") / revision
    if not path.is_dir():
        pytest.skip("Pinned local BERT tokenizer has not been downloaded")
    tokenizer = transformers.AutoTokenizer.from_pretrained(path, local_files_only=True, use_fast=True)
    text = "Cohort Malvaria requires Quendrix clearance under the current revision."
    result = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    end = span_token_end(text, result["offset_mapping"], 0, len(text))
    assert end == len(result["input_ids"])
    assert score_support(oracle(), [claim("c", end=end)], {"c": end - 1}, {"c": {"url": "https://registry.invalid/c"}})["U_sim"] == 0
