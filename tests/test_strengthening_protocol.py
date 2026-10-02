"""Oracle-free operator and live-cache isolation tests; no model downloads/GPU."""
from collections import defaultdict
from dataclasses import replace
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.strengthening import backend
from experiments.strengthening.protocol import (
    BM25, Config, allowed_source, build_configurations, digest, mmr_order, pack,
    reciprocal_rank_fusion, segment, token_windows, url_cap, validate_inputs,
)


def document(chunk_id, text, url="https://allowed/a", collection="collection-a", index=0):
    words, offsets, position = text.split(), [], 0
    for word in words:
        start = text.index(word, position)
        offsets.append((start, start + len(word)))
        position = start + len(word)
    return {"chunk_id": chunk_id, "collection_id": collection, "url": url, "text": text,
            "token_ids": list(range(1000 + index * 100, 1000 + index * 100 + len(words))),
            "offsets": offsets, "text_hash": digest(text), "row_index": index, "raw_rank": index + 1,
            "retrieval_score": 1 / (index + 1), "dense_score": 1 / (index + 1)}


def test_matrix_has_primary_28_and_replication_contrasts():
    configs = build_configurations()
    assert len(configs) == len({c.config_id for c in configs}) == 124
    primary = [c for c in configs if c.retriever == "dense" and c.pool == 64 and c.reranker == "m3"
               and not c.refill and c.packing == "prefix" and c.score_view == "prefix512"
               and c.policy_stage == "none" and c.mmr_lambda is None and c.dense_view == "prefix512"]
    assert len(primary) == 28
    for retriever, ranker in (("dense", "minilm"), ("bm25", "m3"), ("fusion", "m3")):
        for budget in (512, 2048):
            for stage in ("pre", "post"):
                assert Config(retriever=retriever, reranker=ranker, cap=2, cap_stage=stage, budget=budget) in configs
    assert all(Config.from_record(c.record()) == c for c in configs)


@pytest.mark.parametrize("changes", [{"cap": 2}, {"refill": True}, {"cap": 0, "cap_stage": "pre"},
                                     {"budget": 0}, {"score_view": "oracle"}, {"mmr_lambda": 1.5}])
def test_invalid_configuration_rejected(changes):
    with pytest.raises(ValueError):
        Config(**changes)


def test_cap_stable_noop_and_source_prefix():
    items = [document("a", "one"), document("b", "two"), document("c", "three", "https://allowed/b")]
    assert url_cap(items, 2) == items
    assert [x["chunk_id"] for x in url_cap(items, 1)] == ["a", "c"]
    assert allowed_source("https://allowed/a", ["https://allowed/"])
    assert not allowed_source("https://allowed.evil/a", ["https://allowed/"])
    assert allowed_source("https://anything/", [])


def test_prefix_accounts_separators_and_exact_original_text():
    a, b = document("a", "one  two three"), document("b", "four five", index=1)
    final = pack([a, b], 5, 102)
    assert final["used_tokens"] == 5 and final["separator_tokens"] == 1
    assert final["chunks"][0]["text"] == "one  two three"
    assert final["chunks"][1]["text"] == "four"
    assert final["chunks"][1]["partial"]
    for chunk in final["chunks"]:
        original = {"a": a, "b": b}[chunk["chunk_id"]]
        assert chunk["text"] == original["text"][chunk["char_start"]:chunk["char_end"]]
        assert chunk["token_ids"] == original["token_ids"][chunk["source_token_start"]:chunk["source_token_end"]]


def test_whole_skips_long_blocks_while_prefix_stops():
    a, b = document("a", "one two three four five"), document("b", "short text", index=1)
    assert pack([a, b], 3, 102, "whole")["chunks"][0]["chunk_id"] == "b"
    assert pack([a, b], 3, 102, "prefix")["chunks"][0]["chunk_id"] == "a"
    assert pack([a], 3, 102, "whole")["used_tokens"] == 0


