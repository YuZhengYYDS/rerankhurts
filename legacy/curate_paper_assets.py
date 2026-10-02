import json
import math
import os
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = Path(os.getenv("RESULT_DIR", str(BASE_DIR / "result")))
BUNDLE_DIR = Path(
    os.getenv(
        "BUNDLE_DIR",
        RESULT_DIR / "emnlp_full_results_20260427_gpu_final",
    )
)
HUMAN_DIR = BUNDLE_DIR / "human_eval_packets"
PAPER_DIR = BUNDLE_DIR / "paper_assets_curated"


MODE_DISPLAY = {
    "control_dense_only": "Dense",
    "control_hybrid": "Hybrid-TF",
    "bm25_only": "BM25",
    "bm25_base": "BM25+Dedup",
    "hybrid_bm25": "Hybrid-BM25",
    "rrf_hybrid": "RRF",
    "rrf_hybrid_rerank": "RRF+Rerank",
    "baseline": "Base",
    "rerank": "Rerank",
    "rerank_bge_base": "bge-base",
    "rerank_bge_m3": "bge-m3",
    "rerank_medcpt": "MedCPT",
    "rerank_llm": "LLM-RR",
    "strong_reranker": "Strong-Reranker",
    "ablation_no_dedup": "No URL cap",
    "ablation_small_pool": "Small pool",
}

PARETO_SHORT = {
    "Dense": "Dense",
    "Hybrid-TF": "H-TF",
    "BM25": "BM25",
    "BM25+Dedup": "BM25+D",
    "Hybrid-BM25": "H-BM25",
    "RRF": "RRF",
    "RRF+Rerank": "RRF+RR",
    "Base": "Base",
    "Rerank": "RR",
    "bge-base": "bge-b",
    "bge-m3": "bge-m3",
    "MedCPT": "MedCPT",
    "LLM-RR": "LLM-RR",
    "BAAI/bge-base-en-v1.5 | baseline": "BGE-base",
    "BAAI/bge-base-en-v1.5 | rerank": "BGE-b+RR",
    "intfloat/e5-base-v2 | baseline": "E5-base",
    "intfloat/e5-base-v2 | rerank": "E5-b+RR",
    "ablation_small_pool": "SmallPool",
    "ablation_no_dedup": "NoDedup",
    "BAAI/bge-small-en-v1.5 | RR depth 10": "L12-d10",
    "BAAI/bge-small-en-v1.5 | RR depth 24": "L12-d24",
    "BAAI/bge-small-en-v1.5 | RR depth 50": "L12-d50",
    "BAAI/bge-small-en-v1.5 | RR depth 100": "L12-d100",
}

# (dx, dy) in points, or (dx, dy, ha) when the label has to sit on the left.
PARETO_OFFSETS = {
    "SmallPool": (8, 16),
    "NoDedup": (8, 6),
    "BGE-b+RR": (-8, 2, "right"),
    "E5-b+RR": (-8, -2, "right"),
    "Dense": (8, 6),
    "Base": (8, 12),
    "H-TF": (8, 0),
    "BM25": (8, -2),
    "BM25+D": (8, 6),
    "H-BM25": (8, 4),
    "RRF": (8, 0),
    "RR": (8, 2),
    "RRF+RR": (8, -6),
    "BGE-base": (8, 8),
    "E5-base": (8, 2),
    "L12-d10": (8, 8),
    "L12-d24": (8, -2),
    "L12-d50": (8, -12),
    "L12-d100": (8, -22),
}


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
    return 1.0 / math.log2(rank + 1)


def choose_eval_file(human_dir: Path, stem: str) -> Tuple[Optional[Path], str]:
    autofilled = human_dir / f"{stem}_AUTOFILLED.csv"
    original = human_dir / f"{stem}.csv"
    if autofilled.exists():
        return autofilled, "autofilled"
    if original.exists():
        return original, "manual_or_unfilled"
    return None, "missing"


