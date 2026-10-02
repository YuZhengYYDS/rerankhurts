import json
from pathlib import Path

import pandas as pd


QUESTIONS_FILE = "questions.jsonl"
BASELINE_FILE = "rag_results_baseline.csv"
RERANK_FILE = "rag_results_rerank.csv"
OUTPUT_FILE = "case_study_candidates.csv"


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


def safe_len(x):
    if pd.isna(x):
        return 0
    return len(str(x).split())


def prepare_df(path: str, prefix: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # 兼容字段
    if "final_urls" not in df.columns:
        if "reranked_urls" in df.columns:
            df["final_urls"] = df["reranked_urls"]
        elif "retrieved_urls" in df.columns:
            df["final_urls"] = df["retrieved_urls"]
        else:
            df["final_urls"] = ""

    if "final_evidence_texts" not in df.columns:
        df["final_evidence_texts"] = ""

    keep = ["qid", "question", "answer", "insufficient_evidence", "final_urls", "final_evidence_texts"]
    for col in keep:
        if col not in df.columns:
            df[col] = ""

    df = df[keep].copy()
    df.rename(columns={
        "answer": f"{prefix}_answer",
        "insufficient_evidence": f"{prefix}_insufficient_evidence",
        "final_urls": f"{prefix}_final_urls",
        "final_evidence_texts": f"{prefix}_final_evidence_texts",
    }, inplace=True)

    df[f"{prefix}_insufficient_evidence"] = df[f"{prefix}_insufficient_evidence"].apply(normalize_bool)
    df[f"{prefix}_answer_len"] = df[f"{prefix}_answer"].apply(safe_len)

    return df


def main():
    if not Path(QUESTIONS_FILE).exists():
        raise FileNotFoundError(f"{QUESTIONS_FILE} not found")
    if not Path(BASELINE_FILE).exists():
        raise FileNotFoundError(f"{BASELINE_FILE} not found")
    if not Path(RERANK_FILE).exists():
        raise FileNotFoundError(f"{RERANK_FILE} not found")

    qdf = load_questions_jsonl(QUESTIONS_FILE)
    bdf = prepare_df(BASELINE_FILE, "baseline")
    rdf = prepare_df(RERANK_FILE, "rerank")

    merged = qdf.merge(bdf, on=["qid", "question"], how="left")
    merged = merged.merge(rdf, on=["qid", "question"], how="left")

    merged["insufficient_disagreement"] = (
        merged["baseline_insufficient_evidence"].astype(str) !=
        merged["rerank_insufficient_evidence"].astype(str)
    ).astype(int)

    merged["answer_len_gap"] = (merged["baseline_answer_len"] - merged["rerank_answer_len"]).abs()

    merged["candidate_score"] = (
        merged["insufficient_disagreement"] * 10 +
        merged["answer_len_gap"] / 10
    )

    # 每个 topic 先保留 2 条最值得分析的
    rows = []
    for topic in merged["topic"].dropna().unique():
        sub = merged[merged["topic"] == topic].copy()
        sub = sub.sort_values(by="candidate_score", ascending=False)
        rows.append(sub.head(2))

    out = pd.concat(rows, ignore_index=True)

    out_cols = [
        "qid",
        "topic",
        "question",
        "gold_url",
        "baseline_insufficient_evidence",
        "rerank_insufficient_evidence",
        "baseline_answer_len",
        "rerank_answer_len",
        "baseline_final_urls",
        "rerank_final_urls",
        "baseline_answer",
        "rerank_answer",
        "baseline_final_evidence_texts",
        "rerank_final_evidence_texts",
    ]

    out[out_cols].to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved: {OUTPUT_FILE}")
    print(out[out_cols][['qid','topic','question']].to_string(index=False))


if __name__ == "__main__":
    main()