def test_window_selects_late_query_content_without_truth_and_no_overlap():
    row = document("a", "filler filler filler filler cobalt passage target value")
    final = pack([row], 3, 102, "window", query="cobalt target", window_width=4)
    assert final["chunks"][0]["source_token_start"] == 4
    assert final["chunks"][0]["text"] == "cobalt passage target"
    full = pack([row], 20, 102, "window", query="target", window_width=3)
    occupied = []
    for chunk in full["chunks"]:
        occupied.extend(range(chunk["source_token_start"], chunk["source_token_end"]))
    assert len(occupied) == len(set(occupied)) == 8
    assert list(token_windows(9, 4, 1)) == [(0, 4), (3, 7), (6, 9)]


def test_mmr_preserves_membership_and_diversifies():
    items = ["first", "near_duplicate", "different"]
    similarities = [[1, .99, 0], [.99, 1, 0], [0, 0, 1]]
    result = mmr_order(items, similarities, [1, .98, .7], .5)
    assert result == ["first", "different", "near_duplicate"]
    assert set(result) == set(items)


def test_lexical_retrieval_and_rank_fusion():
    scores = BM25(["cobalt cobalt", "unrelated words", "cobalt with more filler filler"]).scores("cobalt")
    assert scores[0] > scores[2] > scores[1] == 0
    scores = reciprocal_rank_fusion([["a", "b"], ["b", "a"]])
    assert scores["a"] == scores["b"]


def test_inputs_reject_metadata_truth_and_cross_tenant_reference():
    corpus = [{"chunk_id": "a", "collection_id": "one", "url": "https://x/", "text": "text"}]
    questions = [{"qid": "q", "collection_id": "one", "question": "question?", "allowed_url_prefixes": []}]
    validate_inputs(corpus, questions)
    for field in ("oracle", "required_fact_ids", "group_id", "split"):
        with pytest.raises(ValueError, match="public"):
            validate_inputs(corpus, [{**questions[0], field: "secret"}])
    with pytest.raises(ValueError, match="missing collection"):
        validate_inputs(corpus, [{**questions[0], "collection_id": "foreign"}])


@pytest.fixture
def fake_runtime(tmp_path):
    runtime = object.__new__(backend.Runtime)
    runtime.device, runtime.torch, runtime.prepared = "cpu", None, True
    runtime.identity_hash, runtime.cache = "test-identity", tmp_path / "cache"
    runtime.model_specs = backend.DEFAULT_MODELS
    runtime._query_cache, runtime._score_cache = {}, {}
    runtime._models = {"m3": object(), "minilm": object()}
    runtime._model_load_count = 0
    runtime.tokenizer = SimpleNamespace(sep_token_id=102)
    runtime.corpus = [document("a", "duplicate text", "https://denied/shared", index=0),
                      document("b", "duplicate text", "https://denied/shared", index=1),
                      document("c", "allowed useful evidence", "https://allowed/c", index=2),
                      document("d", "other usable evidence", "https://allowed/d", index=3)]
    runtime.corpus.extend([{**row, "chunk_id": "paired-" + row["chunk_id"], "collection_id": "collection-b",
                            "row_index": i + 4} for i, row in enumerate(runtime.corpus[:])])
    runtime.by_id = {row["chunk_id"]: row for row in runtime.corpus}
    runtime.collections = defaultdict(list)
    for row in runtime.corpus:
        runtime.collections[row["collection_id"]].append(row)
    runtime.embeddings = np.array([[1, 0], [.9, .1], [.7, .3], [.5, .5]] * 2, dtype=np.float32)
    runtime.view_embeddings = {"prefix512": runtime.embeddings, "prefix128": runtime.embeddings}
    runtime.dense_visibility = {row["text_hash"]: {view: {"char_start": 0, "char_end": len(row["text"])}
                                                  for view in ("prefix128", "prefix512")} for row in runtime.corpus}
    runtime.bm25 = {key: BM25([row["text"] for row in rows]) for key, rows in runtime.collections.items()}
    runtime.questions = [{"qid": "q-a", "collection_id": "collection-a", "question": "useful evidence?",
                          "allowed_url_prefixes": ["https://allowed/"]},
                         {"qid": "q-b", "collection_id": "collection-b", "question": "useful evidence?",
                          "allowed_url_prefixes": ["https://allowed/"]}]
    runtime.questions_by_id = {q["qid"]: q for q in runtime.questions}
    runtime.calls = {"query": 0, "predict": 0, "pairs": 0}

    def encode(texts, **kwargs):
        runtime.calls["query"] += 1
        return np.array([[1, 0]] * len(texts), dtype=np.float32)

    runtime.embedder = SimpleNamespace(encode=encode)
    runtime._load_dense = lambda: None

    def predict(question, texts, reranker, view):
        runtime.calls["predict"] += 1
        runtime.calls["pairs"] += len(texts)
        scores = {key: {"score": float("useful" in text), "pairs": 1,
                        "view_spans": [{"char_start": 0, "char_end": len(text), "pair_tokens": 8, "max_length": 512}]}
                  for key, text in texts.items()}
        return scores, {"measurement_id": digest(list(texts)), "pairs": len(texts), "ms": 10.0}

    runtime._predict = predict
    return runtime


