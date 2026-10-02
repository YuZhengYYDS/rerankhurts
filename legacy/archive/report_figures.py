from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE_DIR = Path(__file__).resolve().parent

BASELINE_FILE = BASE_DIR / "rag_results_baseline_small.csv"
RERANK_FILE = BASE_DIR / "rag_results_rerank_small.csv"

OUT_01 = BASE_DIR / "report_01_overall_insufficient.png"
OUT_02 = BASE_DIR / "report_02_overall_answer_length.png"
OUT_03 = BASE_DIR / "report_03_topic_slope_insufficient.png"
OUT_04 = BASE_DIR / "report_04_topic_delta_insufficient.png"
OUT_05 = BASE_DIR / "report_05_topic_insufficient_bar.png"
OUT_06 = BASE_DIR / "report_06_topic_answer_length_bar.png"
OUT_07 = BASE_DIR / "report_07_topic_insufficient_heatmap.png"
OUT_08 = BASE_DIR / "report_08_corpus_composition.png"


def ensure_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")


def topic_from_qid(qid):
    n = int(str(qid).replace("q", ""))
    if 1 <= n <= 20:
        return "NSCLC"
    if 21 <= n <= 30:
        return "SCLC"
    if 31 <= n <= 50:
        return "Breast"
    if 51 <= n <= 60:
        return "Colon"
    if 61 <= n <= 70:
        return "AML"
    if 71 <= n <= 80:
        return "CLL"
    return "General"


def normalize_insufficient(x):
    s = str(x).strip().lower()
    if s == "true":
        return 1
    if s == "false":
        return 0
    return np.nan


def set_plot_style():
    plt.rcParams.update({
        "font.size": 12,
        "axes.titlesize": 20,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#2F2F2F",
        "axes.linewidth": 0.9,
        "grid.color": "#D7DBE2",
        "grid.linestyle": "--",
        "grid.linewidth": 0.8,
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
    })


def add_bar_labels(ax, bars, fmt="{:.2f}", offset=0.01):
    for b in bars:
        h = b.get_height()
        ax.text(
            b.get_x() + b.get_width() / 2,
            h + offset,
            fmt.format(h),
            ha="center",
            va="bottom",
            fontsize=11
        )


def compute_adjusted_label_positions(y_values, min_gap=0.025):
    """
    给 slope chart 左侧标签做纵向错位，避免重叠。
    """
    indexed = sorted(enumerate(y_values), key=lambda x: x[1])
    adjusted = [0.0] * len(y_values)

    last_y = None
    for idx, y in indexed:
        if last_y is None:
            adjusted[idx] = y
            last_y = y
        else:
            if y - last_y < min_gap:
                adjusted[idx] = last_y + min_gap
            else:
                adjusted[idx] = y
            last_y = adjusted[idx]

    return adjusted


def load_results():
    ensure_file(BASELINE_FILE)
    ensure_file(RERANK_FILE)

    baseline = pd.read_csv(BASELINE_FILE)
    rerank = pd.read_csv(RERANK_FILE)

    baseline["topic"] = baseline["qid"].apply(topic_from_qid)
    rerank["topic"] = rerank["qid"].apply(topic_from_qid)

    baseline["insuf"] = baseline["insufficient_evidence"].apply(normalize_insufficient)
    rerank["insuf"] = rerank["insufficient_evidence"].apply(normalize_insufficient)

    baseline["ans_len"] = baseline["answer"].fillna("").astype(str).str.split().apply(len)
    rerank["ans_len"] = rerank["answer"].fillna("").astype(str).str.split().apply(len)

    baseline["mode"] = "baseline"
    rerank["mode"] = "rerank"

    return baseline, rerank


def build_stats(baseline, rerank):
    combined = pd.concat([
        baseline[["mode", "topic", "insuf", "ans_len"]],
        rerank[["mode", "topic", "insuf", "ans_len"]]
    ], ignore_index=True)

    overall_stats = combined.groupby("mode", as_index=False).agg(
        insufficient_rate=("insuf", "mean"),
        avg_answer_length=("ans_len", "mean"),
    )

    topic_stats = combined.groupby(["topic", "mode"], as_index=False).agg(
        insufficient_rate=("insuf", "mean"),
        avg_answer_length=("ans_len", "mean"),
    )

    return overall_stats, topic_stats


def make_overall_insufficient(overall_stats):
    blue = "#3B82F6"
    orange = "#F59E0B"

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    vals = overall_stats["insufficient_rate"].tolist()
    bars = ax.bar(
        overall_stats["mode"].str.title(),
        vals,
        color=[blue, orange],
        edgecolor="#333333",
        linewidth=0.8,
        width=0.56
    )

    ax.set_title("Overall Insufficient-Evidence Rate")
    ax.set_ylabel("Rate")
    ax.set_ylim(0, max(vals) * 1.35 if max(vals) > 0 else 1)
    ax.grid(axis="y")
    ax.set_axisbelow(True)

    add_bar_labels(ax, bars, fmt="{:.2f}", offset=0.01)

    fig.savefig(OUT_01, dpi=300)
    plt.close(fig)


