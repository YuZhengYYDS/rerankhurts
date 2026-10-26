import json
import os
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


from legacy.paths import resolve_legacy_path
from rerankhuts.paths import ROOT_FILE_RELOCATIONS


BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = BASE_DIR / "result"


def resolve_path(raw_value: str, default: Path) -> Path:
    if not raw_value:
        return default
    candidate = Path(raw_value)
    return resolve_legacy_path(BASE_DIR, candidate)


BUNDLE_NAME = os.getenv("BUNDLE_NAME", "emnlp_full_results_20260427_gpu").strip() or "emnlp_full_results_20260427_gpu"
BUNDLE_DIR = resolve_path(os.getenv("BUNDLE_DIR", ""), RESULT_DIR / BUNDLE_NAME)

QUESTIONS_FILE = RESULT_DIR / "paper_questions_validated.jsonl"
STRONG_BASELINES_SUMMARY = RESULT_DIR / "supp_strong_baselines_validated_overall.csv"
STRONG_BASELINES_RAW = RESULT_DIR / "supp_strong_baselines_validated.csv"
STRONG_BASELINES_TOPIC = RESULT_DIR / "supp_strong_baselines_validated_metrics_by_topic_audited.csv"
MODEL_UPGRADE_SUMMARY = RESULT_DIR / "supp_model_upgrade_summary.csv"
NORMALIZED_SUMMARY = RESULT_DIR / "supp_query_normalization_overall.csv"
NORMALIZED_TOPIC = RESULT_DIR / "supp_query_normalization_metrics_by_topic_audited.csv"


MODE_LABELS = {
    "control_dense_only": "Dense",
    "bm25_only": "BM25",
    "bm25_base": "BM25+Dedup",
    "hybrid_bm25": "Hybrid-BM25",
    "rrf_hybrid": "RRF",
    "rrf_hybrid_rerank": "RRF+Rerank",
    "baseline": "Base",
    "rerank": "Rerank",
}

MODEL_LABELS = {
    ("baseline", "BAAI/bge-base-en-v1.5", "", "all", 0): "BGE-base Base",
    ("rerank", "BAAI/bge-base-en-v1.5", "cross-encoder/ms-marco-MiniLM-L-6-v2", 0, 0): "BGE-base Rerank",
}

HEATMAP_MODES = [
    "control_dense_only",
    "bm25_only",
    "bm25_base",
    "rrf_hybrid",
    "rrf_hybrid_rerank",
    "baseline",
    "rerank",
]

COPY_PATTERNS = [
    "supp_bm25_grid*.csv",
    "supp_strong_baselines_validated*.csv",
    "supp_strong_baselines_full100*.csv",
    "supp_pool_sweep_*.csv",
    "supp_dedup_sweep_*.csv",
    "supp_finalk_sweep_*.csv",
    "supp_rerank_depth_*.csv",
    "supp_source_ablation_*.csv",
    "supp_strong_dense_*.csv",
    "supp_strong_reranker_*.csv",
    "supp_model_upgrade_summary.csv",
    "supp_query_normalization*.csv",
    "supp_query_normalization*.png",
    "paper_questions_validated*.jsonl",
    "paper_questions_validated_normalized*.jsonl",
    "paper_questions_validated_normalization_map.csv",
]

COPY_PATHS = [
    BASE_DIR / "legacy" / "run_rag_eval.py",
    BASE_DIR / "legacy" / "paper_support_analysis.py",
    BASE_DIR / "legacy" / "summarize_supplement_results.py",
    BASE_DIR / "legacy" / "generate_normalized_questions.py",
    BASE_DIR / "legacy" / "prepare_human_eval_packets.py",
    BASE_DIR / "legacy" / "package_emnlp_results.py",
    BASE_DIR / "legacy" / "__init__.py",
    BASE_DIR / "legacy" / "paths.py",
    BASE_DIR / "rerankhuts" / "__init__.py",
    BASE_DIR / "rerankhuts" / "paths.py",
    BASE_DIR / ".env.example",
    BASE_DIR / "legacy" / "requirements.txt",
    RESULT_DIR / "human_eval_packets",
    *(BASE_DIR / relative for relative in ROOT_FILE_RELOCATIONS.values()
      if relative.startswith("data/oncology/")),
]


