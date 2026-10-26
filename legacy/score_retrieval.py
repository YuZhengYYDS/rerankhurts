import json
import math
import os
from pathlib import Path
from typing import List

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = Path(os.getenv("RESULT_DIR", str(BASE_DIR / "result")))
if not RESULT_DIR.is_absolute():
    RESULT_DIR = BASE_DIR / RESULT_DIR
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# Overridable so a second result set (e.g. the expanded-benchmark run) can be
# scored into its own directory without clobbering the main table's combined CSV.
COMBINED_RESULTS_FILE = Path(
    os.getenv("COMBINED_RESULTS_FILE", str(RESULT_DIR / "rag_results_experiments.csv")))
if not COMBINED_RESULTS_FILE.is_absolute():
    COMBINED_RESULTS_FILE = BASE_DIR / COMBINED_RESULTS_FILE
LEGACY_RESULT_FILES = {
    "baseline": RESULT_DIR / "rag_results_baseline.csv",
    "rerank": RESULT_DIR / "rag_results_rerank.csv",
}
QUESTIONS_FILE = Path(os.getenv("QUESTIONS_FILE", str(BASE_DIR / "questions.jsonl")))
if not QUESTIONS_FILE.is_absolute():
    QUESTIONS_FILE = BASE_DIR / QUESTIONS_FILE

OUTPUT_OVERALL = RESULT_DIR / "retrieval_metrics_overall.csv"
OUTPUT_BY_TOPIC = RESULT_DIR / "retrieval_metrics_by_topic.csv"

RESULT_USECOLS = {
    "mode",
    "qid",
    "question",
    "ranking_urls",
    "final_urls",
    "reranked_urls",
    "deduped_urls",
    "retrieved_urls",
}


def load_questions_jsonl(path: str) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def load_results() -> pd.DataFrame:
    combined_path = Path(COMBINED_RESULTS_FILE)
    if combined_path.exists():
        df = pd.read_csv(
            combined_path,
            usecols=lambda col: col in RESULT_USECOLS,
        )
        if "mode" not in df.columns:
            raise ValueError(f"{COMBINED_RESULTS_FILE} must contain a mode column.")
        return df

    frames = []
    for mode_name, path in LEGACY_RESULT_FILES.items():
        file_path = Path(path)
        if not file_path.exists():
            continue
        df = pd.read_csv(
            file_path,
            usecols=lambda col: col in RESULT_USECOLS - {"mode"},
        )
        df["mode"] = mode_name
        frames.append(df)

    if not frames:
        expected = ", ".join([COMBINED_RESULTS_FILE] + list(LEGACY_RESULT_FILES.values()))
        raise FileNotFoundError(f"No result file found. Expected one of: {expected}")

    return pd.concat(frames, ignore_index=True)


def split_urls(urls_text):
    if pd.isna(urls_text):
        return []
    return [x.strip() for x in str(urls_text).split("|") if x.strip()]


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


def get_rank_of_gold(url_list, gold_urls):
    if not gold_urls:
        return None
    for idx, url in enumerate(url_list, start=1):
        if url in gold_urls:
            return idx
    return None


def recall_at_k(rank, k):
    if rank is None or pd.isna(rank):
        return 0.0
    return 1.0 if rank <= k else 0.0


def reciprocal_rank(rank):
    if rank is None or pd.isna(rank):
        return 0.0
    return 1.0 / rank


def ndcg_at_k(rank, k):
    if rank is None or pd.isna(rank) or rank > k:
        return 0.0
    return 1.0 / math.log2(rank + 1)


def choose_ranking_urls(row) -> str:
    if "ranking_urls" in row and pd.notna(row["ranking_urls"]) and str(row["ranking_urls"]).strip():
        return str(row["ranking_urls"])

    mode = str(row.get("mode", "")).strip().lower()
    if mode == "baseline":
        for col in ["deduped_urls", "final_urls", "retrieved_urls"]:
            value = row.get(col)
            if pd.notna(value) and str(value).strip():
                return str(value)
        return ""

    for col in ["final_urls", "reranked_urls", "deduped_urls", "retrieved_urls"]:
        value = row.get(col)
        if pd.notna(value) and str(value).strip():
            return str(value)
    return ""


def prepare_result_df(results_df: pd.DataFrame, questions_df: pd.DataFrame) -> pd.DataFrame:
    df = results_df.copy()
    df["ranking_urls"] = df.apply(choose_ranking_urls, axis=1)

    merged = df.merge(
        questions_df[[col for col in ["qid", "question", "topic", "gold_url", "gold_urls"] if col in questions_df.columns]],
        on=["qid", "question"],
        how="left"
    )

    merged["url_list"] = merged["ranking_urls"].apply(split_urls)
    merged["gold_urls_norm"] = merged.apply(
        lambda row: normalize_gold_urls(row.get("gold_urls"), row.get("gold_url")),
        axis=1,
    )
    merged["gold_rank"] = merged.apply(
        lambda row: get_rank_of_gold(row["url_list"], row["gold_urls_norm"]),
        axis=1
    )

    merged["recall@5"] = merged["gold_rank"].apply(lambda r: recall_at_k(r, 5))
    merged["recall@10"] = merged["gold_rank"].apply(lambda r: recall_at_k(r, 10))
    merged["mrr"] = merged["gold_rank"].apply(reciprocal_rank)
    merged["ndcg@10"] = merged["gold_rank"].apply(lambda r: ndcg_at_k(r, 10))

    return merged


def summarize_metrics(df: pd.DataFrame, group_cols):
    grouped = df.groupby(group_cols, dropna=False, sort=False).agg(
        num_questions=("qid", "count"),
        recall_at_5=("recall@5", "mean"),
        recall_at_10=("recall@10", "mean"),
        mrr=("mrr", "mean"),
        ndcg_at_10=("ndcg@10", "mean"),
    ).reset_index()

    for col in ["recall_at_5", "recall_at_10", "mrr", "ndcg_at_10"]:
        grouped[col] = grouped[col].round(4)

    return grouped


def main():
    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(
            f"{QUESTIONS_FILE} not found. Please save your annotated questions as questions.jsonl"
        )

    questions_df = load_questions_jsonl(str(QUESTIONS_FILE))

    required_cols = {"qid", "question", "topic"}
    missing = required_cols - set(questions_df.columns)
    if missing:
        raise ValueError(
            f"questions.jsonl is missing required fields: {missing}. "
            "Please annotate your questions first."
        )

    if "gold_url" not in questions_df.columns and "gold_urls" not in questions_df.columns:
        raise ValueError("questions.jsonl must contain gold_url or gold_urls for retrieval evaluation.")

    results_df = load_results()
    prepared_df = prepare_result_df(results_df=results_df, questions_df=questions_df)

    overall = summarize_metrics(prepared_df, ["mode"])
    by_topic = summarize_metrics(prepared_df, ["topic", "mode"])

    overall.to_csv(OUTPUT_OVERALL, index=False, encoding="utf-8-sig")
    by_topic.to_csv(OUTPUT_BY_TOPIC, index=False, encoding="utf-8-sig")

    print(f"Saved: {OUTPUT_OVERALL}")
    print(f"Saved: {OUTPUT_BY_TOPIC}")

    print("\n=== Overall Retrieval Metrics ===")
    print(overall.to_string(index=False))

    print("\n=== Retrieval Metrics by Topic ===")
    print(by_topic.to_string(index=False))


if __name__ == "__main__":
    main()
