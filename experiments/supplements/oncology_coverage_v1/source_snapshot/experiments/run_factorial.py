"""Run the 20 distinct E3 configurations and retain content-addressed traces.

Example: python -m experiments.run_factorial --device cuda --limit 2 --output experiments/runs/smoke
No claim of human evidence utility is computed by this program.
"""
from __future__ import annotations

import argparse
import csv
import gc
import importlib.metadata
import json
import os
import platform
import random
import subprocess
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .protocol import (PROTOCOL_VERSION, configurations, digest, file_hash, first_url_loss,
                       freeze_manifest, gold_urls, identify_corpus, load_json, pack_prefix, read_jsonl,
                       rerank, save_json, stage, url_cap, url_metrics)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--corpus", type=Path, default=Path("corpus_chunks_v2.jsonl"))
    p.add_argument("--questions", type=Path, default=Path("questions_expanded_full_validated.jsonl"))
    p.add_argument("--output", type=Path, default=Path("experiments/runs/e3_m3"))
    p.add_argument("--dense-model", default="BAAI/bge-small-en-v1.5")
    p.add_argument("--dense-revision", default="main")
    p.add_argument("--reranker-model", default="BAAI/bge-reranker-v2-m3")
    p.add_argument("--reranker-revision", default="main")
    p.add_argument("--reranker-label", choices=["m3", "minilm"], default="m3")
    p.add_argument("--tokenizer-model", default="google-bert/bert-base-uncased")
    p.add_argument("--tokenizer-revision", default="main")
    p.add_argument("--device", choices=["cpu", "cuda"], default="cuda")
    p.add_argument("--embed-batch-size", type=int, default=32)
    p.add_argument("--rerank-batch-size", type=int, default=8)
    p.add_argument("--max-length", type=int, default=512)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--seed", type=int, default=20260924)
    p.add_argument("--query-prefix", default="", help="Empty matches the legacy bge-small input format.")
    p.add_argument("--summarize-only", action="store_true")
    return p


def sync(torch, device):
    if device == "cuda":
        torch.cuda.synchronize()


def timed(torch, device, function):
    sync(torch, device)
    start = time.perf_counter()
    value = function()
    sync(torch, device)
    return value, (time.perf_counter() - start) * 1000


def resolved_revision(model, revision):
    from huggingface_hub import model_info
    # An immutable SHA avoids silently resuming with a changed upstream model.
    if len(revision) == 40 and all(c in "0123456789abcdef" for c in revision.lower()):
        return revision
    return model_info(model, revision=revision).sha


def local_model_snapshot(spec, output, tokenizer_only=False):
    """Public HF local_dir API avoids Windows symlink privilege requirements.

    Download only root weights and tokenizer/configuration files, excluding ONNX,
    OpenVINO and duplicate PyTorch weights whenever safetensors are available.
    """
    from huggingface_hub import model_info, snapshot_download
    local_dir = Path(".cache/models") / spec["model"].replace("/", "--") / spec["sha"]
    config_patterns = ["*.json", "*.txt", "*.model", "tokenizer*", "merges.txt"]
    weights = []
    if not tokenizer_only:
        files = [s.rfilename for s in model_info(spec["model"], revision=spec["sha"]).siblings]
        weights = [f for f in files if "/" not in f and f.endswith(".safetensors")]
        if not weights:
            weights = [f for f in files if "/" not in f and f.endswith(".bin")]
        if not weights:
            raise ValueError(f"No supported root model weights found: {spec['model']}")
    snapshot_download(repo_id=spec["model"], revision=spec["sha"], local_dir=local_dir,
                      allow_patterns=config_patterns + weights)
    # Log exact bytes rather than claiming the Git object SHA is a file checksum.
    file_manifest = {"model": spec["model"], "sha": spec["sha"], "tokenizer_only": tokenizer_only,
                     "files": {str(p.relative_to(local_dir)): file_hash(p) for p in local_dir.rglob("*")
                               if p.is_file() and ".cache" not in p.relative_to(local_dir).parts}}
    save_json(output / "model_files" / (spec["model"].replace("/", "--") + ".json"), file_manifest)
    return str(local_dir.resolve())


