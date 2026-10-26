import json
import math
import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = Path(os.getenv("RESULT_DIR", str(BASE_DIR / "result")))
if not RESULT_DIR.is_absolute():
    RESULT_DIR = BASE_DIR / RESULT_DIR
RESULT_DIR.mkdir(parents=True, exist_ok=True)


def resolve_path(raw_value: Optional[str], default: Path) -> Path:
    if not raw_value:
        return default
    candidate = Path(raw_value)
    return candidate if candidate.is_absolute() else BASE_DIR / candidate


QUESTIONS_FILE = resolve_path(os.getenv("QUESTIONS_FILE"), BASE_DIR / "questions.jsonl")
# Set when QUESTIONS_FILE is already the validated set (see audit_questions).
ASSUME_VALIDATED = os.getenv("ASSUME_VALIDATED", "0").strip().lower() in {"1", "true", "yes"}
RESULTS_FILE = resolve_path(os.getenv("RESULTS_FILE"), RESULT_DIR / "rag_results_experiments.csv")
# The audit-split table needs the *whole* 100-question pool, but RESULTS_FILE holds
# only the 78 validated questions. Without this second source "full" and "audited"
# both describe the same 78 rows and the held-out row comes out empty.
FULL_POOL_RESULTS_FILE = resolve_path(
    os.getenv("FULL_POOL_RESULTS_FILE"), RESULT_DIR / "supp_strong_baselines_full100.csv")
OUTPUT_PREFIX = os.getenv("ANALYSIS_PREFIX", "paper").strip() or "paper"

AUDIT_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_question_audit.csv"
AUDIT_SUMMARY_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_audit_summary.csv"
VALIDATED_QUESTIONS_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_questions_validated.jsonl"
GENERAL_QUESTIONS_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_questions_general_heldout.jsonl"
METRICS_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_metrics_full_vs_audited.csv"
SUBSET_METRICS_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_metrics_by_subset.csv"
TOPIC_METRICS_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_metrics_by_topic_audited.csv"
PAIRWISE_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_pairwise_vs_baseline.csv"
CASE_STUDY_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_case_studies.csv"
STAGE_RETENTION_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_stage_gold_retention.csv"
RANK_TRANSITION_FILE = RESULT_DIR / f"{OUTPUT_PREFIX}_rank_transition_vs_baseline.csv"

FIG_FULL_VS_AUDITED = RESULT_DIR / f"fig_{OUTPUT_PREFIX}_full_vs_audited.png"
FIG_RANK_CDF = RESULT_DIR / f"fig_{OUTPUT_PREFIX}_rank_cdf.png"
FIG_EFFECTS = RESULT_DIR / f"fig_{OUTPUT_PREFIX}_vs_baseline_effects.png"
FIG_AUDIT_BREAKDOWN = RESULT_DIR / f"fig_{OUTPUT_PREFIX}_audit_breakdown.png"
FIG_STAGE_RETENTION = RESULT_DIR / f"fig_{OUTPUT_PREFIX}_stage_retention.png"
FIG_RANK_TRANSITION = RESULT_DIR / f"fig_{OUTPUT_PREFIX}_rank_transition.png"

RNG_SEED = 42
BOOTSTRAP_ROUNDS = 5000

TOPIC_URLS = {
    "NSCLC": "https://www.cancer.gov/types/lung/hp/non-small-cell-lung-treatment-pdq",
    "SCLC": "https://www.cancer.gov/types/lung/hp/small-cell-lung-treatment-pdq",
    "Breast": "https://www.cancer.gov/types/breast/hp/breast-treatment-pdq",
    "Colon": "https://www.cancer.gov/types/colorectal/hp/colon-treatment-pdq",
    "AML": "https://www.cancer.gov/types/leukemia/hp/adult-aml-treatment-pdq",
    "CLL": "https://www.cancer.gov/types/leukemia/hp/cll-treatment-pdq",
    "General": "https://www.cancer.gov/publications/pdq/information-summaries/genetics",
}

TOPIC_PATTERNS = [
    ("NSCLC", [
        r"non-small cell lung cancer",
        r"\bnsclc\b",
        r"\begfr\b",
        r"\balk\b",
        r"pd-l1",
    ]),
    ("SCLC", [
        r"small cell lung cancer",
        r"\bsclc\b",
    ]),
    ("Breast", [
        r"breast cancer",
        r"\bher2\b",
        r"triple-negative",
        r"hormone receptor-positive",
        r"endocrine therapy",
    ]),
    ("Colon", [
        r"colon cancer",
        r"colorectal",
    ]),
    ("AML", [
        r"acute myeloid leukemia",
        r"\baml\b",
    ]),
    ("CLL", [
        r"chronic lymphocytic leukemia",
        r"\bcll\b",
    ]),
]

MODE_ORDER = [
    "control_dense_only",
    "control_sparse_only",
    "control_hybrid",
    "bm25_only",
    "bm25_base",
    "hybrid_bm25",
    "rrf_hybrid",
    "rrf_hybrid_rerank",
    "baseline",
    "rerank",
    # Re-rankers added for the revision comparison. Without these entries the
    # pairwise/bootstrap tables silently omit them, which would drop exactly the
    # results that answer the reviewers' "only generic lightweight re-rankers
    # were tested" objection.
    "rerank_bge_base",
    "rerank_bge_m3",
    "rerank_medcpt",
    "rerank_llm",
    "ablation_base_no_dedup",
    "ablation_base_small_pool",
    "ablation_no_dedup",
    "ablation_small_pool",
    "hybrid_rerank",
]

MODE_LABELS = {
    "control_dense_only": "Dense",
    "control_sparse_only": "Sparse",
    "control_hybrid": "Hybrid",
    "bm25_only": "BM25",
    "bm25_base": "BM25+Dedup",
    "hybrid_bm25": "Hybrid-BM25",
    "rrf_hybrid": "RRF",
    "rrf_hybrid_rerank": "RRF+RR",
    "baseline": "Base",
    "rerank": "Rerank",
    "rerank_bge_base": "Rerank-bge-base",
    "rerank_bge_m3": "Rerank-bge-m3",
    "rerank_medcpt": "Rerank-MedCPT",
    "rerank_llm": "Rerank-LLM",
    "ablation_base_no_dedup": "Base-NoDedup",
    "ablation_base_small_pool": "Base-SmallPool",
    "ablation_no_dedup": "NoDedup",
    "ablation_small_pool": "SmallPool",
    "hybrid_rerank": "Hyb+RR",
}

