"""Measure whole online requests with resident models and no request-result cache."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
import time

import numpy as np

from experiments.protocol import digest, file_hash, load_json, read_jsonl, save_json
from .downstream import answer_configurations, fixed_world_sample, trace_path, trace_records, write_csv


def request_schedule(qids, conditions, repetitions, seed):
    requests = [(qid, condition, repeat) for repeat in range(repetitions)
                for qid in sorted(qids) for condition in conditions]
    random.Random(seed).shuffle(requests)
    return requests


def delivery_identity(chunks):
    return digest([(chunk["chunk_id"], chunk["source_token_start"], chunk["source_token_end"],
                    chunk["token_ids"]) for chunk in chunks])


def run(args):
    from .backend import Runtime

    args.output.mkdir(parents=True, exist_ok=True)
    metadata = read_jsonl(args.data / "metadata.jsonl")
    groups = fixed_world_sample(metadata, args.worlds_per_seed)
    chosen = []
    for i, group in enumerate(groups):
        variants = sorted((m for m in metadata if m["group_id"] == group), key=lambda m: m["qid"])
        chosen.append(variants[i % len(variants)])
    meta_by_id = {m["qid"]: m for m in chosen}
    configurations = answer_configurations()
    diagnostics = {qid: trace_records(load_json(trace_path(args.run, qid))) for qid in meta_by_id}
    identity = {"kind": "independent-online-request-timing-v1", "groups": groups,
                "qids": sorted(meta_by_id), "configurations": {n: c.record() for n, c in configurations.items()},
                "repetitions": args.repetitions, "warmup_requests_per_configuration": 2,
                "seed": 20261002, "use_result_cache": False,
                "backend_sha256": file_hash(Path(__file__).with_name("backend.py")),
                "protocol_sha256": file_hash(Path(__file__).with_name("protocol.py")),
                "timing_code_sha256": file_hash(Path(__file__)),
                "downstream_code_sha256": file_hash(Path(__file__).with_name("downstream.py")),
                "data": {p.name: file_hash(p) for p in args.data.glob("*.jsonl")},
                "inference_manifest": file_hash(args.run / "manifest.json"),
                "diagnostic_trace_hashes": {qid: file_hash(trace_path(args.run, qid)) for qid in meta_by_id},
                "boundary": "CUDA-synchronized wall time around Runtime.execute(use_cache=False); includes real query embedding, retrieval, CE scoring, policy/cap/packing and in-memory trace construction. Excludes loading, offline doc index, serialization and answer generation.",
                "first_pass": "First measurement after prepare/preload, not a cold-machine, cold-filesystem, or model-load benchmark."}
    identity_hash = digest(identity)
    manifest = args.output / "manifest.json"
    if manifest.exists() and load_json(manifest)["identity_hash"] != identity_hash:
        raise ValueError("Timing identity changed; choose a new output folder")
    save_json(manifest, {"identity_hash": identity_hash, "identity": identity})
    runtime = Runtime(args.data / "corpus.jsonl", args.data / "questions.jsonl", args.run, device=args.device)
    runtime.prepare_indexes()
    runtime.preload_models(names=("m3",))
    rows = []
    # A measured session is indivisible: do not combine restarted first/warm-state
    # observations into an apparently uninterrupted latency trial.
    path = args.output / "requests.jsonl"
    if path.exists():
        raise ValueError("Timing observations already exist; choose a new session directory")
    warmup_qid = sorted(meta_by_id)[0]
    with path.open("w", encoding="utf-8") as stream:
        for phase, repetitions in (("first_pass", 1), ("steady", args.repetitions)):
            if phase == "steady":
                for condition, conf in configurations.items():
                    for _ in range(2):
                        runtime.execute(warmup_qid, conf, use_cache=False)
                runtime.sync()
            schedule = request_schedule(meta_by_id, configurations, repetitions,
                                        20261002 + (1 if phase == "steady" else 0))
            for index, (qid, condition, repeat) in enumerate(schedule, 1):
                runtime.sync()
                start = time.perf_counter()
                trace = runtime.execute(qid, configurations[condition], use_cache=False)
                runtime.sync()
                elapsed = (time.perf_counter() - start) * 1000
                provenance = trace["timing_provenance"]
                if (provenance["scope"] != "independent_live_request" or provenance["query_cache_hit"]
                        or provenance["rerank_cache_hit"] or not provenance["offline_index_and_model_loading_excluded"]):
                    raise ValueError("Timed request reused cached results or loaded a model inside the measured boundary")
                meta = meta_by_id[qid]
                cached_context = diagnostics[qid][configurations[condition].config_id]["final_context"]
                current_delivery = delivery_identity(trace["final_context"]["chunks"])
                row = {"identity_hash": identity_hash, "phase": phase, "qid": qid,
                       "group_id": meta["group_id"], "seed": meta["seed"],
                       "template_family": meta["template_family"], "variant_id": meta["variant_id"],
                       "condition": condition, "repeat": repeat, "latency_ms": elapsed,
                       "rerank_pairs": trace["rerank_pairs"],
                       "evidence_tokens": trace["final_context"]["used_tokens"],
                       "final_delivery_sha256": current_delivery,
                       "same_delivery_as_diagnostic": current_delivery == delivery_identity(cached_context["chunks"]),
                       "timing_ms": trace["timing_ms"], "timing_provenance": trace["timing_provenance"]}
                stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                stream.flush()
                rows.append(row)
                print(json.dumps({"phase": phase, "requests": index, "expected": len(schedule),
                                  "condition": condition, "latency_ms": round(elapsed, 2)}), flush=True)
    summaries = []
    for phase in ("first_pass", "steady"):
        for condition in configurations:
            values = [r for r in rows if r["phase"] == phase and r["condition"] == condition]
            latencies = np.asarray([r["latency_ms"] for r in values])
            summaries.append({"phase": phase, "condition": condition, "requests": len(values),
                              "worlds": len({r["group_id"] for r in values}),
                              "p50_ms": float(np.quantile(latencies, .5)),
                              "p95_ms": float(np.quantile(latencies, .95)),
                              "mean_ms": float(latencies.mean()),
                              "different_delivery_requests": sum(not r["same_delivery_as_diagnostic"] for r in values),
                              "mean_rerank_pairs": float(np.mean([r["rerank_pairs"] for r in values]))})
    write_csv(args.output / "summary.csv", summaries)
    save_json(args.output / "status.json", {"status": "complete", "identity_hash": identity_hash,
              "requests": len(rows), "worlds": len(groups), "warmup_requests_excluded": 8,
              "requests_sha256": file_hash(path), "summary_sha256": file_hash(args.output / "summary.csv"),
              "interpretation": "Actual local per-request latency; repeated requests are not independent worlds, and this is not a production throughput benchmark."})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, default=Path("experiments/strengthening/data/strengthening_v1"))
    p.add_argument("--run", type=Path, default=Path("experiments/runs/strengthening_v1"))
    p.add_argument("--output", type=Path, default=Path("experiments/strengthening/results/strengthening_v1/timing"))
    p.add_argument("--worlds-per-seed", type=int, default=8)
    p.add_argument("--repetitions", type=int, default=5)
    p.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    run(p.parse_args())


if __name__ == "__main__":
    main()
