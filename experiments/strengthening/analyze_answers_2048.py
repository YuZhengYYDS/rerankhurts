"""World-paired follow-up analysis, independent of the frozen generation identity."""
from __future__ import annotations

import csv
from datetime import datetime
import json
import math
from pathlib import Path
import shutil

from .protocol import digest, file_hash, load_json, save_json

CONDITIONS = ("m3_off_prefix", "m3_post_prefix")
ENDPOINTS = ("complete_correct", "complete_grounded_correct", "field_accuracy", "grounded_field_accuracy")
DIAGNOSTICS = ("schema_valid", "unsupported_fields", "unsupported_abstentions", "unsupported_answers",
               "prompt_tokens", "generated_tokens", "generation_ms", "hit_max_new_tokens", "truncated_output")
OUTPUT_NAMES = ("per_answer.csv", "summary.csv", "answer_world_summary.csv", "answer_contrasts.csv",
                "paired_transitions.json", "RESULT_REPORT.md")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, binary=False):
    """Do not interpret the nonempty CSV string 'False' as truth."""
    if isinstance(value, str):
        if value in ("True", "False"):
            value = int(value == "True")
        else:
            value = float(value)
    require(isinstance(value, (bool, int, float)) and math.isfinite(value), "Invalid numeric endpoint")
    value = float(value)
    if binary:
        require(value in (0, 1), "Binary endpoint outside {0,1}")
    return value


def answer_row(record):
    keys = ("qid", "group_id", "seed", "variant_id", "scenario", "policy", "template_family", "condition",
            "config_id", "prompt_tokens", "generated_tokens", "generation_ms", "hit_max_new_tokens", "truncated_output")
    return {**{k: record[k] for k in keys}, **{k: v for k, v in record["evaluation"].items() if k != "fields"}}


def validate_rows(rows, identity):
    tasks = {task["qid"]: task for task in identity["tasks"]}
    require(len(tasks) == len(identity["questions"]) == 120 and set(tasks) == set(identity["questions"]),
            "Analysis requires the exact frozen 120 questions")
    expected = {(q, c) for q in tasks for c in CONDITIONS}
    keys = [(r["qid"], r["condition"]) for r in rows]
    require(len(keys) == len(set(keys)) and set(keys) == expected, "Incomplete/duplicate/foreign answer matrix")
    worlds = {}
    for row in rows:
        meta = tasks[row["qid"]]
        for key in ("group_id", "seed", "variant_id", "scenario", "policy", "template_family"):
            require(row[key] == meta[key], "Answer metadata differs from frozen task: " + key)
        variants = worlds.setdefault((meta["seed"], meta["group_id"]), set())
        variants.add((row["qid"], row["variant_id"]))
        for key in ENDPOINTS:
            value = number(row[key], binary=key.startswith("complete_"))
            require(0 <= value <= 1, "Invalid answer rate")
        number(row["schema_valid"], binary=True)
    require(len(worlds) == 60 and all(len(v) == 2 and {x[1] for x in v} ==
            {"low_concentration", "high_concentration"} for v in worlds.values()), "World pairing differs")
    require({seed: sum(s == seed for s, _ in worlds) for seed in (20261002, 20261003, 20261004)} ==
            {20261002: 20, 20261003: 20, 20261004: 20}, "Analysis seed quotas differ")