PALETTE = {
    "control_dense_only": "#4C78A8",
    "control_sparse_only": "#F58518",
    "control_hybrid": "#54A24B",
    "bm25_only": "#7A5195",
    "bm25_base": "#955196",
    "hybrid_bm25": "#2F4B7C",
    "rrf_hybrid": "#EF5675",
    "rrf_hybrid_rerank": "#BC5090",
    "baseline": "#E45756",
    "rerank": "#72B7B2",
    "ablation_base_no_dedup": "#8C6D31",
    "ablation_base_small_pool": "#B07AA1",
    "ablation_no_dedup": "#B279A2",
    "ablation_small_pool": "#FF9DA6",
    "hybrid_rerank": "#9D755D",
}


def normalize_question(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def infer_topic(question: str) -> str:
    text = str(question).strip().lower()
    matched_topics = [
        topic
        for topic, patterns in TOPIC_PATTERNS
        if any(re.search(pattern, text) for pattern in patterns)
    ]
    if len(matched_topics) == 1:
        return matched_topics[0]
    if not matched_topics:
        return "General"
    return matched_topics[0]


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


def split_urls(urls_text) -> List[str]:
    if pd.isna(urls_text):
        return []
    return [part.strip() for part in str(urls_text).split("|") if part.strip()]


def choose_ranking_urls(row) -> str:
    if pd.notna(row.get("ranking_urls")) and str(row.get("ranking_urls")).strip():
        return str(row.get("ranking_urls"))

    mode = str(row.get("mode", "")).strip().lower()
    if mode == "baseline":
        candidates = ["deduped_urls", "final_urls", "retrieved_urls"]
    else:
        candidates = ["final_urls", "reranked_urls", "deduped_urls", "retrieved_urls"]

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


def has_gold_in_urls(urls_text, gold_urls: Iterable[str]) -> float:
    return 1.0 if get_rank_of_gold(split_urls(urls_text), gold_urls) is not None else 0.0


def reciprocal_rank(rank: Optional[int]) -> float:
    if rank is None or pd.isna(rank):
        return 0.0
    return 1.0 / float(rank)


def ndcg_at_k(rank: Optional[int], k: int) -> float:
    if rank is None or pd.isna(rank) or rank > k:
        return 0.0
    return 1.0 / math.log2(rank + 1)


def recall_at_k(rank: Optional[int], k: int) -> float:
    if rank is None or pd.isna(rank):
        return 0.0
    return 1.0 if rank <= k else 0.0


def normalize_bool(value) -> Optional[bool]:
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def answer_length(text) -> int:
    if pd.isna(text):
        return 0
    return len(str(text).split())


def topic_sort_key(topic: str) -> int:
    order = ["NSCLC", "SCLC", "Breast", "Colon", "AML", "CLL", "General"]
    return order.index(topic) if topic in order else 999


def mode_sort_key(mode: str) -> int:
    return MODE_ORDER.index(mode) if mode in MODE_ORDER else 999


def truncate_text(text, limit: int = 320) -> str:
    if pd.isna(text):
        return ""
    clean = " ".join(str(text).split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3] + "..."


def load_questions(path: Path) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def audit_questions(df: pd.DataFrame) -> pd.DataFrame:
    audited = df.copy()
    if ASSUME_VALIDATED:
        # The caller passed a question file that is already the validated set
        # (e.g. the expanded benchmark, whose items were admitted by the
        # answerability screen). Re-deriving the rule-based audit here would be
        # wrong twice over: TOPIC_PATTERNS only covers the original six cancer
        # types, so every question on a new topic would be dropped as a topic
        # mismatch, silently shrinking the analysis back to the old subset.
        # The audit-summary columns are still read downstream, so define them
        # rather than leave them missing: nothing here is held out or duplicated
        # because the caller already applied those filters.
        audited["normalized_question"] = audited["question"].map(normalize_question)
        audited["qid_num"] = audited["qid"].str.replace("q", "", regex=False).astype(int)
        # Topic checks are vacuous here: the question's own topic label is the
        # ground truth and TOPIC_PATTERNS does not cover the newer cancer types.
        audited["inferred_topic"] = audited["topic"].astype(str)
        audited["topic_matches_inferred"] = True
        audited["topic_mismatch"] = False
        audited["expected_gold_url"] = audited.apply(
            lambda r: r.get("gold_url") or (r.get("gold_urls") or [None])[0], axis=1)
        audited["duplicate_keep"] = True
        audited["is_general_topic"] = False
        audited["is_duplicate_extra"] = False
        audited["general_with_specific_terms"] = False
        audited["has_duplicate_group"] = False
        audited["use_for_audited_eval"] = True
        audited["audit_status"] = "validated"
        return audited
    if "gold_urls" not in audited.columns:
        audited["gold_urls"] = None
    audited["normalized_question"] = audited["question"].map(normalize_question)
    audited["qid_num"] = audited["qid"].str.replace("q", "", regex=False).astype(int)
    audited["inferred_topic"] = audited["question"].map(infer_topic)
    audited["topic_matches_inferred"] = audited["topic"].astype(str) == audited["inferred_topic"].astype(str)
    audited["is_general_topic"] = audited["topic"].astype(str) == "General"
    audited["expected_gold_url"] = audited["inferred_topic"].map(TOPIC_URLS)

    keep_flags = []
    for _, group in audited.groupby("normalized_question", sort=False):
        ordered = group.sort_values(
            by=["topic_matches_inferred", "is_general_topic", "qid_num"],
            ascending=[False, True, True],
        )
        keep_qid = ordered.iloc[0]["qid"]
        keep_flags.extend(
            {"qid": row["qid"], "duplicate_keep": row["qid"] == keep_qid}
            for _, row in group.iterrows()
        )

    keep_df = pd.DataFrame(keep_flags)
    audited = audited.merge(keep_df, on="qid", how="left")
    duplicate_counts = audited.groupby("normalized_question")["qid"].transform("count")
    audited["has_duplicate_group"] = duplicate_counts > 1
    audited["is_duplicate_extra"] = audited["has_duplicate_group"] & (~audited["duplicate_keep"])
    audited["topic_mismatch"] = audited["topic"].astype(str) != audited["inferred_topic"].astype(str)
    audited["general_with_specific_terms"] = audited["is_general_topic"] & (
        audited["inferred_topic"].astype(str) != "General"
    )
    audited["use_for_audited_eval"] = (
        audited["duplicate_keep"]
        & (~audited["topic_mismatch"])
        & (~audited["is_general_topic"])
    )

    audited["audit_status"] = np.where(
        audited["use_for_audited_eval"],
        "validated",
        np.where(
            audited["is_duplicate_extra"],
            "duplicate_extra",
            np.where(audited["is_general_topic"], "general_held_out", "topic_mismatch"),
        ),
    )

    audited = audited.sort_values("qid_num").reset_index(drop=True)
    return audited


def save_question_subset(audited_questions: pd.DataFrame, mask: pd.Series,
                         output_path: Path) -> int:
    """Write one question subset; clear it and report zero when there is none.

    An empty subset used to leave a zero-byte file behind while the run still
    reported the file as saved, which reads the same as a step that failed
    halfway through. Worse, if an earlier round had left a non-empty file at
    that path, this round's empty subset simply overwrote it with nothing --
    or, on a rerun that did not reach this code, left the older file in place to
    be read as current. So an empty subset removes the file rather than
    truncating it, and the count is returned for the caller to report.
    """
    subset = audited_questions[mask].copy()
    keep_columns = [col for col in audited_questions.columns if col in {"qid", "question", "topic", "gold_url", "gold_urls"}]
    if subset.empty:
        output_path.unlink(missing_ok=True)
        return 0
    with open(output_path, "w", encoding="utf-8") as f:
        for _, row in subset[keep_columns].iterrows():
            payload = {col: row[col] for col in keep_columns if pd.notna(row[col])}
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return len(subset)


def load_results(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def prepare_results(results_df: pd.DataFrame, audited_questions: pd.DataFrame) -> pd.DataFrame:
    if "gold_urls" not in audited_questions.columns:
        audited_questions = audited_questions.copy()
        audited_questions["gold_urls"] = None

    merged = results_df.merge(
        audited_questions[
            [
                "qid",
                "question",
                "topic",
                "gold_url",
                "gold_urls",
                "inferred_topic",
                "expected_gold_url",
                "has_duplicate_group",
                "duplicate_keep",
                "is_duplicate_extra",
                "topic_mismatch",
                "is_general_topic",
                "general_with_specific_terms",
                "use_for_audited_eval",
                "audit_status",
            ]
        ],
        on=["qid", "question"],
        how="left",
    )

    merged["ranking_urls_eval"] = merged.apply(choose_ranking_urls, axis=1)
    merged["gold_urls_norm"] = merged.apply(
        lambda row: normalize_gold_urls(row.get("gold_urls"), row.get("gold_url")),
        axis=1,
    )
    merged["ranking_url_list"] = merged["ranking_urls_eval"].map(split_urls)
    merged["final_url_list"] = merged["final_urls"].map(split_urls)
    merged["gold_rank"] = merged.apply(
        lambda row: get_rank_of_gold(row["ranking_url_list"], row["gold_urls_norm"]),
        axis=1,
    )
    merged["gold_url_hit"] = merged.apply(
        lambda row: 1.0 if get_rank_of_gold(row["final_url_list"], row["gold_urls_norm"]) is not None else 0.0,
        axis=1,
    )
    merged["recall_at_5"] = merged["gold_rank"].map(lambda value: recall_at_k(value, 5))
    merged["recall_at_10"] = merged["gold_rank"].map(lambda value: recall_at_k(value, 10))
    merged["mrr"] = merged["gold_rank"].map(reciprocal_rank)
    merged["ndcg_at_10"] = merged["gold_rank"].map(lambda value: ndcg_at_k(value, 10))
    merged["insufficient_evidence_bool"] = merged["insufficient_evidence"].map(normalize_bool)
    merged["insufficient_evidence_num"] = merged["insufficient_evidence_bool"].map(
        lambda value: np.nan if value is None else float(value)
    )
    merged["answer_word_count"] = merged["answer"].map(answer_length)
    return merged


def summarize_metrics(df: pd.DataFrame, subset_name: str) -> pd.DataFrame:
    summary = df.groupby("mode", as_index=False).agg(
        num_questions=("qid", "count"),
        recall_at_5=("recall_at_5", "mean"),
        recall_at_10=("recall_at_10", "mean"),
        mrr=("mrr", "mean"),
        ndcg_at_10=("ndcg_at_10", "mean"),
        gold_url_hit_rate=("gold_url_hit", "mean"),
        insufficient_evidence_rate=("insufficient_evidence_num", "mean"),
        avg_answer_word_count=("answer_word_count", "mean"),
    )
    summary["subset"] = subset_name
    ordered_cols = [
        "subset",
        "mode",
        "num_questions",
        "recall_at_5",
        "recall_at_10",
        "mrr",
        "ndcg_at_10",
        "gold_url_hit_rate",
        "insufficient_evidence_rate",
        "avg_answer_word_count",
    ]
    summary = summary[ordered_cols]
    return summary.sort_values("mode", key=lambda col: col.map(mode_sort_key)).reset_index(drop=True)


def summarize_topic_metrics(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby(["topic", "mode"], as_index=False).agg(
        num_questions=("qid", "count"),
        recall_at_5=("recall_at_5", "mean"),
        recall_at_10=("recall_at_10", "mean"),
        mrr=("mrr", "mean"),
        ndcg_at_10=("ndcg_at_10", "mean"),
        gold_url_hit_rate=("gold_url_hit", "mean"),
        insufficient_evidence_rate=("insufficient_evidence_num", "mean"),
        avg_answer_word_count=("answer_word_count", "mean"),
    )
    return summary.sort_values(
        by=["topic", "mode"],
        key=lambda col: col.map(topic_sort_key) if col.name == "topic" else col.map(mode_sort_key),
    ).reset_index(drop=True)


def build_stage_retention_table(df: pd.DataFrame) -> pd.DataFrame:
    subset = df.copy()
    subset["gold_in_retrieved"] = subset.apply(
        lambda row: has_gold_in_urls(row.get("retrieved_urls", ""), row["gold_urls_norm"]),
        axis=1,
    )
    subset["gold_in_deduped"] = subset.apply(
        lambda row: has_gold_in_urls(row.get("deduped_urls", ""), row["gold_urls_norm"]),
        axis=1,
    )
    subset["gold_in_ranked"] = subset.apply(
        lambda row: has_gold_in_urls(row.get("ranking_urls_eval", ""), row["gold_urls_norm"]),
        axis=1,
    )
    subset["gold_in_final"] = subset.apply(
        lambda row: has_gold_in_urls(row.get("final_urls", ""), row["gold_urls_norm"]),
        axis=1,
    )

    table = subset.groupby("mode", as_index=False).agg(
        num_questions=("qid", "count"),
        retrieved_stage_hit_rate=("gold_in_retrieved", "mean"),
        dedup_stage_hit_rate=("gold_in_deduped", "mean"),
        ranked_stage_hit_rate=("gold_in_ranked", "mean"),
        final_stage_hit_rate=("gold_in_final", "mean"),
    )
    return table.sort_values("mode", key=lambda col: col.map(mode_sort_key)).reset_index(drop=True)


def classify_rank_transition(base_rank: Optional[int], candidate_rank: Optional[int]) -> str:
    base_missing = base_rank is None or pd.isna(base_rank)
    candidate_missing = candidate_rank is None or pd.isna(candidate_rank)

    if base_missing and candidate_missing:
        return "both_missing"
    if base_missing and not candidate_missing:
        return "rescued"
    if (not base_missing) and candidate_missing:
        return "lost"
    if candidate_rank < base_rank:
        return "improved"
    if candidate_rank > base_rank:
        return "worsened"
    return "unchanged"


def confirm_modes(selected: List[str], available, where: str) -> List[str]:
    """Keep only mode names the run actually emits, and say so when one is dead.

    A stale name in a selection list is invisible: the lookup returns no rows and
    the figure just comes out with one fewer series. That is how `hybrid_rerank`
    -- a legacy name the pipeline stopped emitting -- silently dropped a curve
    from the stage-retention and effects figures. Naming the miss turns a
    quietly-thinner figure into a build-time message.
    """
    available = set(available)
    missing = [m for m in selected if m not in available]
    if missing:
        print(f"  !! {where}: no data for mode(s) {', '.join(missing)} -- stale "
              f"name(s); check the selection list against the run's modes")
    return [m for m in selected if m in available]


def build_rank_transition_table(df: pd.DataFrame) -> pd.DataFrame:
    selected_modes = [
        "control_hybrid",
        "bm25_only",
        "bm25_base",
        "hybrid_bm25",
        "rrf_hybrid",
        "rrf_hybrid_rerank",
        "rerank",
        "ablation_base_no_dedup",
        "ablation_base_small_pool",
        "ablation_no_dedup",
        "ablation_small_pool",
    ]
    selected_modes = confirm_modes(selected_modes, df["mode"].unique(), "rank transition")
    baseline_df = df[df["mode"] == "baseline"][["qid", "gold_rank"]].rename(columns={"gold_rank": "baseline_gold_rank"})
    rows = []

    for mode in selected_modes:
        candidate_df = df[df["mode"] == mode][["qid", "gold_rank"]].rename(columns={"gold_rank": "candidate_gold_rank"})
        merged = baseline_df.merge(candidate_df, on="qid", how="inner")
        if merged.empty:
            continue

        merged["transition"] = merged.apply(
            lambda row: classify_rank_transition(row["baseline_gold_rank"], row["candidate_gold_rank"]),
            axis=1,
        )
        counts = merged["transition"].value_counts(dropna=False).to_dict()
        total = len(merged)

        for transition in ["rescued", "improved", "unchanged", "worsened", "lost", "both_missing"]:
            rows.append(
                {
                    "candidate_mode": mode,
                    "transition": transition,
                    "count": int(counts.get(transition, 0)),
                    "rate": float(counts.get(transition, 0) / total),
                    "num_questions": total,
                }
            )

    rank_transition_df = pd.DataFrame(rows)
    return rank_transition_df.sort_values(
        by=["candidate_mode", "transition"],
        key=lambda col: col.map(mode_sort_key) if col.name == "candidate_mode" else col,
    ).reset_index(drop=True)


def bootstrap_delta(base_values: np.ndarray, candidate_values: np.ndarray, rounds: int, seed: int) -> Dict[str, float]:
    rng = np.random.default_rng(seed)
    n = len(base_values)
    if n == 0:
        return {
            "delta": np.nan,
            "ci_low": np.nan,
            "ci_high": np.nan,
            "p_value": np.nan,
        }

    observed = float(candidate_values.mean() - base_values.mean())
    samples = np.empty(rounds, dtype=np.float64)

    for idx in range(rounds):
        sample_idx = rng.integers(0, n, size=n)
        samples[idx] = candidate_values[sample_idx].mean() - base_values[sample_idx].mean()

    ci_low, ci_high = np.quantile(samples, [0.025, 0.975])
    p_left = float(np.mean(samples <= 0.0))
    p_right = float(np.mean(samples >= 0.0))
    p_value = 2 * min(p_left, p_right)

    return {
        "delta": observed,
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "p_value": min(1.0, p_value),
    }


def build_pairwise_table(df: pd.DataFrame) -> pd.DataFrame:
    metric_specs = [
        ("recall_at_10", "higher"),
        ("mrr", "higher"),
        ("ndcg_at_10", "higher"),
        ("gold_url_hit", "higher"),
        ("insufficient_evidence_num", "lower"),
    ]

    pivoted = {}
    subset = df[["qid", "mode", *[name for name, _ in metric_specs]]].copy()
    for metric_name, _ in metric_specs:
        pivot = subset.pivot(index="qid", columns="mode", values=metric_name)
        pivoted[metric_name] = pivot

    rows = []
    base_mode = "baseline"
    candidate_modes = [mode for mode in MODE_ORDER if mode != base_mode]

    for mode_idx, candidate_mode in enumerate(candidate_modes):
        for metric_idx, (metric_name, better_direction) in enumerate(metric_specs):
            pivot = pivoted[metric_name]
            if base_mode not in pivot.columns or candidate_mode not in pivot.columns:
                continue
            paired = pivot[[base_mode, candidate_mode]].dropna()
            if paired.empty:
                continue
            stats = bootstrap_delta(
                base_values=paired[base_mode].to_numpy(dtype=np.float64),
                candidate_values=paired[candidate_mode].to_numpy(dtype=np.float64),
                rounds=BOOTSTRAP_ROUNDS,
                seed=RNG_SEED + mode_idx * 97 + metric_idx,
            )
            rows.append(
                {
                    "baseline_mode": base_mode,
                    "candidate_mode": candidate_mode,
                    "metric": metric_name,
                    "better_direction": better_direction,
                    "num_questions": len(paired),
                    "delta_candidate_minus_baseline": stats["delta"],
                    "ci_low": stats["ci_low"],
                    "ci_high": stats["ci_high"],
                    "p_value_bootstrap": stats["p_value"],
                    "significant_95ci": bool(stats["ci_low"] > 0 or stats["ci_high"] < 0),
                }
            )

    pairwise_df = pd.DataFrame(rows)
    return pairwise_df.sort_values(
        by=["candidate_mode", "metric"],
        key=lambda col: col.map(mode_sort_key) if col.name == "candidate_mode" else col,
    ).reset_index(drop=True)


def score_rank(rank: Optional[int]) -> int:
    return int(rank) if rank is not None and not pd.isna(rank) else 99


def select_case_rows(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "qid",
        "topic",
        "question",
        "mode",
        "gold_rank",
        "gold_url_hit",
        "insufficient_evidence_bool",
        "answer",
        "final_urls",
        "final_evidence_texts",
    ]
    subset = df[df["use_for_audited_eval"] & df["mode"].isin(["baseline", "rerank", "ablation_no_dedup", "ablation_small_pool"])][columns].copy()
    by_mode = {mode: part.set_index("qid") for mode, part in subset.groupby("mode")}
    seen_qids = set()
    cases = []

    def add_cases(candidate_mode: str, comparison: str, improvement: bool, limit: int) -> None:
        if "baseline" not in by_mode or candidate_mode not in by_mode:
            return
        baseline_df = by_mode["baseline"]
        candidate_df = by_mode[candidate_mode]
        common_qids = [qid for qid in baseline_df.index if qid in candidate_df.index and qid not in seen_qids]
        scored = []
        for qid in common_qids:
            base_row = baseline_df.loc[qid]
            cand_row = candidate_df.loc[qid]
            base_score = score_rank(base_row["gold_rank"])
            cand_score = score_rank(cand_row["gold_rank"])
            delta = base_score - cand_score
            if improvement and delta <= 0:
                continue
            if (not improvement) and delta >= 0:
                continue
            scored.append((abs(delta), delta, qid, base_row, cand_row))

        scored.sort(reverse=True, key=lambda item: (item[0], item[1]))
        for _, delta, qid, base_row, cand_row in scored[:limit]:
            seen_qids.add(qid)
            cases.append(
                {
                    "comparison": comparison,
                    "qid": qid,
                    "topic": base_row["topic"],
                    "question": base_row["question"],
                    "baseline_gold_rank": base_row["gold_rank"],
                    "comparison_mode": candidate_mode,
                    "comparison_gold_rank": cand_row["gold_rank"],
                    "baseline_gold_hit": base_row["gold_url_hit"],
                    "comparison_gold_hit": cand_row["gold_url_hit"],
                    "baseline_insufficient": base_row["insufficient_evidence_bool"],
                    "comparison_insufficient": cand_row["insufficient_evidence_bool"],
                    "rank_delta_baseline_minus_comparison": delta,
                    "baseline_answer": truncate_text(base_row["answer"], limit=500),
                    "comparison_answer": truncate_text(cand_row["answer"], limit=500),
                    "baseline_final_urls": base_row["final_urls"],
                    "comparison_final_urls": cand_row["final_urls"],
                    "baseline_evidence_preview": truncate_text(base_row["final_evidence_texts"]),
                    "comparison_evidence_preview": truncate_text(cand_row["final_evidence_texts"]),
                }
            )

    add_cases("ablation_no_dedup", "baseline_vs_no_dedup_improvement", improvement=True, limit=2)
    add_cases("ablation_small_pool", "baseline_vs_small_pool_improvement", improvement=True, limit=2)
    add_cases("rerank", "baseline_vs_rerank_degradation", improvement=False, limit=2)

    return pd.DataFrame(cases)


def set_plot_style() -> None:
    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#444444",
        "axes.linewidth": 0.8,
        "grid.color": "#D9D9D9",
        "grid.linestyle": "--",
        "grid.linewidth": 0.6,
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
    })


# Compact tick labels for the full-vs-audited figure only. The shared
# MODE_LABELS map is sized for tables and for roomier single-panel figures;
# eleven categorical ticks on a half-width panel need shorter strings, and
# editing the shared map to suit this one figure would shorten the labels on
# every other figure and table that reads it.
FULL_VS_AUDITED_TICK_LABELS = {
    "bm25_base": "BM25+Ded",
    "hybrid_bm25": "Hyb-BM25",
}


def plot_full_vs_audited(metrics_df: pd.DataFrame) -> None:
    figure_metrics = [
        ("ndcg_at_10", "nDCG@10"),
        ("gold_url_hit_rate", "Gold URL Hit Rate"),
    ]
    modes = [mode for mode in MODE_ORDER if mode in metrics_df["mode"].unique()]
    x = np.arange(len(modes))
    width = 0.36

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.8), sharex=True)
    subset_labels = [("full", "Full"), ("audited", "Audited")]
    subset_colors = {"full": "#B8C3D9", "audited": "#4C78A8"}

    for ax, (metric_name, metric_label) in zip(axes, figure_metrics):
        for idx, (subset_name, subset_label) in enumerate(subset_labels):
            sub = metrics_df[metrics_df["subset"] == subset_name].set_index("mode")
            values = [float(sub.loc[mode, metric_name]) if mode in sub.index else np.nan for mode in modes]
            offset = (idx - 0.5) * width
            # No per-bar value labels: at eleven mode pairs the three-decimal
            # numbers ran into each other and into the neighbouring bar. Every
            # value is already in Table 1 and in the released metrics CSV.
            ax.bar(
                x + offset,
                values,
                width=width,
                label=subset_label,
                color=subset_colors[subset_name],
                edgecolor="#444444",
                linewidth=0.7,
            )

        ax.set_title(metric_label)
        # Headroom above the tallest bar (0.91) so the legend has an empty
        # corner to sit in rather than landing on the bars.
        ax.set_ylim(0, 1.15)
        ax.grid(axis="y", alpha=0.85)
        ax.set_axisbelow(True)
        ax.set_xticks(x)
        ax.set_xticklabels(
            [FULL_VS_AUDITED_TICK_LABELS.get(mode) or MODE_LABELS.get(mode, mode)
             for mode in modes],
            rotation=45,
            ha="right",
            rotation_mode="anchor",
            fontsize=8,
        )

    axes[0].set_ylabel("Score")
    # Opaque frame so the gridlines do not run through the swatches.
    axes[1].legend(frameon=True, loc="upper right", fontsize=9,
                   framealpha=1.0, borderaxespad=0.8)
    fig.savefig(FIG_FULL_VS_AUDITED, dpi=300)
    plt.close(fig)