def build_answer_eval_summary() -> Tuple[pd.DataFrame, Dict[str, str]]:
    score_file, score_source = choose_eval_file(HUMAN_DIR, "answer_level_blind_eval")
    key_file = HUMAN_DIR / "answer_level_blind_eval_key.csv"
    if score_file is None or not key_file.exists():
        return pd.DataFrame(), {"score_source": score_source}

    df = pd.read_csv(score_file)
    key_df = pd.read_csv(key_file)
    rows: List[Dict] = []
    for _, row in df.iterrows():
        qid = row["qid"]
        for slot in ["A", "B", "C", "D"]:
            rows.append(
                {
                    "qid": qid,
                    "slot": slot,
                    "faithfulness": pd.to_numeric(row.get(f"slot_{slot}_faithfulness_1to5"), errors="coerce"),
                    "citation_support": pd.to_numeric(row.get(f"slot_{slot}_citation_support_1to5"), errors="coerce"),
                    "helpfulness": pd.to_numeric(row.get(f"slot_{slot}_helpfulness_1to5"), errors="coerce"),
                    "abstention_ok": pd.to_numeric(row.get(f"slot_{slot}_abstention_ok_0or1"), errors="coerce"),
                    "notes": row.get(f"slot_{slot}_notes", ""),
                }
            )

    long_df = pd.DataFrame(rows).merge(key_df, on=["qid", "slot"], how="left")
    long_df["method_label"] = long_df["method_alias"].map(MODE_DISPLAY).fillna(long_df["method_alias"])
    long_df["auto_note_flag"] = long_df["notes"].fillna("").astype(str).str.startswith("auto:")
    valid_rows = long_df.dropna(subset=["faithfulness", "citation_support", "helpfulness", "abstention_ok"]).copy()
    if valid_rows.empty:
        return pd.DataFrame(), {"score_source": score_source, "score_file": str(score_file)}

    valid_rows["composite_mean"] = valid_rows[["faithfulness", "citation_support", "helpfulness"]].mean(axis=1)
    summary = valid_rows.groupby(["method_alias", "method_label"], as_index=False).agg(
        num_questions=("qid", "nunique"),
        faithfulness_mean=("faithfulness", "mean"),
        citation_support_mean=("citation_support", "mean"),
        helpfulness_mean=("helpfulness", "mean"),
        abstention_ok_rate=("abstention_ok", "mean"),
        composite_mean=("composite_mean", "mean"),
        auto_note_rate=("auto_note_flag", "mean"),
    )
    summary["annotation_source"] = score_source
    summary["valid_for_human_eval_claim"] = score_source == "manual_or_unfilled" and float(summary["auto_note_rate"].mean()) < 0.5
    summary = summary.sort_values("composite_mean", ascending=False).reset_index(drop=True)
    return summary, {"score_source": score_source, "score_file": str(score_file)}


def build_graded_relevance_summary() -> Tuple[pd.DataFrame, Dict[str, str]]:
    score_file, score_source = choose_eval_file(HUMAN_DIR, "graded_relevance_packet")
    if score_file is None:
        return pd.DataFrame(), {"score_source": score_source}

    df = pd.read_csv(score_file)
    if "relevance_score_0_1_2" not in df.columns:
        return pd.DataFrame(), {"score_source": score_source, "score_file": str(score_file)}

    df["relevance"] = pd.to_numeric(df["relevance_score_0_1_2"], errors="coerce")
    df["review_notes"] = df["review_notes"].fillna("")
    df["auto_note_flag"] = df["review_notes"].astype(str).str.startswith("auto:")
    valid = df.dropna(subset=["relevance"]).copy()
    if valid.empty:
        return pd.DataFrame(), {"score_source": score_source, "score_file": str(score_file)}

    expanded_rows: List[Dict] = []
    for _, row in valid.iterrows():
        try:
            rank_map = json.loads(row["ranks_by_method"])
        except Exception:
            rank_map = {}
        for method_alias, rank in rank_map.items():
            expanded_rows.append(
                {
                    "qid": row["qid"],
                    "method_alias": method_alias,
                    "method_label": MODE_DISPLAY.get(method_alias, method_alias),
                    "rank": int(rank),
                    "relevance": float(row["relevance"]),
                    "auto_note_flag": bool(row["auto_note_flag"]),
                }
            )

    expanded = pd.DataFrame(expanded_rows)
    question_rows: List[Dict] = []
    for (method_alias, method_label, qid), part in expanded.groupby(["method_alias", "method_label", "qid"]):
        top4 = part[part["rank"] <= 4]
        top10 = part[part["rank"] <= 10]
        question_rows.append(
            {
                "method_alias": method_alias,
                "method_label": method_label,
                "qid": qid,
                "top4_mean_relevance": float(top4["relevance"].mean()) if not top4.empty else np.nan,
                "top10_mean_relevance": float(top10["relevance"].mean()) if not top10.empty else np.nan,
                "top4_rel2_hit": float((top4["relevance"] == 2).any()) if not top4.empty else 0.0,
                "top10_rel2_hit": float((top10["relevance"] == 2).any()) if not top10.empty else 0.0,
                "auto_note_flag": bool(part["auto_note_flag"].any()),
            }
        )

    question_df = pd.DataFrame(question_rows)
    summary = question_df.groupby(["method_alias", "method_label"], as_index=False).agg(
        num_questions=("qid", "nunique"),
        top4_mean_relevance=("top4_mean_relevance", "mean"),
        top10_mean_relevance=("top10_mean_relevance", "mean"),
        top4_rel2_hit_rate=("top4_rel2_hit", "mean"),
        top10_rel2_hit_rate=("top10_rel2_hit", "mean"),
        auto_note_rate=("auto_note_flag", "mean"),
    )
    summary["annotation_source"] = score_source
    summary["valid_for_human_eval_claim"] = score_source == "manual_or_unfilled" and float(summary["auto_note_rate"].mean()) < 0.5
    summary = summary.sort_values("top4_mean_relevance", ascending=False).reset_index(drop=True)
    return summary, {"score_source": score_source, "score_file": str(score_file)}


