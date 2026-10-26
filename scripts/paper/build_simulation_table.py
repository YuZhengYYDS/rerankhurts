"""Render held-out simulation results only from a complete, hashed oracle run."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from shutil import copy2

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path, help="Output directory (default: build/reanalysis/tables/simulation)")
    args = parser.parse_args()
    source = args.results.resolve()
    status = json.loads((source / "status.json").read_text(encoding="utf-8"))
    selection = json.loads((source / "selection.json").read_text(encoding="utf-8"))
    if status.get("status") != "complete" or status.get("observed_records") != 2400 or status.get("expected_records") != 2400:
        raise ValueError("A complete 120-task, 20-configuration simulation is required.")
    if status.get("worlds") != 60 or status.get("tasks") != 120 or status.get("split_world_counts") != {"dev": 20, "test": 40}:
        raise ValueError("Unexpected frozen simulation population.")
    for payload in (status, selection):
        if payload.get("annotation_source") != "synthetic_oracle" or payload.get("valid_for_human_eval_claim") is not False:
            raise ValueError("Simulation outcomes must remain explicitly synthetic.")
    if any(status.get(k) for k in ("human_U_available", "human_E2_complete", "answer_A_available")):
        raise ValueError("Unexpected human or answer endpoint.")
    for name in ("selection.json", "summary.csv", "budget_feasibility.json"):
        if sha(source / name) != status["output_sha256"][name]:
            raise ValueError(f"Evaluator output hash mismatch: {name}")
    with (source / "summary.csv").open(encoding="utf-8", newline="") as handle:
        summaries = {(r["split"], r["policy"], r["config_id"]): r
                     for r in csv.DictReader(handle) if r["scope"] == "overall"}
    lines = [
        "% Generated from a complete synthetic-oracle evaluation. Do not edit cells.",
        r"\begin{table}[t]", r"\centering",
        r"\caption{Frozen development-selected configurations on 40 held-out simulated information needs. All selected caps are disabled. $U_{\rm sim}$ is complete fact coverage. The 2,048-token analysis is exploratory.}",
        r"\label{tab:simulation}", r"\begin{tabular}{rrlrrr}", r"\toprule",
        r"Budget & Select by & Ranker & Pool & Test $G$ & Test $U_{\rm sim}$ \\",
        r"\midrule",
    ]
    selected_pairs = {}
    for key in ("primary", "exploratory_2048"):
        result = selection[key]
        if result["status"] != "complete" or result["policy"] != "open" or result["n_dev_information_needs"] != 20 or result["n_test_information_needs"] != 40:
            raise ValueError("Incomplete or incompatible selector analysis.")
        if len(result["configuration_tie_order"]) != 10:
            raise ValueError("Expected ten configurations at each budget.")
        selected_pairs[key] = {}
        for criterion, latex in (("G", "$G$"), ("U_sim", r"$U_{\rm sim}$")):
            config = result["dev_selected_by_" + criterion]
            parts = config.split("_")
            if len(parts) != 4 or parts[1] != "off":
                raise ValueError("Table caption must be updated for a changed selected cap.")
            measured = result["test_selected_config_means"][criterion]
            summary = summaries[("test", "open", config)]
            if int(summary["n_information_needs"]) != 40:
                raise ValueError("Missing held-out information needs.")
            for metric in ("G_final", "U_sim"):
                if not 0 <= measured[metric] <= 1 or abs(float(summary[metric]) - measured[metric]) > 1e-12:
                    raise ValueError("Selected outcome does not match the full summary.")
            lines.append(" & ".join((str(result["budget"]), latex, parts[2], parts[0][1:],
                         f"{measured['G_final']:.3f}", f"{measured['U_sim']:.3f}")) + r" \\")
            selected_pairs[key][criterion] = config
        delta = result["test_selected_config_means"]["U_sim"]["U_sim"] - result["test_selected_config_means"]["G"]["U_sim"]
        if abs(delta - result["test_U_sim_delta_U_selected_minus_G_selected"]) > 1e-12:
            raise ValueError("Selected-pair contrast is inconsistent.")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    destination = args.output.resolve() if args.output else ROOT / "build/reanalysis/tables/simulation"
    generated = destination / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    figure = source / "selection_comparison.pdf"
    if not figure.is_file():
        raise ValueError("Generate the simulation figure before building its paper inputs.")
    (destination / "figures").mkdir(exist_ok=True)
    copy2(figure, destination / "figures" / figure.name)
    tex = generated / "simulation_results.tex"
    tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
    provenance = {
        "kind": "controlled_synthetic_held_out_selection",
        "annotation_source": "synthetic_oracle", "valid_for_human_eval_claim": False,
        "results_directory": source.name, "worlds": 60, "tasks": 120, "configuration_records": 2400,
        "run_identity": status["provenance"]["run_identity"], "selected_pairs": selected_pairs,
        "source_sha256": {name: sha(source / name) for name in
                          ("status.json", "selection.json", "summary.csv", "budget_feasibility.json", "selection_comparison.pdf")},
        "builder_sha256": sha(Path(__file__).resolve()), "generated_tex_sha256": sha(tex),
        "simulation_data_sha256": status["provenance"]["input_files"],
    }
    (generated / "simulation_table_manifest.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