def plot_rank_cdf(df: pd.DataFrame) -> None:
    selected_modes = [
        "control_dense_only",
        "baseline",
        "rerank",
        "ablation_no_dedup",
        "ablation_small_pool",
    ]
    max_k = 10
    fig, ax = plt.subplots(figsize=(8.0, 5.2))

    for mode in selected_modes:
        sub = df[df["mode"] == mode].copy()
        if sub.empty:
            continue
        values = []
        rank_scores = sub["gold_rank"].tolist()
        for k in range(1, max_k + 1):
            hits = [1.0 if rank is not None and not pd.isna(rank) and rank <= k else 0.0 for rank in rank_scores]
            values.append(float(np.mean(hits)))
        ax.plot(
            range(1, max_k + 1),
            values,
            marker="o",
            linewidth=2.2,
            markersize=5,
            color=PALETTE.get(mode, "#444444"),
            label=MODE_LABELS.get(mode, mode),
        )

    ax.set_xlabel("Top-k")
    ax.set_ylabel("Cumulative Gold Hit Rate")
    ax.set_title("Audited Subset Retrieval CDF")
    ax.set_xticks(range(1, max_k + 1))
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.85)
    ax.set_axisbelow(True)
    ax.legend(frameon=True, loc="lower right")
    fig.savefig(FIG_RANK_CDF, dpi=300)
    plt.close(fig)


