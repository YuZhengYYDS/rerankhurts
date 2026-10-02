"""Prepare a fact rubric, then export system-blinded evidence annotation packets.

This creates blank forms. It does not supply clinical judgments or independent
information needs. Keep coordinator_private files away from the annotators.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .protocol import digest, file_hash, load_json, read_jsonl, save_json


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def prepare(questions_path, output):
    questions = read_jsonl(questions_path)
    rows = [{"qid": q["qid"], "question": q["question"], "group_id": q.get("group_id"),
             "information_need_id": q.get("information_need_id"),
             "construction_source": q.get("construction_source", "UNSPECIFIED"),
             "source_policy": "open", "acceptable_sources": [], "necessary_facts": [],
             "rubric_author": "", "frozen_before_system_output": False}
            for q in questions]
    write_jsonl(output / "rubric_template.jsonl", rows)
    save_json(output / "readiness.json", {
        "status": "awaiting_domain_expert_rubric_and_independent_questions",
        "input_questions_sha256": file_hash(questions_path), "questions": len(questions),
        "warning": "Export requires named rubric authors, nonempty necessary facts and a declared pre-output freeze. Existing 78/155 questions do not become independent by creating this template."})


def export(run, rubric_path, output, seed):
    rubric = {r["qid"]: r for r in read_jsonl(rubric_path)}
    for qid, r in rubric.items():
        if not r.get("necessary_facts") or not r.get("rubric_author") or not r.get("frozen_before_system_output"):
            raise ValueError(f"{qid}: freeze a domain-expert necessary-fact rubric before exporting system outputs.")
    rng = random.Random(seed)
    public_chunks, public_bundles, source_phase, coordinator = {}, {}, [], []
    manifest = load_json(run / "manifest.json")
    for path in sorted((run / "traces").glob("*.json.gz")):
        trace = load_json(path)
        if trace["identity_hash"] != manifest["identity_hash"]:
            raise ValueError("Trace belongs to a different run.")
        qid = trace["qid"]
        if qid not in rubric:
            raise ValueError(f"Missing frozen rubric for {qid}")
        r = rubric[qid]
        blind_qid = digest(["question", seed, qid])[:16]
        for config in trace["configurations"]:
            chunk_ids = []
            for c in config["final_context"]["chunks"]:
                # Partial deliveries are different annotation items from full chunks.
                item_id = digest(["chunk", seed, qid, c["text"]])[:20]
                chunk_ids.append(item_id)
                if item_id not in public_chunks:
                    public_chunks[item_id] = {"item_id": item_id, "question_id": blind_qid,
                        "question": r["question"], "necessary_facts": r["necessary_facts"], "text": c["text"],
                        "support_label_0_1_2": None, "supported_fact_ids": [], "support_spans": [],
                        "conflict": None, "outdated": None, "annotator_id": "", "notes": ""}
                    source_phase.append({"item_id": item_id, "url": c["url"],
                        "source_policy": r["source_policy"], "acceptable_sources": r.get("acceptable_sources", []),
                        "source_compliant": None, "annotator_id": "", "notes": ""})
                coordinator.append({"item_id": item_id, "qid": qid, "chunk_id": c["chunk_id"],
                                    "config_id": config["configuration"]["config_id"], "partial": c["partial"]})
            bundle_id = digest(["bundle", seed, qid, chunk_ids])[:20]
            if bundle_id not in public_bundles:
                public_bundles[bundle_id] = {"bundle_id": bundle_id, "question_id": blind_qid,
                    "question": r["question"], "necessary_facts": r["necessary_facts"],
                    "evidence": [{"item_id": cid, "text": public_chunks[cid]["text"]} for cid in chunk_ids],
                    "U_0_insufficient_1_partial_2_sufficient": None, "missing_fact_ids": [],
                    "conflict": None, "annotator_id": "", "notes": ""}
            coordinator.append({"bundle_id": bundle_id, "qid": qid, "config_id": config["configuration"]["config_id"]})
    chunks, bundles = list(public_chunks.values()), list(public_bundles.values())
    rng.shuffle(chunks)
    rng.shuffle(bundles)
    for annotator in ("annotator_a", "annotator_b"):
        write_jsonl(output / annotator / "phase1_chunks.jsonl", chunks)
        write_jsonl(output / annotator / "phase1_bundles.jsonl", bundles)
        write_jsonl(output / annotator / "phase2_sources.jsonl", source_phase)
    write_jsonl(output / "coordinator_private" / "mapping.jsonl", coordinator)
    save_json(output / "packet_manifest.json", {"run_identity_hash": manifest["identity_hash"],
        "rubric_sha256": file_hash(rubric_path), "seed": seed, "chunks": len(chunks), "bundles": len(bundles),
        "scope": "Union of final delivered text only. Full stage support annotation and independent retrieved evidence must be added for mechanism/coverage claims.",
        "blinding": "System names, ranks, gold flags, URL and original IDs hidden in phase1. Clinical text is retained verbatim and may contain source identity cues. Bundle order retained because it is delivered evidence.",
        "adjudication": "Two blank independent forms; a domain expert must adjudicate disagreements. Unannotated items stay unknown. Do not infer U from mean chunk support."})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--questions", type=Path, required=True)
    prep.add_argument("--output", type=Path, required=True)
    exp = sub.add_parser("export")
    exp.add_argument("--run", type=Path, required=True)
    exp.add_argument("--rubric", type=Path, required=True)
    exp.add_argument("--output", type=Path, required=True)
    exp.add_argument("--seed", type=int, default=20260924)
    args = p.parse_args()
    if args.command == "prepare":
        prepare(args.questions, args.output)
    else:
        export(args.run, args.rubric, args.output, args.seed)


if __name__ == "__main__":
    main()
