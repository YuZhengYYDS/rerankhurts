"""Actual local inference for the prospectively frozen strengthening workload.

Only corpus.jsonl and questions.jsonl enter Runtime. Truth, tasks, world metadata
and oracle files are not opened. Offline diagnostic inference can share exact
question/text scores. execute(..., use_cache=False) performs a fresh request,
including query encoding and all required model scoring, without cache writes.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import time

import numpy as np

from .protocol import (BM25, SCHEMA_VERSION, Config, allowed_source, build_configurations,
                       digest, file_hash, load_json, mmr_order, pack, read_jsonl,
                       reciprocal_rank_fusion, save_json, stage, token_windows,
                       url_cap, validate_inputs)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "experiments/strengthening/data/strengthening_v1"
DEFAULT_OUTPUT = ROOT / "experiments/runs/strengthening_v1"
DEFAULT_MODELS = {
    "dense": {"model": "BAAI/bge-small-en-v1.5", "sha": "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"},
    "m3": {"model": "BAAI/bge-reranker-v2-m3", "sha": "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e"},
    "minilm": {"model": "cross-encoder/ms-marco-MiniLM-L6-v2", "sha": "233902d25c440f23af6f7d6e94d2946bac0bee0a"},
    "tokenizer": {"model": "google-bert/bert-base-uncased", "sha": "86b5e0934494bd15c9632b12f734a8a67f723594"},
}


def local_model_path(spec):
    path = Path(spec.get("path") or ROOT / ".cache/models" / spec["model"].replace("/", "--") / spec["sha"])
    if not path.is_dir() or not (path / "config.json").is_file():
        raise FileNotFoundError(f"Pinned local model snapshot missing: {path}; download it separately before running")
    return path.resolve()


def model_identity(spec):
    path = local_model_path(spec)
    files = {p.relative_to(path).as_posix(): file_hash(p) for p in sorted(path.rglob("*"))
             if p.is_file() and ".cache" not in p.relative_to(path).parts}
    return {"model": spec["model"], "sha": spec["sha"], "files": files}


class Runtime:
    def __init__(self, corpus_path, questions_path, output, device="cuda", seed=20261002,
                 model_specs=None, embed_batch_size=32, rerank_batch_size=8):
        self.corpus_path, self.questions_path = Path(corpus_path), Path(questions_path)
        self.corpus, self.questions = read_jsonl(corpus_path), read_jsonl(questions_path)
        validate_inputs(self.corpus, self.questions)
        self.questions_by_id = {q["qid"]: q for q in self.questions}
        self.collections = defaultdict(list)
        self.by_id = {}
        for index, row in enumerate(self.corpus):
            row["row_index"] = index
            row["text_hash"] = digest(row["text"])
            self.by_id[row["chunk_id"]] = row
            self.collections[row["collection_id"]].append(row)
        self.output, self.cache = Path(output), Path(output) / "cache"
        self.device, self.seed = device, seed
        self.embed_batch_size, self.rerank_batch_size = embed_batch_size, rerank_batch_size
        if device not in {"cpu", "cuda"} or min(embed_batch_size, rerank_batch_size) < 1:
            raise ValueError("Invalid device or batch size")
        self.model_specs = {key: dict(value) for key, value in (model_specs or DEFAULT_MODELS).items()}
        if set(self.model_specs) != set(DEFAULT_MODELS):
            raise ValueError("Model specs must declare dense, m3, minilm and tokenizer")
        self.paths = {key: local_model_path(spec) for key, spec in self.model_specs.items()}
        study_plan = Path(__file__).with_name("study_plan.json")
        if not study_plan.is_file():
            raise FileNotFoundError("A frozen study_plan.json must precede model inference")
        identity = {
            "schema_version": SCHEMA_VERSION, "corpus_sha256": file_hash(corpus_path),
            "questions_sha256": file_hash(questions_path), "study_plan_sha256": file_hash(study_plan),
            "models": {key: model_identity(spec) for key, spec in self.model_specs.items()},
            "code_sha256": {p.name: file_hash(p) for p in (Path(__file__), Path(__file__).with_name("protocol.py"))},
            "settings": {"device": device, "seed": seed, "embed_batch_size": embed_batch_size,
                         "rerank_batch_size": rerank_batch_size, "dense_query_max_length": 512,
                         "dense_document_views": ["prefix128", "prefix512", "window512"],
                         "window_pack_tokens": 192, "window_score_overlap": 64,
                         "rrf_constant": 60, "bm25_k1": 1.2, "bm25_b": .75},
            "packages": {name: importlib.metadata.version(name)
                         for name in ("numpy", "torch", "transformers", "sentence-transformers")},
            "configurations": [config.record() for config in build_configurations()],
        }
        specification = self.corpus_path.parent / "specification.json"
        if specification.is_file():
            identity["specification_sha256"] = file_hash(specification)
        self.identity_hash = digest(identity)
        self.manifest = {
            "identity_hash": self.identity_hash, "identity": identity,
            "questions": len(self.questions), "corpus_chunks": len(self.corpus),
            "collections": len(self.collections), "configurations": identity["configurations"],
            "expected_records": len(self.questions) * len(identity["configurations"]),
            "environment": {"platform": platform.platform(), "python": platform.python_version()},
            "input_contract": "Only public question text/document text enter neural models. collection_id isolates retrieval. Explicit URL/prefix fields implement source policy. No oracle or world metadata is read.",
            "budget_definition": "Fixed BERT add_special_tokens=False evidence IDs; one SEP between delivered segments. Original-text char intervals and token intervals retained. Question/prompt/answer tokens excluded.",
            "diagnostic_timing": "Shared exact question/text/view inference measurements; configuration requests may reuse them. These are not independent online latency observations.",
            "refill_definition": "Fixed reservoir is the full tenant collection (80 in this workload). Pre-refill scans retrieval order until pool cap-eligible chunks or exhaustion, then scores. Post-refill scores the reservoir, sorts, caps, then takes pool. Added scoring pairs are reported; no oracle stopping.",
            "scoring_views": "Dense query stays prefix512; dense documents use prefix128/prefix512 or <=512 windows with 64-token overlap, max query cosine across windows. MMR uses fixed prefix512 cosine. CE prefix128/prefix512 use only_second truncation with full question; window512 slides over doc tokens with 64-token overlap and max-aggregates logits. Every CE pair remains <=512 tokens.",
        }
        path = self.output / "manifest.json"
        if path.exists():
            previous = load_json(path)
            if previous["identity_hash"] != self.identity_hash:
                raise ValueError("Run identity changed (code/data/models/settings/study); use a new output directory")
            self.manifest = previous
        else:
            save_json(path, self.manifest)
        self.cache.mkdir(parents=True, exist_ok=True)
        self._query_cache, self._score_cache, self._models, self._pair_tokenizers = {}, {}, {}, {}
        self._model_load_count = 0
        self.embedder = self.tokenizer = self.torch = None
        self.prepared = False

    def _initialize_torch(self):
        if self.torch is not None:
            return
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        import torch
        if self.device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is unavailable")
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.benchmark = False
        torch.backends.cuda.matmul.allow_tf32 = False
        self.torch = torch

    def sync(self):
        if self.torch is not None and self.device == "cuda":
            self.torch.cuda.synchronize()

    def _timed(self, function):
        self.sync()
        start = time.perf_counter()
        result = function()
        self.sync()
        return result, (time.perf_counter() - start) * 1000

    def _load_dense(self):
        self._initialize_torch()
        if self.embedder is None:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer(str(self.paths["dense"]), device=self.device, local_files_only=True)
            self.embedder.max_seq_length = 512
            self._model_load_count += 1

    def preload_models(self, names=("m3", "minilm")):
        self._load_dense()
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        for name in names:
            if name not in {"m3", "minilm"}:
                raise ValueError(f"Unknown reranker: {name}")
            if name in self._models:
                continue
            tokenizer = AutoTokenizer.from_pretrained(str(self.paths[name]), local_files_only=True, use_fast=True)
            if not tokenizer.is_fast:
                raise ValueError("A fast tokenizer is required for scoring visibility offsets")
            dtype = self.torch.float16 if self.device == "cuda" else self.torch.float32
            model = AutoModelForSequenceClassification.from_pretrained(
                str(self.paths[name]), local_files_only=True, torch_dtype=dtype,
                attn_implementation="eager").to(self.device).eval()
            self._models[name], self._pair_tokenizers[name] = model, tokenizer
            self._model_load_count += 1

    def prepare_indexes(self):
        if self.prepared:
            return
        self._initialize_torch()
        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.paths["tokenizer"]), local_files_only=True, use_fast=True)
        if not self.tokenizer.is_fast or self.tokenizer.sep_token_id is None:
            raise ValueError("Budget tokenizer needs fast offsets and SEP")
        unique = {}
        for row in self.corpus:
            unique.setdefault(row["text_hash"], row["text"])
        text_hashes, texts = list(unique), list(unique.values())
        unique_index = {key: index for index, key in enumerate(text_hashes)}
        token_path, embedding_path = self.cache / "tokens.json.gz", self.cache / "document_embeddings.npy"
        index_path = self.cache / "index.json"
        if index_path.exists():
            index = load_json(index_path)
            if index["identity_hash"] != self.identity_hash or index["text_hashes"] != text_hashes:
                raise ValueError("Foreign offline index")
            if file_hash(token_path) != index["tokens_sha256"] or file_hash(embedding_path) != index["embeddings_sha256"]:
                raise ValueError("Offline index checksum mismatch")
            tokens = load_json(token_path)
            unique_embeddings = np.load(embedding_path, allow_pickle=False)
        else:
            tokens = []
            for start in range(0, len(texts), 128):
                encoded = self.tokenizer(texts[start:start + 128], add_special_tokens=False, truncation=False,
                                         return_offsets_mapping=True, verbose=False)
                tokens.extend({"token_ids": ids, "offsets": offsets}
                              for ids, offsets in zip(encoded["input_ids"], encoded["offset_mapping"]))
            save_json(token_path, tokens)
            self._load_dense()
            unique_embeddings, encode_ms = self._timed(lambda: self.embedder.encode(
                texts, batch_size=self.embed_batch_size, normalize_embeddings=True,
                convert_to_numpy=True, show_progress_bar=True))
            temporary = embedding_path.with_name(embedding_path.name + ".tmp")
            with temporary.open("wb") as stream:
                np.save(stream, unique_embeddings, allow_pickle=False)
            temporary.replace(embedding_path)
            save_json(index_path, {"identity_hash": self.identity_hash, "text_hashes": text_hashes,
                                  "tokens_sha256": file_hash(token_path), "embeddings_sha256": file_hash(embedding_path),
                                  "unique_texts": len(texts), "corpus_rows": len(self.corpus),
                                  "encode_ms": encode_ms})
        if unique_embeddings.ndim != 2 or len(unique_embeddings) != len(texts) or len(tokens) != len(texts):
            raise ValueError("Invalid offline index shape")
        if not np.isfinite(unique_embeddings).all():
            raise ValueError("Non-finite document embeddings")
        indices = [unique_index[row["text_hash"]] for row in self.corpus]
        self.embeddings = unique_embeddings[indices]
        for row, index in zip(self.corpus, indices):
            row.update(tokens[index])
        self.bm25 = {key: BM25([row["text"] for row in rows]) for key, rows in self.collections.items()}
        self._prepare_dense_views(texts, text_hashes, indices)
        self.prepared = True

    def _prepare_dense_views(self, texts, text_hashes, row_indices):
        """Store separate document views, sharing exact text across paired tenants."""
        metadata_path = self.cache / "dense_views.json.gz"
        short_path, window_path = self.cache / "dense_prefix128.npy", self.cache / "dense_window512.npy"
        if metadata_path.exists():
            metadata = load_json(metadata_path)
            if metadata["identity_hash"] != self.identity_hash or metadata["text_hashes"] != text_hashes:
                raise ValueError("Foreign dense view index")
            for path in (short_path, window_path):
                if file_hash(path) != metadata["files"][path.name]:
                    raise ValueError("Dense view index checksum mismatch")
            short_embeddings = np.load(short_path, allow_pickle=False)
            window_embeddings = np.load(window_path, allow_pickle=False)
        else:
            self._load_dense()
            dense_tokenizer = self.embedder.tokenizer
            if not dense_tokenizer.is_fast:
                raise ValueError("Dense visibility diagnostics require a fast tokenizer")
            special = dense_tokenizer.num_special_tokens_to_add(pair=False)
            spans, windows, window_texts = {}, {}, []
            for text_hash, text in zip(text_hashes, texts):
                offsets = dense_tokenizer(text, add_special_tokens=False, return_offsets_mapping=True,
                                          truncation=False, verbose=False)["offset_mapping"]
                if not offsets:
                    raise ValueError("Empty dense document tokenization")
                spans[text_hash] = {
                    view: {"char_start": offsets[0][0], "char_end": offsets[min(limit - special, len(offsets)) - 1][1]}
                    for view, limit in (("prefix128", 128), ("prefix512", 512))}
                windows[text_hash] = []
                for begin, end in token_windows(len(offsets), 512 - special, 64):
                    start_char, end_char = offsets[begin][0], offsets[end - 1][1]
                    rendered = text[start_char:end_char]
                    # Starting inside a WordPiece can change re-tokenization.
                    # Log what the newly encoded window actually exposes.
                    actual = dense_tokenizer(rendered, add_special_tokens=False, return_offsets_mapping=True,
                                             truncation=False, verbose=False)["offset_mapping"]
                    visible_end = actual[min(len(actual), 512 - special) - 1][1]
                    windows[text_hash].append({"index": len(window_texts), "char_start": start_char + actual[0][0],
                                               "char_end": start_char + visible_end})
                    window_texts.append(rendered)
            self.embedder.max_seq_length = 128
            short_embeddings, short_ms = self._timed(lambda: self.embedder.encode(
                texts, batch_size=self.embed_batch_size, normalize_embeddings=True,
                convert_to_numpy=True, show_progress_bar=True))
            self.embedder.max_seq_length = 512
            window_embeddings, window_ms = self._timed(lambda: self.embedder.encode(
                window_texts, batch_size=self.embed_batch_size, normalize_embeddings=True,
                convert_to_numpy=True, show_progress_bar=True))
            for path, vectors in ((short_path, short_embeddings), (window_path, window_embeddings)):
                temporary = path.with_name(path.name + ".tmp")
                with temporary.open("wb") as stream:
                    np.save(stream, vectors, allow_pickle=False)
                temporary.replace(path)
            metadata = {"identity_hash": self.identity_hash, "text_hashes": text_hashes,
                        "prefix_spans": spans, "windows": windows,
                        "files": {path.name: file_hash(path) for path in (short_path, window_path)},
                        "prefix128_encode_ms": short_ms, "window512_encode_ms": window_ms,
                        "window_pairs": len(window_texts)}
            save_json(metadata_path, metadata)
        if len(short_embeddings) != len(texts) or not np.isfinite(short_embeddings).all() or not np.isfinite(window_embeddings).all():
            raise ValueError("Invalid alternate document embeddings")
        self.view_embeddings = {"prefix512": self.embeddings, "prefix128": short_embeddings[row_indices]}
        self.window_embeddings = window_embeddings
        self.dense_visibility, self.dense_windows = metadata["prefix_spans"], metadata["windows"]

    def _question(self, question):
        result = self.questions_by_id[question] if isinstance(question, str) else question
        if result.get("qid") not in self.questions_by_id or result != self.questions_by_id[result["qid"]]:
            raise ValueError("Request differs from the frozen public question")
        return result

    def _query_embedding(self, question, use_cache):
        key = digest(question["question"])
        if use_cache and key in self._query_cache:
            return self._query_cache[key], True
        self._load_dense()
        self.embedder.max_seq_length = 512
        vector = self.embedder.encode([question["question"]], normalize_embeddings=True,
                                      convert_to_numpy=True, show_progress_bar=False)[0]
        if use_cache:
            self._query_cache[key] = vector
        return vector, False

    def retrieve(self, question, method="dense", depth=None, use_cache=True, allowed_prefixes=None, dense_view="prefix512"):
        if not self.prepared:
            raise RuntimeError("Call prepare_indexes() before retrieval")
        question = self._question(question)
        rows = self.collections[question["collection_id"]]
        dense_scores, sparse_scores, query_cache_hit = None, None, False
        if method in {"dense", "fusion"}:
            vector, query_cache_hit = self._query_embedding(question, use_cache)
            visible = {}
            if dense_view == "window512":
                dense_scores = []
                for i, row in enumerate(rows):
                    windows = self.dense_windows[row["text_hash"]]
                    similarities = self.window_embeddings[[window["index"] for window in windows]] @ vector
                    best = int(np.argmax(similarities))
                    dense_scores.append(float(similarities[best]))
                    visible[i] = windows[best]
            elif dense_view in self.view_embeddings:
                dense_scores = self.view_embeddings[dense_view][[row["row_index"] for row in rows]] @ vector
                visible = {i: self.dense_visibility[row["text_hash"]][dense_view] for i, row in enumerate(rows)}
            else:
                raise ValueError(f"Unknown dense view: {dense_view}")
        if method in {"bm25", "fusion"}:
            sparse_scores = self.bm25[question["collection_id"]].scores(question["question"])
        eligible = [i for i, row in enumerate(rows) if allowed_source(row["url"], allowed_prefixes or [])]
        if method == "dense":
            scores = dense_scores
        elif method == "bm25":
            scores = sparse_scores
        elif method == "fusion":
            rankings = [sorted(eligible, key=lambda i: (-float(values[i]), i)) for values in (dense_scores, sparse_scores)]
            scores = reciprocal_rank_fusion(rankings)
        else:
            raise ValueError(f"Unknown retriever: {method}")
        order = sorted(eligible, key=lambda i: (-float(scores[i]), i))
        if depth is not None:
            order = order[:depth]
        return ([{**rows[i], "retrieval_score": float(scores[i]),
                  "dense_score": float(dense_scores[i]) if dense_scores is not None else None,
                  "dense_view": dense_view if dense_scores is not None else None,
                  "dense_visible_char_start": visible[i]["char_start"] if dense_scores is not None else None,
                  "dense_visible_char_end": visible[i]["char_end"] if dense_scores is not None else None,
                  "raw_rank": rank} for rank, i in enumerate(order, 1)],
                {"query_cache_hit": query_cache_hit, "eligible_documents": len(eligible)})

    def _score_document_views(self, question, text, tokenizer, view):
        limit = 128 if view == "prefix128" else 512
        query_length = len(tokenizer(question, add_special_tokens=False)["input_ids"])
        available = limit - query_length - tokenizer.num_special_tokens_to_add(pair=True)
        if available < 1:
            raise ValueError("Question alone exceeds the configured scoring field of view")
        if view != "window512":
            return [(text, 0, len(text), limit)]
        encoded = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True, truncation=False, verbose=False)
        offsets = encoded["offset_mapping"]
        ranges = token_windows(len(offsets), available, min(64, max(available - 1, 0)))
        return [(text[offsets[start][0]:offsets[end - 1][1]], offsets[start][0], offsets[end - 1][1], limit)
                for start, end in ranges]

    def _predict(self, question, texts_by_hash, reranker, view):
        self.preload_models((reranker,))
        tokenizer, model = self._pair_tokenizers[reranker], self._models[reranker]
        pairs = []
        for text_hash, text in texts_by_hash.items():
            for rendered, start, end, limit in self._score_document_views(question, text, tokenizer, view):
                pairs.append((text_hash, rendered, start, end, limit))
        values = {key: {"score": -float("inf"), "view_spans": [], "pairs": 0} for key in texts_by_hash}

        def compute():
            with self.torch.inference_mode():
                for begin in range(0, len(pairs), self.rerank_batch_size):
                    batch = pairs[begin:begin + self.rerank_batch_size]
                    encoded = tokenizer([question] * len(batch), [row[1] for row in batch],
                                        padding=True, truncation="only_second", max_length=batch[0][4],
                                        return_offsets_mapping=True, return_tensors="pt")
                    offsets = encoded.pop("offset_mapping").tolist()
                    visible = []
                    for i, row in enumerate(batch):
                        document_offsets = [offset for seq, offset in zip(encoded.sequence_ids(i), offsets[i])
                                            if seq == 1 and offset[1] > offset[0]]
                        visible.append({"char_start": row[2] + document_offsets[0][0],
                                        "char_end": row[2] + document_offsets[-1][1],
                                        "pair_tokens": int(encoded["attention_mask"][i].sum()),
                                        "max_length": row[4]})
                    logits = model(**encoded.to(self.device)).logits
                    if logits.ndim != 2 or logits.shape[1] != 1:
                        raise ValueError("A scalar cross-encoder logit is required")
                    scores = logits[:, 0].float().cpu().tolist()
                    if not np.isfinite(scores).all():
                        raise ValueError("Non-finite reranker logits")
                    for row, score, span in zip(batch, scores, visible):
                        entry = values[row[0]]
                        entry["score"] = max(entry["score"], score)
                        entry["view_spans"].append(span)
                        entry["pairs"] += 1
            return values
        values, measured_ms = self._timed(compute)
        if any(not np.isfinite(entry["score"]) for entry in values.values()):
            raise ValueError("A document had no scoreable tokens")
        measurement = {"measurement_id": digest({"question": question, "text_hashes": list(texts_by_hash),
                                                  "reranker": reranker, "view": view}),
                       "pairs": len(pairs), "ms": measured_ms,
                       "peak_cuda_allocated_bytes": self.torch.cuda.max_memory_allocated() if self.device == "cuda" else None}
        return values, measurement

    def score(self, question, candidate_ids, reranker="m3", view="prefix512", use_cache=True):
        question = self._question(question)
        items = [self.by_id[chunk_id] for chunk_id in candidate_ids]
        if any(item["collection_id"] != question["collection_id"] for item in items):
            raise ValueError("Cross-collection candidates are forbidden")
        if not items:
            return {}, {"pairs": 0, "new_pairs": 0, "cache_hit": False, "measurements": [], "visibility": {}}
        key = digest({"question": question["question"], "reranker": reranker, "view": view,
                      "model": self.model_specs[reranker], "identity_hash": self.identity_hash})
        path = self.cache / "scores" / f"{key}.json.gz"
        if use_cache:
            if key not in self._score_cache:
                stored = load_json(path) if path.exists() else {"identity_hash": self.identity_hash, "scores": {}, "measurements": []}
                if stored["identity_hash"] != self.identity_hash:
                    raise ValueError("Foreign scoring cache")
                self._score_cache[key] = stored
            stored = self._score_cache[key]
        else:
            stored = {"identity_hash": self.identity_hash, "scores": {}, "measurements": []}
        # Diagnostic caches share identical texts; live requests score every
        # candidate row, including duplicate texts, with no reused pair results.
        entry_key = "text_hash" if use_cache else "chunk_id"
        requested = {item[entry_key]: item["text"] for item in items}
        missing = {key: value for key, value in requested.items() if key not in stored["scores"]}
        cache_hit, new_pairs = not missing, 0
        if missing:
            values, measurement = self._predict(question["question"], missing, reranker, view)
            for value in values.values():
                value["measurement_id"] = measurement["measurement_id"]
            stored["scores"].update(values)
            stored["measurements"].append(measurement)
            new_pairs = measurement["pairs"]
            if use_cache:
                save_json(path, stored)
        selected = {item["chunk_id"]: stored["scores"][item[entry_key]] for item in items}
        measurement_ids = {entry["measurement_id"] for entry in selected.values()}
        return ({key: entry["score"] for key, entry in selected.items()},
                {"pairs": sum(entry["pairs"] for entry in selected.values()), "new_pairs": new_pairs,
                 "cache_hit": cache_hit, "measurements": [m for m in stored["measurements"] if m["measurement_id"] in measurement_ids],
                 "visibility": {key: entry["view_spans"] for key, entry in selected.items()}})

    def prime_scores(self, question, configurations=None):
        """Score a frozen tenant reservoir once per model/view for diagnostics."""
        question = self._question(question)
        configs = configurations or build_configurations()
        requests = sorted({(config.reranker, config.score_view) for config in configs if config.reranker != "none"})
        ids = [row["chunk_id"] for row in self.collections[question["collection_id"]]]
        for reranker, view in requests:
            self.score(question, ids, reranker, view, use_cache=True)

    def execute(self, question, config, use_cache=True):
        if not self.prepared:
            raise RuntimeError("Call prepare_indexes() before execute")
        question = self._question(question)
        if isinstance(config, dict):
            config = Config.from_record(config)
        missing_dense = (config.retriever in {"dense", "fusion"} or config.mmr_lambda is not None) and self.embedder is None
        missing_reranker = config.reranker != "none" and config.reranker not in self._models
        if not use_cache and (missing_dense or missing_reranker):
            raise RuntimeError("Call preload_models() before independent live requests; model loading is outside the timed workload")
        load_count_before = self._model_load_count
        self.sync()
        request_start = time.perf_counter()
        timings = {}
        prefixes = question["allowed_url_prefixes"]
        (reservoir, retrieval_info), timings["retrieval"] = self._timed(lambda: self.retrieve(
            question, config.retriever, use_cache=use_cache,
            allowed_prefixes=prefixes if config.policy_stage == "pre_retrieve" else None, dense_view=config.dense_view))
        raw = reservoir[:config.pool]
        start = time.perf_counter()
        after_policy = [row for row in raw if allowed_source(row["url"], prefixes)] if config.policy_stage == "post_retrieve" else raw
        refill_reservoir = ([row for row in reservoir if allowed_source(row["url"], prefixes)]
                            if config.policy_stage == "post_retrieve" else reservoir)
        if config.refill:
            inputs = url_cap(refill_reservoir, config.cap)[:config.pool] if config.cap_stage == "pre" else refill_reservoir
        else:
            inputs = url_cap(after_policy, config.cap) if config.cap_stage == "pre" else after_policy
        timings["pre_cap_filter"] = (time.perf_counter() - start) * 1000
        if config.reranker != "none":
            (scores, score_info), timings["rerank_call"] = self._timed(lambda: self.score(
                question, [row["chunk_id"] for row in inputs], config.reranker, config.score_view, use_cache))
        else:
            scores, score_info = {}, {"pairs": 0, "new_pairs": 0, "cache_hit": False, "measurements": [], "visibility": {}}
            timings["rerank_call"] = 0.0
        start = time.perf_counter()
        ordered = sorted(inputs, key=lambda row: (-scores[row["chunk_id"]], row["raw_rank"])) if scores else list(inputs)
        if config.mmr_lambda is not None and ordered:
            vectors = self.embeddings[[row["row_index"] for row in ordered]]
            if any(row["dense_score"] is None for row in ordered):
                query, _ = self._query_embedding(question, use_cache)
                relevance = vectors @ query
            else:
                relevance = [row["dense_score"] for row in ordered]
            ordered = mmr_order(ordered, vectors @ vectors.T, relevance, config.mmr_lambda)
        post_cap = url_cap(ordered, config.cap) if config.cap_stage == "post" else ordered
        if config.refill and config.cap_stage == "post":
            post_cap = post_cap[:config.pool]
        post_policy = [row for row in post_cap if allowed_source(row["url"], prefixes)] if config.policy_stage == "post_rerank" else post_cap
        timings["sort_post_cap_filter"] = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        final = pack(post_policy, config.budget, self.tokenizer.sep_token_id, config.packing, question["question"])
        timings["packing"] = (time.perf_counter() - start) * 1000
        self.sync()
        timings["request_total"] = (time.perf_counter() - request_start) * 1000
        models_loaded_in_request = self._model_load_count - load_count_before
        return {"qid": question["qid"], "collection_id": question["collection_id"],
                "configuration": config.record(), "candidate_reservoir": stage(reservoir),
                "stages": {"raw": stage(raw), "after_retrieval_policy": stage(after_policy),
                           "pre_cap": stage(inputs), "rerank": stage(ordered, scores),
                           "post_cap": stage(post_cap, scores), "post_policy": stage(post_policy, scores)},
                "final_context": final, "timing_ms": timings, "rerank_pairs": score_info["pairs"],
                "rerank_new_pairs": score_info["new_pairs"], "score_visibility": score_info["visibility"],
                "timing_provenance": {"scope": "diagnostic_shared_inference" if use_cache else "independent_live_request",
                                      "query_cache_hit": retrieval_info["query_cache_hit"],
                                      "rerank_cache_hit": score_info["cache_hit"],
                                      "shared_measurements": score_info["measurements"],
                                      "required_models_resident_at_request_start": not (missing_dense or missing_reranker),
                                      "models_loaded_in_request": models_loaded_in_request,
                                      "offline_index_and_model_loading_excluded": models_loaded_in_request == 0}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_DATA / "corpus.jsonl")
    parser.add_argument("--questions", type=Path, default=DEFAULT_DATA / "questions.jsonl")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--seed", type=int, default=20261002)
    parser.add_argument("--phase", choices=("prepare", "run"), default="run")
    parser.add_argument("--limit", type=int, default=0, help="Smoke only; partial status retains the full denominator")
    args = parser.parse_args(argv)
    runtime = Runtime(args.corpus, args.questions, args.output, args.device, args.seed)
    runtime.prepare_indexes()
    if args.phase == "prepare":
        print(json.dumps({"status": "indexes_prepared", "identity_hash": runtime.identity_hash}))
        return
    configs = build_configurations()
    questions = runtime.questions[:args.limit] if args.limit else runtime.questions
    runtime.preload_models()
    for index, question in enumerate(questions, 1):
        path = runtime.output / "traces" / f"{digest(question['qid'])[:24]}.json.gz"
        if path.exists():
            trace = load_json(path)
            if trace["identity_hash"] != runtime.identity_hash or len(trace["configurations"]) != len(configs):
                raise ValueError("Foreign or incomplete saved trace")
            print(f"[{index}/{len(questions)}] resumed {question['qid']}", flush=True)
            continue
        runtime.prime_scores(question, configs)
        records = [runtime.execute(question, config) for config in configs]
        save_json(path, {"schema_version": SCHEMA_VERSION, "identity_hash": runtime.identity_hash,
                         **question, "configurations": records})
        print(f"[{index}/{len(questions)}] completed {question['qid']} / {len(records)} configurations", flush=True)
    observed = 0
    for path in (runtime.output / "traces").glob("*.json.gz"):
        trace = load_json(path)
        if trace["identity_hash"] != runtime.identity_hash:
            raise ValueError("Foreign trace in output directory")
        observed += len(trace["configurations"])
    status = {"status": "complete" if observed == runtime.manifest["expected_records"] else "partial",
              "observed_records": observed, "expected_records": runtime.manifest["expected_records"],
              "identity_hash": runtime.identity_hash, "human_labels": False,
              "timing_scope": "Shared diagnostic inference; independent online timing is a separate experiment"}
    save_json(runtime.output / "status.json", status)
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