def plot_effects(pairwise_df: pd.DataFrame) -> None:
    # Every mode here is measured on both panels, so the figure is the re-ranking
    # comparison the caption describes rather than the two rows that survived the
    # one-panel-only filter below.
    selected_modes = [
        "control_dense_only",
        "bm25_only",
        "rrf_hybrid",
        "rerank",
        "rrf_hybrid_rerank",
    ]
    selected_modes = confirm_modes(selected_modes, pairwise_df["candidate_mode"].unique(),
                                   "effects figure")
    metric_panels = [
        ("ndcg_at_10", "Delta vs Base on nDCG@10"),
        ("insufficient_evidence_num", "Delta vs Base on Insufficient Rate"),
    ]

    # The panels share a y axis, so they must carry the same rows: the reader takes
    # row i to be the same system in both. `insufficient_evidence_num` is answer-level
    # and the retrieval-only ablation arms generate no answers, so those two rows exist
    # on the left only -- which silently shrank the shared axis and clipped the left
    # panel. Restrict to the systems measured on both, as `make_figures.py` does for
    # its answer-level charts rather than drawing a row that is not a measured zero.
    modes_per_panel = [
        set(pairwise_df.loc[pairwise_df["metric"] == metric_name, "candidate_mode"])
        for metric_name, _ in metric_panels
    ]
    shared_modes = [mode for mode in selected_modes if all(mode in modes for modes in modes_per_panel)]
    skipped = [mode for mode in selected_modes if mode not in shared_modes]
    if skipped:
        print(f"  .. effects figure: {', '.join(skipped)} measured on one panel only; "
              "left out so both panels stay row-aligned")
    if not shared_modes:
        print("  !! effects figure: no system is measured on both panels; nothing to plot")
        return

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.0), sharey=True)
    modes_in_order = sorted(shared_modes, key=mode_sort_key)

    for ax, (metric_name, title) in zip(axes, metric_panels):
        sub = pairwise_df[pairwise_df["metric"] == metric_name].copy()
        sub = sub[sub["candidate_mode"].isin(modes_in_order)].copy()
        sub["candidate_order"] = sub["candidate_mode"].map(mode_sort_key)
        sub = sub.sort_values("candidate_order")

        y = np.arange(len(sub))
        deltas = sub["delta_candidate_minus_baseline"].to_numpy(dtype=np.float64)
        ci_low = sub["ci_low"].to_numpy(dtype=np.float64)
        ci_high = sub["ci_high"].to_numpy(dtype=np.float64)
        colors = [PALETTE.get(mode, "#444444") for mode in sub["candidate_mode"]]

        ax.axvline(0.0, color="#777777", linewidth=1.0, linestyle="--")
        ax.hlines(y, ci_low, ci_high, color=colors, linewidth=2.4)
        ax.scatter(deltas, y, color=colors, s=42, zorder=3)

        for idx, delta in enumerate(deltas):
            ax.text(
                delta + (0.004 if delta >= 0 else -0.004),
                y[idx] + 0.1,
                f"{delta:+.3f}",
                fontsize=8,
                ha="left" if delta >= 0 else "right",
                va="bottom",
            )

        ax.set_title(title)
        ax.grid(axis="x", alpha=0.8)
        ax.set_axisbelow(True)
        # Headroom: the topmost row's value label sits above its point and would
        # otherwise run into the panel title.
        ax.set_ylim(-0.6, len(modes_in_order) - 0.35)

    # Set the ticks once, with the labels, and only on the left panel. Under
    # sharey=True each panel's set_yticks re-shares the locator, and a FixedFormatter
    # installed by a separate set_yticklabels call does not survive that: the last two
    # rows came out unlabelled. Passing labels= to set_yticks keeps the pair together.
    axes[0].set_yticks(np.arange(len(modes_in_order)),
                       labels=[MODE_LABELS.get(mode, mode) for mode in modes_in_order])
    axes[1].tick_params(labelleft=False)

    axes[0].set_xlabel("Candidate - Base")
    axes[1].set_xlabel("Candidate - Base")
    # The rows are systems, and the tick labels name them without saying so; the
    # panels share a y axis, so one label for the pair.
    axes[0].set_ylabel("Candidate system")
    fig.savefig(FIG_EFFECTS, dpi=300)
    plt.close(fig)