def build_main_tables() -> None:
    baseline_path = RESULT_DIR / "supp_strong_baselines_validated_overall.csv"
    model_path = RESULT_DIR / "supp_model_upgrade_summary.csv"

    if baseline_path.exists():
        df = pd.read_csv(baseline_path)
        keep = [
            "control_dense_only",
            "bm25_only",
            "bm25_base",
            "hybrid_bm25",
            "rrf_hybrid",
            "baseline",
            "rerank",
        ]
        table = df[df["mode"].isin(keep)].copy()
        table["method"] = table["mode"].map(MODE_DISPLAY)
        table = table[["method", "recall_at_10", "mrr", "ndcg_at_10", "gold_url_hit_rate"]].sort_values("ndcg_at_10", ascending=False)
        table.to_csv(BUNDLE_DIR / "paper_table_main_baselines.csv", index=False, encoding="utf-8-sig")

    if model_path.exists():
        df = pd.read_csv(model_path)
        rows: List[Dict] = []
        for _, row in df.iterrows():
            if row["mode"] == "baseline" and row["embed_model_name"] == "BAAI/bge-base-en-v1.5":
                method = "BGE-base Base"
            elif row["mode"] == "baseline" and row["embed_model_name"] == "intfloat/e5-base-v2":
                method = "E5-base Base"
            elif row["mode"] == "rerank" and row["embed_model_name"] == "BAAI/bge-base-en-v1.5":
                method = "BGE-base + MiniLM-L6"
            elif row["mode"] == "rerank" and row["embed_model_name"] == "intfloat/e5-base-v2":
                method = "E5-base + MiniLM-L6"
            elif row["mode"] == "rerank" and row["embed_model_name"] == "BAAI/bge-small-en-v1.5":
                method = f"BGE-small + MiniLM-L12 (d={int(row['rerank_depth'])})"
            else:
                continue
            rows.append(
                {
                    "method": method,
                    "recall_at_10": row["recall_at_10"],
                    "mrr": row["mrr"],
                    "ndcg_at_10": row["ndcg_at_10"],
                    "final_top_k_hit_rate": row["final_top_k_hit_rate"],
                }
            )
        if rows:
            pd.DataFrame(rows).sort_values("ndcg_at_10", ascending=False).to_csv(
                BUNDLE_DIR / "paper_table_model_upgrades.csv",
                index=False,
                encoding="utf-8-sig",
            )


def retrieval_side_ms(part: pd.DataFrame) -> float:
    """Per-question latency of producing the evidence list, in ms.

    This is `retrieval_ms + rerank_ms`, and it is deliberately not `total_ms`.
    The two groups on this figure come from different batches: the baseline
    family ran with answer generation on, the model upgrades with it off. Their
    `total_ms` therefore measures different things -- BM25's 1560 ms is 1557 ms
    of DeepSeek generation around 3 ms of retrieval, plotted against upgrades
    whose whole pipeline is under 200 ms. The x-axis read as a 4000x cost gap
    where the retrieval-side gap is at most 200x, so the figure's own claim
    (re-ranking buys accuracy at a modest, bounded latency cost) was being
    contradicted by an artefact of which batch had generation enabled.

    Generation cost is a real cost but not this figure's; the y-axis is a
    retrieval metric, so the x-axis is the cost of the retrieval that produced
    it. A mode with no re-ranking records `rerank_ms` as a measured 0.0, so the
    sum needs no fill.
    """
    return float((part["retrieval_ms"] + part["rerank_ms"]).mean())


