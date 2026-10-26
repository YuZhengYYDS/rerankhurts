import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import math
import os
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = Path(os.getenv("RESULT_DIR", str(BASE_DIR / "result")))
if not RESULT_DIR.is_absolute():
    RESULT_DIR = BASE_DIR / RESULT_DIR

# The audited 78-question set lives in the frozen bundle, not in the run directory.
_QUESTIONS_CANDIDATES = [
    RESULT_DIR / "paper_questions_validated.jsonl",
    BASE_DIR / "result" / "emnlp_full_results_20260427_gpu_final" / "paper_questions_validated.jsonl",
]
QUESTIONS_FILE = next((p for p in _QUESTIONS_CANDIDATES if p.exists()), _QUESTIONS_CANDIDATES[0])

STRONG_BASELINES_FILE = RESULT_DIR / "supp_strong_baselines_validated.csv"

# `paper_support_analysis.py` names its outputs after ANALYSIS_PREFIX. The
# revision driver runs it with the default prefix ("paper"), while the earlier
# round used this run's stem. Accept either rather than require the two scripts
# to be kept in sync by hand.
_STRONG_BASELINES_METRICS_CANDIDATES = [
    RESULT_DIR / "supp_strong_baselines_validated_metrics_full_vs_audited.csv",
    RESULT_DIR / "paper_metrics_full_vs_audited.csv",
]
STRONG_BASELINES_METRICS_FILE = next(
    (p for p in _STRONG_BASELINES_METRICS_CANDIDATES if p.exists()),
    _STRONG_BASELINES_METRICS_CANDIDATES[0],
)

POOL_PATTERN = "supp_pool_sweep_p[0-9][0-9].csv"
DEDUP_PATTERN = "supp_dedup_sweep_c*.csv"
DEPTH_PATTERN = "supp_rerank_depth_d*.csv"
FINALK_PATTERN = "supp_finalk_sweep_k*.csv"
SOURCE_PATTERN = "supp_source_ablation_*.csv"
STRONG_DENSE_PATTERN = "supp_strong_dense_*.csv"
STRONG_RERANKER_PATTERN = "supp_strong_reranker_*.csv"
BM25_GRID_PATTERN = "supp_bm25_grid_k*.csv"

OUTPUT_STRONG_BASELINES = RESULT_DIR / "supp_strong_baselines_validated_overall.csv"
OUTPUT_POOL_SUMMARY = RESULT_DIR / "supp_pool_sweep_summary.csv"
OUTPUT_DEDUP_SUMMARY = RESULT_DIR / "supp_dedup_sweep_summary.csv"
OUTPUT_DEPTH_SUMMARY = RESULT_DIR / "supp_rerank_depth_summary.csv"
OUTPUT_FINALK_SUMMARY = RESULT_DIR / "supp_finalk_sweep_summary.csv"
OUTPUT_SOURCE_SUMMARY = RESULT_DIR / "supp_source_ablation_summary.csv"
OUTPUT_MODEL_UPGRADE_SUMMARY = RESULT_DIR / "supp_model_upgrade_summary.csv"
OUTPUT_BM25_GRID_SUMMARY = RESULT_DIR / "supp_bm25_grid_summary.csv"
OUTPUT_BM25_GRID_BEST = RESULT_DIR / "supp_bm25_grid_best.csv"

QUERY_NORMALIZATION_FILE = RESULT_DIR / "supp_query_normalization.csv"
OUTPUT_QUERY_NORMALIZATION = RESULT_DIR / "supp_query_normalization_overall.csv"


def load_jsonl(path: Path) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def split_urls(urls_text) -> List[str]:
    if pd.isna(urls_text):
        return []
    return [part.strip() for part in str(urls_text).split("|") if part.strip()]


def normalize_gold_urls(value, fallback_gold_url) -> List[str]:
    if isinstance(value, list):
        gold_urls = [str(item).strip() for item in value if str(item).strip()]
    elif pd.isna(value):
        gold_urls = []
    else:
        try:
            parsed = json.loads(value) if isinstance(value, str) else value
            if isinstance(parsed, list):
                gold_urls = [str(item).strip() for item in parsed if str(item).strip()]
            else:
                gold_urls = []
        except Exception:
            gold_urls = []

    if not gold_urls and pd.notna(fallback_gold_url) and str(fallback_gold_url).strip():
        gold_urls = [str(fallback_gold_url).strip()]
    return gold_urls


