"""Independently recount manuscript endpoint pairs from frozen simulation CSV.

Only the Python standard library is used. This script neither imports the
simulation evaluator nor runs a retrieval/model/annotation pipeline. It audits
the published paired counts, conditional on the upstream span scores.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELL_ORDER = ("G1_U1", "G1_U0", "G0_U1", "G0_U0")
CONFIGS = {"dense": "p16_off_none_b512", "m3": "p16_off_m3_b512"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary(value, field):
    require(value in {"0", "1"}, f"{field} must be an explicit binary CSV value")
    return int(value)


def audit(csv_path, specification_path):
    status_path = csv_path.parent / "status.json"
    status = read_json(status_path)
    require(status.get("status") == "complete" and status.get("observed_records") == 2400,
            "Require the completed 120-task by 20-configuration simulation")
    require(status.get("annotation_source") == "synthetic_oracle" and status.get("human_E2_complete") is False,
            "This audit accepts explicitly synthetic results only")
    require(status["output_sha256"].get(csv_path.name) == sha256(csv_path),
            "CSV does not match the completed evaluation's recorded hash")
    specification = read_json(specification_path)
    require(status["provenance"]["input_files"]["specification.json"] == sha256(specification_path),
            "Frozen specification does not match the evaluation")
    test_groups = set(specification["selection"]["test_groups"])
    dev_groups = set(specification["selection"]["dev_groups"])
    require(len(test_groups) == 40 and len(dev_groups) == 20 and not test_groups & dev_groups,
            "Expected separate sets of 20 development and 40 test worlds")
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    require(len(rows) == len({(row["qid"], row["config_id"]) for row in rows}) == 2400,
            "Missing or duplicate question/configuration rows")
    require(all(row["annotation_source"] == "synthetic_oracle"
                and row["valid_for_human_eval_claim"].lower() == "false" for row in rows),
            "Rows must not be presented as human annotations")
    by_config = {}
    for label, config_id in CONFIGS.items():
        selected = [row for row in rows if row["split"] == "test" and row["policy"] == "open"
                    and row["config_id"] == config_id]
        indexed = {row["group_id"]: row for row in selected}
        require(len(selected) == len(indexed) == 40 and set(indexed) == test_groups,
                f"{config_id}: expected one open task from every held-out world")
        require(all(row["budget"] == "512" and row["pool"] == "16" and row["cap"] == "off"
                    and row["reranker"] == ("none" if label == "dense" else "m3") for row in selected),
                "Configuration ID and factor columns disagree")
        by_config[label] = indexed

    cells = {}
    for label, indexed in by_config.items():
        counts = Counter(f"G{binary(row['G_final'], 'G_final')}_U{binary(row['U_sim'], 'U_sim')}"
                         for row in indexed.values())
        cells[label] = {"config_id": CONFIGS[label], "n_test_worlds": 40,
                        "cells": {cell: counts[cell] for cell in CELL_ORDER},
                        "counts_in_cell_order": [counts[cell] for cell in CELL_ORDER],
                        "G_successes": counts["G1_U1"] + counts["G1_U0"],
                        "U_sim_successes": counts["G1_U1"] + counts["G0_U1"]}

    changes = defaultdict(list)
    per_world = []
    for group in sorted(test_groups):
        dense, m3 = by_config["dense"][group], by_config["m3"][group]
        require(dense["qid"] == m3["qid"] and dense["scenario"] == m3["scenario"],
                "Paired configurations refer to different information needs")
        dg, du, mg, mu = (binary(value, "paired endpoint") for value in
                           (dense["G_final"], dense["U_sim"], m3["G_final"], m3["U_sim"]))
        g_delta, u_delta = mg - dg, mu - du
        changes[g_delta, u_delta].append(group)
        per_world.append({"group_id": group, "qid": dense["qid"], "scenario": dense["scenario"],
                          "dense_G": dg, "dense_U_sim": du, "m3_G": mg, "m3_U_sim": mu,
                          "G_delta_m3_minus_dense": g_delta, "U_sim_delta_m3_minus_dense": u_delta})

    # Expected values are manuscript claims to be checked, not computation inputs.
    checks = {
        "dense_cells_match_manuscript": cells["dense"]["counts_in_cell_order"] == [8, 4, 14, 14],
        "m3_cells_match_manuscript": cells["m3"]["counts_in_cell_order"] == [8, 4, 19, 9],
        "two_worlds_lose_G_gain_U": len(changes[-1, 1]) == 2,
        "one_world_gains_G_loses_U": len(changes[1, -1]) == 1,
    }
    require(all(checks.values()), "At least one manuscript endpoint-pair claim does not match the frozen CSV")
    return {
        "status": "PASS", "annotation_source": "synthetic_oracle", "valid_for_human_eval_claim": False,
        "scope": "Independent recount of paired endpoint frequencies from the frozen per-record CSV; no evaluator functions or model execution used. Upstream complete-span oracle scores are inputs to this audit.",
        "subset": {"split": "test", "policy": "open", "budget": 512, "n_independent_worlds": 40},
        "cell_order": list(CELL_ORDER), "configuration_cross_tabs": cells,
        "paired_changes": [{"G_delta_m3_minus_dense": gd, "U_sim_delta_m3_minus_dense": ud,
                            "count": len(groups), "group_ids": groups}
                           for (gd, ud), groups in sorted(changes.items())],
        "opposite_direction_changes": {
            "G_down_U_up": {"count": len(changes[-1, 1]), "group_ids": changes[-1, 1]},
            "G_up_U_down": {"count": len(changes[1, -1]), "group_ids": changes[1, -1]}},
        "manuscript_claim_checks": checks, "per_world_pairs": per_world,
        "interpretation": "The paired counts establish endpoint disagreement in this controlled environment. They do not establish harmful URL-based selection, human evidence quality, or real-world transfer. Forty worlds are the paired units; repeated configurations do not create additional independent samples.",
        "sha256": {"per_record_csv": sha256(csv_path), "evaluation_status": sha256(status_path),
                   "frozen_specification": sha256(specification_path), "audit_code": sha256(__file__)},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "experiments/simulation/results/pilot_v2/per_record.csv")
    parser.add_argument("--specification", type=Path, default=ROOT / "experiments/simulation/data/pilot_v2/specification.json")
    parser.add_argument("--output", type=Path, default=ROOT / "validation/simulation_endpoint_pairs.json")
    args = parser.parse_args()
    report = audit(args.input.resolve(), args.specification.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "cell_order": report["cell_order"],
                      "dense": report["configuration_cross_tabs"]["dense"]["counts_in_cell_order"],
                      "m3": report["configuration_cross_tabs"]["m3"]["counts_in_cell_order"],
                      "G_down_U_up": report["opposite_direction_changes"]["G_down_U_up"]["count"],
                      "G_up_U_down": report["opposite_direction_changes"]["G_up_U_down"]["count"]}, indent=2))


if __name__ == "__main__":
    main()