def split_pipe(value) -> List[str]:
    if pd.isna(value):
        return []
    return [item.strip() for item in str(value).split("|") if item.strip()]


def normalize_gold_urls(value, fallback_gold_url) -> List[str]:
    if isinstance(value, list):
        urls = [str(item).strip() for item in value if str(item).strip()]
    elif pd.isna(value):
        urls = []
    else:
        try:
            parsed = json.loads(value) if isinstance(value, str) else value
            if isinstance(parsed, list):
                urls = [str(item).strip() for item in parsed if str(item).strip()]
            else:
                urls = []
        except Exception:
            urls = []
    if not urls and pd.notna(fallback_gold_url) and str(fallback_gold_url).strip():
        urls = [str(fallback_gold_url).strip()]
    return urls


def get_rank_of_gold(urls: Iterable[str], gold_urls: Iterable[str]) -> Optional[int]:
    gold_set = set(gold_urls)
    if not gold_set:
        return None
    for index, url in enumerate(urls, start=1):
        if url in gold_set:
            return index
    return None


def ndcg_at_k(rank: Optional[int], k: int) -> float:
    if rank is None or pd.isna(rank) or rank > k:
        return 0.0
    return 1.0 / np.log2(rank + 1)


def ensure_bundle_dir() -> None:
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)


def copy_result_assets() -> None:
    for pattern in COPY_PATTERNS:
        for path in RESULT_DIR.glob(pattern):
            target = BUNDLE_DIR / path.name
            shutil.copy2(path, target)

    for path in COPY_PATHS:
        if not path.exists():
            continue
        # Keep code and data at their importable/default relative locations.
        # Historical derived result assets remain at the bundle root.
        relative = Path(path.name) if path.is_relative_to(RESULT_DIR) else path.relative_to(BASE_DIR)
        target = BUNDLE_DIR / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(path, target)
        else:
            shutil.copy2(path, target)


def build_pareto_table() -> pd.DataFrame:
    if not QUESTIONS_FILE.exists() or not STRONG_BASELINES_RAW.exists():
        return pd.DataFrame()

    questions_df = pd.read_json(QUESTIONS_FILE, lines=True)
    questions_df["gold_urls_norm"] = questions_df.apply(
        lambda row: normalize_gold_urls(row.get("gold_urls"), row.get("gold_url")),
        axis=1,
    )

    raw_df = pd.read_csv(STRONG_BASELINES_RAW)
    merged = raw_df.merge(
        questions_df[["qid", "gold_url", "gold_urls_norm"]],
        on="qid",
        how="left",
    )
    merged["ranking_urls_eval"] = merged.apply(
        lambda row: row["ranking_urls"]
        if "ranking_urls" in row and pd.notna(row["ranking_urls"]) and str(row["ranking_urls"]).strip()
        else row.get("final_urls", ""),
        axis=1,
    )
    merged["gold_rank"] = merged.apply(
        lambda row: get_rank_of_gold(split_pipe(row["ranking_urls_eval"]), row["gold_urls_norm"]),
        axis=1,
    )
    merged["ndcg_at_10"] = merged["gold_rank"].map(lambda rank: ndcg_at_k(rank, 10))

    rows: List[Dict] = []
    for mode, part in merged.groupby("mode"):
        rows.append(
            {
                "method_label": MODE_LABELS.get(mode, mode),
                "source_group": "strong_baselines",
                "avg_retrieval_ms": float(part["retrieval_ms"].mean()) if "retrieval_ms" in part else np.nan,
                "avg_rerank_ms": float(part["rerank_ms"].mean()) if "rerank_ms" in part else np.nan,
                "avg_generation_ms": float(part["generation_ms"].mean()) if "generation_ms" in part else np.nan,
                "avg_total_ms": float(part["total_ms"].mean()) if "total_ms" in part else np.nan,
                "ndcg_at_10": float(part["ndcg_at_10"].mean()),
            }
        )

    for path in [
        RESULT_DIR / "supp_strong_dense_BAAI__bge_base_en_v1_5.csv",
        RESULT_DIR / "supp_strong_dense_intfloat__e5_base_v2.csv",
        RESULT_DIR / "supp_strong_reranker_minilm_l12_d010.csv",
        RESULT_DIR / "supp_strong_reranker_minilm_l12_d024.csv",
        RESULT_DIR / "supp_strong_reranker_minilm_l12_d050.csv",
        RESULT_DIR / "supp_strong_reranker_minilm_l12_d100.csv",
    ]:
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        merged_model = frame.merge(
            questions_df[["qid", "gold_url", "gold_urls_norm"]],
            on="qid",
            how="left",
        )
        merged_model["ranking_urls_eval"] = merged_model.apply(
            lambda row: row["ranking_urls"]
            if "ranking_urls" in row and pd.notna(row["ranking_urls"]) and str(row["ranking_urls"]).strip()
            else row.get("final_urls", ""),
            axis=1,
        )
        merged_model["gold_rank"] = merged_model.apply(
            lambda row: get_rank_of_gold(split_pipe(row["ranking_urls_eval"]), row["gold_urls_norm"]),
            axis=1,
        )
        merged_model["ndcg_at_10"] = merged_model["gold_rank"].map(lambda rank: ndcg_at_k(rank, 10))

        for _, part in merged_model.groupby(["mode", "embed_model_name", "rerank_model_name", "rerank_depth"]):
            row0 = part.iloc[0]
            label = f"{row0['embed_model_name']} | {row0['mode']}"
            if row0["mode"] == "rerank" and str(row0.get("rerank_model_name", "")).strip():
                label = f"{row0['embed_model_name']} | RR depth {int(row0['rerank_depth'])}"
            rows.append(
                {
                    "method_label": label,
                    "source_group": "model_upgrade",
                    "avg_retrieval_ms": float(part["retrieval_ms"].mean()) if "retrieval_ms" in part else np.nan,
                    "avg_rerank_ms": float(part["rerank_ms"].mean()) if "rerank_ms" in part else np.nan,
                    "avg_generation_ms": float(part["generation_ms"].mean()) if "generation_ms" in part else np.nan,
                    "avg_total_ms": float(part["total_ms"].mean()) if "total_ms" in part else np.nan,
                    "ndcg_at_10": float(part["ndcg_at_10"].mean()),
                }
            )

    table = pd.DataFrame(rows).drop_duplicates(subset=["method_label", "source_group"]).sort_values("avg_total_ms")
    return table


