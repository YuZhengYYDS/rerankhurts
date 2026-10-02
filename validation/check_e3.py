"""Independently check complete E3 traces and frozen-score numerical sensitivity.

Uses the Python standard library, saved traces and the original corpus only.
No model, scorer implementation, cache or network is required. It does not
modify a run, and it does not turn designated-page retention into utility.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith(".gz") else data)


def normalize(url):
    value = urlsplit(str(url).strip())
    return urlunsplit((value.scheme.lower(), value.netloc.lower(), value.path.rstrip("/"), value.query, ""))


def ids(rows):
    return [row["chunk_id"] for row in rows]


def cap_two(rows):
    counts, result = Counter(), []
    for row in rows:
        url = normalize(row["url"])
        if counts[url] < 2:
            result.append(row)
            counts[url] += 1
    return result


def prefix_by_length(rows, budget):
    chosen, remaining = [], budget
    for row in rows:
        if not row["chunk_tokens"]:
            continue
        available = remaining - int(bool(chosen))
        if available <= 0:
            break
        take = min(row["chunk_tokens"], available)
        chosen.append({**row, "delivered_tokens": take})
        remaining = available - take
        if take < row["chunk_tokens"]:
            break
    return chosen, budget - remaining


def metric(rows, gold):
    pages = list(dict.fromkeys(normalize(row["url"]) for row in rows))
    ranks = [rank for rank, page in enumerate(pages, 1) if page in gold]
    dcg = sum(1 / math.log2(rank + 1) for rank in ranks if rank <= 10)
    ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(10, len(gold)) + 1))
    return int(bool(ranks)), dcg / ideal


def check(run, output):
    manifest = read_json(run / "manifest.json")
    status = read_json(run / "status.json")
    if status["status"] != "complete":
        raise ValueError("Only complete runs may produce the final E3 integrity report")
    corpus_path = Path(manifest["identity"]["settings"]["corpus"])
    if not corpus_path.is_absolute():
        corpus_path = ROOT / corpus_path
    corpus_bytes = corpus_path.read_bytes()
    if hashlib.sha256(corpus_bytes).hexdigest() != manifest["identity"]["corpus_sha256"]:
        raise ValueError("Original corpus hash does not match the run manifest")
    corpus = [json.loads(line) for line in corpus_bytes.decode("utf-8-sig").splitlines() if line.strip()]
    legacy_counts = Counter(row["chunk_id"] for row in corpus)
    canonical_ids = [f"{row['chunk_id']}::row{i:06d}" if legacy_counts[row["chunk_id"]] > 1 else row["chunk_id"] for i, row in enumerate(corpus)]
    if len(canonical_ids) != len(set(canonical_ids)):
        raise ValueError("Canonical corpus IDs are not unique")
    expected_configs = {row["config_id"]: row for row in manifest["configurations"]}
    errors, sensitivity, query_ids = [], [], set()
    stage_loss, separators = Counter(), Counter()
    shared_pairs, changed_pairs, max_difference = 0, 0, 0.0
    records = 0
    trace_paths = sorted((run / "traces").glob("*.json.gz"))

    def require(condition, message, qid, config=None):
        if not condition:
            errors.append({"qid": qid, "config_id": config, "message": message})

    for path in trace_paths:
        trace = read_json(path)
        qid = trace["qid"]
        require(qid not in query_ids, "duplicate query trace", qid)
        query_ids.add(qid)
        require(trace["identity_hash"] == manifest["identity_hash"], "identity hash mismatch", qid)
        gold = set(trace["gold_urls"])
        configs = trace["configurations"]
        lookup = {row["configuration"]["config_id"]: row for row in configs}
        require(len(configs) == len(lookup) == len(expected_configs), "missing/duplicate configuration", qid)
        require(set(lookup) == set(expected_configs), "configuration IDs do not match manifest", qid)
        require(len(trace["raw_max"]) == 64, "raw pool is not 64 rows", qid)
        require(len(ids(trace["raw_max"])) == len(set(ids(trace["raw_max"]))), "raw canonical ID collision", qid)
        for record in configs:
            records += 1
            conf = record["configuration"]
            cid = conf["config_id"]
            require(conf == expected_configs.get(cid), "configuration differs from manifest", qid, cid)
            stages = record["stages"]
            raw, pre, ordered, post = (stages[key] for key in ("raw", "pre_cap", "rerank", "post_cap"))
            final = record["final_context"]
            require(ids(raw) == ids(trace["raw_max"][:conf["pool"]]), "unequal shared raw prefix", qid, cid)
            require(ids(pre) == ids(cap_two(raw) if conf["cap"] == "pre" else raw), "invalid pre-cap", qid, cid)
            require(len(ordered) == len(pre) and set(ids(ordered)) == set(ids(pre)), "rerank changed membership", qid, cid)
            expected_order = sorted(ordered, key=lambda row: (-row["rerank_score"], row["raw_rank"])) if conf["reranker"] != "none" else pre
            require(ids(ordered) == ids(expected_order), "invalid ranking or tie handling", qid, cid)
            require(ids(post) == ids(cap_two(ordered) if conf["cap"] == "post" else ordered), "invalid post-cap", qid, cid)
            expected_final, used = prefix_by_length(post, conf["budget"])
            require(ids(final["chunks"]) == ids(expected_final), "invalid token budget prefix", qid, cid)
            require(final["used_tokens"] == used == len(final["token_ids"]) <= conf["budget"], "inconsistent token count", qid, cid)
            require(final["separator_tokens"] == max(len(final["chunks"]) - 1, 0), "wrong separator count", qid, cid)
            cursor = 0
            for i, chunk in enumerate(final["chunks"]):
                if i:
                    separators[final["token_ids"][cursor]] += 1
                    cursor += 1
                tokens = chunk["token_ids"]
                require(final["token_ids"][cursor:cursor + len(tokens)] == tokens, "chunk IDs differ from evidence stream", qid, cid)
                require(len(tokens) == chunk["delivered_tokens"] > 0, "empty or wrong delivered token count", qid, cid)
                require(chunk["partial"] == (len(tokens) < chunk["chunk_tokens"]), "wrong partial chunk flag", qid, cid)
                require(i == len(final["chunks"]) - 1 or not chunk["partial"], "nonfinal partial chunk", qid, cid)
                cursor += len(tokens)
            for rows in (*stages.values(), final["chunks"]):
                for row in rows:
                    original = corpus[row["corpus_row"]]
                    require(row["chunk_id"] == canonical_ids[row["corpus_row"]], "canonical ID does not identify corpus row", qid, cid)
                    require(row["original_chunk_id"] == original["chunk_id"] and row["url"] == original["url"], "corpus metadata mismatch", qid, cid)
            g, _ = metric(final["chunks"], gold)
            _, ndcg = metric(post, gold)
            require(g == record["metrics"]["G_final"], "wrong G", qid, cid)
            require(abs(ndcg - record["metrics"]["ranking_url_ndcg10"]) < 1e-12, "wrong distinct-page nDCG", qid, cid)
            loss = "retained"
            for name, rows in (("candidate_not_covered", raw), ("pre_cap", pre), ("rerank_membership", ordered), ("post_cap", post), ("budget", final["chunks"])):
                if metric(rows, gold)[0] == 0:
                    loss = name
                    break
            require(loss == record["first_url_loss"], "wrong first-loss stage", qid, cid)
            stage_loss[loss] += 1
            if conf["budget"] == 512:
                other = lookup[cid.replace("_b512", "_b2048")]
                require(record["metrics"]["G_final"] <= other["metrics"]["G_final"], "G decreases as prefix budget grows", qid, cid)
                require(record["metrics"]["ranking_url_ndcg10"] == other["metrics"]["ranking_url_ndcg10"], "ranking metric depends on final budget", qid, cid)

        rankers = {row["configuration"]["reranker"] for row in configs} - {"none"}
        for ranker in sorted(rankers):
            for pool in (16, 64):
                pre = lookup[f"p{pool}_pre_{ranker}_b512"]["stages"]["rerank"]
                off = lookup[f"p{pool}_off_{ranker}_b512"]["stages"]["rerank"]
                off_scores = {row["chunk_id"]: row["rerank_score"] for row in off}
                differences = [abs(row["rerank_score"] - off_scores[row["chunk_id"]]) for row in pre]
                shared_pairs += len(differences)
                changed_pairs += sum(diff > 0 for diff in differences)
                max_difference = max(max_difference, *differences)
                counterfactual = sorted(pre, key=lambda row: (-off_scores[row["chunk_id"]], row["raw_rank"]))
                for budget in (512, 2048):
                    observed = lookup[f"p{pool}_pre_{ranker}_b{budget}"]
                    alternate_final, _ = prefix_by_length(counterfactual, budget)
                    alternate_g, _ = metric(alternate_final, gold)
                    _, alternate_ndcg = metric(counterfactual, gold)
                    sensitivity.append({
                        "qid": qid, "pool": pool, "budget": budget, "reranker": ranker,
                        "common_pairs": len(differences), "changed_pair_scores": sum(diff > 0 for diff in differences),
                        "max_abs_logit_difference": max(differences),
                        "changed_pre_order": ids(pre) != ids(counterfactual),
                        "changed_final_chunk_ids": ids(observed["final_context"]["chunks"]) != ids(alternate_final),
                        "observed_G": observed["metrics"]["G_final"], "fixed_off_score_G": alternate_g,
                        "G_difference": alternate_g - observed["metrics"]["G_final"],
                        "observed_ranking_url_ndcg10": observed["metrics"]["ranking_url_ndcg10"],
                        "fixed_off_score_ranking_url_ndcg10": alternate_ndcg,
                    })

    require(records == manifest["expected_records"], "record count differs from manifest", "all")
    require(len(query_ids) == manifest["questions"], "query count differs from manifest", "all")
    require(len(separators) <= 1, "separator IDs differ within run", "all")
    output.mkdir(parents=True, exist_ok=True)
    with (output / "e3_score_sensitivity.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sensitivity[0]))
        writer.writeheader()
        writer.writerows(sensitivity)
    report = {
        "status": "pass" if not errors else "fail", "run_identity": manifest["identity_hash"],
        "queries": len(query_ids), "records_checked": records, "corpus_rows": len(corpus),
        "canonical_corpus_ids_unique": True, "first_url_loss_counts": dict(stage_loss),
        "trace_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in trace_paths},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "checks": ["shared candidate prefixes", "no canonical ID collisions", "stage corpus-row identity", "operator ordering and stable ties", "exact budget prefix and token stream", "partial chunk flags", "unique-page metric/complete-gold IDCG", "budget G monotonicity", "cutoff-invariant ranking metric", "first page-loss stage"],
        "score_sensitivity": {
            "definition": "Keep the pre-cap membership fixed and rerank with saved no-cap scores for those same pairs; no new model execution.",
            "scope": "Floating-point/batch-input sensitivity, not human utility or a randomized effect.",
            "shared_pairs_counted_once_per_query_pool": shared_pairs,
            "nonidentical_pair_scores": changed_pairs,
            "maximum_absolute_logit_difference": max_difference,
            "query_pool_order_changes": sum(row["changed_pre_order"] for row in sensitivity if row["budget"] == 512),
            "query_pool_budget_final_id_changes": sum(row["changed_final_chunk_ids"] for row in sensitivity),
            "query_pool_budget_G_changes": sum(row["G_difference"] != 0 for row in sensitivity),
            "by_config": [{"pool": pool, "budget": budget,
                           "n": sum(row["pool"] == pool and row["budget"] == budget for row in sensitivity),
                           "G_changes": sum(row["G_difference"] != 0 for row in sensitivity if row["pool"] == pool and row["budget"] == budget),
                           "G_sum_difference": sum(row["G_difference"] for row in sensitivity if row["pool"] == pool and row["budget"] == budget)}
                          for pool in (16, 64) for budget in (512, 2048)],
        },
        "limitations": ["This verifies the frozen run's structural and metric consistency; it does not independently rerun embedding or reranker inference.",
                        "Final G counts any designated page with at least one delivered token; no support/utility claim follows.",
                        "Fixed-score ordering is a post-run sensitivity analysis; original timing measurements are not recomputed.",
                        "Identical raw chunk ID prefixes establish candidate fairness here; all content remains the reused, source-informed benchmark."],
        "errors": errors,
    }
    (output / "e3_integrity.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "queries", "records_checked", "score_sensitivity")}, indent=2))
    return int(bool(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "experiments/runs/e3_m3")
    parser.add_argument("--output", type=Path, default=ROOT / "validation/results")
    args = parser.parse_args()
    return check(args.run.resolve(), args.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
