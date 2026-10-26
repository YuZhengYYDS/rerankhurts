from pathlib import Path
import json
import os
import shutil

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


from rerankhuts.paths import oncology_path


BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = Path(os.getenv("RESULT_DIR", str(BASE_DIR / "result")))
RESULT_DIR.mkdir(parents=True, exist_ok=True)

RETRIEVAL_OVERALL = RESULT_DIR / "retrieval_metrics_overall.csv"
RETRIEVAL_BY_TOPIC = RESULT_DIR / "retrieval_metrics_by_topic.csv"
ANSWER_OVERALL = RESULT_DIR / "analysis_overall.csv"
ANSWER_BY_TOPIC = RESULT_DIR / "analysis_by_topic.csv"
CORPUS_FILE = oncology_path("corpus_chunks_v1.jsonl", root=BASE_DIR)

FIG_DPI = 300
FONT_SIZE = 11
TITLE_SIZE = 14
LABEL_SIZE = 12
TICK_SIZE = 10
LEGEND_SIZE = 10
EDGE_COLOR = "#444444"
GRID_COLOR = "#D9D9D9"

# Order and labels follow the paper's main results table. Every mode the paper
# plots must appear here: anything missing falls back to its raw identifier in
# the legend and sorts to the end, which is how the BM25 and fusion rows used to
# end up labelled "bm25_base" / "rrf_hybrid" at the far right of the figure.
MODE_ORDER_HINTS = {
    "control_dense_only": 0,
    "control_sparse_only": 1,
    "control_hybrid": 2,
    "baseline": 3,
    "hybrid_bm25": 4,
    "rrf_hybrid": 5,
    "rerank": 6,
    "rerank_bge_base": 7,
    "rerank_bge_m3": 8,
    "rerank_medcpt": 9,
    "rerank_llm": 10,
    "rrf_hybrid_rerank": 11,
    "bm25_base": 12,
    "bm25_only": 13,
    "ablation_no_dedup": 14,
    "ablation_small_pool": 15,
    "hybrid_rerank": 16,
}

MODE_LABELS = {
    "control_dense_only": "Dense",
    "control_sparse_only": "Sparse",
    "control_hybrid": "Hybrid",
    "baseline": "Base",
    "hybrid_bm25": "Hybrid-BM25",
    "rrf_hybrid": "RRF",
    "rerank": "Rerank (MiniLM)",
    "rerank_bge_base": "Rerank (bge-base)",
    "rerank_bge_m3": "Rerank (bge-m3)",
    "rerank_medcpt": "Rerank (MedCPT)",
    "rerank_llm": "Rerank (LLM)",
    "rrf_hybrid_rerank": "RRF+Rerank",
    "bm25_base": "BM25+Dedup",
    "bm25_only": "BM25",
    "ablation_no_dedup": "NoDedup",
    "ablation_small_pool": "SmallPool",
    "hybrid_rerank": "Hyb+RR",
}

# Tableau-10. It has to hold every mode a figure plots: `mode_colors` used to wrap
# with `idx % len(PALETTE)`, so a 10-system bar chart silently gave Base and
# SmallPool the same orange and drew two different systems in one colour.
PALETTE = [
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#E45756",
    "#72B7B2",
    "#B279A2",
    "#FF9DA6",
    "#9D755D",
    "#EDC948",
    "#BAB0AC",
]


def ensure_file(path: str):
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} not found")


def set_paper_style():
    plt.rcParams.update({
        "font.size": FONT_SIZE,
        "axes.titlesize": TITLE_SIZE,
        "axes.labelsize": LABEL_SIZE,
        "xtick.labelsize": TICK_SIZE,
        "ytick.labelsize": TICK_SIZE,
        "legend.fontsize": LEGEND_SIZE,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": EDGE_COLOR,
        "axes.linewidth": 0.8,
        "grid.color": GRID_COLOR,
        "grid.linestyle": "--",
        "grid.linewidth": 0.6,
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
    })


def ordered_modes(modes):
    return sorted(modes, key=lambda mode: (MODE_ORDER_HINTS.get(mode, 100), mode))


def display_mode(mode):
    return MODE_LABELS.get(str(mode), str(mode))


def mode_colors(modes):
    """One colour per mode, and never a repeat.

    Cycling the palette would draw two different systems in one colour, which reads
    as a duplicated series rather than as a bug. Extend PALETTE instead.
    """
    modes = list(modes)
    if len(modes) > len(PALETTE):
        raise ValueError(
            f"{len(modes)} modes but only {len(PALETTE)} palette colours; "
            "extend PALETTE so every series stays distinguishable"
        )
    return {mode: PALETTE[idx] for idx, mode in enumerate(modes)}


def add_value_labels(ax, bars, fmt="{:.3f}", fontsize=9, y_offset=0.01):
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + y_offset,
            fmt.format(height),
            ha="center",
            va="bottom",
            fontsize=fontsize,
        )


