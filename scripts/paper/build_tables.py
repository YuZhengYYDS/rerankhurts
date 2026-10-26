"""Regenerate frozen paper tables from shipped CSVs, without model execution.

Generated .tex files are historical reanalysis outputs under build/.
This script never labels automatic scores as human.
"""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "results" / "tables"
GENERATED = ROOT / "build/reanalysis/tables/legacy"


def rows(name):
    with (TABLES / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write(name, lines):
    (GENERATED / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    GENERATED.mkdir(parents=True, exist_ok=True)
    family = rows("rev_table_rerankers.csv")
    labels = {
        "None (dense Base)": "Dense Base",
        "MiniLM-L6": "MiniLM-L6",
        "bge-reranker-base": "BGE-reranker-base",
        "MedCPT-Cross-Encoder": "MedCPT",
        "LLM listwise (DeepSeek)": "LLM candidate scoring",
        "bge-reranker-v2-m3": "BGE-reranker-v2-m3",
        "MiniLM-L6 + NCI source prior": "MiniLM + NCI prior (diagnostic)",
    }
    output = [
        r"\begin{table*}[t]", r"\centering", r"\caption{Historical frozen results, checked by E0. L-nDCG is the legacy first-gold-chunk score; $G$ is final top-four designated-page retention. The 155-question view is a related expansion. These are not new model executions.}",
        r"\label{tab:legacy}", r"\begin{tabular}{lrrrr}", r"\toprule",
        r" & \multicolumn{2}{c}{78 questions / base corpus} & \multicolumn{2}{c}{155 questions / expanded corpus} \\",
        r"Configuration & L-nDCG@10 & $G$ & L-nDCG@10 & $G$ \\", r"\midrule",
    ]
    for row in family:
        output.append(labels[row["method"]] + " & " + " & ".join(
            f"{float(row[key]):.4f}" for key in ("orig78_ndcg", "orig78_hit", "exp155_ndcg", "exp155_hit")
        ) + r" \\")
    output.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])
    write("legacy_results.tex", output)

    judge = rows("rev_table_judge.csv")
    quality = {r["mode"]: r for r in judge if r["judge"] == "answer_quality_1to5"}
    relevance = {r["mode"]: r for r in judge if r["judge"] == "graded_relevance_0to2"}
    modes = [
        ("baseline", "Dense Base"), ("rerank", "MiniLM"),
        ("rerank_bge_base", "BGE-base"), ("rerank_bge_m3", "BGE-m3"),
        ("rerank_medcpt", "MedCPT"), ("rrf_hybrid", "RRF"),
        ("rerank_source_aware", "NCI prior"),
    ]
    output = [
        r"\begin{table}[t]", r"\centering", r"\caption{Historical automatic judgments on 155 questions. Both columns are LLM outputs, not human support or clinical judgments. Relevance is question-balanced across distinct delivered URLs.}",
        r"\label{tab:judge}", r"\begin{tabular}{lrr}", r"\toprule",
        r"Configuration & Answer (1--5) & Relevance (0--2) \\", r"\midrule",
    ]
    for mode, label in modes:
        assert quality[mode]["valid_for_human_eval_claim"].lower() == "false"
        assert relevance[mode]["valid_for_human_eval_claim"].lower() == "false"
        output.append(f"{label} & {float(quality[mode]['composite_mean']):.3f} & {float(relevance[mode]['distinct_source_mean_relevance']):.3f}" + r" \\")
    output.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    write("judge_results.tex", output)
    manifest = {
        "kind": "frozen_csv_summary_replay_not_model_execution",
        "inputs": {
            str((TABLES / name).relative_to(ROOT)).replace("\\", "/"):
            hashlib.sha256((TABLES / name).read_bytes()).hexdigest()
            for name in ("rev_table_rerankers.csv", "rev_table_judge.csv")
        },
        "generated": ["legacy_results.tex", "judge_results.tex"],
    }
    (GENERATED / "legacy_table_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