def plot_audit_breakdown(audited_questions: pd.DataFrame) -> None:
    display_order = ["validated", "general_held_out", "duplicate_extra", "topic_mismatch"]
    label_map = {
        "validated": "Validated",
        "general_held_out": "General Held-out",
        "duplicate_extra": "Duplicate Extra",
        "topic_mismatch": "Topic Mismatch",
    }
    color_map = {
        "validated": "#4C78A8",
        "general_held_out": "#F58518",
        "duplicate_extra": "#E45756",
        "topic_mismatch": "#B279A2",
    }

    counts = audited_questions["audit_status"].value_counts().to_dict()
    labels = [label_map[item] for item in display_order if counts.get(item, 0) > 0]
    values = [counts.get(item, 0) for item in display_order if counts.get(item, 0) > 0]
    colors = [color_map[item] for item in display_order if counts.get(item, 0) > 0]

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    bars = ax.bar(labels, values, color=colors, edgecolor="#444444", linewidth=0.7)
    upper = max(values + [1]) * 1.2
    ax.set_ylim(0, upper)
    ax.set_ylabel("Questions")
    ax.set_title("Question Audit Breakdown")
    ax.grid(axis="y", alpha=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=15)

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + upper * 0.02,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    fig.savefig(FIG_AUDIT_BREAKDOWN, dpi=300)
    plt.close(fig)