def plot_grouped_metrics(
    df,
    metrics,
    labels,
    title,
    save_path,
    ylabel="Score",
    ylim=None,
    value_fmt="{:.3f}",
    annotate=True,
):
    modes = ordered_modes(df["mode"].astype(str).tolist())
    colors = mode_colors(modes)
    num_modes = max(len(modes), 1)
    width = 0.8 / num_modes
    x = list(range(len(metrics)))

    fig, ax = plt.subplots(figsize=(8.8, 5.4))

    for idx, mode in enumerate(modes):
        row = df[df["mode"] == mode].iloc[0]
        values = [row[metric] for metric in metrics]
        shift = (idx - (num_modes - 1) / 2) * width
        bars = ax.bar(
            [pos + shift for pos in x],
            values,
            width=width,
            label=display_mode(mode),
            color=colors[mode],
            edgecolor=EDGE_COLOR,
            linewidth=0.6,
        )

        if annotate:
            offset = 0.01
            if ylim is not None:
                offset = (ylim[1] - ylim[0]) * 0.015
            add_value_labels(ax, bars, fmt=value_fmt, y_offset=offset)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=12)
    ax.grid(axis="y", alpha=0.8)
    ax.set_axisbelow(True)

    if ylim is not None:
        ax.set_ylim(*ylim)

    # Legend below the axes, not inside them: with eight series the in-axes box
    # covered the tallest bars and their value labels.
    ncol = min(4, max(len(modes), 1))
    legend = ax.legend(
        frameon=True,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=ncol,
        fontsize=8,
        borderpad=0.4,
        labelspacing=0.3,
        columnspacing=1.2,
        handlelength=1.2,
    )
    legend.get_frame().set_edgecolor("#CCCCCC")
    legend.get_frame().set_linewidth(0.8)
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.95)

    plt.tight_layout()
    plt.savefig(save_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_single_metric_by_mode(df, metric, title, save_path, ylabel, value_fmt="{:.3f}"):
    df = df.copy()
    df["mode_order"] = df["mode"].map(lambda x: MODE_ORDER_HINTS.get(str(x), 100))
    df = df.sort_values(["mode_order", "mode"])

    modes = df["mode"].astype(str).tolist()
    colors = mode_colors(modes)
    values = df[metric].tolist()

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    bars = ax.bar(
        [display_mode(mode) for mode in modes],
        values,
        color=[colors[mode] for mode in modes],
        edgecolor=EDGE_COLOR,
        linewidth=0.6,
    )

    upper = max(values + [0.01]) * 1.18
    ax.set_ylim(0, upper)
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=12)
    ax.grid(axis="y", alpha=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=20)

    add_value_labels(ax, bars, fmt=value_fmt, y_offset=upper * 0.02)

    plt.tight_layout()
    plt.savefig(save_path, dpi=FIG_DPI)
    plt.close(fig)


def plot_heatmap(df, value_col, title, save_path, cmap, vmin=None, vmax=None):
    pivot = df.pivot(index="topic", columns="mode", values=value_col).fillna(0)
    desired_topic_order = ["NSCLC", "SCLC", "Breast", "Colon", "AML", "CLL", "General"]
    topic_order = [topic for topic in desired_topic_order if topic in pivot.index]
    remaining_topics = [topic for topic in pivot.index if topic not in topic_order]
    pivot = pivot.reindex(topic_order + remaining_topics)

    ordered_cols = ordered_modes([str(col) for col in pivot.columns])
    pivot = pivot[ordered_cols]
    display_cols = [display_mode(col) for col in pivot.columns]

    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    image = ax.imshow(pivot.values, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(display_cols, rotation=0, ha="center", fontsize=9)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title(title, pad=12)

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            value = pivot.iloc[i, j]
            text_color = "white" if value >= 0.5 else "black"
            ax.text(j, i, f"{value:.3f}", ha="center", va="center", color=text_color, fontsize=9)

    cbar = plt.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=FIG_DPI)
    plt.close(fig)


def plot_corpus_composition(save_path, summary_path):
    counts = {}
    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            source_name = str(row.get("source_name", "unknown"))
            counts[source_name] = counts.get(source_name, 0) + 1

    summary_df = pd.DataFrame(
        [{"source_name": name, "num_chunks": count} for name, count in counts.items()]
    ).sort_values("num_chunks", ascending=False)
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    colors = PALETTE[:len(summary_df)]
    bars = ax.bar(
        summary_df["source_name"],
        summary_df["num_chunks"],
        color=colors,
        edgecolor=EDGE_COLOR,
        linewidth=0.6,
    )

    upper = max(summary_df["num_chunks"].tolist() + [1]) * 1.15
    ax.set_ylim(0, upper)
    ax.set_ylabel("Chunks")
    ax.set_title("Corpus Composition by Source", pad=12)
    ax.grid(axis="y", alpha=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=20)
    add_value_labels(ax, bars, fmt="{:.0f}", y_offset=upper * 0.02)

    plt.tight_layout()
    plt.savefig(save_path, dpi=FIG_DPI)
    plt.close(fig)