def plot_pareto(table: pd.DataFrame) -> None:
    if table.empty:
        return

    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    colors = np.where(table["source_group"] == "strong_baselines", "#4C78A8", "#E45756")
    ax.scatter(table["avg_total_ms"], table["ndcg_at_10"], c=colors, s=70, edgecolors="#333333", linewidths=0.7)

    for _, row in table.iterrows():
        ax.text(
            row["avg_total_ms"] + 8,
            row["ndcg_at_10"] + 0.002,
            row["method_label"],
            fontsize=8,
            ha="left",
            va="bottom",
        )

    ax.set_xlabel("Average latency per question (ms)")
    ax.set_ylabel("nDCG@10 on validated-78")
    ax.set_title("Accuracy-Cost Pareto")
    ax.grid(alpha=0.8, linestyle="--", linewidth=0.6)
    fig.savefig(BUNDLE_DIR / "fig_accuracy_cost_pareto.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_topic_heatmap() -> None:
    if not STRONG_BASELINES_TOPIC.exists():
        return

    topic_df = pd.read_csv(STRONG_BASELINES_TOPIC)
    topic_df = topic_df[topic_df["mode"].isin(HEATMAP_MODES)].copy()
    topic_df["method_label"] = topic_df["mode"].map(MODE_LABELS)
    pivot = topic_df.pivot(index="topic", columns="method_label", values="ndcg_at_10")

    if pivot.empty:
        return

    ordered_cols = [MODE_LABELS[mode] for mode in HEATMAP_MODES if MODE_LABELS.get(mode) in pivot.columns]
    pivot = pivot.reindex(columns=ordered_cols)
    pivot.to_csv(BUNDLE_DIR / "topic_heatmap_ndcg.csv", encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    image = ax.imshow(pivot.to_numpy(dtype=np.float64), cmap="YlOrRd", aspect="auto", vmin=0.0, vmax=1.0)
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=25, ha="right")
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Topic-Level nDCG@10 Heatmap")

    for row_idx in range(len(pivot.index)):
        for col_idx in range(len(pivot.columns)):
            value = pivot.iloc[row_idx, col_idx]
            ax.text(col_idx, row_idx, f"{value:.2f}", ha="center", va="center", fontsize=8, color="#111111")

    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="nDCG@10")
    fig.savefig(BUNDLE_DIR / "fig_topic_heatmap_ndcg.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_index_note() -> None:
    lines: List[str] = []
    lines.append(f"# {BUNDLE_NAME}")
    lines.append("")
    lines.append("## Bundle contents")
    lines.append("- GPU-rerun retrieval experiments and summaries")
    lines.append("- Tuned BM25 grid search outputs and best-parameter table")
    lines.append("- Source ablation, pool/dedup/final-k/rerank-depth sweeps")
    lines.append("- Strong dense and stronger reranker comparisons")
    lines.append("- Query normalization analysis outputs")
    lines.append("- Human evaluation packets for answer-level blind review and graded relevance")
    lines.append("- Pareto and topic-heatmap figures for supplementary writing")
    lines.append("")

    if STRONG_BASELINES_SUMMARY.exists():
        summary_df = pd.read_csv(STRONG_BASELINES_SUMMARY)
        lines.append("## Validated-78 headline")
        for mode in ["baseline", "rerank", "rrf_hybrid", "rrf_hybrid_rerank", "bm25_only", "bm25_base", "control_dense_only"]:
            sub = summary_df[summary_df["mode"] == mode]
            if sub.empty:
                continue
            row = sub.iloc[0]
            lines.append(
                f"- {MODE_LABELS.get(mode, mode)}: nDCG@10={row['ndcg_at_10']:.4f}, "
                f"MRR={row['mrr']:.4f}, Recall@10={row['recall_at_10']:.4f}, "
                f"FinalHit={row['gold_url_hit_rate']:.4f}"
            )
        lines.append("")

    bm25_best = RESULT_DIR / "supp_bm25_grid_best.csv"
    if bm25_best.exists():
        best_df = pd.read_csv(bm25_best)
        lines.append("## Tuned BM25")
        for _, row in best_df.iterrows():
            lines.append(
                f"- {row['mode']}: k1={row['bm25_k1']}, b={row['bm25_b']}, "
                f"nDCG@10={row['ndcg_at_10']:.4f}, MRR={row['mrr']:.4f}, Recall@10={row['recall_at_10']:.4f}"
            )
        lines.append("")

    if NORMALIZED_SUMMARY.exists():
        norm_df = pd.read_csv(NORMALIZED_SUMMARY)
        lines.append("## Query normalization")
        for mode in norm_df["mode"].tolist():
            row = norm_df[norm_df["mode"] == mode].iloc[0]
            lines.append(
                f"- {MODE_LABELS.get(mode, mode)} normalized: nDCG@10={row['ndcg_at_10']:.4f}, "
                f"MRR={row['mrr']:.4f}, Recall@10={row['recall_at_10']:.4f}, FinalHit={row['gold_url_hit_rate']:.4f}"
            )
        lines.append("")

    lines.append("## Key file groups")
    lines.append("- `supp_*`: main supplementary experiment outputs")
    lines.append("- `human_eval_packets/`: sample questions and annotation sheets")
    lines.append("- `fig_accuracy_cost_pareto.png`: latency vs nDCG summary")
    lines.append("- `fig_topic_heatmap_ndcg.png`: topic x method heatmap")
    lines.append("")
    lines.append("## Repro scripts")
    lines.append("Run these modules from the bundle root with `python -m legacy.<name>`.")
    lines.append("- `legacy/run_rag_eval.py`")
    lines.append("- `legacy/paper_support_analysis.py`")
    lines.append("- `legacy/summarize_supplement_results.py`")
    lines.append("- `legacy/generate_normalized_questions.py`")
    lines.append("- `legacy/prepare_human_eval_packets.py`")
    lines.append("- `legacy/package_emnlp_results.py`")
    lines.append("")

    (BUNDLE_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_bundle_dir()
    copy_result_assets()
    pareto_table = build_pareto_table()
    if not pareto_table.empty:
        pareto_table.to_csv(BUNDLE_DIR / "accuracy_cost_pareto.csv", index=False, encoding="utf-8-sig")
        plot_pareto(pareto_table)
    plot_topic_heatmap()
    write_index_note()
    print(f"Saved bundle: {BUNDLE_DIR}")


if __name__ == "__main__":
    main()
