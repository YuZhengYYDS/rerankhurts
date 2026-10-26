"""Create the E3 manuscript table only from a complete 155-question model run."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from shutil import copy2

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, help="Output directory (default: build/reanalysis/tables/e3)")
    args = parser.parse_args()
    run = args.run.resolve()
    status = json.loads((run / "status.json").read_text(encoding="utf-8"))
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    with (run / "summary.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if status["status"] != "complete" or manifest["questions"] != 155:
        raise ValueError("Only a completed full 155-question model run can enter the paper; smoke/partial runs are excluded.")
    if len(rows) != 20 or any(int(row["n_questions"]) != 155 for row in rows):
        raise ValueError("Expected twenty complete configurations.")
    if status["expected_records"] != 3100 or status["observed_records"] != 3100:
        raise ValueError("Expected all 3,100 question--configuration records.")
    by_id = {row["config_id"]: row for row in rows}
    if len(by_id) != 20:
        raise ValueError("Duplicate configuration identifier.")
    if any(status.get(key, False) for key in ("human_U_available", "source_C_available", "answer_A_available")):
        raise ValueError("Unexpected outcome type; update the manuscript protocol before using this run.")
    for row in rows:
        for key in ("G_final", "ranking_url_ndcg10", "ranking_url_mrr"):
            if not 0 <= float(row[key]) <= 1:
                raise ValueError(f"Invalid {key}")
        if float(row["mean_context_tokens"]) > int(row["budget"]):
            raise ValueError("Budget overrun.")
    lines = [
        "% Generated from a completed model run. Do not edit numerical cells.",
        r"\begin{table*}[t]", r"\centering",
        r"\caption{All 20 configurations on 155 oncology questions. $G$ is designated-page retention after packing; URL-nDCG uses distinct URLs before packing. Tokens are mean delivered evidence tokens. Timing percentiles summarize shared measured component sums, with budget variants reusing retrieval and scoring work.}",
        r"\label{tab:e3}", r"\begin{tabular}{rllrrrrrr}", r"\toprule",
        r"Pool & Cap & Re-ranker & Budget & $G$ & URL-nDCG@10 & Tokens & p50 (ms) & p95 (ms) \\",
        r"\midrule",
    ]
    for row in rows:
        label = "none" if row["reranker"] == "none" else "m3"
        lines.append(" & ".join([
            row["pool"], row["cap"], label, row["budget"],
            f"{float(row['G_final']):.4f}", f"{float(row['ranking_url_ndcg10']):.4f}",
            f"{float(row['mean_context_tokens']):.1f}", f"{float(row['latency_p50_ms']):.1f}",
            f"{float(row['latency_p95_ms']):.1f}",
        ]) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
    destination = args.output.resolve() if args.output else ROOT / "build/reanalysis/tables/e3"
    generated = destination / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    figure = run / "G_factorial.pdf"
    if not figure.exists():
        raise ValueError("Run scripts/analyze_factorial.py before building the paper table and figure.")
    (destination / "figures").mkdir(exist_ok=True)
    copy2(figure, destination / "figures" / figure.name)
    (generated / "e3_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    provenance = {
        "kind": "new_model_execution_summary",
        "run_identity_hash": manifest["identity_hash"],
        "run_directory": run.name,
        "questions": 155,
        "configurations": 20,
        "input_sha256": {name: hashlib.sha256((run / name).read_bytes()).hexdigest()
                         for name in ("manifest.json", "status.json", "summary.csv", "G_factorial.pdf", "G_contrasts.csv")},
    }
    (generated / "e3_table_manifest.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
