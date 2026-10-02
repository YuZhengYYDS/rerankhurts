"""Recompute E3 URL-retention diagnostics, never human evidence utility.

Eight interactions: (rerank gain with cap - rerank gain without cap) at each
pool/budget for pre/post cap. Intervals are pointwise exploratory grouped
bootstrap intervals; they are not corrected confirmatory hypothesis tests.
"""
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .protocol import file_hash, load_json, save_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260924)
    parser.add_argument("--bootstrap", type=int, default=5000)
    args = parser.parse_args()
    status = load_json(args.run / "status.json")
    if status["status"] != "complete":
        raise ValueError("Summarize a completed run before factorial analysis.")
    with (args.run / "per_question.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    by_config = defaultdict(dict)
    groups = {}
    losses = defaultdict(Counter)
    for row in rows:
        by_config[row["config_id"]][row["qid"]] = float(row["G_final"])
        groups[row["qid"]] = row["group_id"]
        losses[row["config_id"]][row["first_url_loss"]] += 1
    qids = sorted(groups)
    group_names = sorted(set(groups.values()))
    group_indices = [np.array([i for i, q in enumerate(qids) if groups[q] == g]) for g in group_names]
    rng = np.random.default_rng(args.seed)
    sampled_indices = [np.concatenate([group_indices[i] for i in rng.integers(len(group_names), size=len(group_names))])
                       for _ in range(args.bootstrap)]
    ranker = load_json(args.run / "manifest.json")["identity"]["settings"]["reranker_label"]
    interactions = []
    for pool in (16, 64):
        for budget in (512, 2048):
            for cap in ("pre", "post"):
                names = [f"p{pool}_{cap}_{ranker}_b{budget}", f"p{pool}_pre_none_b{budget}",
                         f"p{pool}_off_{ranker}_b{budget}", f"p{pool}_off_none_b{budget}"]
                arrays = [np.array([by_config[name][q] for q in qids]) for name in names]
                contrast = arrays[0] - arrays[1] - arrays[2] + arrays[3]
                boot = [float(contrast[idx].mean()) for idx in sampled_indices]
                lo, hi = np.percentile(boot, [2.5, 97.5])
                interactions.append({"pool": pool, "budget": budget, "cap_order": cap,
                    "endpoint": "designated_page_retention_G", "interaction": float(contrast.mean()),
                    "pointwise_group_bootstrap_95CI": [float(lo), float(hi)], "configuration_order": names})
    save_json(args.run / "factorial_diagnostics.json", {"endpoint": "G, not U",
        "per_question_sha256": file_hash(args.run / "per_question.csv"),
        "analysis_code_sha256": file_hash(__file__), "seed": args.seed, "bootstrap": args.bootstrap,
        "questions": len(qids), "groups": len(group_names), "interactions": interactions,
        "first_URL_loss_counts": {c: dict(v) for c, v in losses.items()},
        "limitations": "URL-defined page groups on reused questions; pointwise exploratory intervals without multiple-comparison correction. Retention of a partial gold chunk is not sufficient evidence. No causal support-loss or true utility claim."})
    print(f"Saved {len(interactions)} G-only contrasts to {args.run / 'factorial_diagnostics.json'}")


if __name__ == "__main__":
    main()