def choose_ranking_urls(row) -> str:
    if pd.notna(row.get("ranking_urls")) and str(row.get("ranking_urls")).strip():
        return str(row.get("ranking_urls"))

    mode = str(row.get("mode", "")).strip().lower()
    if mode == "baseline":
        candidates = ["deduped_urls", "final_urls", "retrieved_urls"]
    else:
        candidates = ["final_urls", "reranked_urls", "deduped_urls", "retrieved_urls", "ranking_urls"]

    for col in candidates:
        value = row.get(col)
        if pd.notna(value) and str(value).strip():
            return str(value)
    return ""


def get_rank_of_gold(url_list: Iterable[str], gold_urls: Iterable[str]) -> Optional[int]:
    gold_set = set(gold_urls)
    if not gold_set:
        return None
    for idx, url in enumerate(url_list, start=1):
        if url in gold_set:
            return idx
    return None


def recall_at_k(rank: Optional[int], k: int) -> float:
    if rank is None or pd.isna(rank):
        return 0.0
    return 1.0 if rank <= k else 0.0


def reciprocal_rank(rank: Optional[int]) -> float:
    if rank is None or pd.isna(rank):
        return 0.0
    return 1.0 / float(rank)


def ndcg_at_k(rank: Optional[int], k: int) -> float:
    if rank is None or pd.isna(rank) or rank > k:
        return 0.0
    return 1.0 / math.log2(rank + 1)


def prepare_results(df: pd.DataFrame, questions_df: pd.DataFrame) -> pd.DataFrame:
    # Query normalization changes text while preserving the information need's
    # stable ID. A text join silently discarded its gold labels and scored the
    # resulting missing annotation as a retrieval failure.
    from legacy.generate_normalized_questions import rewrite_question

    if questions_df["qid"].duplicated().any():
        raise ValueError("Question IDs must be unique in the annotation file")
    labels = questions_df[[col for col in ["qid", "question", "topic", "gold_url", "gold_urls"] if col in questions_df.columns]].rename(columns={"question": "reference_question"})
    merged = df.merge(
        labels,
        on="qid",
        how="left",
        validate="many_to_one",
        indicator=True,
        suffixes=("_run", ""),
    )
    if (merged["_merge"] != "both").any():
        raise ValueError("Run contains question IDs without reference annotations")
    valid_text = merged.apply(
        lambda row: str(row["question"]) in {
            str(row["reference_question"]), rewrite_question(str(row["reference_question"]))[0]
        }, axis=1,
    )
    if not valid_text.all():
        raise ValueError("Question ID reused for an unrecognized query rewrite")
    merged = merged.drop(columns=["_merge"])
    merged["ranking_urls_eval"] = merged.apply(choose_ranking_urls, axis=1)
    merged["gold_urls_norm"] = merged.apply(
        lambda row: normalize_gold_urls(row.get("gold_urls"), row.get("gold_url")),
        axis=1,
    )
    if merged["gold_urls_norm"].map(len).eq(0).any():
        raise ValueError("Missing gold annotations must not be scored as retrieval failures")
    merged["gold_rank"] = merged.apply(
        lambda row: get_rank_of_gold(split_urls(row["ranking_urls_eval"]), row["gold_urls_norm"]),
        axis=1,
    )
    merged["final_gold_hit"] = merged.apply(
        lambda row: 1.0 if get_rank_of_gold(split_urls(row.get("final_urls", "")), row["gold_urls_norm"]) is not None else 0.0,
        axis=1,
    )
    merged["recall_at_10"] = merged["gold_rank"].map(lambda rank: recall_at_k(rank, 10))
    merged["mrr"] = merged["gold_rank"].map(reciprocal_rank)
    merged["ndcg_at_10"] = merged["gold_rank"].map(lambda rank: ndcg_at_k(rank, 10))
    return merged