def plot_stage_retention(stage_df: pd.DataFrame) -> None:
    selected_modes = [
        "control_dense_only",
        "baseline",
        "rerank",
        "ablation_no_dedup",
        "ablation_small_pool",
        "rrf_hybrid_rerank",
    ]
    selected_modes = confirm_modes(selected_modes, stage_df["mode"].unique(),
                                   "stage-retention figure")
    stages = [
        ("retrieved_stage_hit_rate", "Retrieved"),
        ("dedup_stage_hit_rate", "Deduped"),
        ("ranked_stage_hit_rate", "Ranked"),
        ("final_stage_hit_rate", "Final Top-4"),
    ]

    fig, ax = plt.subplots(figsize=(8.6, 5.3))

    for mode in selected_modes:
        sub = stage_df[stage_df["mode"] == mode]
        if sub.empty:
            continue
        row = sub.iloc[0]
        values = [float(row[col]) for col, _ in stages]
        ax.plot(
            range(len(stages)),
            values,
            marker="o",
            linewidth=2.4,
            markersize=6,
            color=PALETTE.get(mode, "#444444"),
            label=MODE_LABELS.get(mode, mode),
        )

    ax.set_xticks(range(len(stages)))
    ax.set_xticklabels([label for _, label in stages])
    ax.set_xlabel("Pipeline stage")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Gold URL Retention Rate")
    ax.set_title("Gold URL Retention Across Retrieval Stages")
    ax.grid(alpha=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=True, loc="lower left", ncol=2)

    fig.savefig(FIG_STAGE_RETENTION, dpi=300)
    plt.close(fig)