def compute(rows, identity):
    import pandas as pd
    from .analyze import paired_world_values, world_statistics, bh_adjust

    validate_rows(rows, identity)
    frame = pd.DataFrame(rows)
    for column in (*ENDPOINTS, *DIAGNOSTICS):
        frame[column] = [number(v, binary=column in ("complete_correct", "complete_grounded_correct", "schema_valid",
                                                     "hit_max_new_tokens", "truncated_output")) for v in frame[column]]
    grouped = frame.groupby(["group_id", "seed", "condition"], sort=True)[[*ENDPOINTS, *DIAGNOSTICS]].mean().reset_index()
    require(len(grouped) == 120, "Expected 60 worlds times two conditions")
    summaries = []
    for condition in CONDITIONS:
        part = frame[frame.condition == condition]
        world = grouped[grouped.condition == condition]
        summary = {"condition": condition, "answers": len(part), "worlds": len(world)}
        for column in (*ENDPOINTS, *DIAGNOSTICS):
            summary[column + "_world_mean"] = float(world[column].mean())
        for column in ("complete_correct", "complete_grounded_correct", "schema_valid", "hit_max_new_tokens", "truncated_output"):
            summary[column + "_numerator"] = int(part[column].sum())
            summary[column + "_denominator"] = len(part)
        for column in ("unsupported_fields", "unsupported_abstentions", "unsupported_answers"):
            summary[column + "_total"] = int(part[column].sum())
        summary["invalid_json_outputs"] = sum(r["parsed_json_object"] is False for r in rows if r["condition"] == condition)
        summaries.append(summary)
    renamed = frame.rename(columns={"condition": "config_id", "config_id": "evidence_config_id"})
    contrasts = []
    for endpoint in ENDPOINTS:
        worlds, pairs = paired_world_values(renamed, "m3_post_prefix", "m3_off_prefix", endpoint)
        require(len(pairs) == 120 and len(worlds) == 60 and worlds.n_tasks.eq(2).all(), "Incomplete paired worlds")
        contrasts.append({"endpoint": endpoint, "role": "core" if endpoint.startswith("complete_") else "secondary",
                          "direction": "post_minus_off", "family": "answer_quality_followup_2048",
                          "analysis": "followup", "n_task_pairs": len(pairs),
                          "left_world_mean": float(worlds.left.mean()), "right_world_mean": float(worlds.right.mean()),
                          **world_statistics(worlds, repeats=5000, permutation_repeats=20000, seed=20261002)})
    for row, qvalue in zip(contrasts, bh_adjust([r["p_sign_flip"] for r in contrasts])):
        row.update(q_bh_within_family=qvalue, family_size=4, difference_pp=100 * row["difference"],
                   ci95_low_pp=100 * row["ci95_low"], ci95_high_pp=100 * row["ci95_high"])
    indexed = {(r["qid"], r["condition"]): r for r in rows}
    transitions = {}
    for endpoint in ENDPOINTS[:2]:
        cells = {"both_correct": 0, "only_no_cap_correct": 0, "only_post_cap_correct": 0, "both_incorrect": 0}
        for qid in identity["questions"]:
            a, b = (number(indexed[qid, c][endpoint], binary=True) for c in CONDITIONS)
            key = {(1, 1): "both_correct", (1, 0): "only_no_cap_correct", (0, 1): "only_post_cap_correct", (0, 0): "both_incorrect"}[a, b]
            cells[key] += 1
        require(sum(cells.values()) == 120, "Paired transition denominator differs")
        transitions[endpoint] = {"task_pairs": 120, "worlds": 60, "counts": cells,
                                 "interpretation": "Descriptive task counts; inference clusters both variants within each world."}
    return {"rows": rows, "summary": summaries, "world_summary": grouped.to_dict("records"),
            "contrasts": contrasts, "transitions": transitions}


def write_csv(path, rows):
    rows = list(rows)
    require(bool(rows), "Cannot publish an empty analysis table")
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def compare_csv(path, expected):
    with path.open(encoding="utf-8", newline="") as stream:
        actual = list(csv.DictReader(stream))
    require(len(actual) == len(expected) and bool(actual), "CSV denominator differs: " + str(path))
    for old, new in zip(actual, expected):
        require(set(old) == set(new), "CSV schema differs: " + str(path))
        for key, value in new.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                require(math.isclose(float(old[key]), float(value), rel_tol=1e-12, abs_tol=1e-12), "CSV numeric mismatch: " + key)
            else:
                require(old[key] == str(value), "CSV value mismatch: " + key)


def analysis_identity(output, manifest, plan):
    return {"generation_identity_hash": manifest["identity_hash"], "plan_sha256": digest(plan),
            "statistics": plan["statistics"], "endpoints": list(ENDPOINTS),
            "analysis_sha256": file_hash(Path(__file__)), "original_analyze_sha256": file_hash(Path(__file__).with_name("analyze.py")),
            "response_sha256": {p.name: file_hash(p) for p in sorted((output / "responses").glob("*.json"))}}


