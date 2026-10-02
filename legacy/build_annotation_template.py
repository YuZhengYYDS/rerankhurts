import json
import os
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = BASE_DIR / "result"


def resolve_path(raw_value: str, default: Path) -> Path:
    if not raw_value:
        return default
    candidate = Path(raw_value)
    return candidate if candidate.is_absolute() else BASE_DIR / candidate


default_questions_file = RESULT_DIR / "paper_questions_validated.jsonl"
if not default_questions_file.exists():
    default_questions_file = BASE_DIR / "questions.jsonl"

QUESTIONS_FILE = resolve_path(os.getenv("QUESTIONS_FILE", ""), default_questions_file)
BASELINE_FILE = resolve_path(os.getenv("BASELINE_FILE", ""), RESULT_DIR / "rag_results_baseline.csv")
RERANK_FILE = resolve_path(os.getenv("RERANK_FILE", ""), RESULT_DIR / "rag_results_rerank.csv")
OUTPUT_FILE = resolve_path(os.getenv("OUTPUT_FILE", ""), BASE_DIR / "annotation_template_30.csv")

# 每个 topic 先抽这些数量，凑成约 30 条
TOPIC_QUOTA = {
    "NSCLC": 6,
    "SCLC": 4,
    "Breast": 6,
    "Colon": 4,
    "AML": 4,
    "CLL": 3,
    "General": 3,
}


def load_questions_jsonl(path: str) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


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


def answer_len(x):
    if pd.isna(x):
        return 0
    return len(str(x).split())


def prepare_results(result_path: str, mode: str) -> pd.DataFrame:
    df = pd.read_csv(result_path)
    keep_cols = ["qid", "question", "answer", "insufficient_evidence"]
    for col in keep_cols:
        if col not in df.columns:
            df[col] = ""

    df = df[keep_cols].copy()
    df.rename(columns={
        "answer": f"{mode}_answer",
        "insufficient_evidence": f"{mode}_insufficient_evidence"
    }, inplace=True)
    df[f"{mode}_answer_len"] = df[f"{mode}_answer"].apply(answer_len)
    df[f"{mode}_insufficient_evidence"] = df[f"{mode}_insufficient_evidence"].apply(normalize_bool)
    return df


def select_subset(df: pd.DataFrame) -> pd.DataFrame:
    selected_parts = []

    for topic, quota in TOPIC_QUOTA.items():
        sub = df[df["topic"] == topic].copy()
        if len(sub) == 0:
            continue

        # 优先选更值得分析的题：
        # 1) baseline/rerank 是否对 insufficient 判断不同
        # 2) answer 长度差异较大
        sub["flag_disagreement"] = (
            sub["baseline_insufficient_evidence"].astype(str) !=
            sub["rerank_insufficient_evidence"].astype(str)
        ).astype(int)

        sub["answer_len_gap"] = (sub["baseline_answer_len"] - sub["rerank_answer_len"]).abs()

        sub = sub.sort_values(
            by=["flag_disagreement", "answer_len_gap"],
            ascending=[False, False]
        )

        selected_parts.append(sub.head(quota))

    result = pd.concat(selected_parts, ignore_index=True)

    # 保证总数不超过 30
    return result.head(30)


def main():
    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(f"{QUESTIONS_FILE} not found")
    if not BASELINE_FILE.exists():
        raise FileNotFoundError(f"{BASELINE_FILE} not found")
    if not RERANK_FILE.exists():
        raise FileNotFoundError(f"{RERANK_FILE} not found")

    questions_df = load_questions_jsonl(str(QUESTIONS_FILE))
    baseline_df = prepare_results(str(BASELINE_FILE), "baseline")
    rerank_df = prepare_results(str(RERANK_FILE), "rerank")

    merged = questions_df.merge(baseline_df, on=["qid", "question"], how="left")
    merged = merged.merge(rerank_df, on=["qid", "question"], how="left")

    subset = select_subset(merged)

    # 加人工标注列
    subset["gold_chunk_id"] = ""
    subset["gold_evidence_text"] = ""
    subset["expected_insufficient_evidence"] = ""
    subset["error_type"] = ""
    subset["review_comment"] = ""

    out_cols = [
        "qid",
        "topic",
        "question",
        "gold_url",
        "baseline_insufficient_evidence",
        "rerank_insufficient_evidence",
        "baseline_answer_len",
        "rerank_answer_len",
        "baseline_answer",
        "rerank_answer",
        "gold_chunk_id",
        "gold_evidence_text",
        "expected_insufficient_evidence",
        "error_type",
        "review_comment",
    ]

    subset[out_cols].to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved: {OUTPUT_FILE}")
    print(subset[out_cols][['qid','topic','question']].to_string(index=False))


if __name__ == "__main__":
    main()