def plot_rank_transition(rank_transition_df: pd.DataFrame) -> None:
    category_order = ["rescued", "improved", "unchanged", "worsened", "lost", "both_missing"]
    category_labels = {
        "rescued": "Rescued",
        "improved": "Improved",
        "unchanged": "Unchanged",
        "worsened": "Worsened",
        "lost": "Lost",
        "both_missing": "Both Missing",
    }
    category_colors = {
        "rescued": "#2E8B57",
        "improved": "#7BC96F",
        "unchanged": "#C7C7C7",
        "worsened": "#F28E2B",
        "lost": "#E15759",
        "both_missing": "#8E6C8A",
    }

    modes = rank_transition_df["candidate_mode"].drop_duplicates().tolist()
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    left = np.zeros(len(modes), dtype=np.float64)

    for category in category_order:
        values = []
        for mode in modes:
            sub = rank_transition_df[
                (rank_transition_df["candidate_mode"] == mode)
                & (rank_transition_df["transition"] == category)
            ]
            values.append(float(sub.iloc[0]["rate"]) if not sub.empty else 0.0)

        bars = ax.barh(
            y=np.arange(len(modes)),
            width=values,
            left=left,
            color=category_colors[category],
            edgecolor="white",
            linewidth=0.8,
            label=category_labels[category],
        )

        for idx, (bar, value) in enumerate(zip(bars, values)):
            if value >= 0.08:
                ax.text(
                    left[idx] + value / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="black",
                )
        left += np.array(values)

    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Proportion of Audited Questions")
    ax.set_yticks(np.arange(len(modes)))
    ax.set_yticklabels([MODE_LABELS.get(mode, mode) for mode in modes])
    ax.set_title("Rank Transition Relative to Baseline")
    ax.grid(axis="x", alpha=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=True, bbox_to_anchor=(1.02, 1.0), loc="upper left")

    fig.savefig(FIG_RANK_TRANSITION, dpi=300)
    plt.close(fig)


