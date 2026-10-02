# 结果与论文的对应关系

## 论文

`paper/main.pdf` 与 `paper/main.tex` 是当前九页稿件，`authors.tex` 记录 Zheng Yu
为第一作者、Jingbang Chen 为通讯作者。Overview 在第二页保留空白；本轮代码整理
不会改动论文或实验结论。

## 新 E3：155 题 × 20 配置

在 `experiments/runs/e3_m3/`：

- `manifest.json`：数据、模型、代码和实验参数身份。
- `summary.csv`：全部 20 配置的页面保留率、URL-nDCG、token 数和组件时间。
- `per_question.csv`：3,100 条逐题配置结果。
- `traces/`：155 个压缩逐题轨迹，每个包含 20 配置。
- `G_contrasts.csv`：16 个探索性配对比较。
- `factorial_diagnostics.json`：另八个 cap/re-ranker 交互。
- `G_factorial.pdf`：论文页面保留率热图。

`paper/build_e3_table.py` 从上述冻结文件生成论文表 I 和来源记录。
`validation/results/e3_integrity.json` 保存独立轨迹核验；执行 `verify` 的新报告
写在 `build/verification/e3/`。

## 仿真：60 个世界、120 个任务 × 20 配置

输入在 `experiments/simulation/data/pilot_v2/`：corpus、questions、oracle 与 specification。
实际模型轨迹在 `experiments/runs/simulation_pilot_v2/`，共 120 个逐任务 trace。
同一世界的 open/constrained 任务属于同一实验单位。

评分和选择结果在 `experiments/simulation/results/pilot_v2/`：

- `per_record.csv`：2,400 条 G、完整覆盖、部分覆盖、冲突/过时暴露、来源合规记录。
- `summary.csv`：总体及各场景、split、policy、配置的聚合值。
- `selection.json`：固定开发集选择、全部并列集合、测试对比、区间和选择稳定性。
- `budget_feasibility.json`：512-token 下 late-evidence 的结构不可达条件与保留分母。
- `status.json`：完整性、输入与输出哈希，明确标记 synthetic_oracle。
- `selection_comparison.pdf`：论文测试集配置对比图。

`paper/build_simulation_table.py` 生成论文表 II。
`validation/simulation_audit.json` 为独立结果复核；
`validation/simulation_endpoint_pairs.json` 为论文 G/U 配对频数的独立复算。

## 历史结果与修正

`result/emnlp_full_results_20260427_gpu_final/` 和 `results/` 保留原发布记录。
这两个相似目录名来自原代码包，为保持路径可追溯而保留，不能将它们简单合并。
`validation/results/` 给出原日志审计、417 单元核对和修正结果；
`corrected_supp_query_normalization_overall.csv` 是查询规范化指标的更正值。

历史 nDCG 的计算单位是首个 gold chunk，新实验 URL-nDCG 则按不同 URL 计分。
原始表与修正表不能按相同名字混用。E0 是日志重算，不是历史模型/API 重跑。

## 重新分析与结果包

`pixi run --locked e0` 与 `analyze-e3` 把新产物写到 `build/reanalysis/`。
`pixi run --locked -e gpu sim-evaluate` 将完整 oracle 复算写到
`build/reanalysis/simulation/`。这些路径不进入发布包。

结果专用 ZIP 保留上述冻结文件的原相对路径和来源清单。它便于查看结果，
但不等于完整复现包；需要代码与输入语料时请使用 `rerankhuts_icde2027.zip`。