def report_text(result, manifest, plan, evidence, work, output):
    baseline = load_json(work / "baseline512/comparison.json")
    smoke = load_json(work / "smoke2048/comparison.json")
    lines = ["# 2048-token 回答对照补实验结果", "", "本轮是追加的受控合成实验，沿用原 Fig.9 的 60 个测试世界、120 个任务，共 240 个正式回答。",
             "比较方向统一为 Post-cap2 M3 − No-cap M3。两组使用原轨迹保存的 B2048 上下文，dense/pool64/M3、prefix packing、检索与评分 prefix512 保持一致。",
             "", "模型为 Qwen/Qwen2.5-1.5B-Instruct，revision `" + manifest["identity"]["model"]["sha"] + "`。",
             "生成采用 CUDA FP16、SDPA、逐条 greedy、max_new_tokens=256，复用原 build_messages 与 score_answer。", "",
             "| 指标 | No-cap | Post-cap2 | Post−Off（百分点） | 世界级95% CI（百分点） | p | BH q（4项族） |",
             "|---|---:|---:|---:|---|---:|---:|"]
    summaries = {r["condition"]: r for r in result["summary"]}
    for row in result["contrasts"]:
        endpoint = row["endpoint"]
        def cell(condition):
            s = summaries[condition]
            rate = s[endpoint + "_world_mean"]
            return f"{s[endpoint + '_numerator']}/120 ({100 * rate:.2f}%)" if endpoint.startswith("complete_") else f"{rate:.6f}"
        lines.append(f"| {endpoint} | {cell(CONDITIONS[0])} | {cell(CONDITIONS[1])} | {100 * row['difference']:.2f} | "
                     f"[{100 * row['ci95_low']:.2f}, {100 * row['ci95_high']:.2f}] | {row['p_sign_flip']:.6f} | {row['q_bh_within_family']:.6f} |")
    lines += ["", "统计先按 qid 配对，再在每个世界内平均两个 URL 版本差异；60 世界为独立单位。按生成种子分层 bootstrap 5000 次，whole-world sign-flip 20000 次，seed=20261002。",
              "本轮四项检验族独立于原回答分析；没有改动原 study_plan 的主要比较。符号翻转依赖零假设下世界差异的符号可交换性。", "",
              "| 本轮120任务的证据指标 | No-cap | Post-cap2 |", "|---|---:|---:|"]
    for key in ("G_final", "U_sim", "fact_coverage", "admissible_U_sim"):
        vals = [sum(float(r[key]) for r in evidence if r["condition"] == c) / 120 for c in CONDITIONS]
        lines.append(f"| {key} | {vals[0]:.6f} | {vals[1]:.6f} |")
    coverage_counts = [sum(int(float(r["U_sim"])) for r in evidence if r["condition"] == c) for c in CONDITIONS]
    lines += ["", f"本轮完整证据覆盖分别为 {coverage_counts[0]}/120 和 {coverage_counts[1]}/120，"
              f"Post−Off 为 {100 * (coverage_counts[1] - coverage_counts[0]) / 120:.2f} 个百分点。"]
    lines += ["", "上述证据指标来自本轮120任务子集，不能替换 Fig.4 全600任务的结果。证据完整到达、回答正确、正确且有合法引用支持是不同端点。", "",
              "512迁移检查：6任务×2次；同机原始token重复一致。与旧机器比较的差异如下（不按结果挑选设置）：",
              "```json", json.dumps(baseline, ensure_ascii=False, indent=2), "```", "",
              "2048试跑：6任务×2条件×2次；比较报告：", "```json", json.dumps(smoke, ensure_ascii=False, indent=2), "```", "",
              "正式两组始终在同一新环境配对执行。跨旧硬件/平台差异如上披露，不据此修改提示词、种子或attention实现。", "",
              "| 诊断 | No-cap | Post-cap2 |", "|---|---:|---:|"]
    for key in ("invalid_json_outputs", "schema_valid_numerator", "hit_max_new_tokens_numerator", "truncated_output_numerator",
                "unsupported_fields_total", "unsupported_abstentions_total", "unsupported_answers_total"):
        lines.append(f"| {key} | {summaries[CONDITIONS[0]][key]} | {summaries[CONDITIONS[1]][key]} |")
    diagnostics = result["generation_diagnostics"]
    status = load_json(output / "status.json")
    commands = [json.loads(line) for line in (work / "commands.jsonl").read_text().splitlines() if line.strip()]
    first_run = min(datetime.fromisoformat(r["started_at_utc"]) for r in commands if r["stage"] == "run")
    finished = datetime.fromisoformat(status["finished_at_utc"])
    lines += ["", f"正式 model.generate 调用累计 {diagnostics['generation_seconds_sum']:.2f} 秒；"
              f"从首次正式命令启动至完成的墙钟跨度为 {(finished - first_run).total_seconds():.2f} 秒，包含输入审计；"
              "若续跑曾中断，该跨度也包含间隔，分会话时长另见 status.json。",
              f"正式 prompt 长度范围为 {diagnostics['prompt_tokens_min']}–{diagnostics['prompt_tokens_max']} 个 Qwen tokens；"
              f"逐次生成记录的最大显存峰值为 {diagnostics['max_generation_peak_cuda_bytes'] / 1024 ** 2:.2f} MiB。",
              "baseline512 的12次和 smoke2048 的24次与正式240次分开保存；本流程共276次生成调用，工程检查不进入正式统计。"]
    lines += ["", "所有正式输出均保留，包含错误与无效JSON；没有格式修复或成绩筛选。grounding复用原评测器，不等于人工语义质量或完整citation precision。",
              "零经验差异或CI包含零不证明总体等效；显著性与方向按实际结果报告。本实验不单独识别事实覆盖的纯中介因果效应，不证明外部真实场景或普适部署收益。", "",
              "环境记录：", "```json", json.dumps(manifest["identity"]["environment"], ensure_ascii=False, indent=2), "```", "",
              "生成身份：`" + manifest["identity_hash"] + "`。分析身份、各回答及汇总哈希见 analysis_manifest.json；最终验收见 verification.json。",
              "完整命令与带时区的运行时间记录在 `" + str(work / "commands.jsonl") + "`，各阶段wall time见状态文件；generation_ms仅是model.generate调用成本。", "",
              "新增源码为 downstream_2048.py 与 analyze_answers_2048.py，新增测试为 test_strengthening_downstream_2048.py；原论文、原数据、原回答、轨迹、代码及锁文件的保护检查见 verification.json。",
              "正式结果目录：`" + str(output) + "`。"]
    return "\n".join(lines) + "\n"