def main():
    ensure_file(RETRIEVAL_OVERALL)
    ensure_file(RETRIEVAL_BY_TOPIC)
    ensure_file(ANSWER_OVERALL)
    ensure_file(ANSWER_BY_TOPIC)

    set_paper_style()

    retrieval_overall = pd.read_csv(RETRIEVAL_OVERALL)
    retrieval_by_topic = pd.read_csv(RETRIEVAL_BY_TOPIC)
    answer_overall = pd.read_csv(ANSWER_OVERALL)
    answer_by_topic = pd.read_csv(ANSWER_BY_TOPIC)

    # The retrieval-only ablation arms generate no answers, so their answer-level
    # metrics are undefined and `analyze_results.py` records them as NaN rather
    # than as measured zeros. Leaving them in would draw an empty slot in an
    # answer-quality chart, which reads as a system that never once abstained and
    # answered in zero words -- the best possible score on both metrics. These
    # charts cover the systems that answer; the same modes' retrieval numbers are
    # in the retrieval tables and figures, where they are measured.
    answer_overall = answer_overall[answer_overall["insufficient_evidence_rate"].notna()].copy()
    answer_by_topic = answer_by_topic[answer_by_topic["insufficient_evidence_rate"].notna()].copy()

    plot_grouped_metrics(
        df=retrieval_overall,
        metrics=["recall_at_5", "recall_at_10", "mrr", "ndcg_at_10"],
        labels=["Recall@5", "Recall@10", "MRR", "nDCG@10"],
        title="Overall Page-Level Retrieval Metrics",
        save_path=RESULT_DIR / "fig_main_retrieval.png",
        ylabel="Score",
        ylim=(0, 1.08),
        value_fmt="{:.3f}",
        annotate=False,
    )

    plot_grouped_metrics(
        df=answer_overall,
        metrics=["insufficient_evidence_rate", "gold_url_hit_rate"],
        labels=["Insufficient\nEvidence Rate", "Gold URL\nHit Rate"],
        title="Overall Answer-Level Rates",
        save_path=RESULT_DIR / "fig_answer_rates.png",
        ylabel="Rate",
        ylim=(0, 1.05),
        value_fmt="{:.3f}",
    )

    plot_single_metric_by_mode(
        df=answer_overall,
        metric="avg_answer_word_count",
        title="Average Answer Length by Experiment",
        save_path=RESULT_DIR / "fig_answer_length.png",
        ylabel="Words",
        value_fmt="{:.1f}",
    )

    # The paper bundle references this heatmap under two names: `fig_topic_retrieval.png`
    # in the appendix and `fig_topic_heatmap_ndcg.png` in the main text. Both were
    # previously written by different scripts, so the main-text copy could silently go
    # stale. Draw it once here and publish it under both names.
    topic_ndcg_path = RESULT_DIR / "fig_topic_retrieval.png"
    plot_heatmap(
        df=retrieval_by_topic,
        value_col="ndcg_at_10",
        title="Page-Level Retrieval nDCG@10 by Topic",
        save_path=topic_ndcg_path,
        cmap="YlGnBu",
        vmin=0,
        vmax=1.0,
    )
    shutil.copy2(topic_ndcg_path, RESULT_DIR / "fig_topic_heatmap_ndcg.png")

    plot_heatmap(
        df=answer_by_topic,
        value_col="insufficient_evidence_rate",
        title="Insufficient Evidence Rate by Topic",
        save_path=RESULT_DIR / "fig_topic_insufficient.png",
        cmap="OrRd",
        vmin=0,
        vmax=max(0.5, answer_by_topic["insufficient_evidence_rate"].max()),
    )

    plot_heatmap(
        df=answer_by_topic,
        value_col="gold_url_hit_rate",
        title="Gold URL Hit Rate by Topic",
        save_path=RESULT_DIR / "fig_topic_gold_hit.png",
        cmap="Blues",
        vmin=0,
        vmax=1.0,
    )

    plot_corpus_composition(
        save_path=RESULT_DIR / "fig_corpus_composition.png",
        summary_path=RESULT_DIR / "corpus_source_summary.csv",
    )

    print("Saved figures:")
    print("- fig_main_retrieval.png")
    print("- fig_topic_retrieval.png")
    print("- fig_topic_heatmap_ndcg.png")
    print("- fig_answer_rates.png")
    print("- fig_answer_length.png")
    print("- fig_topic_insufficient.png")
    print("- fig_topic_gold_hit.png")
    print("- fig_corpus_composition.png")


if __name__ == "__main__":
    main()