def environment(torch):
    packages = {}
    for name in ("numpy", "torch", "transformers", "sentence-transformers", "huggingface-hub"):
        packages[name] = importlib.metadata.version(name)
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        git_commit = None
    return {"platform": platform.platform(), "python": platform.python_version(),
            "packages": packages, "cpu": platform.processor(), "git_commit": git_commit,
            "cuda_runtime": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cpu_threads": torch.get_num_threads()}


def write_csv(path, rows):
    if not rows:
        return
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize(output):
    manifest = load_json(output / "manifest.json")
    groups, per_question = defaultdict(list), []
    for path in sorted((output / "traces").glob("*.json.gz")):
        trace = load_json(path)
        if trace["identity_hash"] != manifest["identity_hash"]:
            raise ValueError(f"Foreign trace in run: {path}")
        for record in trace["configurations"]:
            row = {"qid": trace["qid"], "topic": trace["topic"],
                   "group_id": trace["group_id"], "construction_source": trace["construction_source"],
                   **record["configuration"], **record["metrics"], **record["timing_ms"],
                   "rerank_pairs": record["rerank_pairs"],
                   "context_tokens": record["final_context"]["used_tokens"],
                   "partial_chunks": sum(c["partial"] for c in record["final_context"]["chunks"]),
                   "first_url_loss": record["first_url_loss"]}
            per_question.append(row)
            groups[row["config_id"]].append(row)
    write_csv(output / "per_question.csv", per_question)
    rows = []
    for conf in manifest["configurations"]:
        values = groups[conf["config_id"]]
        if not values:
            continue
        rows.append({**conf, "n_questions": len(values),
                     "G_final": np.mean([r["G_final"] for r in values]),
                     "ranking_url_ndcg10": np.mean([r["ranking_url_ndcg10"] for r in values]),
                     "ranking_url_mrr": np.mean([r["ranking_url_mrr"] for r in values]),
                     "mean_context_tokens": np.mean([r["context_tokens"] for r in values]),
                     "latency_p50_ms": np.percentile([r["component_total"] for r in values], 50),
                     "latency_p95_ms": np.percentile([r["component_total"] for r in values], 95),
                     "rerank_pairs_mean": np.mean([r["rerank_pairs"] for r in values])})
    write_csv(output / "summary.csv", rows)
    status = {"status": "complete" if len(per_question) == manifest["expected_records"] else "partial",
              "observed_records": len(per_question), "expected_records": manifest["expected_records"],
              "human_U_available": False, "source_C_available": False, "answer_A_available": False,
              "interpretation": "G is designated-page retention only; these data do not establish evidence utility or selection regret.",
              "timing": "Synchronized measured shared-component sum; cached measurements are reused across budgets/configurations. Not independent end-to-end trials. Offline index/model loading excluded."}
    save_json(output / "status.json", status)
    print(json.dumps(status, indent=2), flush=True)
    return rows


def main(argv=None):
    args = parser().parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)
    if args.summarize_only:
        summarize(args.output)
        return
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    import torch
    from sentence_transformers import SentenceTransformer
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable; install the pixi GPU environment or explicitly choose --device cpu.")
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    corpus, corpus_identity = identify_corpus(read_jsonl(args.corpus))
    questions = read_jsonl(args.questions)
    if args.limit:
        questions = questions[:args.limit]
    if len(corpus) < 64 or not questions:
        raise ValueError("The factorial protocol requires at least 64 corpus chunks and one question.")
    if len({q["qid"] for q in questions}) != len(questions):
        raise ValueError("Duplicate question IDs.")
    if any(not gold_urls(q) for q in questions):
        raise ValueError("All diagnostic questions must supply gold_url(s).")

    # Preserve the original resolved SHA on resumption even if the main branch moved.
    previous = load_json(args.output / "manifest.json") if (args.output / "manifest.json").exists() else None
    models = {}
    for key in ("dense", "reranker", "tokenizer"):
        model, requested = getattr(args, f"{key}_model"), getattr(args, f"{key}_revision")
        old = previous["identity"]["models"].get(key) if previous else None
        sha = old["sha"] if old and old["model"] == model and old["requested_revision"] == requested else resolved_revision(model, requested)
        models[key] = {"model": model, "requested_revision": requested, "sha": sha}
    settings = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items() if k not in ("output", "summarize_only")}
    identity = {"protocol_version": PROTOCOL_VERSION, "settings": settings, "models": models,
                "corpus_sha256": file_hash(args.corpus), "questions_sha256": file_hash(args.questions),
                "code_sha256": {p.name: file_hash(p) for p in (Path(__file__), Path(__file__).with_name("protocol.py"))},
                "packages": environment(torch)["packages"]}
    configs = configurations(args.reranker_label)
    manifest = freeze_manifest(args.output / "manifest.json", {
        "identity_hash": digest(identity), "identity": identity, "environment": environment(torch),
        "created_utc": datetime.now(timezone.utc).isoformat(), "configurations": [c.record() for c in configs],
        "corpus_chunks": len(corpus), "questions": len(questions), "expected_records": 20 * len(questions),
        "corpus_identity": corpus_identity,
        "scope": "E3/E5 source-retention audit on reused, page-informed data; E1/E2/E4 remain unverified.",
        "budget_definition": "Evidence token stream: add_special_tokens=False chunk IDs, one SEP between chunks, prefix truncation including partial last chunk; excludes question and generation prompt.",
        "URL_metric": "Binary unique URL ranking; stable URL collapse; nDCG@10 IDCG includes every gold URL; final G=any designated page with >=1 delivered token.",
        "source_policy": "Open evidence diagnostic. No retrospective NCI requirement; C unavailable.",
        "timing_definition": "One synchronized observation per shared query retrieval and distinct rerank input set, reused across configurations. Per-config packing/cap CPU measured. Offline loading/indexing excluded. Sequential first-stage retrieval and reranking phases; not deployment throughput.",
        "operator_equivalence": "No-reranker post-cap is identical to pre-cap and is omitted; 24 nominal cells collapse to 20."})
    run_hash = manifest["identity_hash"]
    cache = args.output / "cache"
    cache.mkdir(exist_ok=True)
    tokenizer_path = local_model_snapshot(models["tokenizer"], args.output, tokenizer_only=True)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True)
    if tokenizer.sep_token_id is None:
        raise ValueError("Context tokenizer must define a SEP token.")
    tok_path = cache / "corpus_tokens.json.gz"
    if tok_path.exists():
        token_ids = load_json(tok_path)
    else:
        token_ids = tokenizer([c["text"] for c in corpus], add_special_tokens=False,
                              truncation=False, verbose=False)["input_ids"]
        save_json(tok_path, token_ids)
    for c, ids in zip(corpus, token_ids):
        c["token_ids"] = ids
    corpus_by_id = {c["chunk_id"]: c for c in corpus}
    retrieval_path = cache / "retrieval.json.gz"
    retrieval_cache_hit = retrieval_path.exists()
    offline = load_json(args.output / "offline.json") if (args.output / "offline.json").exists() else {}
    if retrieval_path.exists():
        retrieval = load_json(retrieval_path)
    else:
        print(f"Loading dense encoder {args.dense_model}@{models['dense']['sha']}", flush=True)
        load_start = time.perf_counter()
        dense_path = local_model_snapshot(models["dense"], args.output)
        embedder = SentenceTransformer(dense_path, device=args.device, local_files_only=True)
        embedder.max_seq_length = args.max_length
        offline["dense_load_ms"] = (time.perf_counter() - load_start) * 1000
        emb_path = cache / "corpus_embeddings.npy"
        if emb_path.exists():
            embeddings = np.load(emb_path, allow_pickle=False)
        else:
            embeddings, offline["corpus_encode_ms"] = timed(torch, args.device, lambda: embedder.encode(
                [c["text"] for c in corpus], batch_size=args.embed_batch_size,
                normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=True))
            np.save(emb_path, embeddings, allow_pickle=False)
        # An excluded query warmup makes the online timing regime explicit.
        embedder.encode([args.query_prefix + questions[0]["question"]], normalize_embeddings=True)
        retrieval = {}
        for q in questions:
            def retrieve():
                query = embedder.encode([args.query_prefix + q["question"]], normalize_embeddings=True, convert_to_numpy=True)[0]
                scores = embeddings @ query
                # Stable ties use the frozen corpus order.
                indices = np.argsort(-scores, kind="stable")[:64]
                return [{"chunk_id": corpus[int(i)]["chunk_id"], "retrieval_score": float(scores[i]), "raw_rank": rank}
                        for rank, i in enumerate(indices, 1)]
            candidates, ms = timed(torch, args.device, retrieve)
            retrieval[q["qid"]] = {"candidates": candidates, "retrieval_ms": ms}
        save_json(retrieval_path, retrieval)
        embedder.to("cpu")
        del embedder, embeddings
        gc.collect()
        if args.device == "cuda":
            torch.cuda.empty_cache()
        save_json(args.output / "offline.json", offline)

    model = None
    pair_tokenizer = None
    for qi, q in enumerate(questions, 1):
        trace_path = args.output / "traces" / (digest(q["qid"])[:20] + ".json.gz")
        if trace_path.exists():
            if load_json(trace_path)["identity_hash"] != run_hash:
                raise ValueError("Trace identity mismatch")
            print(f"[{qi}/{len(questions)}] resumed {q['qid']}", flush=True)
            continue
        raw_max = [{**corpus_by_id[r["chunk_id"]], **r} for r in retrieval[q["qid"]]["candidates"]]
        # Warm/score each unique operator input separately: pre-cap costs must be measured.
        score_sets = {}
        for pool in (16, 64):
            for cap_mode in ("off", "pre"):
                raw = raw_max[:pool]
                inputs = url_cap(raw) if cap_mode == "pre" else raw
                key = digest({"qid": q["qid"], "ids": [x["chunk_id"] for x in inputs]})
                cache_path = cache / "scores" / f"{key}.json"
                if cache_path.exists():
                    scored = load_json(cache_path)
                    scored["cache_hit"] = True
                else:
                    if model is None:
                        print(f"Loading reranker {args.reranker_model}@{models['reranker']['sha']}", flush=True)
                        start = time.perf_counter()
                        reranker_path = local_model_snapshot(models["reranker"], args.output)
                        pair_tokenizer = AutoTokenizer.from_pretrained(reranker_path, local_files_only=True)
                        dtype = torch.float16 if args.device == "cuda" else torch.float32
                        model = AutoModelForSequenceClassification.from_pretrained(
                            reranker_path, local_files_only=True, torch_dtype=dtype,
                            attn_implementation="eager").to(args.device).eval()
                        offline["reranker_load_ms"] = (time.perf_counter() - start) * 1000
                        with torch.inference_mode():
                            warm = pair_tokenizer([q["question"]], [inputs[0]["text"]], padding=True,
                                                  truncation=True, max_length=args.max_length, return_tensors="pt").to(args.device)
                            model(**warm)
                        sync(torch, args.device)
                        del warm
                        save_json(args.output / "offline.json", offline)

                    def predict():
                        scores, lengths, untruncated_lengths = [], [], []
                        with torch.inference_mode():
                            for start in range(0, len(inputs), args.rerank_batch_size):
                                batch = inputs[start:start + args.rerank_batch_size]
                                pairs = [[q["question"], c["text"]] for c in batch]
                                full = pair_tokenizer(pairs, truncation=False, padding=False, verbose=False)
                                untruncated_lengths.extend(len(v) for v in full["input_ids"])
                                encoded = pair_tokenizer(pairs, padding=True, truncation=True,
                                                         max_length=args.max_length, return_tensors="pt").to(args.device)
                                lengths.extend(encoded["attention_mask"].sum(dim=1).cpu().tolist())
                                logits = model(**encoded).logits
                                if logits.shape[-1] != 1:
                                    raise ValueError("Protocol requires a scalar-logit cross encoder.")
                                scores.extend(logits[:, 0].float().cpu().tolist())
                        return scores, lengths, untruncated_lengths
                    (scores, lengths, full_lengths), ms = timed(torch, args.device, predict)
                    if not np.isfinite(scores).all():
                        raise ValueError("Non-finite reranker scores; no result checkpoint was written.")
                    scored = {"scores": {c["chunk_id"]: s for c, s in zip(inputs, scores)}, "rerank_ms": ms,
                              "input_ids": [c["chunk_id"] for c in inputs], "pair_tokens": lengths,
                              "untruncated_pair_tokens": full_lengths, "pairs": len(inputs),
                              "peak_cuda_allocated_bytes": torch.cuda.max_memory_allocated() if args.device == "cuda" else None}
                    save_json(cache_path, scored)
                    scored["cache_hit"] = False
                score_sets[(pool, cap_mode)] = scored
        records = []
        for config in configs:
            raw = raw_max[:config.pool]
            start = time.perf_counter()
            pre = url_cap(raw) if config.cap == "pre" else raw
            pre_ms = (time.perf_counter() - start) * 1000
            scored = score_sets[(config.pool, "pre" if config.cap == "pre" else "off")] if config.reranker != "none" else None
            start = time.perf_counter()
            ordered = rerank(pre, scored["scores"]) if scored else pre
            sort_ms = (time.perf_counter() - start) * 1000
            start = time.perf_counter()
            post = url_cap(ordered) if config.cap == "post" else ordered
            post_ms = (time.perf_counter() - start) * 1000
            start = time.perf_counter()
            final = pack_prefix(post, config.budget, tokenizer.sep_token_id,
                                lambda ids: tokenizer.decode(ids, skip_special_tokens=False, clean_up_tokenization_spaces=False))
            pack_ms = (time.perf_counter() - start) * 1000
            rank_metrics = url_metrics(post, gold_urls(q))
            final_metrics = url_metrics(final["chunks"], gold_urls(q))
            times = {"retrieval": retrieval[q["qid"]]["retrieval_ms"], "pre_cap": pre_ms,
                     "rerank": scored["rerank_ms"] if scored else 0.0,
                     "score_sort": sort_ms, "post_cap": post_ms, "pack": pack_ms}
            times["component_total"] = sum(times.values())
            records.append({"configuration": config.record(),
                            "stages": {"raw": stage(raw), "pre_cap": stage(pre),
                                       "rerank": stage(ordered, scored["scores"] if scored else None),
                                       "post_cap": stage(post, scored["scores"] if scored else None)},
                            "final_context": final, "timing_ms": times,
                            "timing_provenance": {"scope": "synchronized_shared_component_sum",
                                                  "retrieval_cache_hit": retrieval_cache_hit,
                                                  "rerank_cache_hit": scored["cache_hit"] if scored else False,
                                                  "measurements_shared_across_budgets": True,
                                                  "inference_ms_is_original_measurement": True},
                            "rerank_pairs": scored["pairs"] if scored else 0,
                            "rerank_pair_tokens": scored["pair_tokens"] if scored else [],
                            "rerank_untruncated_pair_tokens": scored["untruncated_pair_tokens"] if scored else [],
                            "metrics": {"G_raw": url_metrics(raw, gold_urls(q))["G"], "G_final": final_metrics["G"],
                                        "ranking_url_ndcg10": rank_metrics["url_ndcg_at_10"],
                                        "ranking_url_mrr": rank_metrics["url_mrr"], "U": None, "C": None, "A": None},
                            "first_url_loss": first_url_loss(raw, pre, ordered, post, final["chunks"], gold_urls(q))})
        save_json(trace_path, {"identity_hash": run_hash, "qid": q["qid"], "question": q["question"],
                               "topic": q.get("topic", "unknown"), "gold_urls": gold_urls(q),
                               "group_id": q.get("group_id") or "|".join(gold_urls(q)),
                               "construction_source": q.get("construction_source", "legacy_page_informed"),
                               "raw_max": stage(raw_max), "configurations": records})
        print(f"[{qi}/{len(questions)}] completed {q['qid']} / 20 configurations", flush=True)
    summarize(args.output)


if __name__ == "__main__":
    main()
