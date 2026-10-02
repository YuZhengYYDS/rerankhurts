"""Exploratory, page-clustered source-retention contrasts from completed E3 traces."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def cluster_interval(values, groups, repeats=5000, seed=20260924):
    frame = pd.DataFrame({"value": np.asarray(values), "group": np.asarray(groups)})
    aggregates = frame.groupby("group").value.agg(["sum", "count"])
    rng = np.random.default_rng(seed)
    samples = rng.integers(0, len(aggregates), (repeats, len(aggregates)))
    means = aggregates["sum"].to_numpy()[samples].sum(axis=1) / aggregates["count"].to_numpy()[samples].sum(axis=1)
    return tuple(np.quantile(means, [0.025, 0.975]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=Path("experiments/runs/e3_m3"))
    args = parser.parse_args()
    run = args.run
    status = json.loads((run / "status.json").read_text(encoding="utf-8"))
    if status["status"] != "complete":
        raise ValueError("Refusing a paper analysis of incomplete experiment outputs")
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    ranker = manifest["identity"]["settings"]["reranker_label"]
    df = pd.read_csv(run / "per_question.csv")
    if df.duplicated(["qid", "config_id"]).any() or len(df) != manifest["expected_records"]:
        raise ValueError("Unexpected or duplicated query/configuration records")
    wide = df.pivot(index="qid", columns="config_id", values="G_final")
    if wide.isna().any().any():
        raise ValueError("Unpaired configuration results")
    groups = df.drop_duplicates("qid").set_index("qid").loc[wide.index, "group_id"].to_numpy()
    contrasts = []

    def add(name, pool, budget, delta):
        lo, hi = cluster_interval(delta, groups)
        contrasts.append({"contrast": name, "pool": pool, "budget": budget,
                          "n_questions": len(wide), "n_page_clusters": len(set(groups)),
                          "G_difference": float(np.mean(delta)), "ci95_low": lo, "ci95_high": hi,
                          "analysis": "exploratory; paired page-cluster percentile bootstrap; no multiplicity-adjusted claim"})

    for pool in (16, 64):
        for budget in (512, 2048):
            key = lambda cap, rank: f"p{pool}_{cap}_{rank}_b{budget}"
            off = wide[key("off", ranker)] - wide[key("off", "none")]
            pre = wide[key("pre", ranker)] - wide[key("pre", "none")]
            add(f"{ranker}_minus_none_no_cap", pool, budget, off)
            add(f"{ranker}_minus_none_pre_cap", pool, budget, pre)
            add("cap_by_reranking_interaction", pool, budget, pre - off)
            add(f"post_cap_minus_pre_cap_{ranker}", pool, budget,
                wide[key("post", ranker)] - wide[key("pre", ranker)])
    pd.DataFrame(contrasts).to_csv(run / "G_contrasts.csv", index=False)
    for column in ("construction_source", "topic"):
        df.groupby([column, "config_id"], dropna=False).agg(n_questions=("qid", "count"), G_final=("G_final", "mean")).reset_index().to_csv(run / f"G_by_{column}.csv", index=False)
    losses = df.groupby(["config_id", "first_url_loss"], dropna=False).size().rename("n_queries").reset_index()
    losses.to_csv(run / "first_page_loss.csv", index=False)

    summary = pd.read_csv(run / "summary.csv")
    labels = [("off", "none", "No cap / dense"), ("pre", "none", "Cap / dense"),
              ("off", ranker, f"No cap / {ranker}"), ("pre", ranker, f"Cap before / {ranker}"),
              ("post", ranker, f"Cap after / {ranker}")]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.7), constrained_layout=True, sharey=True)
    for ax, pool in zip(axes, (16, 64)):
        values = np.array([[float(summary.loc[summary.config_id.eq(f"p{pool}_{cap}_{rank}_b{b}"), "G_final"].iloc[0]) for b in (512, 2048)] for cap, rank, _ in labels])
        ax.imshow(values, cmap="Blues", vmin=0, vmax=1, aspect="auto")
        for i in range(5):
            for j in range(2):
                ax.text(j, i, f"{values[i,j]:.3f}", ha="center", va="center", color="white" if values[i,j] > .62 else "black")
        ax.set_xticks([0, 1], ["512 tokens", "2048 tokens"])
        ax.set_yticks(range(5), [x[2] for x in labels])
        ax.set_title(f"Candidate pool = {pool}")
        ax.tick_params(length=0)
    fig.savefig(run / "G_factorial.pdf", bbox_inches="tight")
    fig.savefig(run / "G_factorial.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    notes = {"endpoint": "designated-page retention G, not human evidence utility",
             "questions": len(wide), "page_clusters": len(set(groups)),
             "bootstrap_repeats": 5000, "seed": 20260924,
             "analysis_status": "exploratory contrasts specified after implementation; not a preregistered confirmatory E2 test",
             "run_identity": manifest["identity_hash"],
             "input_sha256": hashlib.sha256((run / "per_question.csv").read_bytes()).hexdigest()}
    (run / "analysis_manifest.json").write_text(json.dumps(notes, indent=2), encoding="utf-8")
    print(json.dumps(notes, indent=2))


if __name__ == "__main__":
    main()
