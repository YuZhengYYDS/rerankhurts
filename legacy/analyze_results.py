import json
import os
from pathlib import Path
from typing import List

import pandas as pd

from rerankhuts.paths import oncology_path
from legacy.paths import resolve_legacy_path


BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = Path(os.getenv("RESULT_DIR", str(BASE_DIR / "result")))
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
QUESTIONS_FILE = Path(os.getenv("QUESTIONS_FILE", str(oncology_path("questions.jsonl", root=BASE_DIR))))
if not QUESTIONS_FILE.is_absolute():
    QUESTIONS_FILE = resolve_legacy_path(BASE_DIR, QUESTIONS_FILE)

OUTPUT_OVERALL = RESULT_DIR / "analysis_overall.csv"
OUTPUT_BY_TOPIC = RESULT_DIR / "analysis_by_topic.csv"

RESULT_USECOLS = {
    "mode",
    "qid",
    "question",
    "answer",
    "insufficient_evidence",
    "final_urls",
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


def normalize_bool(x):
    if pd.isna(x):
        return None
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    if s in {"true", "1", "yes"}:
        return True
    if s in {"false", "0", "no"}:
        return False
    return None


def answer_length(text):
    """Words in a generated answer, or NaN when no answer was generated.

    This returned 0 for a missing answer, which counts a system that answered
    nothing as a system that answered in zero words. The retrieval-only ablation
    arms inject their mode's rows with the answer columns blank, so they were
    aggregated as measured 0.0-word systems and drawn that way in
    `fig_answer_length.png`.
    """
    if pd.isna(text) or not str(text).strip():
        return float("nan")
    return len(str(text).split())


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


def gold_url_hit(final_urls: str, gold_urls: List[str]) -> int:
    if pd.isna(final_urls) or not gold_urls:
        return 0
    final_urls_text = str(final_urls)
    return 1 if any(gold_url in final_urls_text for gold_url in gold_urls) else 0


def prepare_result_df(results_df: pd.DataFrame, questions_df: pd.DataFrame) -> pd.DataFrame:
    df = results_df.copy()

    if "final_urls" not in df.columns:
        df["final_urls"] = ""

    df["insufficient_evidence_norm"] = df["insufficient_evidence"].apply(normalize_bool)
    df["answer_word_count"] = df["answer"].apply(answer_length)

    merged = df.merge(
        questions_df[[col for col in ["qid", "question", "topic", "gold_url", "gold_urls"] if col in questions_df.columns]],
        on=["qid", "question"],
        how="left"
    )

    merged["gold_urls_norm"] = merged.apply(
        lambda row: normalize_gold_urls(row.get("gold_urls"), row.get("gold_url")),
        axis=1,
    )

    merged["gold_url_hit"] = merged.apply(
        lambda row: gold_url_hit(row.get("final_urls", ""), row.get("gold_urls_norm", [])),
        axis=1
    )

    return merged


def build_overall_table(df: pd.DataFrame) -> pd.DataFrame:
    # Plain means, so an unrecorded abstention stays unmeasured (NaN) instead of
    # being read as `False` -- "the evidence was sufficient" -- which is the most
    # favourable value the metric can take. That fill is what put the
    # retrieval-only ablation arms at a perfect 0.0% insufficient evidence in
    # `fig_answer_rates.png`. `gold_url_hit_rate` is derived from retrieval alone
    # and so stays measured for those modes.
    overall = df.groupby("mode", as_index=False, sort=False).agg(
        num_questions=("qid", "count"),
        insufficient_evidence_rate=("insufficient_evidence_norm", "mean"),
        avg_answer_word_count=("answer_word_count", "mean"),
        gold_url_hit_rate=("gold_url_hit", "mean"),
    )

    for col in ["insufficient_evidence_rate", "avg_answer_word_count", "gold_url_hit_rate"]:
        digits = 2 if col == "avg_answer_word_count" else 4
        overall[col] = overall[col].round(digits)

    return overall


def build_topic_table(df: pd.DataFrame) -> pd.DataFrame:
    # Same reasoning as `build_overall_table`: unmeasured stays NaN.
    topic_df = df.groupby(["topic", "mode"], as_index=False, sort=False).agg(
        num_questions=("qid", "count"),
        insufficient_evidence_rate=("insufficient_evidence_norm", "mean"),
        avg_answer_word_count=("answer_word_count", "mean"),
        gold_url_hit_rate=("gold_url_hit", "mean"),
    )

    for col in ["insufficient_evidence_rate", "avg_answer_word_count", "gold_url_hit_rate"]:
        digits = 2 if col == "avg_answer_word_count" else 4
        topic_df[col] = topic_df[col].round(digits)

    return topic_df


def main():
    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(
            f"{QUESTIONS_FILE} not found. "
            "Please make sure your annotated questions file is saved as questions.jsonl"
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
        raise ValueError("questions.jsonl must contain gold_url or gold_urls for evaluation.")

    results_df = load_results()
    prepared_df = prepare_result_df(results_df=results_df, questions_df=questions_df)

    overall_df = build_overall_table(prepared_df)
    topic_df = build_topic_table(prepared_df)

    overall_df.to_csv(OUTPUT_OVERALL, index=False, encoding="utf-8-sig")
    topic_df.to_csv(OUTPUT_BY_TOPIC, index=False, encoding="utf-8-sig")

    print(f"Saved: {OUTPUT_OVERALL}")
    print(f"Saved: {OUTPUT_BY_TOPIC}")

    print("\n=== Overall Summary ===")
    print(overall_df.to_string(index=False))

    print("\n=== By Topic Summary ===")
    print(topic_df.to_string(index=False))


if __name__ == "__main__":
    main()