def main() -> None:
    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(f"{QUESTIONS_FILE} not found")
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"{RESULTS_FILE} not found")

    questions_df = load_questions(QUESTIONS_FILE)
    audited_questions = audit_questions(questions_df)
    audited_questions.to_csv(AUDIT_FILE, index=False, encoding="utf-8-sig")
    n_validated = save_question_subset(
        audited_questions,
        audited_questions["use_for_audited_eval"],
        VALIDATED_QUESTIONS_FILE,
    )
    n_general = save_question_subset(
        audited_questions,
        audited_questions["audit_status"] == "general_held_out",
        GENERAL_QUESTIONS_FILE,
    )
    # Said out loud, because an absent file and an empty file look alike in a
    # directory listing and neither says which of the two it is.
    print(f"Question subsets: {n_validated} validated, "
          f"{n_general} general held-out"
          + ("" if n_general else " (none in this set; no file written)"))

    audit_summary = pd.DataFrame(
        [
            {"metric": "total_questions", "value": int(len(audited_questions))},
            {"metric": "validated_questions", "value": int(audited_questions["use_for_audited_eval"].sum())},
            {"metric": "held_out_general_questions", "value": int(audited_questions["is_general_topic"].sum())},
            {"metric": "duplicate_extra_questions", "value": int(audited_questions["is_duplicate_extra"].sum())},
            {
                "metric": "general_questions_with_specific_terms",
                "value": int(audited_questions["general_with_specific_terms"].sum()),
            },
            {
                "metric": "duplicate_question_groups",
                "value": int(audited_questions["has_duplicate_group"].groupby(audited_questions["normalized_question"]).max().sum()),
            },
        ]
    )
    audit_summary.to_csv(AUDIT_SUMMARY_FILE, index=False, encoding="utf-8-sig")

    results_df = load_results(RESULTS_FILE)
    prepared_df = prepare_results(results_df, audited_questions)

    # The split table is about the audited 100-question pool, so it is computed
    # from the 100-question run when that run is present. RESULTS_FILE only holds
    # the 78 validated questions, so using it here would make "full" and "audited"
    # the same rows and leave the held-out row empty -- reporting the audit as
    # having no effect, which is the opposite of what the table exists to show.
    split_df = prepared_df
    if FULL_POOL_RESULTS_FILE.exists():
        candidate = prepare_results(load_results(FULL_POOL_RESULTS_FILE), audited_questions)
        if candidate["use_for_audited_eval"].notna().any():
            split_df = candidate
        else:
            print(f"!! {FULL_POOL_RESULTS_FILE.name} matched no audited question ids; "
                  f"falling back to {RESULTS_FILE.name}")
    else:
        print(f"!! {FULL_POOL_RESULTS_FILE.name} not found; the full/audited split "
              f"will be computed over {RESULTS_FILE.name} alone")

    full_metrics = summarize_metrics(split_df, subset_name="full")
    # The audited rows come from the dedicated 78-question run, not from the
    # 100-question run restricted to the same 78 ids. Both are the same
    # measurement in principle, but the second stage re-ranks candidates in
    # batches whose composition depends on how many questions are encoded at
    # once, so near-tied candidates can flip between the two runs: on
    # `rrf_hybrid_rerank` the 100-question projection reads nDCG@10 0.7232 where
    # the 78-question run reads 0.7214. Every other audited table in this file
    # (`topic_metrics`, `pairwise`, `stage_retention`, `rank_transition`) is
    # computed from `prepared_df`, and Table 1 in the paper is too. Reporting the
    # projection here would put a second, slightly different value for the same
    # benchmark in the same published directory.
    audited_metrics = summarize_metrics(
        prepared_df[prepared_df["use_for_audited_eval"]].copy(),
        subset_name="audited",
    )
    general_metrics = summarize_metrics(
        split_df[split_df["audit_status"] == "general_held_out"].copy(),
        subset_name="general_held_out",
    )
    metrics_df = pd.concat([full_metrics, audited_metrics], ignore_index=True)
    metrics_df.to_csv(METRICS_FILE, index=False, encoding="utf-8-sig")
    subset_metrics_df = pd.concat([full_metrics, audited_metrics, general_metrics], ignore_index=True)
    subset_metrics_df.to_csv(SUBSET_METRICS_FILE, index=False, encoding="utf-8-sig")

    topic_metrics_df = summarize_topic_metrics(prepared_df[prepared_df["use_for_audited_eval"]].copy())
    topic_metrics_df.to_csv(TOPIC_METRICS_FILE, index=False, encoding="utf-8-sig")

    pairwise_df = build_pairwise_table(prepared_df[prepared_df["use_for_audited_eval"]].copy())
    pairwise_df.to_csv(PAIRWISE_FILE, index=False, encoding="utf-8-sig")

    case_study_df = select_case_rows(prepared_df)
    case_study_df.to_csv(CASE_STUDY_FILE, index=False, encoding="utf-8-sig")

    stage_retention_df = build_stage_retention_table(prepared_df[prepared_df["use_for_audited_eval"]].copy())
    stage_retention_df.to_csv(STAGE_RETENTION_FILE, index=False, encoding="utf-8-sig")

    rank_transition_df = build_rank_transition_table(prepared_df[prepared_df["use_for_audited_eval"]].copy())
    rank_transition_df.to_csv(RANK_TRANSITION_FILE, index=False, encoding="utf-8-sig")

    set_plot_style()
    plot_audit_breakdown(audited_questions)
    plot_full_vs_audited(metrics_df)
    plot_rank_cdf(prepared_df[prepared_df["use_for_audited_eval"]].copy())
    plot_effects(pairwise_df)
    plot_stage_retention(stage_retention_df)
    plot_rank_transition(rank_transition_df)

    print("Saved:")
    print(f"- {AUDIT_FILE}")
    print(f"- {AUDIT_SUMMARY_FILE}")
    print(f"- {VALIDATED_QUESTIONS_FILE}")
    print(f"- {GENERAL_QUESTIONS_FILE}")
    print(f"- {METRICS_FILE}")
    print(f"- {SUBSET_METRICS_FILE}")
    print(f"- {TOPIC_METRICS_FILE}")
    print(f"- {PAIRWISE_FILE}")
    print(f"- {CASE_STUDY_FILE}")
    print(f"- {STAGE_RETENTION_FILE}")
    print(f"- {RANK_TRANSITION_FILE}")
    print(f"- {FIG_AUDIT_BREAKDOWN}")
    print(f"- {FIG_FULL_VS_AUDITED}")
    print(f"- {FIG_RANK_CDF}")
    print(f"- {FIG_EFFECTS}")
    print(f"- {FIG_STAGE_RETENTION}")
    print(f"- {FIG_RANK_TRANSITION}")


if __name__ == "__main__":
    main()
