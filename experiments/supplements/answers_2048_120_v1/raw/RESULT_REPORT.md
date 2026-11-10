# 2048-token 回答对照补实验结果

本轮是追加的受控合成实验，沿用原 Fig.9 的 60 个测试世界、120 个任务，共 240 个正式回答。
比较方向统一为 Post-cap2 M3 − No-cap M3。两组使用原轨迹保存的 B2048 上下文，dense/pool64/M3、prefix packing、检索与评分 prefix512 保持一致。

模型为 Qwen/Qwen2.5-1.5B-Instruct，revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`。
生成采用 CUDA FP16、SDPA、逐条 greedy、max_new_tokens=256，复用原 build_messages 与 score_answer。

| 指标 | No-cap | Post-cap2 | Post−Off（百分点） | 世界级95% CI（百分点） | p | BH q（4项族） |
|---|---:|---:|---:|---|---:|---:|
| complete_correct | 32/120 (26.67%) | 30/120 (25.00%) | -1.67 | [-5.83, 2.50] | 0.690365 | 0.690365 |
| complete_grounded_correct | 14/120 (11.67%) | 12/120 (10.00%) | -1.67 | [-4.17, 0.00] | 0.503425 | 0.671233 |
| field_accuracy | 0.473611 | 0.494444 | 2.08 | [-2.22, 6.74] | 0.413279 | 0.671233 |
| grounded_field_accuracy | 0.229167 | 0.216667 | -1.25 | [-4.31, 1.74] | 0.473126 | 0.671233 |

统计先按 qid 配对，再在每个世界内平均两个 URL 版本差异；60 世界为独立单位。按生成种子分层 bootstrap 5000 次，whole-world sign-flip 20000 次，seed=20261002。
本轮四项检验族独立于原回答分析；没有改动原 study_plan 的主要比较。符号翻转依赖零假设下世界差异的符号可交换性。

| 本轮120任务的证据指标 | No-cap | Post-cap2 |
|---|---:|---:|
| G_final | 0.891667 | 0.891667 |
| U_sim | 0.616667 | 0.583333 |
| fact_coverage | 0.786111 | 0.764583 |
| admissible_U_sim | 0.616667 | 0.583333 |

本轮完整证据覆盖分别为 74/120 和 70/120，Post−Off 为 -3.33 个百分点。

上述证据指标来自本轮120任务子集，不能替换 Fig.4 全600任务的结果。证据完整到达、回答正确、正确且有合法引用支持是不同端点。

512迁移检查：6任务×2次；同机原始token重复一致。与旧机器比较的差异如下（不按结果挑选设置）：
```json
{
  "compared": [
    "messages",
    "prompt_sha256",
    "prompt_token_ids",
    "generated_token_ids",
    "response",
    "evaluation"
  ],
  "generations": 12,
  "migration_interpretation": "Identical pinned inputs/protocol and stable new-machine repeats. Old-machine differences, if any, are disclosed; no parameter tuning.",
  "old_evaluation_differences": 0,
  "old_machine_comparisons": [
    {
      "evaluation_same": true,
      "new_evaluation": {
        "complete_correct": 0,
        "complete_grounded_correct": 0,
        "field_accuracy": 0.0,
        "fields": [
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "release_code",
            "shape_valid": false,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "review_days",
            "shape_valid": false,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "route",
            "shape_valid": false,
            "unsupported_answer": true
          }
        ],
        "grounded_field_accuracy": 0.0,
        "schema_valid": false,
        "unsupported_abstentions": 0,
        "unsupported_answers": 3,
        "unsupported_fields": 3
      },
      "old_evaluation": {
        "complete_correct": 0,
        "complete_grounded_correct": 0,
        "field_accuracy": 0.0,
        "fields": [
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "release_code",
            "shape_valid": false,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "review_days",
            "shape_valid": false,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "route",
            "shape_valid": false,
            "unsupported_answer": true
          }
        ],
        "grounded_field_accuracy": 0.0,
        "schema_valid": false,
        "unsupported_abstentions": 0,
        "unsupported_answers": 3,
        "unsupported_fields": 3
      },
      "qid": "711d2df2142d42abe22a4bd32180",
      "response_same": true
    },
    {
      "evaluation_same": true,
      "new_evaluation": {
        "complete_correct": 1,
        "complete_grounded_correct": 1,
        "field_accuracy": 1.0,
        "fields": [
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "route",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "review_days",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "release_code",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "retention_days",
            "shape_valid": true,
            "unsupported_answer": false
          }
        ],
        "grounded_field_accuracy": 1.0,
        "schema_valid": true,
        "unsupported_abstentions": 0,
        "unsupported_answers": 0,
        "unsupported_fields": 0
      },
      "old_evaluation": {
        "complete_correct": 1,
        "complete_grounded_correct": 1,
        "field_accuracy": 1.0,
        "fields": [
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "route",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "review_days",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "release_code",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "retention_days",
            "shape_valid": true,
            "unsupported_answer": false
          }
        ],
        "grounded_field_accuracy": 1.0,
        "schema_valid": true,
        "unsupported_abstentions": 0,
        "unsupported_answers": 0,
        "unsupported_fields": 0
      },
      "qid": "916204137416b35d529be0143939",
      "response_same": true
    },
    {
      "evaluation_same": true,
      "new_evaluation": {
        "complete_correct": 1,
        "complete_grounded_correct": 1,
        "field_accuracy": 1.0,
        "fields": [
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "route",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "review_days",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "release_code",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "retention_days",
            "shape_valid": true,
            "unsupported_answer": false
          }
        ],
        "grounded_field_accuracy": 1.0,
        "schema_valid": true,
        "unsupported_abstentions": 0,
        "unsupported_answers": 0,
        "unsupported_fields": 0
      },
      "old_evaluation": {
        "complete_correct": 1,
        "complete_grounded_correct": 1,
        "field_accuracy": 1.0,
        "fields": [
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "route",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "review_days",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "release_code",
            "shape_valid": true,
            "unsupported_answer": false
          },
          {
            "abstained": false,
            "answerable": true,
            "correct": true,
            "grounded_correct": true,
            "key": "retention_days",
            "shape_valid": true,
            "unsupported_answer": false
          }
        ],
        "grounded_field_accuracy": 1.0,
        "schema_valid": true,
        "unsupported_abstentions": 0,
        "unsupported_answers": 0,
        "unsupported_fields": 0
      },
      "qid": "cc016c1f29cb8c29e80156792695",
      "response_same": true
    },
    {
      "evaluation_same": true,
      "new_evaluation": {
        "complete_correct": 0,
        "complete_grounded_correct": 0,
        "field_accuracy": 0.0,
        "fields": [
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "release_code",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "review_days",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "route",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "retention_days",
            "shape_valid": true,
            "unsupported_answer": true
          }
        ],
        "grounded_field_accuracy": 0.0,
        "schema_valid": true,
        "unsupported_abstentions": 0,
        "unsupported_answers": 4,
        "unsupported_fields": 4
      },
      "old_evaluation": {
        "complete_correct": 0,
        "complete_grounded_correct": 0,
        "field_accuracy": 0.0,
        "fields": [
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "release_code",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "review_days",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "route",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "retention_days",
            "shape_valid": true,
            "unsupported_answer": true
          }
        ],
        "grounded_field_accuracy": 0.0,
        "schema_valid": true,
        "unsupported_abstentions": 0,
        "unsupported_answers": 4,
        "unsupported_fields": 4
      },
      "qid": "d241f04f92cc48b0def16989c336",
      "response_same": true
    },
    {
      "evaluation_same": true,
      "new_evaluation": {
        "complete_correct": 0,
        "complete_grounded_correct": 0,
        "field_accuracy": 0.0,
        "fields": [
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "release_code",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "review_days",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "route",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "retention_days",
            "shape_valid": true,
            "unsupported_answer": true
          }
        ],
        "grounded_field_accuracy": 0.0,
        "schema_valid": true,
        "unsupported_abstentions": 0,
        "unsupported_answers": 4,
        "unsupported_fields": 4
      },
      "old_evaluation": {
        "complete_correct": 0,
        "complete_grounded_correct": 0,
        "field_accuracy": 0.0,
        "fields": [
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "release_code",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "review_days",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "route",
            "shape_valid": true,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "retention_days",
            "shape_valid": true,
            "unsupported_answer": true
          }
        ],
        "grounded_field_accuracy": 0.0,
        "schema_valid": true,
        "unsupported_abstentions": 0,
        "unsupported_answers": 4,
        "unsupported_fields": 4
      },
      "qid": "ed76cfecb87f88c062b561d2ef75",
      "response_same": true
    },
    {
      "evaluation_same": true,
      "new_evaluation": {
        "complete_correct": 0,
        "complete_grounded_correct": 0,
        "field_accuracy": 0.0,
        "fields": [
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "release_code",
            "shape_valid": false,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "review_days",
            "shape_valid": false,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "route",
            "shape_valid": false,
            "unsupported_answer": true
          }
        ],
        "grounded_field_accuracy": 0.0,
        "schema_valid": false,
        "unsupported_abstentions": 0,
        "unsupported_answers": 3,
        "unsupported_fields": 3
      },
      "old_evaluation": {
        "complete_correct": 0,
        "complete_grounded_correct": 0,
        "field_accuracy": 0.0,
        "fields": [
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "release_code",
            "shape_valid": false,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "review_days",
            "shape_valid": false,
            "unsupported_answer": true
          },
          {
            "abstained": false,
            "answerable": false,
            "correct": false,
            "grounded_correct": false,
            "key": "route",
            "shape_valid": false,
            "unsupported_answer": true
          }
        ],
        "grounded_field_accuracy": 0.0,
        "schema_valid": false,
        "unsupported_abstentions": 0,
        "unsupported_answers": 3,
        "unsupported_fields": 3
      },
      "qid": "f8751591886bc562861f52eb24e5",
      "response_same": true
    }
  ],
  "old_response_differences": 0,
  "original_generated_token_ids_available": false,
  "same_machine_identical": true,
  "status": "PASS",
  "task_condition_pairs": 6,
  "timing_compared": false
}
```

2048试跑：6任务×2条件×2次；比较报告：
```json
{
  "compared": [
    "messages",
    "prompt_sha256",
    "prompt_token_ids",
    "generated_token_ids",
    "response",
    "evaluation"
  ],
  "generations": 24,
  "same_machine_identical": true,
  "status": "PASS",
  "task_condition_pairs": 12,
  "timing_compared": false
}
```

正式两组始终在同一新环境配对执行。跨旧硬件/平台差异如上披露，不据此修改提示词、种子或attention实现。

| 诊断 | No-cap | Post-cap2 |
|---|---:|---:|
| invalid_json_outputs | 8 | 5 |
| schema_valid_numerator | 110 | 115 |
| hit_max_new_tokens_numerator | 6 | 5 |
| truncated_output_numerator | 6 | 5 |
| unsupported_fields_total | 86 | 98 |
| unsupported_abstentions_total | 6 | 5 |
| unsupported_answers_total | 278 | 282 |

正式 model.generate 调用累计 483.39 秒；从首次正式命令启动至完成的墙钟跨度为 638.50 秒，包含输入审计；若续跑曾中断，该跨度也包含间隔，分会话时长另见 status.json。
正式 prompt 长度范围为 2237–2556 个 Qwen tokens；逐次生成记录的最大显存峰值为 3238.58 MiB。
baseline512 的12次和 smoke2048 的24次与正式240次分开保存；本流程共276次生成调用，工程检查不进入正式统计。

所有正式输出均保留，包含错误与无效JSON；没有格式修复或成绩筛选。grounding复用原评测器，不等于人工语义质量或完整citation precision。
零经验差异或CI包含零不证明总体等效；显著性与方向按实际结果报告。本实验不单独识别事实覆盖的纯中介因果效应，不证明外部真实场景或普适部署收益。

环境记录：
```json
{
  "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
  "CUDA_VISIBLE_DEVICES": "0",
  "HF_HUB_OFFLINE": "1",
  "PYTHONHASHSEED": "20260924",
  "TOKENIZERS_PARALLELISM": "false",
  "TRANSFORMERS_OFFLINE": "1",
  "compute_capability": [
    12,
    0
  ],
  "cuda_runtime": "12.8",
  "cudnn_version": 91002,
  "driver": "580.95.05",
  "gpu_name": "NVIDIA GeForce RTX 5090",
  "gpu_uuid": "GPU-b7938351-2403-eed1-8a09-e38cbebfc01c",
  "packages": {
    "hf-xet": "1.6.0",
    "huggingface-hub": "0.36.2",
    "numpy": "2.2.6",
    "pandas": "2.3.3",
    "sentence-transformers": "5.1.2",
    "torch": "2.8.0+cu128",
    "transformers": "4.57.1"
  },
  "physical_gpu": "0",
  "platform": "Linux-5.14.0-284.25.1.el9_2.x86_64-x86_64-with-glibc2.31",
  "python": "3.11.16"
}
```

生成身份：`970030dc1802d8e992fb4c6648250191a945391942f0b7e591cbb937fb1588c4`。分析身份、各回答及汇总哈希见 analysis_manifest.json；最终验收见 verification.json。
完整命令与带时区的运行时间记录在 `/data/L202500309/JIELI/RAG/github files/rerankhurts-main/rerankhurts-main/build/answer2048_120/commands.jsonl`，各阶段wall time见状态文件；generation_ms仅是model.generate调用成本。

新增源码为 downstream_2048.py 与 analyze_answers_2048.py，新增测试为 test_strengthening_downstream_2048.py；原论文、原数据、原回答、轨迹、代码及锁文件的保护检查见 verification.json。
正式结果目录：`/data/L202500309/JIELI/RAG/github files/rerankhurts-main/rerankhurts-main/experiments/strengthening/results/strengthening_v1/answers_2048_120`。
