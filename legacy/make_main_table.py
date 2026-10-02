from pathlib import Path
import os

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = Path(os.getenv("RESULT_DIR", str(BASE_DIR / "result")))
RESULT_DIR.mkdir(parents=True, exist_ok=True)

RETRIEVAL_FILE = RESULT_DIR / "retrieval_metrics_overall.csv"
ANSWER_FILE = RESULT_DIR / "analysis_overall.csv"
OUTPUT_FILE = RESULT_DIR / "main_results_table.csv"


def ensure_file(path: str):
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} not found")


def method_sort_key(name: str):
    preferred = {
        "control_dense_only": 0,
        "control_sparse_only": 1,
        "control_hybrid": 2,
        "baseline": 3,
        "rerank": 4,
        "ablation_no_dedup": 5,
        "ablation_small_pool": 6,
        "hybrid_rerank": 7,
    }
    return preferred.get(str(name), 100)


def main():
    ensure_file(RETRIEVAL_FILE)
    ensure_file(ANSWER_FILE)

    retrieval_df = pd.read_csv(RETRIEVAL_FILE)
    answer_df = pd.read_csv(ANSWER_FILE)

    merged = retrieval_df.merge(answer_df, on="mode", how="inner")

    final_df = merged[
        [
            "mode",
            "recall_at_5",
            "recall_at_10",
            "mrr",
            "ndcg_at_10",
            "insufficient_evidence_rate",
            "gold_url_hit_rate",
            "avg_answer_word_count",
        ]
    ].copy()

    final_df = final_df.sort_values(
        by="mode",
        key=lambda col: col.map(method_sort_key),
    )

    final_df.columns = [
        "Method",
        "Recall@5",
        "Recall@10",
        "MRR",
        "nDCG@10",
        "InsufficientEvidenceRate",
        "GoldURLHitRate",
        "AvgAnswerLength",
    ]

    for col in final_df.columns[1:]:
        final_df[col] = final_df[col].round(4)

    final_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved: {OUTPUT_FILE}")
    print(final_df.to_string(index=False))


if __name__ == "__main__":
    main()