def analyze(output, work):
    output, work = Path(output), Path(work)
    manifest, status, plan = load_json(output / "manifest.json"), load_json(output / "status.json"), load_json(work / "followup_plan.json")
    require(status["status"] == "complete" and status["observed_answers"] == 240, "Formal generation is incomplete")
    require(manifest["identity"]["plan_sha256"] == digest(plan), "Analysis plan changed")
    records = [load_json(p) for p in sorted((output / "responses").glob("*.json"))]
    require(all(r["identity_hash"] == manifest["identity_hash"] for r in records), "Foreign answer identity")
    rows = [dict(answer_row(r), parsed_json_object=r["parsed_json_object"]) for r in records]
    result = compute(rows, manifest["identity"])
    result["generation_diagnostics"] = {
        "generation_seconds_sum": sum(r["generation_ms"] for r in records) / 1000,
        "prompt_tokens_min": min(r["prompt_tokens"] for r in records), "prompt_tokens_max": max(r["prompt_tokens"] for r in records),
        "max_generation_peak_cuda_bytes": max(r["peak_cuda_allocated_bytes"] for r in records)}
    identity = analysis_identity(output, manifest, plan)
    current = output / "analysis_manifest.json"
    if current.exists() and load_json(current)["analysis_identity_hash"] != digest(identity):
        old = load_json(current)
        archive = work / "analysis_history" / old["analysis_identity_hash"]
        archive.mkdir(parents=True, exist_ok=True)
        for name in (*OUTPUT_NAMES, "analysis_manifest.json", "verification.json"):
            src, dest = output / name, archive / name
            if src.exists():
                if dest.exists():
                    require(file_hash(dest) == file_hash(src), "Analysis history would be overwritten")
                else:
                    shutil.copy2(src, dest)
    write_csv(output / "per_answer.csv", rows)
    write_csv(output / "summary.csv", result["summary"])
    write_csv(output / "answer_world_summary.csv", result["world_summary"])
    write_csv(output / "answer_contrasts.csv", result["contrasts"])
    save_json(output / "paired_transitions.json", result["transitions"])
    with (output / "evidence_2048_subset.csv").open(encoding="utf-8", newline="") as f:
        evidence = list(csv.DictReader(f))
    (output / "RESULT_REPORT.md").write_text(report_text(result, manifest, plan, evidence, work, output), encoding="utf-8")
    save_json(current, {"status": "complete", "analysis_identity_hash": digest(identity), "identity": identity,
                        "output_hashes": {n: file_hash(output / n) for n in OUTPUT_NAMES}})
    return result


def verify_analysis(output, work, records):
    output, work = Path(output), Path(work)
    manifest, plan, saved = load_json(output / "manifest.json"), load_json(work / "followup_plan.json"), load_json(output / "analysis_manifest.json")
    identity = analysis_identity(output, manifest, plan)
    require(saved["status"] == "complete" and saved["identity"] == identity and saved["analysis_identity_hash"] == digest(identity),
            "Analysis identity is stale")
    for name, expected in saved["output_hashes"].items():
        require(name in OUTPUT_NAMES and file_hash(output / name) == expected, "Analysis output hash differs: " + name)
    require(set(saved["output_hashes"]) == set(OUTPUT_NAMES), "Analysis output set differs")
    rows = [dict(answer_row(r), parsed_json_object=r["parsed_json_object"]) for r in records]
    result = compute(rows, manifest["identity"])
    for name, values in (("per_answer.csv", rows), ("summary.csv", result["summary"]),
                         ("answer_world_summary.csv", result["world_summary"]), ("answer_contrasts.csv", result["contrasts"])):
        compare_csv(output / name, values)
    require(load_json(output / "paired_transitions.json") == result["transitions"], "Paired transitions differ")
    return {"analysis_identity_hash": saved["analysis_identity_hash"], "endpoints": len(result["contrasts"]), "worlds": 60, "task_pairs": 120}