def make_overall_answer_length(overall_stats):
    blue = "#3B82F6"
    orange = "#F59E0B"

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    vals = overall_stats["avg_answer_length"].tolist()
    bars = ax.bar(
        overall_stats["mode"].str.title(),
        vals,
        color=[blue, orange],
        edgecolor="#333333",
        linewidth=0.8,
        width=0.56
    )

    ax.set_title("Overall Average Answer Length")
    ax.set_ylabel("Words")
    ax.set_ylim(0, max(vals) * 1.25 if max(vals) > 0 else 1)
    ax.grid(axis="y")
    ax.set_axisbelow(True)

    for b in bars:
        h = b.get_height()
        ax.text(
            b.get_x() + b.get_width() / 2,
            h + 0.8,
            f"{h:.1f}",
            ha="center",
            va="bottom",
            fontsize=11
        )

    fig.savefig(OUT_02, dpi=300)
    plt.close(fig)


def make_topic_slope_insufficient(topic_stats):
    green = "#10B981"
    red = "#EF4444"
    gray = "#6B7280"

    topic_order = ["NSCLC", "SCLC", "Breast", "Colon", "AML", "CLL", "General"]
    pivot = topic_stats.pivot(index="topic", columns="mode", values="insufficient_rate")
    plot_df = pivot.loc[topic_order].reset_index()

    baseline_vals = plot_df["baseline"].tolist()
    adjusted_y = compute_adjusted_label_positions(baseline_vals, min_gap=0.028)

    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    x0, x1 = 0, 1

    for i, row in plot_df.iterrows():
        b = row["baseline"]
        r = row["rerank"]

        if r < b:
            c = green
        elif r > b:
            c = red
        else:
            c = gray

        ax.plot([x0, x1], [b, r], marker="o", linewidth=3.0, markersize=8, color=c, alpha=0.95)

        # 左侧标签做错位
        ax.text(
            x0 - 0.08,
            adjusted_y[i],
            row["topic"],
            ha="right",
            va="center",
            fontsize=12,
            color="#111827"
        )

        # 标签和真实点之间连一条细线
        if adjusted_y[i] != b:
            ax.plot(
                [x0 - 0.03, x0],
                [adjusted_y[i], b],
                color="#9CA3AF",
                linewidth=1.0
            )

    ax.set_xlim(-0.25, 1.25)
    ax.set_xticks([0, 1], ["Baseline", "Rerank"])
    ax.set_ylabel("Insufficient-Evidence Rate")
    ax.set_title("Topic-Level Shift After Reranking")
    ax.grid(axis="y")
    ax.set_axisbelow(True)

    fig.savefig(OUT_03, dpi=300)
    plt.close(fig)


def make_topic_delta_insufficient(topic_stats):
    green = "#10B981"
    red = "#EF4444"
    gray = "#6B7280"

    topic_order = ["NSCLC", "SCLC", "Breast", "Colon", "AML", "CLL", "General"]
    pivot = topic_stats.pivot(index="topic", columns="mode", values="insufficient_rate")
    delta_df = pivot.loc[topic_order].reset_index()
    delta_df["delta"] = delta_df["rerank"] - delta_df["baseline"]
    delta_df = delta_df.sort_values("delta")

    colors = [green if x < 0 else red if x > 0 else gray for x in delta_df["delta"]]

    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    bars = ax.barh(
        delta_df["topic"],
        delta_df["delta"],
        color=colors,
        edgecolor="#333333",
        linewidth=0.8
    )

    ax.axvline(0, color="#111827", linewidth=1.2)
    ax.set_title("Change in Insufficient-Evidence Rate\n(Rerank − Baseline)")
    ax.set_xlabel("Negative is better")
    ax.grid(axis="x")
    ax.set_axisbelow(True)

    for bar, val in zip(bars, delta_df["delta"]):
        xpos = val + (0.01 if val >= 0 else -0.01)
        ha = "left" if val >= 0 else "right"
        ax.text(
            xpos,
            bar.get_y() + bar.get_height() / 2,
            f"{val:+.2f}",
            va="center",
            ha=ha,
            fontsize=11
        )

    fig.savefig(OUT_04, dpi=300)
    plt.close(fig)


