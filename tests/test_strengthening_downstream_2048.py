"""Follow-up invariants against frozen inputs and substantive corruption cases."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("fcntl", reason="Original follow-up execution uses Linux fcntl locking")

from experiments.strengthening import downstream_2048 as followup
from experiments.strengthening import analyze_answers_2048 as analysis
from experiments.strengthening.protocol import digest, load_json, save_json


@pytest.fixture(scope="module")
def frozen_tasks():
    baseline = load_json(followup.BASELINE)
    metadata = {r["qid"]: r for r in followup.read_jsonl(followup.DATA / "metadata.jsonl")}
    return baseline, [metadata[q] for q in sorted(baseline["identity"]["questions"])]


def test_exact_original_sample_and_world_variants(frozen_tasks):
    baseline, tasks = frozen_tasks
    require_qids = baseline["identity"]["questions"]
    assert len(require_qids) == len(set(require_qids)) == 120
    assert {t["group_id"] for t in tasks} == set(baseline["identity"]["worlds"])
    for seed in (20261002, 20261003, 20261004):
        part = [t for t in tasks if t["seed"] == seed]
        assert len(part) == 40 and len({t["group_id"] for t in part}) == 20
    for group in baseline["identity"]["worlds"]:
        assert {t["variant_id"] for t in tasks if t["group_id"] == group} == {"low_concentration", "high_concentration"}


def test_conditions_are_m3_and_differ_only_in_cap():
    off, post = [c.record() for c in followup.CONDITIONS.values()]
    assert (off["config_id"], post["config_id"]) == followup.EXPECTED_CONFIG_IDS
    assert off["reranker"] == post["reranker"] == "m3"
    assert {k for k in off if off[k] != post[k]} == {"config_id", "cap", "cap_stage"}
    assert off["budget"] == 2048 and off["dense_view"] == off["score_view"] == "prefix512"


def test_duplicate_or_missing_original_sample_is_rejected(tmp_path, frozen_tasks):
    baseline, _ = frozen_tasks
    altered = copy.deepcopy(baseline)
    altered["identity"]["questions"] = altered["identity"]["questions"][:-1]
    altered["identity_hash"] = digest(altered["identity"])
    path = tmp_path / "manifest.json"
    save_json(path, altered)
    with pytest.raises(ValueError, match="sample size"):
        followup.baseline_checks(SimpleNamespace(baseline_manifest=path))


def test_saved_context_is_used_without_repacking(frozen_tasks):
    baseline, tasks = frozen_tasks
    qid = tasks[0]["qid"]
    trace = load_json(followup.trace_path(followup.RUN, qid))
    records = {r["configuration"]["config_id"]: r for r in trace["configurations"]}
    final = records[followup.EXPECTED_CONFIG_IDS[0]]["final_context"]
    bundle = {"finals": {(qid, "m3_off_prefix"): final}}
    assert followup.selected_final(bundle, "run", qid, "m3_off_prefix") is final
    fragments = followup.input_evidence(final)
    assert [r["chunk_id"] for r in fragments] == [c["chunk_id"] for c in final["chunks"]]
    assert fragments[-1]["source_token_end"] == final["chunks"][-1]["source_token_end"]


def test_real_pinned_intervals_reject_altered_text_and_token(frozen_tasks):
    from transformers import AutoTokenizer
    baseline, tasks = frozen_tasks
    manifest = load_json(followup.RUN / "manifest.json")
    spec = manifest["identity"]["models"]["tokenizer"]
    path = followup.model_path(spec)
    if not path.is_dir():
        pytest.skip("Pinned tokenizer download has not completed")
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, use_fast=True)
    qid = tasks[0]["qid"]
    trace = load_json(followup.trace_path(followup.RUN, qid))
    final = next(r for r in trace["configurations"] if r["configuration"]["config_id"] == followup.EXPECTED_CONFIG_IDS[0])["final_context"]
    ids = {c["chunk_id"] for c in final["chunks"]}
    corpus = {c["chunk_id"]: c for c in followup.read_jsonl(followup.DATA / "corpus.jsonl") if c["chunk_id"] in ids}
    encoded = followup.encode_corpus(corpus, tokenizer)
    assert followup.verify_final_context(final, corpus, encoded, tokenizer.sep_token_id)
    changed = copy.deepcopy(final)
    changed["chunks"][0]["token_ids"][0] += 1
    with pytest.raises(ValueError, match="token IDs"):
        followup.verify_final_context(changed, corpus, encoded, tokenizer.sep_token_id)
    changed = copy.deepcopy(final)
    changed["chunks"][0]["text"] += " forged"
    with pytest.raises(ValueError, match="text differs"):
        followup.verify_final_context(changed, corpus, encoded, tokenizer.sep_token_id)


def test_resume_skips_valid_checkpoint_and_rejects_foreign_or_bad_score(tmp_path):
    path = tmp_path / "responses/item.json"
    calls = []
    def produce():
        calls.append(1)
        return {"identity_hash": "a", "evaluation": 1}
    def validate(record):
        if record["evaluation"] != 1:
            raise ValueError("Bad saved score")
    assert followup.checkpoint(path, "a", produce, validate)[1]
    assert not followup.checkpoint(path, "a", produce, validate)[1]
    assert len(calls) == 1
    with pytest.raises(ValueError, match="different generation identity"):
        followup.checkpoint(path, "b", produce, validate)
    save_json(path, {"identity_hash": "a", "evaluation": 0})
    with pytest.raises(ValueError, match="Bad saved score"):
        followup.checkpoint(path, "a", produce, validate)
    assert len(calls) == 1


def test_writer_lock_prevents_second_writer(tmp_path):
    with followup.writer_lock(tmp_path):
        with pytest.raises(ValueError, match="Another writer"):
            with followup.writer_lock(tmp_path):
                pass


@pytest.fixture
def answer_matrix(frozen_tasks):
    baseline, tasks = frozen_tasks
    identity = {"questions": sorted(baseline["identity"]["questions"]), "tasks": tasks}
    rows = []
    for task in tasks:
        for condition in analysis.CONDITIONS:
            post = condition == "m3_post_prefix"
            rows.append({**{k: task[k] for k in ("qid", "group_id", "seed", "variant_id", "scenario", "policy", "template_family")},
                         "condition": condition, "config_id": followup.CONDITIONS[condition].config_id,
                         "complete_correct": int(post), "complete_grounded_correct": 0,
                         "field_accuracy": .75 if post else .25, "grounded_field_accuracy": 0.,
                         "schema_valid": True, "unsupported_fields": 1, "unsupported_abstentions": 0, "unsupported_answers": 1,
                         "prompt_tokens": 2500, "generated_tokens": 100, "generation_ms": 1000.,
                         "hit_max_new_tokens": False, "truncated_output": False, "parsed_json_object": True})
    return identity, rows


def test_analysis_direction_world_weighting_and_four_endpoint_family(answer_matrix):
    identity, rows = answer_matrix
    result = analysis.compute(rows, identity)
    assert len(result["world_summary"]) == 120
    first, null = result["contrasts"][:2]
    assert first["difference"] == 1 and first["ci95_low"] == first["ci95_high"] == 1
    assert first["n_worlds"] == 60 and first["n_task_pairs"] == 120
    assert null["difference"] == 0 and null["all_world_differences_zero"] is True
    assert "not proof of equivalence" in null["interval_interpretation"]
    assert len(result["contrasts"]) == 4 and all(r["family_size"] == 4 for r in result["contrasts"])
    assert result["transitions"]["complete_correct"]["counts"]["only_post_cap_correct"] == 120


@pytest.mark.parametrize("corruption", ["missing", "duplicate", "extra_old_condition", "wrong_variant", "wrong_world"])
def test_analysis_rejects_incomplete_or_foreign_pairs(answer_matrix, corruption):
    identity, rows = copy.deepcopy(answer_matrix)
    if corruption == "missing":
        rows.pop()
    elif corruption == "duplicate":
        rows[-1] = rows[0]
    elif corruption == "extra_old_condition":
        rows[-1]["condition"] = "dense_prefix"
    elif corruption == "wrong_variant":
        rows[-1]["variant_id"] = "unknown_variant"
    else:
        rows[-1]["group_id"] = "foreign_world"
    with pytest.raises(ValueError):
        analysis.compute(rows, identity)


def test_false_string_is_not_truthy_in_analysis():
    assert analysis.number("False", binary=True) == 0
    assert analysis.number("True", binary=True) == 1
    with pytest.raises(ValueError):
        analysis.number("maybe", binary=True)
    with pytest.raises(ValueError):
        analysis.number("nan")


def test_repeats_compare_raw_tokens_even_if_text_and_scores_match():
    identity = {"questions": ["q"], "conditions": {"c": {}}}
    common = {"qid": "q", "condition": "c", "messages": [], "prompt_sha256": "p", "prompt_token_ids": [1],
              "generated_token_ids": [2], "response": "same", "evaluation": {"complete_correct": 0}}
    records = [dict(common, repeat=0), dict(common, repeat=1)]
    assert followup.compare_repeats(records, identity)["same_machine_identical"]
    records[1]["generated_token_ids"] = [3]
    with pytest.raises(ValueError, match="repeatability failed"):
        followup.compare_repeats(records, identity)


def test_generation_identity_excludes_analysis_module():
    hashes = followup.generation_code_hashes()
    assert set(hashes) == {*followup.ORIGINAL_CODE, "downstream_2048.py"}
    assert "analyze_answers_2048.py" not in hashes


def test_formal_gate_rejects_changed_hardware_before_generation(tmp_path):
    identity = {"environment": {"gpu_uuid": "GPU-original"}, "effective_generation_config": {"num_beams": 1}, "chat_template_sha256": "a"}
    for gate in ("baseline512", "smoke2048"):
        save_json(tmp_path / gate / "manifest.json", {"identity": identity})
    args = SimpleNamespace(work=tmp_path)
    followup.require_gate_environment(args, identity, "run")
    altered = copy.deepcopy(identity)
    altered["environment"]["gpu_uuid"] = "GPU-other"
    with pytest.raises(ValueError, match="different hardware"):
        followup.require_gate_environment(args, altered, "run")


def test_outputs_cannot_enter_original_directories(tmp_path):
    args = SimpleNamespace(baseline_manifest=followup.BASELINE, data=followup.DATA, run=followup.RUN,
                           work=tmp_path / "work", output=followup.BASELINE.parent / "new")
    with pytest.raises(ValueError, match="protected original"):
        followup.validate_paths(args)
