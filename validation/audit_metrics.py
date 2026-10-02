"""Independent, offline E0 audit of the frozen release (Python standard library).

This never imports the original scorer and never calls a model. Original
first-gold chunk metrics and distinct-page metrics are separate columns. No
URL metric is labelled content utility or human evaluation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FIELDS = (
    "retrieve_pool_size", "final_top_k", "max_chunks_per_url", "hybrid_alpha",
    "rerank_depth", "sparse_backend", "fusion_method", "rerank_model",
    "embed_model_name", "corpus_chunk_count",
)
METRICS = (
    "hit_at_5_chunk", "hit_at_10_chunk", "mrr_first_gold_chunk",
    "first_gold_discount_at_10", "final_gold_page_hit", "hit_full_ranking",
    "url_recall_at_10_distinct_pages", "url_ndcg_at_10_distinct_pages",
    "mrr_first_gold_distinct_page",
)
METHODS = {
    "Base": "baseline", "Dense": "control_dense_only", "Hybrid-BM25": "hybrid_bm25",
    "RRF": "rrf_hybrid", "Rerank": "rerank", "BM25+Dedup": "bm25_base",
    "BM25": "bm25_only", "None (dense Base)": "baseline", "MiniLM-L6": "rerank",
    "bge-reranker-base": "rerank_bge_base", "MedCPT-Cross-Encoder": "rerank_medcpt",
    "LLM listwise (DeepSeek)": "rerank_llm", "bge-reranker-v2-m3": "rerank_bge_m3",
    "MiniLM-L6 + NCI source prior": "rerank_source_aware",
}
OLD_COLUMNS = {
    "recall_at_5": "hit_at_5_chunk", "recall_at_10": "hit_at_10_chunk",
    "mrr": "mrr_first_gold_chunk", "ndcg_at_10": "first_gold_discount_at_10",
    "gold_url_hit_rate": "final_gold_page_hit", "final_top_k_hit_rate": "final_gold_page_hit",
}


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    rows = list(rows)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_questions(path):
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    index = {str(row["qid"]): row for row in rows}
    if len(index) != len(rows):
        raise ValueError(f"Duplicate question IDs in {path}")
    return index


def load_normalizer(root):
    """Use the released wording transformation, never its metric scorer."""
    spec = importlib.util.spec_from_file_location("audit_question_normalizer", root / "generate_normalized_questions.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.rewrite_question


def split_urls(value):
    return [part.strip() for part in str(value or "").split("|") if part.strip()]


def gold_urls(question):
    value = question.get("gold_urls")
    if isinstance(value, str):
        value = json.loads(value)
    return set(value or [question["gold_url"]])


def first_rank(urls, gold):
    return next((rank for rank, url in enumerate(urls, 1) if url in gold), None)


def measure(ranking, final, gold, k=10):
    """Exact URL matching; repeated URLs consume chunk positions, not page ranks.

    Distinct-page nDCG has binary page relevance, stable deduplication, and IDCG
    computed from the *complete frozen gold set*, including non-retrieved gold.
    It evaluates k distinct pages, a different budget from k chunks.
    """
    if not gold:
        raise ValueError("Missing gold annotation is unknown, not an irrelevant query")
    rank = first_rank(ranking, gold)
    pages = list(dict.fromkeys(ranking))
    page_rank = first_rank(pages, gold)
    discount = lambda pos: 1.0 / math.log2(pos + 1)
    dcg = sum(discount(i) for i, url in enumerate(pages[:k], 1) if url in gold)
    idcg = sum(discount(i) for i in range(1, min(k, len(gold)) + 1))
    return {
        "first_gold_chunk_rank": rank,
        "first_gold_distinct_page_rank": page_rank,
        "hit_at_5_chunk": float(rank is not None and rank <= 5),
        "hit_at_10_chunk": float(rank is not None and rank <= k),
        "mrr_first_gold_chunk": 0.0 if rank is None else 1.0 / rank,
        "first_gold_discount_at_10": 0.0 if rank is None or rank > k else discount(rank),
        "final_gold_page_hit": float(first_rank(final, gold) is not None),
        "hit_full_ranking": float(rank is not None),
        "url_recall_at_10_distinct_pages": len(set(pages[:k]) & gold) / len(gold),
        "url_ndcg_at_10_distinct_pages": dcg / idcg,
        "mrr_first_gold_distinct_page": 0.0 if page_rank is None else 1.0 / page_rank,
    }


def summarize(rows, source, subset="all"):
    groups = defaultdict(list)
    for row in rows:
        groups[row["mode"]].append(row)
    summaries = []
    for mode, group in sorted(groups.items()):
        summaries.append({
            "source": source, "subset": subset, "mode": mode, "num_questions": len(group),
            **{key: statistics.mean(row[key] for row in group) for key in METRICS},
            "rerank_ms": statistics.mean(float(row.get("rerank_ms") or 0) for row in group),
        })
    return summaries


def transition(base, candidate, cutoff):
    b = base["first_gold_chunk_rank"]
    c = candidate["first_gold_chunk_rank"]
    if cutoff is not None:
        b = b if b is not None and b <= cutoff else None
        c = c if c is not None and c <= cutoff else None
    if b is None and c is None:
        return "both_missing"
    if b is None:
        return "rescued"
    if c is None:
        return "lost"
    return "improved" if c < b else "worsened" if c > b else "unchanged"


def paired_bootstrap(rows, source, modes, repeats=5000):
    by_mode = defaultdict(dict)
    for row in rows:
        by_mode[row["mode"]][row["qid"]] = row
    out = []
    for mode in modes:
        common = sorted(set(by_mode["baseline"]) & set(by_mode[mode]))
        if not common:
            continue
        for metric in ("first_gold_discount_at_10", "final_gold_page_hit"):
            differences = [by_mode[mode][qid][metric] - by_mode["baseline"][qid][metric] for qid in common]
            clusters = defaultdict(list)
            for qid, diff in zip(common, differences):
                clusters[by_mode["baseline"][qid]["gold_page_group"]].append(diff)
            for unit in ("question", "gold_page_cluster"):
                units = [[x] for x in differences] if unit == "question" else list(clusters.values())
                rng = random.Random(42)
                draws = []
                for _ in range(repeats):
                    chosen = [units[rng.randrange(len(units))] for _ in units]
                    draws.append(sum(sum(group) for group in chosen) / sum(len(group) for group in chosen))
                draws.sort()
                out.append({
                    "source": source, "mode": mode, "reference": "baseline", "metric": metric,
                    "resampling_unit": unit, "n_questions": len(common), "n_gold_page_clusters": len(clusters),
                    "difference": statistics.mean(differences), "ci_low": draws[int(.025 * repeats)],
                    "ci_high": draws[min(repeats - 1, int(.975 * repeats))],
                    "bootstrap_repeats": repeats, "seed": 42,
                    "interpretation": "descriptive sensitivity; no independent utility labels; no multiplicity adjustment",
                })
    return out


def audit(root, out, bootstrap_repeats=5000):
    out.mkdir(parents=True, exist_ok=True)
    qpaths = {
        "original100": root / "questions.jsonl",
        "audited78": root / "result/emnlp_full_results_20260427_gpu_final/paper_questions_validated.jsonl",
        "expanded155": root / "questions_expanded_full_validated.jsonl",
    }
    questions = {key: read_questions(path) for key, path in qpaths.items()}
    all_rows, summaries, inventory, issues, configs, input_paths = [], [], [], [], [], list(qpaths.values())
    input_paths.extend(root / filename for filename in (
        "corpus_chunks_v1.jsonl", "corpus_chunks_v2.jsonl", "run_rag_eval.py",
        "score_retrieval.py", "paper_support_analysis.py", "summarize_supplement_results.py",
        "generate_normalized_questions.py",
    ))
    rewrite_question = load_normalizer(root)
    normalization_rows, normalization_zeroed = [], []
    rows_by_source = {}
    for path in sorted((root / "results/per_question").glob("*.csv")):
        raw = read_csv(path)
        if not raw or not {"mode", "qid", "ranking_urls", "final_urls"} <= raw[0].keys():
            continue
        source = path.stem
        qset = "expanded155" if source.startswith("p4_expanded") else "original100" if "full100" in source else "audited78"
        qindex = questions[qset]
        measured, keys, changed_text = [], set(), 0
        for row in raw:
            key = (row["mode"], row["qid"])
            if key in keys:
                issues.append({"source": source, "kind": "duplicate_query_mode", "qid": row["qid"], "mode": row["mode"]})
                continue
            keys.add(key)
            if row["qid"] not in qindex:
                issues.append({"source": source, "kind": "missing_question_id", "qid": row["qid"]})
                continue
            question = qindex[row["qid"]]
            mismatch = row.get("question") != question["question"]
            changed_text += mismatch
            if mismatch and source != "supp_query_normalization":
                issues.append({"source": source, "kind": "question_text_mismatch", "qid": row["qid"]})
            if source == "supp_query_normalization" and rewrite_question(question["question"])[0] != row["question"]:
                issues.append({"source": source, "kind": "unexpected_normalized_text", "qid": row["qid"]})
            ranking, final = split_urls(row["ranking_urls"]), split_urls(row["final_urls"])
            final_k = int(float(row.get("final_top_k") or len(final)))
            if final != ranking[:final_k]:
                issues.append({"source": source, "kind": "final_not_ranking_prefix", "qid": row["qid"], "mode": row["mode"]})
            for field, actual in (("ranking_count", len(ranking)), ("final_count", len(final))):
                if row.get(field) and int(float(row[field])) != actual:
                    issues.append({"source": source, "kind": field + "_mismatch", "qid": row["qid"], "mode": row["mode"]})
            measured.append({
                "source": source, "question_set": qset, "mode": row["mode"], "qid": row["qid"],
                "gold_page_group": "|".join(sorted(gold_urls(question))),
                "construction_source": question.get("construction_source", "original"),
                "ranking_url_count": len(ranking), "ranking_distinct_page_count": len(set(ranking)),
                "final_url_count": len(final), "final_distinct_page_count": len(set(final)),
                "rerank_ms": float(row.get("rerank_ms") or 0),
                **measure(ranking, final, gold_urls(question)),
            })
            if source == "supp_query_normalization":
                # Reproduce the historical (qid, question) left join: changed
                # wording became an unmatched annotation and was scored zero.
                normalization_zeroed.append({**measured[-1], **{key: 0.0 if mismatch else measured[-1][key] for key in METRICS}})
                if mismatch:
                    normalization_rows.append({"mode": row["mode"], "qid": row["qid"],
                                               "original_question": question["question"], "normalized_question": row["question"],
                                               "legacy_join_matches": False, "released_rewrite_verified": True,
                                               **{key: measured[-1][key] for key in METRICS}})
        rows_by_source[source] = measured
        all_rows.extend(measured)
        summaries.extend(summarize(measured, source))
        if qset == "expanded155":
            for subset, filter_fn in (
                ("original78", lambda row: row["qid"] in questions["audited78"]),
                ("added77", lambda row: row["qid"] not in questions["audited78"]),
            ):
                summaries.extend(summarize([row for row in measured if filter_fn(row)], source, subset))
        modes = sorted(set(row["mode"] for row in raw))
        missing_counts = {mode: len(set(qindex) - {row["qid"] for row in raw if row["mode"] == mode}) for mode in modes}
        inventory.append({
            "source": source, "question_set": qset, "rows": len(raw), "modes": len(modes),
            "question_text_differences": changed_text, "expected_normalized_query": source == "supp_query_normalization",
            "missing_query_counts": json.dumps(missing_counts, sort_keys=True),
            "has_raw_candidates": "retrieved_chunk_ids" in raw[0],
            "has_final_chunk_ids": "final_chunk_ids" in raw[0],
            "has_final_evidence_texts": "final_evidence_texts" in raw[0],
            "has_run_timestamp": any(key in raw[0] for key in ("timestamp", "run_timestamp", "run_id")),
        })
        for mode in modes:
            configs.append({"source": source, "mode": mode, **{
                field: json.dumps(sorted(set(row.get(field, "") for row in raw if row["mode"] == mode))) for field in CONFIG_FIELDS
            }})
        input_paths.append(path)

    lookup = {(row["source"], row["subset"], row["mode"]): row for row in summaries}
    comparisons = []
    historical_normalization = {row["mode"]: row for row in summarize(normalization_zeroed, "supp_query_normalization_legacy_join")}

    def compare(table, row_id, published, actual, metric, tolerance=5.1e-5):
        difference = actual - float(published)
        explained_legacy_bug = (
            table == "supp_query_normalization_overall" and metric in OLD_COLUMNS
            and abs(historical_normalization[row_id][OLD_COLUMNS[metric]] - float(published)) <= tolerance
            and abs(difference) > tolerance
        )
        comparisons.append({"table": table, "row": row_id, "metric": metric,
                            "published": float(published), "recomputed": actual, "difference": difference,
                            "tolerance": tolerance, "pass": abs(difference) <= tolerance,
                            "explained_historical_query_join_bug": explained_legacy_bug})

    mappings = {
        "paper_table_main_baselines": "rag_results_experiments",
        "retrieval_metrics_overall": "rag_results_experiments",
        "supp_strong_baselines_validated_overall": "supp_strong_baselines_validated",
        "supp_query_normalization_overall": "supp_query_normalization",
    }
    for table, source in mappings.items():
        path = root / "results/tables" / (table + ".csv")
        input_paths.append(path)
        for row in read_csv(path):
            mode = row.get("mode") or METHODS[row["method"]]
            actual = lookup[(source, "all", mode)]
            for published_metric, audit_metric in OLD_COLUMNS.items():
                if row.get(published_metric):
                    compare(table, mode, row[published_metric], actual[audit_metric], published_metric)

    views = {"orig78": "supp_new_rerankers_combined", "iso78": "p4_iso_v2corpus_78q", "exp155": "p4_expanded_retrieval_combined"}
    table = "rev_table_rerankers"
    input_paths.append(root / "results/tables" / (table + ".csv"))
    for row in read_csv(input_paths[-1]):
        for view, source in views.items():
            actual = lookup[(source, "all", METHODS[row["method"]])]
            for suffix, metric in {"ndcg": "first_gold_discount_at_10", "mrr": "mrr_first_gold_chunk", "r10": "hit_at_10_chunk", "hit": "final_gold_page_hit", "rerank_ms": "rerank_ms"}.items():
                compare(table, view + ":" + METHODS[row["method"]], row[view + "_" + suffix], actual[metric], suffix, .051 if suffix == "rerank_ms" else 5.1e-5)

    sweeps = {
        "supp_pool_sweep_summary": lambda row: "supp_pool_sweep_p" + str(int(float(row["pool_size"]))).zfill(2),
        "supp_rerank_depth_summary": lambda row: "supp_rerank_depth_d" + str(int(float(row["depth"]))).zfill(3),
        "supp_dedup_sweep_summary": lambda row: "supp_dedup_sweep_c" + row["dedup_cap"],
        "supp_finalk_sweep_summary": lambda row: "supp_finalk_sweep_k" + str(int(float(row["final_k"]))),
        "supp_source_ablation_summary": lambda row: "supp_source_ablation_" + row["corpus_source_preset"],
    }
    for table, source_fn in sweeps.items():
        path = root / "results/tables" / (table + ".csv")
        input_paths.append(path)
        for row in read_csv(path):
            source = source_fn(row)
            actual = lookup[(source, "all", row["mode"])]
            for old, new in OLD_COLUMNS.items():
                if row.get(old):
                    compare(table, source + ":" + row["mode"], row[old], actual[new], old)

    transitions, cases = [], []
    main = rows_by_source["rag_results_experiments"]
    main_index = {(row["mode"], row["qid"]): row for row in main}
    for mode in sorted({row["mode"] for row in main} - {"baseline"}):
        candidates = [row for row in main if row["mode"] == mode]
        for cutoff in (None, 10, 4):
            counts = Counter(transition(main_index[("baseline", row["qid"])], row, cutoff) for row in candidates)
            for category in ("both_missing", "improved", "lost", "rescued", "unchanged", "worsened"):
                transitions.append({"mode": mode, "cutoff": "full" if cutoff is None else cutoff,
                                    "transition": category, "count": counts[category], "n": len(candidates)})
        for row in candidates:
            base = main_index[("baseline", row["qid"])]
            if base["final_gold_page_hit"] != row["final_gold_page_hit"]:
                cases.append({"mode": mode, "qid": row["qid"], "question": questions["audited78"][row["qid"]]["question"],
                              "base_rank": base["first_gold_chunk_rank"], "candidate_rank": row["first_gold_chunk_rank"],
                              "base_final_hit": base["final_gold_page_hit"], "candidate_final_hit": row["final_gold_page_hit"],
                              "event": "true_top4_loss" if base["final_gold_page_hit"] else "true_top4_rescue"})

    cross_run = []
    expanded_index = {(row["mode"], row["qid"]): row for row in rows_by_source["p4_expanded_retrieval_combined"]}
    iso_raw = {(row["mode"], row["qid"]): row for row in read_csv(root / "results/per_question/p4_iso_v2corpus_78q.csv")}
    exp_raw = {(row["mode"], row["qid"]): row for row in read_csv(root / "results/per_question/p4_expanded_retrieval_combined.csv")}
    for mode in sorted({row["mode"] for row in rows_by_source["p4_iso_v2corpus_78q"]}):
        rows = [row for row in rows_by_source["p4_iso_v2corpus_78q"] if row["mode"] == mode]
        full_order_changed = sum(iso_raw[(mode, row["qid"])]["ranking_urls"] != exp_raw[(mode, row["qid"])]["ranking_urls"] for row in rows)
        rank_changed = sum(row["first_gold_chunk_rank"] != expanded_index[(mode, row["qid"])]["first_gold_chunk_rank"] for row in rows)
        first = lookup[("p4_iso_v2corpus_78q", "all", mode)]
        second = lookup[("p4_expanded_retrieval_combined", "original78", mode)]
        cross_run.append({"mode": mode, "n_common": len(rows), "changed_url_order": full_order_changed,
                          "changed_first_gold_rank": rank_changed, "iso78_discount": first["first_gold_discount_at_10"],
                          "expanded_original78_discount": second["first_gold_discount_at_10"],
                          "difference": second["first_gold_discount_at_10"] - first["first_gold_discount_at_10"]})

    judge_inventory = []
    for filename in ("p4_judge_answer_eval.csv", "p4_judge_relevance_eval.csv", "p4_judge_stability.csv"):
        path = root / "results/per_question" / filename
        rows = read_csv(path)
        judge_inventory.append({"file": filename, "rows": len(rows), "annotation_sources": sorted({r["annotation_source"] for r in rows}),
                                "human_claim_true_count": sum(r["valid_for_human_eval_claim"].lower() == "true" for r in rows)})
        input_paths.append(path)

    bootstrap = []
    for source in ("rag_results_experiments", "p4_expanded_retrieval_combined"):
        modes = ["rerank"] if source == "rag_results_experiments" else ["rerank", "rerank_bge_m3"]
        bootstrap.extend(paired_bootstrap(rows_by_source[source], source, modes, bootstrap_repeats))

    report = {
        "schema_version": 1, "kind": "offline_frozen_log_recomputation_not_model_rerun",
        "audit_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": {"retrieval_log_files": len(inventory), "query_system_rows": len(all_rows), "summary_rows": len(summaries),
                  "published_cells_checked": len(comparisons), "published_cell_failures": sum(not row["pass"] for row in comparisons),
                  "explained_historical_cell_failures": sum(row["explained_historical_query_join_bug"] for row in comparisons),
                  "unexpected_published_cell_failures": sum(not row["pass"] and not row["explained_historical_query_join_bug"] for row in comparisons),
                  "row_integrity_issues": len(issues)},
        "question_sets": {key: {"n": len(index), "gold_count_distribution": dict(Counter(len(gold_urls(q)) for q in index.values())),
                                 "distinct_gold_pages": len({url for q in index.values() for url in gold_urls(q)})} for key, index in questions.items()},
        "metric_contract": {
            "original_recall_at_k": "First gold URL at a chunk position <= k: a hit rate, not multi-gold recall.",
            "original_ndcg_at_10": "1/log2(1+first gold chunk rank), zero after 10; only first hit contributes; implicit IDCG=1.",
            "original_mrr": "Reciprocal first gold chunk rank in complete stored ranking (not MRR@10).",
            "final_gold_page_hit": "G: gold page in actual final_urls; no claim of content support or compliance with a prespecified source policy.",
            "distinct_page_metrics": "Stable unique URL order; binary relevance; IDCG from ALL frozen gold pages, including unretrieved ones. Ten pages and ten chunks are different budgets.",
            "url_matching": "Exact string after outer whitespace stripping, matching the frozen original scorer; no URL canonicalization.",
            "missing_annotation": "Hard error or flagged unmatched record; never treated as irrelevant.",
            "query_normalization": "Only named normalization log is joined by stable qid despite changed question text; tracked explicitly.",
        },
        "e0_findings": [
            {"id": "E0-NORMALIZED-JOIN", "status": "scoring_bug_identified", "detail": "Seven changed queries per mode fail the original (qid, question) annotation join and are scored zero. All released rewritten query texts are reproduced by generate_normalized_questions.py. Stable qid with validated rewrite recovers their original gold; see normalization_join_diagnosis.csv and corrected_normalization_metrics.csv."},
            {"id": "E0-LLM-RUNS", "status": "discrepancy_reproduced", "detail": "iso78 and original78 slice of exp155 are different frozen outputs; see cross_run_comparison.csv. Historical run IDs, API response IDs and timestamps are absent. Retain both with source file hashes; no repeated-run distribution can be inferred."},
            {"id": "E0-NODEDUP", "status": "configuration_explained", "detail": "ablation_no_dedup retains reranking; ablation_base_no_dedup removes cap without reranking. Compare their named configurations, not the generic NoDedup label."},
            {"id": "E0-RANK-CUTOFF", "status": "recomputed", "detail": "Full-list, top-10, and top-4 transition tables are provided separately. Both-missing is cutoff dependent; final hit equality can conceal offsetting losses and rescues."},
            {"id": "E0-POOL-DEPTH", "status": "configuration_explained", "detail": "Depth24 uses pool100, whereas pool24 reranks the post-cap pool from 24 retrieved chunks. The unreranked tail is appended by implementation. These are not the same setting."},
            {"id": "E0-CASE-STUDIES", "status": "corrected_cases_available", "detail": "Prior examples q58 (5->12) and q9 (8->12) are ranking degradations with no top-4 loss. true_top4_transitions.csv enumerates actual delivered gold-page losses/rescues."},
            {"id": "E0-LLM-NAMING", "status": "implementation_reviewed", "detail": "The LLM sees a candidate list and assigns each chunk a 0-2 score (500 characters each); stable sorting yields order. Describe as joint-context ordinal chunk scoring, not direct list permutation. temperature=0; request failures silently return all-zero scores in historical code."},
        ],
        "limitations": [
            "Only ranking/final URLs are in compact retrieval logs; no candidate IDs, chunk IDs, raw candidate URLs, final text, or raw model responses. Earlier-stage plots and content utility cannot be independently rebuilt from these logs.",
            "URL-level candidate equality cannot establish identical chunk-level candidate sets.",
            "Original and expanded questions use only designated NCI pages; the expansion includes original questions and source-conditioned construction, not independent external validation.",
            "All present evaluation labels are automatic. No human U, acceptable multi-source labels, clinical validation, or independent E1/E2 test is present.",
            "Four chunks is not a fixed tokenizer-measured token budget. Stored latency is historical wall time; hardware/model revision/API cost metadata are incomplete.",
            "Recorded configuration tables can omit modes present in merged logs. File hashes identify frozen artifacts, not historical model snapshots or a missing run manifest.",
            "Question and page-cluster bootstrap intervals are descriptive sensitivity analyses; few page groups and unadjusted multiple comparisons limit inferential claims.",
        ],
        "automatic_judge_inventory": judge_inventory,
        "normalization_historical_join_reproduction": summarize(normalization_zeroed, "supp_query_normalization_legacy_join"),
        "issues": issues,
    }
    outputs = {
        "recomputed_per_question.csv": all_rows, "recomputed_metrics.csv": summaries,
        "published_table_checks.csv": comparisons, "log_inventory.csv": inventory,
        "logged_configurations.csv": configs, "rank_transitions.csv": transitions,
        "true_top4_transitions.csv": cases, "cross_run_comparison.csv": cross_run,
        "paired_bootstrap_sensitivity.csv": bootstrap,
        "normalization_join_diagnosis.csv": normalization_rows,
        "corrected_normalization_metrics.csv": [row for row in summaries if row["source"] == "supp_query_normalization"],
        "corrected_supp_query_normalization_overall.csv": [
            {"mode": row["mode"], "num_questions": row["num_questions"],
             **{old: row[new] for old, new in OLD_COLUMNS.items() if old in ("recall_at_10", "mrr", "ndcg_at_10", "final_top_k_hit_rate")}}
            for row in summaries if row["source"] == "supp_query_normalization"
        ],
    }
    for filename, rows in outputs.items():
        write_csv(out / filename, rows)
    manifest = [{"path": str(path.relative_to(root)).replace("\\", "/"), "bytes": path.stat().st_size,
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(set(input_paths))]
    (out / "input_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "e0_audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["scope"], indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "validation/results")
    parser.add_argument("--bootstrap-repeats", type=int, default=5000)
    args = parser.parse_args()
    if args.bootstrap_repeats < 100:
        parser.error("bootstrap repeats must be at least 100")
    result = audit(args.root.resolve(), args.output.resolve(), args.bootstrap_repeats)
    # Historical tables stay frozen. Exactly reproduced join defects remain
    # visible in the report; unexpected differences and malformed logs fail.
    return int(bool(result["scope"]["unexpected_published_cell_failures"] or result["scope"]["row_integrity_issues"]))


if __name__ == "__main__":
    raise SystemExit(main())