def build_pareto_table() -> pd.DataFrame:
    questions_file = RESULT_DIR / "paper_questions_validated.jsonl"
    raw_file = RESULT_DIR / "supp_strong_baselines_validated.csv"
    if not questions_file.exists() or not raw_file.exists():
        return pd.DataFrame()

    questions_df = pd.read_json(questions_file, lines=True)
    questions_df["gold_urls_norm"] = questions_df.apply(
        lambda row: normalize_gold_urls(row.get("gold_urls"), row.get("gold_url")),
        axis=1,
    )
    raw_df = pd.read_csv(raw_file)
    merged = raw_df.merge(questions_df[["qid", "gold_url", "gold_urls_norm"]], on="qid", how="left")
    merged["ranking_urls_eval"] = merged.apply(
        lambda row: row["ranking_urls"] if pd.notna(row.get("ranking_urls")) and str(row.get("ranking_urls")).strip() else row.get("final_urls", ""),
        axis=1,
    )
    merged["gold_rank"] = merged.apply(
        lambda row: get_rank_of_gold(split_pipe(row["ranking_urls_eval"]), row["gold_urls_norm"]),
        axis=1,
    )
    merged["ndcg_at_10"] = merged["gold_rank"].map(lambda rank: ndcg_at_k(rank, 10))

    rows: List[Dict] = []
    for mode, part in merged.groupby("mode"):
        display = MODE_DISPLAY.get(mode, mode)
        rows.append(
            {
                "full_label": display,
                "short_label": PARETO_SHORT.get(display, display),
                "source_group": "baseline_family",
                "avg_retrieval_ms": retrieval_side_ms(part),
                "ndcg_at_10": float(part["ndcg_at_10"].mean()),
            }
        )

    upgrade_paths = [
        RESULT_DIR / "supp_strong_dense_BAAI__bge_base_en_v1_5.csv",
        RESULT_DIR / "supp_strong_dense_intfloat__e5_base_v2.csv",
        RESULT_DIR / "supp_strong_reranker_minilm_l12_d010.csv",
        RESULT_DIR / "supp_strong_reranker_minilm_l12_d024.csv",
        RESULT_DIR / "supp_strong_reranker_minilm_l12_d050.csv",
        RESULT_DIR / "supp_strong_reranker_minilm_l12_d100.csv",
    ]
    for path in upgrade_paths:
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        merged_model = frame.merge(questions_df[["qid", "gold_url", "gold_urls_norm"]], on="qid", how="left")
        merged_model["ranking_urls_eval"] = merged_model.apply(
            lambda row: row["ranking_urls"] if pd.notna(row.get("ranking_urls")) and str(row.get("ranking_urls")).strip() else row.get("final_urls", ""),
            axis=1,
        )
        merged_model["gold_rank"] = merged_model.apply(
            lambda row: get_rank_of_gold(split_pipe(row["ranking_urls_eval"]), row["gold_urls_norm"]),
            axis=1,
        )
        merged_model["ndcg_at_10"] = merged_model["gold_rank"].map(lambda rank: ndcg_at_k(rank, 10))

        # dropna=False is required: the embedding-upgrade files carry no rerank_depth,
        # so every group key holds a NaN and the default groupby silently drops all of
        # them. That is how bge-base and e5-base went missing from the Pareto figure
        # while the caption still described them.
        for _, part in merged_model.groupby(
            ["mode", "embed_model_name", "rerank_model_name", "rerank_depth"], dropna=False
        ):
            row0 = part.iloc[0]
            depth = row0["rerank_depth"]
            if row0["mode"] == "baseline" and not pd.isna(depth):
                # The depth-sweep files re-run the unchanged Base alongside each depth.
                # That row is the same system already plotted as "Base"; its latency was
                # measured in a different batch, so plotting it again would put two
                # points for one configuration on the axis and invite a cross-batch
                # latency comparison. Skip it.
                continue
            if row0["mode"] == "baseline":
                full_label = f"{row0['embed_model_name']} | baseline"
            elif pd.isna(depth):
                # an embedding swap re-ranked at the default depth, not a depth sweep
                full_label = f"{row0['embed_model_name']} | rerank"
            else:
                full_label = f"{row0['embed_model_name']} | RR depth {int(depth)}"
            rows.append(
                {
                    "full_label": full_label,
                    "short_label": PARETO_SHORT.get(full_label, full_label),
                    "source_group": "model_upgrade",
                    "avg_retrieval_ms": retrieval_side_ms(part),
                    "ndcg_at_10": float(part["ndcg_at_10"].mean()),
                }
            )

    return pd.DataFrame(rows).drop_duplicates(subset=["full_label"]).sort_values("avg_retrieval_ms")


PARETO_CANDIDATES = [
    (8, 0),
    (8, 12),
    (8, -12),
    (-8, 0),
    (-8, 12),
    (-8, -12),
    (20, 0),
    (20, -14),
    (-20, 0),
    (-20, -14),
    (8, 24),
    (8, -24),
    (34, 0),
    (-34, 0),
]


