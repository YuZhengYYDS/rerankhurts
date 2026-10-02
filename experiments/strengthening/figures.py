"""Publication-sized scientific figures from frozen strengthening CSV outputs.

No models are run and no task is treated as an independent replicate of its
world. Descriptive points are equal-world means; uncertainty bars come only from
the separately specified world-level contrasts. Run after PDF workflow marking.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .evaluate import DEFAULT_OUTPUT, dump_json, read_json, sha256

COLORS = {"off": "#525252", "pre": "#d06d28", "post": "#247ba0"}
SCENARIOS = ("single_chunk", "same_url_complementary", "cross_url_complementary", "equivalent_support", "temporal_conflict", "position")
SCENARIO_LABELS = ("Single chunk", "Same URL", "Cross URL", "Alternative cover", "Time/conflict", "Late positions")


def select(frame, **settings):
    result = frame
    for key, value in settings.items():
        result = result[result[key].isna()] if value is None else result[result[key] == value]
    if result.empty:
        raise ValueError(f"No frozen observations for figure selection: {settings}")
    return result


def anchor(frame, **changes):
    settings = dict(retriever="dense", pool=64, reranker="m3", cap=0, cap_stage="off", refill=False,
                    packing="prefix", score_view="prefix512", dense_view="prefix512", policy_stage="none", mmr_lambda=None)
    settings.update(changes)
    return select(frame, **settings)


def world_mean(frame, metric="U_sim", by=()):
    if isinstance(by, str):
        by = [by]
    by = list(by)
    worlds = frame.groupby([*by, "group_id"], dropna=False)[metric].mean()
    return worlds.groupby(level=by).mean() if by else float(worlds.mean())


def cap_delta(frame, budget=512, cap=2):
    subset = anchor(frame, budget=budget, cap=cap, cap_stage="post")
    pre = anchor(frame, budget=budget, cap=cap, cap_stage="pre")
    keys = ["qid", "group_id", "scenario", "variant_id"]
    paired = subset[keys + ["U_sim"]].merge(pre[keys + ["U_sim"]], on=keys, suffixes=("_post", "_pre"), validate="one_to_one")
    if len(paired) != len(subset) or len(paired) != len(pre):
        raise ValueError("Unpaired cap figure observations")
    paired["difference"] = paired.U_sim_post - paired.U_sim_pre
    return paired


def style_axes(axis, title, xlabel=None, ylabel=None, probability=False):
    axis.set_title(title, loc="left", fontweight="bold", pad=5)
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", alpha=.17, linewidth=.5)
    axis.set_axisbelow(True)
    if xlabel:
        axis.set_xlabel(xlabel)
    if ylabel:
        axis.set_ylabel(ylabel)
    if probability:
        axis.set_ylim(0, 1.03)


def budget_and_mechanisms(frame, plt):
    fig = plt.figure(figsize=(6.8, 5.5), constrained_layout=True)
    grid = fig.add_gridspec(2, 6, height_ratios=(1, 1.35))
    budgets = [256, 512, 1024, 2048]
    for column, family in enumerate(("prose", "list", "qa")):
        axis = fig.add_subplot(grid[0, column * 2:(column + 1) * 2])
        for cap, stage in ((0, "off"), (2, "pre"), (2, "post")):
            values = world_mean(anchor(frame, cap=cap, cap_stage=stage, template_family=family), by="budget")
            axis.plot(range(4), values.reindex(budgets), marker="o", markersize=3, color=COLORS[stage], label="No cap" if stage == "off" else stage + " cap2")
        axis.set_xticks(range(4), ["256", "512", "1024", "2048"], rotation=30)
        style_axes(axis, f"{chr(97 + column)}  {family.upper() if family == 'qa' else family.title()}", "Evidence token budget", "Full fact coverage" if column == 0 else None, True)
        if column == 0:
            axis.legend(frameon=False, fontsize=6, loc="upper left")
    matrices = []
    for variant in ("low_concentration", "high_concentration"):
        columns = []
        for cap in (1, 2, 4):
            pairs = cap_delta(frame, 512, cap)
            means = world_mean(pairs[pairs.variant_id == variant], "difference", "scenario")
            columns.append(means.reindex(SCENARIOS).to_numpy())
        matrices.append(np.column_stack(columns))
    scale = max(.05, float(np.nanmax(np.abs(matrices))))
    for index, (variant, matrix) in enumerate(zip(("Low concentration", "High concentration"), matrices)):
        axis = fig.add_subplot(grid[1, index * 3:(index + 1) * 3])
        image = axis.imshow(matrix, aspect="auto", cmap="RdBu", vmin=-scale, vmax=scale)
        axis.set_xticks(range(3), ["cap1", "cap2", "cap4"])
        axis.set_yticks(range(6), SCENARIO_LABELS if index == 0 else [""] * 6)
        axis.set_title(f"{chr(100 + index)}  {variant}: post − pre, B=512", loc="left", fontweight="bold")
        for y in range(6):
            for x in range(3):
                value = matrix[y, x]
                axis.text(x, y, f"{value:+.2f}" if value else "0.00", ha="center", va="center", fontsize=6,
                          color="white" if abs(value) > scale * .58 else "black")
    fig.colorbar(image, ax=fig.axes[-2:], shrink=.7, pad=.02, label="Full-coverage difference")
    return fig


def support_and_source(frame, plt):
    fig, axes = plt.subplots(2, 2, figsize=(6.8, 5.0), constrained_layout=True)
    stages = ["raw", "pre_cap", "rerank", "post_cap", "post_policy", "final"]
    stage_names = ["Candidates", "Pre-cap", "Rerank", "Post-cap", "Policy", "Budget"]
    for index, budget in enumerate((512, 2048)):
        axis = axes[0, index]
        for stage in ("pre", "post"):
            subset = anchor(frame, budget=budget, cap=2, cap_stage=stage)
            values = [world_mean(subset, name + "_U_sim") for name in stages]
            axis.plot(range(len(stages)), values, marker="o", markersize=3, color=COLORS[stage], label=stage + " cap2")
        axis.set_xticks(range(len(stages)), stage_names, rotation=35, ha="right")
        style_axes(axis, f"{chr(97 + index)}  Support flow, B={budget}", ylabel="Full fact coverage" if index == 0 else None, probability=True)
        axis.legend(frameon=False, fontsize=6)
    for index, budget in enumerate((512, 2048)):
        axis = axes[1, index]
        samples = [anchor(frame, budget=budget, cap=cap, cap_stage=stage).copy()
                   for cap, stage in ((0, "off"), (2, "pre"), (2, "post"))]
        bottom = np.zeros(3)
        for (g, u), color in zip(((0, 0), (1, 0), (0, 1), (1, 1)), ("#d9d9d9", "#e5aa70", "#75b4c6", "#226b8d")):
            values = []
            for subset in samples:
                subset["cell"] = ((subset.G_final == g) & (subset.U_sim == u)).astype(int)
                values.append(world_mean(subset, "cell"))
            axis.bar(range(3), values, bottom=bottom, color=color, label=f"G={g}, U={u}", width=.65)
            bottom += values
        axis.set_xticks(range(3), ["No cap", "Pre cap2", "Post cap2"])
        style_axes(axis, f"{chr(99 + index)}  Source × fact coverage, B={budget}", ylabel="World-weighted share" if index == 0 else None, probability=True)
        if index == 1:
            axis.legend(frameon=False, fontsize=6, loc="center left", bbox_to_anchor=(1, .5))
    return fig


def visibility_packing_policy(frame, plt):
    fig, axes = plt.subplots(2, 2, figsize=(6.8, 5.1), constrained_layout=True)
    definitions = [
        ("packing", ["prefix", "whole", "window"], {"cap": 2, "cap_stage": "post"}, "a  Packing, post cap2"),
        ("dense_view", ["prefix128", "prefix512", "window512"], {}, "b  Dense view, no cap"),
        ("score_view", ["prefix128", "prefix512", "window512"], {"cap": 2, "cap_stage": "post"}, "c  CE view, post cap2"),
    ]
    for axis, (field, levels, conditions, title) in zip((axes[0, 0], axes[0, 1], axes[1, 0]), definitions):
        for offset, (budget, color) in enumerate(((512, "#e49b59"), (2048, "#247ba0"))):
            values = [world_mean(anchor(frame, budget=budget, **conditions, **{field: level})) for level in levels]
            axis.bar(np.arange(3) + (offset - .5) * .34, values, width=.32, color=color, label=f"B={budget}")
        axis.set_xticks(range(3), [level.replace("prefix", "P").replace("window", "W") if field != "packing" else level for level in levels])
        style_axes(axis, title, ylabel="Full fact coverage", probability=True)
        axis.legend(frameon=False, fontsize=6)
    axis = axes[1, 1]
    markers = {"none": "o", "pre_retrieve": "s", "post_retrieve": "^", "post_rerank": "D"}
    short = {"none": "No filter", "pre_retrieve": "Before retrieve", "post_retrieve": "After retrieve", "post_rerank": "After rerank"}
    for budget, color in ((512, "#e49b59"), (2048, "#247ba0")):
        for stage, marker in markers.items():
            subset = anchor(frame, budget=budget, cap=2, cap_stage="post", policy_stage=stage, policy="constrained")
            x, y = world_mean(subset, "C_sim"), world_mean(subset, "admissible_U_sim")
            axis.scatter(x, y, marker=marker, color=color, s=28, alpha=.85,
                         label=short[stage] if budget == 512 else None)
    axis.set_xlim(-.04, 1.04)
    style_axes(axis, "d  Allowed-source filter placement", "Unconditional source compliance", "Admissible full coverage", True)
    axis.legend(frameon=False, fontsize=5.6, loc="lower left")
    return fig


def empirical_answers_timing(results, plt):
    answers, timing = results / "answers", results / "timing"
    needed = (answers / "per_answer.csv", timing / "summary.csv", results / "answer_contrasts.csv", results / "timing_world_contrasts.csv")
    if not all(path.exists() for path in needed):
        return None, []
    if read_json(answers / "status.json").get("status") != "complete" or read_json(timing / "status.json").get("status") != "complete":
        return None, []
    answers_frame = pd.read_csv(answers / "per_answer.csv")
    timing_frame = pd.read_csv(timing / "summary.csv")
    answer_contrasts = pd.read_csv(results / "answer_contrasts.csv")
    timing_contrasts = pd.read_csv(results / "timing_world_contrasts.csv")
    fig, axes = plt.subplots(2, 2, figsize=(6.8, 5.3), constrained_layout=True)
    names = ["dense_prefix", "m3_pre_prefix", "m3_post_prefix", "m3_post_window", "closed_book", "no_support"]
    labels = ["Dense", "Pre", "Post", "Window", "Closed", "Wrong world"]
    for index, (endpoint, color, label) in enumerate((("complete_correct", "#e49b59", "Correct"),
                                                    ("complete_grounded_correct", "#247ba0", "Correct + grounded"))):
        values = [world_mean(select(answers_frame, condition=name), endpoint) for name in names]
        axes[0, 0].bar(np.arange(6) + (index - .5) * .34, values, .32, color=color, label=label)
    axes[0, 0].set_xticks(range(6), labels, rotation=35, ha="right")
    style_axes(axes[0, 0], "a  Actual generated answers", ylabel="Complete-answer rate", probability=True)
    axes[0, 0].legend(frameon=False, fontsize=6)
    rows = answer_contrasts[answer_contrasts.endpoint.isin(["complete_correct", "complete_grounded_correct"])].copy()
    rows["label"] = rows["name"].map({"post_minus_pre": "Post − pre", "window_minus_prefix": "Window − prefix"}) + rows.endpoint.map(
        {"complete_correct": ": correct", "complete_grounded_correct": ": grounded"})
    forest(axes[0, 1], rows, "b  Answer contrasts", "World mean difference")
    live = timing_frame[timing_frame.phase == "steady"].set_index("condition")
    for index, (metric, color, label) in enumerate((("p50_ms", "#e49b59", "Request p50"), ("p95_ms", "#247ba0", "Request p95"))):
        axes[1, 0].bar(np.arange(4) + (index - .5) * .34, live.reindex(names[:4])[metric] / 1000, .32, color=color, label=label)
    axes[1, 0].set_xticks(range(4), labels[:4])
    style_axes(axes[1, 0], "c  Measured online request latency", ylabel="Seconds")
    axes[1, 0].legend(frameon=False, fontsize=6)
    timing_contrasts["label"] = timing_contrasts.name.map({"post_minus_pre_latency": "Post − pre", "window_minus_prefix_latency": "Window − prefix"})
    forest(axes[1, 1], timing_contrasts, "d  Repeated-request world means", "Latency difference (ms)")
    return fig, [str(path.relative_to(results)).replace("\\", "/") for path in needed]


def forest(axis, rows, title, xlabel):
    for index, (_, row) in enumerate(rows.iterrows()):
        axis.plot([row.ci95_low, row.ci95_high], [index, index], color="#247ba0", linewidth=1.4)
        axis.plot(row.difference, index, "o", color="#247ba0", markersize=3)
    axis.axvline(0, color=".6", linewidth=.7)
    axis.set_yticks(range(len(rows)), rows.label, fontsize=6)
    style_axes(axis, title, xlabel)


def generate(results=DEFAULT_OUTPUT, output=None):
    results = Path(results)
    output = Path(output) if output else results / "figures"
    if read_json(results / "status.json").get("status") != "complete":
        raise ValueError("Figures require complete independently evaluated results")
    analysis = read_json(results / "analysis.json")
    if analysis["evaluated_per_record_sha256"] != sha256(results / "per_record.csv"):
        raise ValueError("Evaluated CSV has changed since the statistical analysis")
    for name, expected in analysis.get("output_hashes", {}).items():
        if sha256(results / name) != expected:
            raise ValueError(f"Frozen analysis output changed: {name}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.titlesize": 7.5,
                         "axes.labelsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6,
                         "legend.fontsize": 6, "pdf.fonttype": 42, "ps.fonttype": 42})
    frame = pd.read_csv(results / "per_record.csv")
    frame = frame[frame.split == "test"].copy()
    output.mkdir(parents=True, exist_ok=True)
    figures = [("budget_and_mechanisms", budget_and_mechanisms(frame, plt)),
               ("support_and_source", support_and_source(frame, plt)),
               ("visibility_packing_policy", visibility_packing_policy(frame, plt))]
    auxiliary, auxiliary_sources = empirical_answers_timing(results, plt)
    if auxiliary is not None:
        figures.append(("answers_and_timing", auxiliary))
    generated = []
    for name, figure in figures:
        for extension in ("pdf", "png"):
            path = output / f"{name}.{extension}"
            figure.savefig(path, dpi=250)
            generated.append(path)
        plt.close(figure)
    sources = ["per_record.csv", "primary_contrasts.csv", "exploratory_contrasts.csv", *auxiliary_sources]
    manifest = {"status": "complete", "figures_code_sha256": sha256(__file__),
                "source_csv_sha256": {name: sha256(results / name) for name in sorted(set(sources))},
                "figure_sha256": {path.name: sha256(path) for path in generated},
                "captions": {
                    "budget_and_mechanisms": "Test-world means under the designed mixture. QA is an unseen rendering family on held-out worlds, not a within-world template intervention. Lower panels show conditional post-minus-pre differences; printed zeros are rounded descriptive estimates, not equivalence claims.",
                    "support_and_source": "Full-set membership is scored before the final budget stage. Pure sorting preserves membership. The joint G/U shares average paired variants within each world; designated-source retention and complete fact coverage are distinct endpoints.",
                    "visibility_packing_policy": "Fixed matched submatrices: packing and CE-view contrasts use post cap2, dense-view contrasts use no cap. Policy panel includes constrained tasks only; empty outputs count as noncompliant. Points/bars are descriptive world means; no per-task independence or inferential interval is implied.",
                    "answers_and_timing": "Actual local answer-model outputs and online requests. Confidence bars come from exploratory seed-stratified paired-world analysis. Latency p50/p95 summarize measured requests; the interval panel first averages repetitions within each world. These are fictional administrative tasks, not clinical validation."},
                "human_semantic_audit_complete": False}
    dump_json(output / "manifest.json", manifest)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = generate(args.results, args.output)
    print(f"Created {len(result['figure_sha256'])} PDF/PNG files with source hashes")


if __name__ == "__main__":
    main()