def is_result_frame(df: pd.DataFrame) -> bool:
    required = {"qid", "question", "mode"}
    return required.issubset(df.columns)


def summarize_group(df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
    summary = df.groupby(group_cols, as_index=False).agg(
        num_questions=("qid", "count"),
        recall_at_10=("recall_at_10", "mean"),
        mrr=("mrr", "mean"),
        ndcg_at_10=("ndcg_at_10", "mean"),
        final_top_k_hit_rate=("final_gold_hit", "mean"),
    )
    return summary


def collapse_duplicates(df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
    metric_cols = [col for col in df.columns if col not in group_cols]
    agg_map = {
        col: "mean" if pd.api.types.is_numeric_dtype(df[col]) else "first"
        for col in metric_cols
    }
    return df.groupby(group_cols, as_index=False).agg(agg_map)


def build_strong_baselines_summary(metrics_file: Optional[Path] = None, output: Optional[Path] = None) -> None:
    metrics_file = metrics_file or STRONG_BASELINES_METRICS_FILE
    output = output or OUTPUT_STRONG_BASELINES
    metrics_df = pd.read_csv(metrics_file)
    audited = metrics_df[metrics_df["subset"] == "audited"].copy()
    cols = [
        "mode",
        "num_questions",
        "recall_at_10",
        "mrr",
        "ndcg_at_10",
        "gold_url_hit_rate",
    ]
    audited[cols].to_csv(output, index=False, encoding="utf-8-sig")


def _parse_bm25_grid_stem(stem: str) -> Optional[Dict[str, float]]:
    """Parse `supp_bm25_grid_k<k1>_b<b>` where digits encode k1 and b."""
    import re
    m = re.search(r"supp_bm25_grid_k(\d+)b(\d+)$", stem)
    if not m:
        return None
    k1_digits, b_digits = m.group(1), m.group(2)
    k1 = int(k1_digits) / (10 ** (len(k1_digits) - 1))
    b = int(b_digits) / (10 ** (len(b_digits) - 1))
    return {"bm25_k1": k1, "bm25_b": b}


def build_bm25_grid_summary(questions_df: pd.DataFrame) -> None:
    frames = []
    for path in sorted(RESULT_DIR.glob(BM25_GRID_PATTERN)):
        if any(marker in path.stem for marker in ["summary", "settings", "best"]):
            continue
        parsed = _parse_bm25_grid_stem(path.stem)
        if parsed is None:
            continue
        df = pd.read_csv(path)
        if not is_result_frame(df):
            continue
        prepared = prepare_results(df, questions_df)
        prepared["bm25_k1"] = parsed["bm25_k1"]
        prepared["bm25_b"] = parsed["bm25_b"]
        summary = summarize_group(prepared, ["mode", "bm25_k1", "bm25_b"])
        frames.append(summary)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined = collapse_duplicates(combined, ["mode", "bm25_k1", "bm25_b"])
        combined = combined.sort_values(["bm25_k1", "bm25_b"])
        combined.to_csv(OUTPUT_BM25_GRID_SUMMARY, index=False, encoding="utf-8-sig")
        best = combined.sort_values("ndcg_at_10", ascending=False).head(1)
        best.to_csv(OUTPUT_BM25_GRID_BEST, index=False, encoding="utf-8-sig")


def build_query_normalization_summary(questions_df: pd.DataFrame) -> None:
    """Overall metrics for the re-run on normalized question wording.

    This sweep had no summary step before, so the appendix's normalization table
    had nothing current to cite; it is built exactly like the main validated
    summary so the two are directly comparable.
    """
    if not QUERY_NORMALIZATION_FILE.exists():
        print(f"!! {QUERY_NORMALIZATION_FILE.name} not found; skipping query normalization")
        return
    df = pd.read_csv(QUERY_NORMALIZATION_FILE)
    if not is_result_frame(df):
        print(f"!! {QUERY_NORMALIZATION_FILE.name} is not a per-question result frame; skipping")
        return
    prepared = prepare_results(df, questions_df)
    summary = summarize_group(prepared, ["mode"])
    summary.to_csv(OUTPUT_QUERY_NORMALIZATION, index=False, encoding="utf-8-sig")


def build_pool_summary(questions_df: pd.DataFrame) -> None:
    frames = []
    for path in sorted(RESULT_DIR.glob(POOL_PATTERN)):
        df = pd.read_csv(path)
        if not is_result_frame(df):
            continue
        prepared = prepare_results(df, questions_df)
        summary = summarize_group(prepared, ["mode", "retrieve_pool_size"])
        summary.rename(columns={"retrieve_pool_size": "pool_size"}, inplace=True)
        frames.append(summary)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined = collapse_duplicates(combined, ["mode", "pool_size"])
        combined = combined.sort_values(["mode", "pool_size"])
        combined.to_csv(OUTPUT_POOL_SUMMARY, index=False, encoding="utf-8-sig")


def build_dedup_summary(questions_df: pd.DataFrame) -> None:
    frames = []
    for path in sorted(RESULT_DIR.glob(DEDUP_PATTERN)):
        df = pd.read_csv(path)
        if not is_result_frame(df):
            continue
        prepared = prepare_results(df, questions_df)
        prepared["dedup_cap_group"] = prepared.apply(
            lambda row: "inf"
            if not bool(row.get("use_dedup"))
            else ("" if pd.isna(row.get("max_chunks_per_url")) else str(int(row["max_chunks_per_url"]))),
            axis=1,
        )
        summary = summarize_group(prepared, ["mode", "dedup_cap_group", "use_dedup"])
        summary.rename(columns={"dedup_cap_group": "dedup_cap"}, inplace=True)
        summary["max_chunks_per_url"] = pd.to_numeric(summary["dedup_cap"], errors="coerce")
        summary["mode_family"] = summary["mode"].map({
            "baseline": "baseline",
            "ablation_base_no_dedup": "baseline",
            "rerank": "rerank",
            "ablation_no_dedup": "rerank",
        }).fillna(summary["mode"])
        frames.append(summary)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined["dedup_cap_sort"] = combined["dedup_cap"].map({"1": 1, "2": 2, "3": 3, "inf": 999})
        combined = collapse_duplicates(combined, ["mode", "dedup_cap"])
        combined["dedup_cap_sort"] = combined["dedup_cap"].map({"1": 1, "2": 2, "3": 3, "inf": 999})
        combined = combined.sort_values(["mode_family", "dedup_cap_sort", "mode"]).drop(columns=["dedup_cap_sort"])
        combined.to_csv(OUTPUT_DEDUP_SUMMARY, index=False, encoding="utf-8-sig")


def build_depth_summary(questions_df: pd.DataFrame) -> None:
    frames = []
    for path in sorted(RESULT_DIR.glob(DEPTH_PATTERN)):
        df = pd.read_csv(path)
        if not is_result_frame(df):
            continue
        prepared = prepare_results(df, questions_df)
        summary = summarize_group(prepared, ["mode", "rerank_depth", "retrieve_pool_size"])
        summary.rename(columns={"rerank_depth": "depth", "retrieve_pool_size": "pool_size"}, inplace=True)
        frames.append(summary)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined = collapse_duplicates(combined, ["mode", "depth", "pool_size"])
        combined = combined.sort_values(["mode", "depth"])
        combined.to_csv(OUTPUT_DEPTH_SUMMARY, index=False, encoding="utf-8-sig")


def build_finalk_summary(questions_df: pd.DataFrame) -> None:
    frames = []
    for path in sorted(RESULT_DIR.glob(FINALK_PATTERN)):
        df = pd.read_csv(path)
        if not is_result_frame(df):
            continue
        prepared = prepare_results(df, questions_df)
        summary = summarize_group(prepared, ["mode", "final_top_k", "retrieve_pool_size"])
        summary.rename(columns={"final_top_k": "final_k", "retrieve_pool_size": "pool_size"}, inplace=True)
        frames.append(summary)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined = collapse_duplicates(combined, ["mode", "final_k", "pool_size"])
        combined = combined.sort_values(["mode", "final_k"])
        combined.to_csv(OUTPUT_FINALK_SUMMARY, index=False, encoding="utf-8-sig")


def build_source_summary(questions_df: pd.DataFrame) -> None:
    frames = []
    for path in sorted(RESULT_DIR.glob(SOURCE_PATTERN)):
        if "summary" in path.stem:
            continue
        df = pd.read_csv(path)
        if not is_result_frame(df):
            continue
        prepared = prepare_results(df, questions_df)
        group_cols = ["mode", "corpus_source_preset"]
        if "corpus_chunk_count" in prepared.columns:
            group_cols.append("corpus_chunk_count")
        summary = summarize_group(prepared, group_cols)
        frames.append(summary)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        group_cols = ["mode", "corpus_source_preset"]
        if "corpus_chunk_count" in combined.columns:
            group_cols.append("corpus_chunk_count")
        combined = collapse_duplicates(combined, group_cols)
        combined = combined.sort_values(["mode", "corpus_source_preset"])
        combined.to_csv(OUTPUT_SOURCE_SUMMARY, index=False, encoding="utf-8-sig")


def build_model_upgrade_summary(questions_df: pd.DataFrame) -> None:
    frames = []
    for pattern in [STRONG_DENSE_PATTERN, STRONG_RERANKER_PATTERN]:
        for path in sorted(RESULT_DIR.glob(pattern)):
            stem = path.stem
            if any(marker in stem for marker in ["summary", "settings", "metrics", "audit", "questions", "pairwise", "stage", "rank_transition", "case_studies"]):
                continue
            if stem.endswith("_baseline") or stem.endswith("_rerank"):
                continue
            df = pd.read_csv(path)
            if not is_result_frame(df):
                continue
            prepared = prepare_results(df, questions_df)
            prepared["rerank_depth"] = prepared["rerank_depth"].fillna(0)
            prepared["rerank_model_name"] = prepared["rerank_model_name"].fillna("")
            prepared.loc[prepared["rerank_model_name"] == "", "rerank_depth"] = 0
            group_cols = [
                "mode",
                "embed_model_name",
                "rerank_model_name",
                "corpus_source_preset",
                "rerank_depth",
            ]
            summary = summarize_group(prepared, group_cols)
            frames.append(summary)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined = collapse_duplicates(
            combined,
            ["mode", "embed_model_name", "rerank_model_name", "corpus_source_preset", "rerank_depth"],
        )
        combined = combined.sort_values(["embed_model_name", "rerank_model_name", "mode", "rerank_depth"])
        combined.to_csv(OUTPUT_MODEL_UPGRADE_SUMMARY, index=False, encoding="utf-8-sig")


def main() -> None:
    questions_df = load_jsonl(QUESTIONS_FILE)
    build_strong_baselines_summary()
    build_pool_summary(questions_df)
    build_dedup_summary(questions_df)
    build_depth_summary(questions_df)
    build_finalk_summary(questions_df)
    build_source_summary(questions_df)
    build_model_upgrade_summary(questions_df)
    build_bm25_grid_summary(questions_df)
    build_query_normalization_summary(questions_df)
    print(f"Saved: {OUTPUT_STRONG_BASELINES}")
    print(f"Saved: {OUTPUT_POOL_SUMMARY}")
    print(f"Saved: {OUTPUT_DEDUP_SUMMARY}")
    print(f"Saved: {OUTPUT_DEPTH_SUMMARY}")
    print(f"Saved: {OUTPUT_FINALK_SUMMARY}")
    print(f"Saved: {OUTPUT_SOURCE_SUMMARY}")
    print(f"Saved: {OUTPUT_MODEL_UPGRADE_SUMMARY}")
    print(f"Saved: {OUTPUT_BM25_GRID_SUMMARY}")
    print(f"Saved: {OUTPUT_BM25_GRID_BEST}")
    if OUTPUT_QUERY_NORMALIZATION.exists():
        print(f"Saved: {OUTPUT_QUERY_NORMALIZATION}")


if __name__ == "__main__":
    main()