def place_pareto_labels(ax, fig, table) -> None:
    """Label every point, trying offsets until the label clears what is already down.

    Hand-tuned offsets do not survive a data change: this figure has been rebuilt
    several times, and each round shifted a point far enough to bury one label under
    another. The markers are known before anything is placed, so they are obstacles
    from the start; each label then takes the first candidate offset that overlaps no
    placed label and contains no marker. A preferred offset from PARETO_OFFSETS is
    tried first, so a deliberate placement still wins when it is free.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    markers = [ax.transData.transform((row["avg_retrieval_ms"], row["ndcg_at_10"]))
               for _, row in table.iterrows()]
    placed: List = []
    # Left to right, so the crowded low-latency cluster gets first pick of its side.
    for _, row in table.sort_values("avg_retrieval_ms").iterrows():
        label = row["short_label"]
        preferred = PARETO_OFFSETS.get(label)
        candidates = PARETO_CANDIDATES
        if preferred is not None:
            candidates = [tuple(preferred[:2])] + [c for c in PARETO_CANDIDATES
                                                   if c != tuple(preferred[:2])]
        annotation = None
        for dx, dy in candidates:
            annotation = ax.annotate(
                label,
                xy=(row["avg_retrieval_ms"], row["ndcg_at_10"]),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=9,
                ha="left" if dx >= 0 else "right",
                va="center",
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.85),
                zorder=4,
            )
            fig.canvas.draw()
            box = annotation.get_window_extent(renderer)
            if not any(box.overlaps(other) for other in placed) and not any(
                box.contains(px, py) for px, py in markers
            ):
                break
            annotation.remove()
            annotation = None
        if annotation is None:
            # Every candidate collided. Keep the last one so the point is still
            # labelled, and let the overlap be visible rather than silently dropping it.
            annotation = ax.annotate(
                label,
                xy=(row["avg_retrieval_ms"], row["ndcg_at_10"]),
                xytext=PARETO_CANDIDATES[-1],
                textcoords="offset points",
                fontsize=9,
                ha="right",
                va="center",
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.85),
                zorder=4,
            )
        fig.canvas.draw()
        placed.append(annotation.get_window_extent(renderer))


def build_clean_pareto() -> None:
    table = build_pareto_table()
    if table.empty:
        return

    table.to_csv(BUNDLE_DIR / "accuracy_cost_pareto_clean.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(10.8, 6.4))
    color_map = {"baseline_family": "#4C78A8", "model_upgrade": "#E45756"}
    for group_name, part in table.groupby("source_group"):
        ax.scatter(
            part["avg_retrieval_ms"],
            part["ndcg_at_10"],
            s=90,
            c=color_map[group_name],
            edgecolors="#333333",
            linewidths=0.8,
            label="Baseline family" if group_name == "baseline_family" else "Model upgrades",
            zorder=3,
        )

    max_x = float(table["avg_retrieval_ms"].max())
    ax.set_xlim(-2, max_x + 18)
    # Headroom so a label can sit above the highest point (E5-base) without
    # colliding with it or leaving the axes.
    ax.set_ylim(float(table["ndcg_at_10"].min()) - 0.02, float(table["ndcg_at_10"].max()) + 0.02)

    place_pareto_labels(ax, fig, table)

    ax.set_xlabel("Average retrieval latency per question (ms)")
    ax.set_ylabel("nDCG@10 on validated-78")
    ax.set_title("Accuracy-Latency Trade-off")
    ax.grid(alpha=0.8, linestyle="--", linewidth=0.6)
    ax.legend(frameon=True, loc="lower right")
    fig.savefig(BUNDLE_DIR / "fig_accuracy_cost_pareto_clean.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# `paper_support_analysis.py` names the stage-retention table after its analysis
# prefix, and the re-ranker-family run wrote its own copy under `newrr_eval/`.
# The re-ranker copy is preferred because it is the one that covers every
# re-ranker on a single benchmark, which is what the figure is cited for.
_STAGE_RETENTION_CANDIDATES = [
    RESULT_DIR / "newrr_eval" / "newrr_stage_gold_retention.csv",
    RESULT_DIR / "supp_strong_baselines_validated_stage_gold_retention.csv",
    RESULT_DIR / "paper_stage_gold_retention.csv",
]


def _find_stage_retention() -> Optional[Path]:
    for path in _STAGE_RETENTION_CANDIDATES:
        if path.exists():
            return path
    hits = sorted(RESULT_DIR.glob("*_stage_gold_retention.csv"))
    return hits[0] if hits else None


# This figure is about the re-ranker family, so its labels name the re-ranker
# that was added to an otherwise identical dense pipeline. The generic
# MODE_DISPLAY names ("Rerank", "bge-b") are too terse to read off a legend.
STAGE_RETENTION_LABELS = {
    "baseline": "Base (no re-rank)",
    "rerank": "+ MiniLM-L6",
    "rerank_bge_base": "+ bge-reranker-base",
    "rerank_medcpt": "+ MedCPT",
    "rerank_llm": "+ LLM listwise",
    "rerank_bge_m3": "+ bge-reranker-v2-m3",
}


def build_stage_retention_figure() -> None:
    stage_path = _find_stage_retention()
    if stage_path is None:
        return

    df = pd.read_csv(stage_path)
    keep = [
        "control_dense_only",
        "bm25_only",
        "hybrid_bm25",
        "rrf_hybrid",
        "baseline",
        "rerank",
        "rerank_bge_base",
        "rerank_medcpt",
        "rerank_llm",
        "rerank_bge_m3",
    ]
    df = df[df["mode"].isin(keep)].copy()
    if df.empty:
        return
    # Plot in the narrative order (weakest to strongest re-ranker) rather than by
    # final score, so the legend reads the same way as the re-ranker table.
    df["_order"] = df["mode"].map({m: i for i, m in enumerate(keep)})
    df = df.sort_values("_order")

    stage_columns = [
        ("retrieved_stage_hit_rate", "Retrieved"),
        ("dedup_stage_hit_rate", "Dedup"),
        ("ranked_stage_hit_rate", "Ranked"),
        ("final_stage_hit_rate", "Final"),
    ]
    x = np.arange(len(stage_columns))

    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    for _, row in df.iterrows():
        y = [float(row[col]) for col, _ in stage_columns]
        label = STAGE_RETENTION_LABELS.get(
            row["mode"], MODE_DISPLAY.get(row["mode"], row["mode"]))
        ax.plot(
            x,
            y,
            marker="o",
            linewidth=2.0,
            markersize=5.5,
            label=label,
        )

    ax.set_xticks(x)
    ax.set_xticklabels([label for _, label in stage_columns])
    # Scale to the data instead of a fixed window: the original bracket was tuned
    # for the 6-mode run and would clip a worse (or waste space on a better) set.
    values = df[[col for col, _ in stage_columns]].to_numpy(dtype=float)
    ax.set_ylim(max(0.50, float(values.min()) - 0.05), min(1.02, float(values.max()) + 0.01))
    ax.set_xlabel("Pipeline stage")
    ax.set_ylabel("Gold evidence retention rate")
    ax.set_title("Gold Evidence Retention Across Retrieval Stages")
    ax.grid(alpha=0.8, linestyle="--", linewidth=0.6)
    ax.legend(ncol=2, frameon=True, loc="lower left", fontsize=9)
    fig.savefig(BUNDLE_DIR / "fig_stage_retention_validated.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_status_and_asset_map(answer_summary: pd.DataFrame, answer_meta: Dict[str, str], graded_summary: pd.DataFrame, graded_meta: Dict[str, str]) -> None:
    status_lines: List[str] = [
        "# Human Eval Status",
        "",
        f"- Answer-level source: `{answer_meta.get('score_source', 'missing')}`",
    ]
    if answer_meta.get("score_file"):
        status_lines.append(f"- Answer-level file: `{answer_meta['score_file']}`")
    status_lines.append(f"- Graded-relevance source: `{graded_meta.get('score_source', 'missing')}`")
    if graded_meta.get("score_file"):
        status_lines.append(f"- Graded-relevance file: `{graded_meta['score_file']}`")
    status_lines.append("")

    score_sources = {
        answer_meta.get("score_source", "missing"),
        graded_meta.get("score_source", "missing"),
    }
    if score_sources == {"missing"}:
        status_lines.extend(
            [
                "## Status",
                "",
                "- No completed human evaluation is present.",
                "- No human-evaluation or inter-annotator-agreement claim can be made.",
                "",
            ]
        )
    elif "autofilled" in score_sources:
        status_lines.extend(
            [
                "## Warning",
                "",
                "- The current files are `*_AUTOFILLED.csv`.",
                "- They contain `auto:` notes and heuristic-filled scores.",
                "- They cannot be reported as `human evaluation` or `manual annotation` in the paper.",
                "- They can only be used as an internal sanity check unless replaced by real human scoring.",
                "",
            ]
        )
    elif (not answer_summary.empty and not graded_summary.empty
          and bool(answer_summary["valid_for_human_eval_claim"].iloc[0])
          and bool(graded_summary["valid_for_human_eval_claim"].iloc[0])):
        status_lines.extend(
            [
                "## Status",
                "",
                "- Completed human files passed the packet validity checks.",
                "- Report annotator counts and agreement from the checked files.",
                "",
            ]
        )
    else:
        status_lines.extend(
            [
                "## Status",
                "",
                "- Human-evaluation packets are incomplete or failed validity checks.",
                "- They cannot support a human-evaluation claim.",
                "",
            ]
        )

    status_lines.extend(
        [
            "## Separate Automatic Evaluation",
            "",
            "- `p4_judge_answer_eval.csv` contains automatic answer judgments when present.",
            "- `p4_judge_relevance_eval.csv` contains automatic distinct-source relevance judgments when present.",
            "- Both use `annotation_source = llm_judge_automatic` and "
            "`valid_for_human_eval_claim = False`; they may be reported only as automatic evaluation.",
            "",
        ]
    )

    (BUNDLE_DIR / "HUMAN_EVAL_STATUS.md").write_text("\n".join(status_lines), encoding="utf-8")

    lines: List[str] = [
        "# Paper Asset Map",
        "",
        "## Main-paper quantitative sources",
        "",
        "- Table 1: `paper_table_main_baselines.csv`",
        "  Validated-78 retrieval leaderboard.",
        "- Table 2: `rev_table_rerankers.csv`",
        "  Six second-stage variants across orig78, iso78, and exp155.",
        "- Table 3: `rev_table_inversion.csv`, `rev_table_judge.csv`, "
        "`rev_table_judge_ci.csv`, and `rev_table_spearman.csv`",
        "  Automatic answer quality, question-balanced distinct-source relevance, "
        "confidence intervals, and system-level rank correlations.",
        "",
        "## Generated figures",
        "",
        "- `fig_main_retrieval.png` and `fig_answer_rates.png`: main performance summaries.",
        "- `fig_stage_retention_validated.png`: stage-wise gold-page retention.",
        "- `fig_heatmap_retrieval_ndcg.png` and `fig_heatmap_insufficient.png`: "
        "non-duplicated topic-level heatmaps with canonical labels.",
        "",
        "## Manually maintained conceptual diagrams",
        "",
        "- `RAG 检索到生成的简化流程图.png`",
        "- `黄金证据保留丢失机制图.png`",
        "  These illustrations contain no measured values and are not regenerated from CSVs.",
    ]

    if not answer_summary.empty and bool(answer_summary["valid_for_human_eval_claim"].iloc[0]):
        lines.extend(
            [
                "- Table 3: `paper_table_answer_eval.csv`",
                "  Can be used as manual answer-level blind evaluation.",
            ]
        )
    else:
        lines.extend(
            [
                "- No valid manual answer-level evaluation is available.",
                "  Automatic answer scores may be reported only with their automatic provenance.",
            ]
        )

    if not graded_summary.empty and bool(graded_summary["valid_for_human_eval_claim"].iloc[0]):
        lines.extend(
            [
                "- Table 4: `paper_table_graded_relevance.csv`",
                "  Can be used as manual graded-relevance evaluation.",
            ]
        )
    else:
        lines.extend(
            [
                "- No valid manual graded-relevance evaluation is available.",
                "  Automatic distinct-source relevance may be reported only as LLM-judge output.",
            ]
        )

    # Derived from the files that actually exist in the bundle, not from a
    # hand-maintained list. The list previously named several sources that had
    # since been renamed (`supp_strong_baselines_full100_metrics_by_subset.csv`
    # is now `paper_metrics_by_subset.csv`, and the two `paper_table_*` answer
    # tables were replaced by `rev_table_judge.csv`), so the map described a
    # bundle that was not there. Reading the directory keeps the description
    # true by construction.
    appendix_note = {
        "supp_bm25_grid_summary.csv": "BM25 parameter sweep",
        "supp_pool_sweep_summary.csv": "pool-size ablation",
        "supp_dedup_sweep_summary.csv": "URL dedup-cap ablation",
        "supp_finalk_sweep_summary.csv": "final evidence count ablation",
        "supp_rerank_depth_summary.csv": "rerank depth ablation",
        "supp_source_ablation_summary.csv": "source-mixture ablation",
        "supp_query_normalization_overall.csv": "query-normalization analysis",
        "paper_metrics_by_subset.csv": "full100 / audited / general-held-out split comparison",
        "paper_metrics_full_vs_audited.csv": "full-pool versus audited comparison",
        "paper_pairwise_vs_baseline.csv": "paired significance against Base",
        "accuracy_cost_pareto_clean.csv": "numerical source table for the clean Pareto figure",
        "rev_table_benchmark.csv": "benchmark sizes across the three result views",
        "rev_table_rerankers.csv": "re-ranker comparison across the three result views",
        "rev_table_inversion.csv": "aligned retrieval, relevance, and answer metrics",
        "rev_table_judge.csv": "automatic answer and question-balanced relevance summaries",
        "rev_table_judge_ci.csv": "automatic answer-score confidence intervals",
        "rev_table_spearman.csv": "system-level rank correlations",
        "rev_table_relevance_by_source.csv": "distinct-source relevance by source category",
    }
    present = sorted(p.name for p in BUNDLE_DIR.glob("*.csv"))
    lines.extend(["", "## Appendix", ""])
    listed = [n for n in present if n in appendix_note]
    for name in listed:
        lines.append(f"- `{name}`: {appendix_note[name]}")
    unlisted = [n for n in present if n not in appendix_note]
    for name in unlisted:
        lines.append(f"- `{name}`")
    if not present:
        lines.append("_No CSVs in the bundle._")

    lines.extend(
        [
            "",
            "## Human Eval",
            "",
            "- `HUMAN_EVAL_STATUS.md`: whether the current annotation files are valid for paper use",
            "- `rev_table_judge.csv`: automatic LLM-judge scores, not human annotation "
            "(every row carries `valid_for_human_eval_claim = False`); cite it only as "
            "an automatic evaluation.",
            "",
            "## Curated Folder",
            "",
            "- `paper_assets_curated/`: compact folder containing only paper-ready tables, figures, and key appendix summaries",
            "",
        ]
    )

    (BUNDLE_DIR / "PAPER_ASSET_MAP.md").write_text("\n".join(lines), encoding="utf-8")


def export_curated_paper_assets() -> None:
    PAPER_DIR.mkdir(parents=True, exist_ok=True)
    # Every CSV and PNG the bundle holds is curated, plus the two status docs.
    # Naming them one by one meant a renamed table silently stopped being
    # copied (the copy loop skips missing sources without a word), so the
    # curated folder could quietly omit a table the paper cites.
    curated_files = (
        sorted(p.name for p in BUNDLE_DIR.glob("*.csv"))
        + sorted(p.name for p in BUNDLE_DIR.glob("*.png"))
        + ["HUMAN_EVAL_STATUS.md", "PAPER_ASSET_MAP.md"]
    )
    copied = []
    for name in curated_files:
        src = BUNDLE_DIR / name
        if src.exists():
            shutil.copy2(src, PAPER_DIR / name)
            copied.append(name)

    readme_lines = [
        "# Curated Paper Assets",
        "",
        "This folder contains the compact set of tables and figures to use while writing the paper.",
        "Generated by `curate_paper_assets.py`; the list below is what was actually copied.",
        "",
        "## Main paper",
        "",
        "- `paper_table_main_baselines.csv`",
        "- `paper_table_model_upgrades.csv`",
        "- `rev_table_rerankers.csv`",
        "- `fig_accuracy_cost_pareto_clean.png`",
        "- `fig_stage_retention_validated.png`",
        "- `fig_topic_heatmap_ndcg.png`",
        "",
        "## Appendix / support",
        "",
    ]
    readme_lines += [f"- `{name}`" for name in copied if name.endswith(".csv")]
    readme_lines += [
        "",
        "## Human eval",
        "",
        "- Check `HUMAN_EVAL_STATUS.md` before citing any human-eval table.",
        "- `rev_table_judge.csv` holds automatic LLM-judge scores, not human "
        "annotation; cite it only as an automatic evaluation.",
        "",
    ]
    (PAPER_DIR / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")


def main() -> None:
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_DIR.mkdir(parents=True, exist_ok=True)

    build_main_tables()
    build_clean_pareto()
    build_stage_retention_figure()

    answer_summary, answer_meta = build_answer_eval_summary()
    graded_summary, graded_meta = build_graded_relevance_summary()

    if not answer_summary.empty:
        answer_summary.to_csv(BUNDLE_DIR / "paper_table_answer_eval.csv", index=False, encoding="utf-8-sig")
    if not graded_summary.empty:
        graded_summary.to_csv(BUNDLE_DIR / "paper_table_graded_relevance.csv", index=False, encoding="utf-8-sig")

    write_status_and_asset_map(answer_summary, answer_meta, graded_summary, graded_meta)
    export_curated_paper_assets()
    print(f"Updated curated assets in: {BUNDLE_DIR}")


if __name__ == "__main__":
    main()