def test_shared_scores_reuse_only_identical_question_text_across_tenants(fake_runtime):
    runtime = fake_runtime
    a, info_a = runtime.score("q-a", ["a", "b", "c", "d"])
    b, info_b = runtime.score("q-b", ["paired-a", "paired-b", "paired-c", "paired-d"])
    assert runtime.calls["predict"] == 1 and runtime.calls["pairs"] == 3
    assert info_a["pairs"] == info_b["pairs"] == 4
    assert info_b["cache_hit"] and info_b["new_pairs"] == 0
    assert {"paired-" + key: value for key, value in a.items()} == b
    with pytest.raises(ValueError, match="Cross-collection"):
        runtime.score("q-a", ["paired-a"])


def test_live_requests_ignore_caches_recompute_queries_and_every_pair(fake_runtime):
    runtime = fake_runtime
    config = Config(pool=4)
    runtime.execute("q-a", config, use_cache=True)
    before = dict(runtime.calls)
    files_before = {p: p.read_bytes() for p in runtime.cache.rglob("*") if p.is_file()}
    for _ in range(2):
        record = runtime.execute("q-a", config, use_cache=False)
        assert record["timing_provenance"]["scope"] == "independent_live_request"
        assert not record["timing_provenance"]["query_cache_hit"]
        assert not record["timing_provenance"]["rerank_cache_hit"]
        assert record["rerank_pairs"] == record["rerank_new_pairs"] == 4
    assert runtime.calls["query"] - before["query"] == 2
    assert runtime.calls["predict"] - before["predict"] == 2
    assert runtime.calls["pairs"] - before["pairs"] == 8
    assert files_before == {p: p.read_bytes() for p in runtime.cache.rglob("*") if p.is_file()}


def test_policy_placement_applies_explicit_public_allowed_sources(fake_runtime):
    runtime = fake_runtime
    before = runtime.execute("q-a", Config(pool=2, policy_stage="pre_retrieve"))
    after = runtime.execute("q-a", Config(pool=2, policy_stage="post_retrieve"))
    last = runtime.execute("q-a", Config(pool=2, policy_stage="post_rerank"))
    assert len(before["final_context"]["chunks"]) == 2
    assert after["final_context"]["chunks"] == last["final_context"]["chunks"] == []
    for chunk in before["final_context"]["chunks"]:
        assert chunk["url"].startswith("https://allowed/")


