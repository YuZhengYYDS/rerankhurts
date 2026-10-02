"""Render the frozen primary held-out simulation comparison from verified CSVs."""
from pathlib import Path
import argparse
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path("experiments/simulation/results/pilot_v2"))
    args = parser.parse_args()
    root = args.results
    status = json.loads((root / "status.json").read_text(encoding="utf-8"))
    if status.get("status") != "complete" or status.get("annotation_source") != "synthetic_oracle":
        raise ValueError("Only completed synthetic-oracle results can be plotted")
    for filename, expected in status["output_sha256"].items():
        if hashlib.sha256((root / filename).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Changed evaluator artifact: {filename}")
    selection = json.loads((root / "selection.json").read_text(encoding="utf-8"))["primary"]
    table = pd.read_csv(root / "summary.csv")
    table = table[(table.scope == "overall") & (table.split == "test") & (table.policy == "open")]
    order = selection["configuration_tie_order"]
    table = table.set_index("config_id").loc[order]
    if len(table) != 10 or not (table.n_information_needs == 40).all():
        raise ValueError("Expected the ten frozen configurations on 40 held-out needs")
    labels = []
    for cid in order:
        pool, cap, ranker, _budget = cid.split("_")
        selected = []
        if cid == selection["dev_selected_by_G"]:
            selected.append("G")
        if cid == selection["dev_selected_by_U_sim"]:
            selected.append("U")
        marker = "\nchosen: " + "/".join(selected) if selected else "\n"
        labels.append(f"{pool[1:]} / {cap}\n{ranker}" + marker)
    with plt.rc_context({"font.size": 9.5, "pdf.fonttype": 42, "ps.fonttype": 42}):
        fig, ax = plt.subplots(figsize=(9.4, 3.7), constrained_layout=True)
        x = np.arange(len(order))
        ax.bar(x - .19, table.G_final, .36, color="#426A9C", label="Designated-page retention G")
        ax.bar(x + .19, table.U_sim, .36, color="#CE8251", label="Complete fact coverage U_sim")
        ax.set_xticks(x, labels)
        ax.set_ylim(0, 1.12)
        ax.set_yticks(np.linspace(0, 1, 6))
        ax.set_ylabel("Fraction of 40 held-out simulated needs")
        ax.set_xlabel("Candidate pool / cap placement / ranker; chosen labels refer to development-set selectors")
        ax.grid(axis="y", alpha=.18)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(loc="upper right", ncol=2, frameon=False, fontsize=9.5)
        fig.suptitle("Controlled simulation · open evidence · 512-token budget", fontsize=11)
        for suffix in ("pdf", "png"):
            fig.savefig(root / f"selection_comparison.{suffix}", dpi=180)
        plt.close(fig)
    (root / "figure_provenance.json").write_text(json.dumps({
        "kind": "controlled_synthetic_figure", "endpoint": "complete fact coverage, not human utility",
        "inputs": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                   for name in ("summary.csv", "selection.json", "status.json")},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }, indent=2) + "\n", encoding="utf-8")
    print(root / "selection_comparison.pdf")


if __name__ == "__main__":
    main()
