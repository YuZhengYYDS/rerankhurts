from pathlib import Path
import os

import matplotlib
matplotlib.use("Agg")

import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]


def _canonical_mode_display():
    """The paper's mode labels, from the one file that defines them.

    These labels used to be a second, hand-kept copy, and it drifted: the map
    here still named `hybrid_rerank`, a mode the pipeline stopped emitting, so
    that name was ordered and labelled while the mode actually being run
    (`rrf_hybrid_rerank`) fell through to its raw identifier and sorted last.
    Importing the canonical map removes the copy that can drift.
    """
    from legacy.curate_paper_assets import MODE_DISPLAY
    return MODE_DISPLAY
RESULT_DIR = Path(os.getenv("RESULT_DIR", str(BASE_DIR / "result")))
RESULT_DIR.mkdir(parents=True, exist_ok=True)

ANSWER_BY_TOPIC = RESULT_DIR / "analysis_by_topic.csv"
RETRIEVAL_BY_TOPIC = RESULT_DIR / "retrieval_metrics_by_topic.csv"

OUTPUT_HEATMAP_INSUFFICIENT = RESULT_DIR / "fig_heatmap_insufficient.png"
OUTPUT_HEATMAP_RETRIEVAL = RESULT_DIR / "fig_heatmap_retrieval_ndcg.png"

FIG_DPI = 300
FONT_SIZE = 11
TITLE_SIZE = 14
LABEL_SIZE = 12
TICK_SIZE = 10

# Reading order for the columns: retrieval families left to right, then the
# re-ranked pipeline, then the ablations. Only ordering lives here -- the labels
# come from `curate_paper_assets.MODE_DISPLAY`.
MODE_ORDER_HINTS = {
    "control_dense_only": 0,
    "bm25_only": 1,
    "bm25_base": 2,
    "hybrid_bm25": 3,
    "rrf_hybrid": 4,
    "rrf_hybrid_rerank": 5,
    "control_hybrid": 6,
    "baseline": 7,
    "rerank": 8,
    "ablation_no_dedup": 9,
    "ablation_small_pool": 10,
}

MODE_LABELS = _canonical_mode_display()


def ensure_file(path: str):
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} not found")


def set_style():
    plt.rcParams.update({
        "font.size": FONT_SIZE,
        "axes.titlesize": TITLE_SIZE,
        "axes.labelsize": LABEL_SIZE,
        "xtick.labelsize": TICK_SIZE,
        "ytick.labelsize": TICK_SIZE,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
    })


def ordered_modes(modes):
    return sorted(modes, key=lambda mode: (MODE_ORDER_HINTS.get(str(mode), 100), str(mode)))


def display_mode(mode):
    return MODE_LABELS.get(str(mode), str(mode))


def draw_heatmap(df_pivot, title, save_path, cmap="Blues", vmin=None, vmax=None,
                 cbar_label=""):
    fig, ax = plt.subplots(figsize=(6.5, 4.8))

    im = ax.imshow(df_pivot.values, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)

    ax.set_xticks(range(len(df_pivot.columns)))
    # Rotated: eleven modes do not fit at 0 degrees without overlapping.
    ax.set_xticklabels([display_mode(col) for col in df_pivot.columns],
                       rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(df_pivot.index)))
    ax.set_yticklabels(df_pivot.index)

    ax.set_title(title, pad=12)

    # 在每个格子里加数值
    for i in range(df_pivot.shape[0]):
        for j in range(df_pivot.shape[1]):
            value = df_pivot.iloc[i, j]
            text_color = "white" if value > 0.5 else "black"
            ax.text(j, i, f"{value:.3f}", ha="center", va="center", color=text_color, fontsize=9)

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=9)
    # An unlabelled colorbar leaves the reader to infer the quantity from the
    # title; name it on the bar itself.
    if cbar_label:
        cbar.set_label(cbar_label, fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=FIG_DPI)
    plt.close(fig)


def main():
    ensure_file(ANSWER_BY_TOPIC)
    ensure_file(RETRIEVAL_BY_TOPIC)
    set_style()

    answer_df = pd.read_csv(ANSWER_BY_TOPIC)
    retrieval_df = pd.read_csv(RETRIEVAL_BY_TOPIC)

    # 1. Insufficient evidence heatmap
    #
    # The retrieval-only ablation arms produce no answers, so they have no
    # insufficient-evidence rate to show -- `analyze_results.py` records those as
    # NaN. Filling them with 0 would paint the deepest cell of an "insufficient
    # evidence" heatmap for systems that never abstained because they never
    # answered at all, so they are dropped instead of filled.
    answer_df = answer_df[answer_df["insufficient_evidence_rate"].notna()]
    answer_pivot = answer_df.pivot(index="topic", columns="mode", values="insufficient_evidence_rate").fillna(0)

    desired_order = ["NSCLC", "SCLC", "Breast", "Colon", "AML", "CLL", "General"]
    answer_pivot = answer_pivot.reindex([x for x in desired_order if x in answer_pivot.index])
    answer_cols = ordered_modes(answer_pivot.columns.tolist())
    answer_pivot = answer_pivot[answer_cols]

    draw_heatmap(
        df_pivot=answer_pivot,
        title="Insufficient Evidence Rate by Topic",
        save_path=OUTPUT_HEATMAP_INSUFFICIENT,
        cmap="OrRd",
        vmin=0,
        vmax=max(0.5, answer_pivot.values.max()),
        cbar_label="Insufficient-evidence rate",
    )

    # 2. Retrieval nDCG heatmap
    retrieval_pivot = retrieval_df.pivot(index="topic", columns="mode", values="ndcg_at_10").fillna(0)
    retrieval_pivot = retrieval_pivot.reindex([x for x in desired_order if x in retrieval_pivot.index])
    retrieval_cols = ordered_modes(retrieval_pivot.columns.tolist())
    retrieval_pivot = retrieval_pivot[retrieval_cols]

    draw_heatmap(
        df_pivot=retrieval_pivot,
        title="Page-Level Retrieval nDCG@10 by Topic",
        save_path=OUTPUT_HEATMAP_RETRIEVAL,
        cmap="YlGnBu",
        vmin=0,
        vmax=1.0,
        cbar_label="nDCG@10",
    )

    print(f"Saved: {OUTPUT_HEATMAP_INSUFFICIENT}")
    print(f"Saved: {OUTPUT_HEATMAP_RETRIEVAL}")


if __name__ == "__main__":
    main()