def test_live_requires_resident_models_and_diagnostics_report_loading(fake_runtime):
    runtime = fake_runtime
    del runtime._models["m3"]
    with pytest.raises(RuntimeError, match="preload_models"):
        runtime.execute("q-a", Config(pool=4), use_cache=False)
    predict = runtime._predict

    def load_then_predict(*args):
        runtime._model_load_count += 1
        runtime._models["m3"] = object()
        return predict(*args)

    runtime._predict = load_then_predict
    record = runtime.execute("q-a", Config(pool=4), use_cache=True)
    provenance = record["timing_provenance"]
    assert provenance["models_loaded_in_request"] == 1
    assert not provenance["required_models_resident_at_request_start"]
    assert not provenance["offline_index_and_model_loading_excluded"]


def test_refill_additions_and_pure_sort_membership_are_explicit(fake_runtime):
    runtime = fake_runtime
    nofill = runtime.execute("q-a", Config(pool=2, cap=1, cap_stage="pre"))
    pre = runtime.execute("q-a", Config(pool=2, cap=1, cap_stage="pre", refill=True))
    post = runtime.execute("q-a", Config(pool=2, cap=1, cap_stage="post", refill=True))
    assert nofill["rerank_pairs"] == 1 and pre["rerank_pairs"] == 2 and post["rerank_pairs"] == 4
    assert len(pre["stages"]["pre_cap"]) == len(post["stages"]["post_cap"]) == 2
    for record in (nofill, pre, post):
        assert {row["chunk_id"] for row in record["stages"]["pre_cap"]} == {row["chunk_id"] for row in record["stages"]["rerank"]}


def test_noop_cap_keeps_identical_final_order_and_spans(fake_runtime):
    runtime = fake_runtime
    runtime.prime_scores("q-a", [Config()])
    pre = runtime.execute("q-a", Config(pool=4, cap=2, cap_stage="pre"))
    post = runtime.execute("q-a", Config(pool=4, cap=2, cap_stage="post"))
    assert pre["final_context"] == post["final_context"]


def test_dense_document_views_change_retrieval_but_share_same_query_vector(fake_runtime):
    runtime = fake_runtime
    runtime.view_embeddings["prefix128"] = runtime.embeddings[::-1].copy()
    prefix, _ = runtime.retrieve("q-a", dense_view="prefix512")
    short, _ = runtime.retrieve("q-a", dense_view="prefix128")
    assert prefix[0]["chunk_id"] != short[0]["chunk_id"]
    assert runtime.calls["query"] == 1
    runtime.window_embeddings = np.array([[0, 1], [1, 0]], dtype=np.float32)
    runtime.dense_windows = {row["text_hash"]: [
        {"index": 0, "char_start": 0, "char_end": 3},
        {"index": 1, "char_start": 4, "char_end": 8}] for row in runtime.corpus}
    windows, _ = runtime.retrieve("q-a", dense_view="window512")
    assert all(row["dense_visible_char_start"] == 4 and row["dense_visible_char_end"] == 8 for row in windows)
    assert runtime.calls["query"] == 1


def test_run_identity_binds_input_and_code_before_resume(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus.jsonl"
    questions = tmp_path / "questions.jsonl"
    row = {"chunk_id": "a", "collection_id": "c", "url": "https://x/", "text": "first"}
    corpus.write_text(json.dumps(row) + "\n", encoding="utf-8")
    questions.write_text(json.dumps({"qid": "q", "collection_id": "c", "question": "Which?", "allowed_url_prefixes": []}) + "\n", encoding="utf-8")
    monkeypatch.setattr(backend, "local_model_path", lambda _: tmp_path)
    monkeypatch.setattr(backend, "model_identity", lambda spec: {"model": spec["model"], "sha": spec["sha"], "files": {}})
    monkeypatch.setattr(backend.importlib.metadata, "version", lambda _: "test")
    output = tmp_path / "output"
    first = backend.Runtime(corpus, questions, output, device="cpu")
    second = backend.Runtime(corpus, questions, output, device="cpu")
    assert first.identity_hash == second.identity_hash
    corpus.write_text(json.dumps({**row, "text": "changed"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Run identity changed"):
        backend.Runtime(corpus, questions, output, device="cpu")