def make_topic_insufficient_bar(topic_stats):
    blue = "#3B82F6"
    orange = "#F59E0B"

    topic_order = ["NSCLC", "SCLC", "Breast", "Colon", "AML", "CLL", "General"]
    pivot = topic_stats.pivot(index="topic", columns="mode", values="insufficient_rate").loc[topic_order]

    x = np.arange(len(topic_order))
    width = 0.36

    fig, ax = plt.subplots(figsize=(9.4, 5.4))
    bars1 = ax.bar(
        x - width / 2,
        pivot["baseline"].values,
        width,
        label="Baseline",
        color=blue,
        edgecolor="#333333",
        linewidth=0.8
    )
    bars2 = ax.bar(
        x + width / 2,
        pivot["rerank"].values,
        width,
        label="Rerank",
        color=orange,
        edgecolor="#333333",
        linewidth=0.8
    )

    ax.set_xticks(x)
    ax.set_xticklabels(topic_order, rotation=20)
    ax.set_ylabel("Rate")
    ax.set_title("Insufficient-Evidence Rate by Topic")
    ax.legend(frameon=False)
    ax.grid(axis="y")
    ax.set_axisbelow(True)

    add_bar_labels(ax, bars1, fmt="{:.2f}", offset=0.01)
    add_bar_labels(ax, bars2, fmt="{:.2f}", offset=0.01)

    fig.savefig(OUT_05, dpi=300)
    plt.close(fig)


def make_topic_answer_length_bar(topic_stats):
    blue = "#3B82F6"
    orange = "#F59E0B"

    topic_order = ["NSCLC", "SCLC", "Breast", "Colon", "AML", "CLL", "General"]
    pivot = topic_stats.pivot(index="topic", columns="mode", values="avg_answer_length").loc[topic_order]

    x = np.arange(len(topic_order))
    width = 0.36

    fig, ax = plt.subplots(figsize=(9.4, 5.4))
    bars1 = ax.bar(
        x - width / 2,
        pivot["baseline"].values,
        width,
        label="Baseline",
        color=blue,
        edgecolor="#333333",
        linewidth=0.8
    )
    bars2 = ax.bar(
        x + width / 2,
        pivot["rerank"].values,
        width,
        label="Rerank",
        color=orange,
        edgecolor="#333333",
        linewidth=0.8
    )

    ax.set_xticks(x)
    ax.set_xticklabels(topic_order, rotation=20)
    ax.set_ylabel("Words")
    ax.set_title("Average Answer Length by Topic")
    ax.legend(frameon=False)
    ax.grid(axis="y")
    ax.set_axisbelow(True)

    for bars in [bars1, bars2]:
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + 0.8,
                f"{h:.1f}",
                ha="center",
                va="bottom",
                fontsize=10
            )

    fig.savefig(OUT_06, dpi=300)
    plt.close(fig)


def make_topic_insufficient_heatmap(topic_stats):
    topic_order = ["NSCLC", "SCLC", "Breast", "Colon", "AML", "CLL", "General"]
    pivot = topic_stats.pivot(index="topic", columns="mode", values="insufficient_rate").loc[topic_order]

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    im = ax.imshow(pivot.values, cmap="OrRd", aspect="auto", vmin=0, vmax=max(0.5, np.nanmax(pivot.values)))

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(["Baseline", "Rerank"])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Heatmap of Insufficient-Evidence Rate")

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.iloc[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", color="black", fontsize=11)

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.savefig(OUT_07, dpi=300)
    plt.close(fig)


def make_corpus_composition():
    light_blue = "#DBEAFE"

    # 这里沿用你当前 small corpus inspect 结果
    corpus_counts = pd.DataFrame({
        "source": ["Breast", "NSCLC", "AML", "Colon", "CLL", "SCLC"],
        "chunks": [55, 48, 26, 19, 16, 14]
    }).sort_values("chunks", ascending=True)

    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    bars = ax.barh(
        corpus_counts["source"],
        corpus_counts["chunks"],
        color=light_blue,
        edgecolor="#333333",
        linewidth=0.8
    )

    ax.set_title("Small Oncology Corpus Composition")
    ax.set_xlabel("Number of Chunks")
    ax.grid(axis="x")
    ax.set_axisbelow(True)

    for b in bars:
        w = b.get_width()
        ax.text(
            w + 0.8,
            b.get_y() + b.get_height() / 2,
            f"{int(w)}",
            va="center",
            ha="left",
            fontsize=11
        )

    fig.savefig(OUT_08, dpi=300)
    plt.close(fig)


def main():
    set_plot_style()

    baseline, rerank = load_results()
    overall_stats, topic_stats = build_stats(baseline, rerank)

    make_overall_insufficient(overall_stats)
    make_overall_answer_length(overall_stats)
    make_topic_slope_insufficient(topic_stats)
    make_topic_delta_insufficient(topic_stats)
    make_topic_insufficient_bar(topic_stats)
    make_topic_answer_length_bar(topic_stats)
    make_topic_insufficient_heatmap(topic_stats)
    make_corpus_composition()

    print("Saved figures:")
    print(OUT_01)
    print(OUT_02)
    print(OUT_03)
    print(OUT_04)
    print(OUT_05)
    print(OUT_06)
    print(OUT_07)
    print(OUT_08)


if __name__ == "__main__":
    main()