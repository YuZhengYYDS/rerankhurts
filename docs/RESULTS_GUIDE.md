# 结果与论文的对应关系

## 论文

`paper/main.tex` 是 2026-10-26 从用户提供的 ZIP 替换的当前稿件源文件。
正文位于 `paper/sections/`，图表布局在 `paper/layout.tex`；F1–F3 使用 PDF，
F4–F12 使用布局文件直接引用的 `*-v2.pdf`。当前稿件包含 58 个粗体开头段落、
7 个编号章节、12 幅图和 4 张表。作者信息以 `paper/authors.tex` 为准。

`python scripts/build_paper.py` 优先使用 PDFLaTeX/BibTeX，否则使用 Tectonic，
只将最终 PDF 写入 `paper/main.pdf`，编译中间文件保存在 `build/paper/`。
构建身份与页数见 `validation/paper_build.json`，结构检查见
`validation/manuscript_checks.json`。当前构建为 12 页；编号图允许共享页面，
F12 位于第 11 页。正文上限检查把与致谢或参考文献共享的正文浮动图页计入正文。

替换前的完整论文及绘图输入保存在 `archive/paper_20261022/`，包括旧版
`generated/`、draw.io 文件、来源数据和历史审计记录。这些归档文件保持原字节；
下文冻结实验的目录和统计结果保持不变，本次替换没有重新运行模型。

## 扩展实验：360个世界、720任务 × 124配置

完整流程与指标说明见 [STRENGTHENING_GUIDE.md](STRENGTHENING_GUIDE.md)，
研究设计见 [模块说明](../experiments/strengthening/README.md)。2026-10-02实验完成状态：
四阶段自动化部分已完成：89,280条主推断及独立评分记录、720个实际回答、576个正式计时请求。
计时另有8次warm-up不计入结果；主推断、评分、回答和计时分别记录 `complete`。

输入在 `experiments/strengthening/data/strengthening_v1/`：

- `corpus.jsonl`、`questions.jsonl`：公开推断接口，720个互相隔离的80-chunk集合。
- `truth.jsonl`、`metadata.jsonl`、`claims.jsonl`：世界事实、配对与split信息、已由独立parser核对的断言。
- `specification.json`：生成代码、计划、维度及数据哈希。
- `audit/`：独立文本解析审计和 60 世界人工审核材料；人工语义审核已完成。

实际主推断在 `experiments/runs/strengthening_v1/`：`manifest.json` 固定124配置、
模型、代码和输入身份，`traces/` 保存720个压缩逐题轨迹，`status.json` 记录主推断完成数。
每个独立世界的两个任务只改变来源URL集中度，不能当作两份独立世界。

评估与分析位于 `experiments/strengthening/results/strengthening_v1/`。
下列已完成产物由对应状态、来源哈希和完整性检查关联：

- `per_record.csv`、`feasibility.csv`、`status.json`：实际交付跨度评分、预算必要可行性界和输入身份。
- `primary_contrasts.csv`、`exploratory_contrasts.csv`、`subgroup_summary.csv`：世界级主对比、探索族和分层分析。
- `support_flow.csv`、`source_coverage_four_cells.csv`、`controls.json`、`redundant_support_control.json`：阶段支持损失、G/U组合及结构控制。
- `answers/`：60测试世界、两个变体、六条件的实际Qwen回答、输入prompt、token成本与评分。
- `timing/`：24测试世界、每世界一个变体、四配置的96个first-pass和480个steady测量；8次warm-up不计入。
- `analysis.json`、`figures/manifest.json`：统计设置、输入身份和图文件来源。

当前稿件直接包含正文中的表格，不依赖历史 `paper/generated/` 文件。
历史扩展实验表及来源记录保存在 `archive/paper_20261022/generated/`。
`python -m rerankhuts tables` 使用 `scripts/paper/` 下的生成器，
将 E3、pilot 和扩展实验表重算到 `build/reanalysis/tables/`，不写入当前论文或归档。
主研究与旧 E3、`pilot_v2` 使用不同目录。

```text
# 新复现尚未结束时可使用的检查，不将PENDING当作完成
pixi run --locked strengthen-verify --allow-in-progress

# 已完成交付结果的严格检查
pixi run --locked strengthen-verify --require-complete
```

## 冻结 E3：155 题 × 20 配置

在 `experiments/runs/e3_m3/`：

- `manifest.json`：数据、模型、代码和实验参数身份。
- `summary.csv`：全部 20 配置的页面保留率、URL-nDCG、token 数和组件时间。
- `per_question.csv`：3,100 条逐题配置结果。
- `traces/`：155 个压缩逐题轨迹，每个包含 20 配置。
- `G_contrasts.csv`：16 个探索性配对比较。
- `factorial_diagnostics.json`：另八个 cap/re-ranker 交互。
- `G_factorial.pdf`：论文页面保留率热图。

`scripts/paper/build_e3_table.py` 从上述冻结文件重算历史 E3 表和来源记录，
输出位于 `build/reanalysis/tables/e3/`。
`validation/results/e3_integrity.json` 保存独立轨迹核验；执行 `verify` 的新报告
写在 `build/verification/e3/`。

## 冻结 pilot_v2：60 个世界、120 个任务 × 20 配置

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

`scripts/paper/build_simulation_table.py` 重算历史 pilot 选择比较表，
输出位于 `build/reanalysis/tables/simulation/`。
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

扩展实验的无模型重算入口为：

```text
pixi run --locked -e gpu strengthen-evaluate --output build/reanalysis/strengthening
pixi run --locked strengthen-analyze --results build/reanalysis/strengthening --answers experiments/strengthening/results/strengthening_v1/answers --timing experiments/strengthening/results/strengthening_v1/timing
```

该评分只需要固定fast tokenizer，不运行检索或答案模型。答案/测时目录必须是已完成版本，
缺失或未完成的步骤不能通过新增CSV名称补成结果。输入与模型准备细节见扩展实验指南。

结果专用 ZIP 保留上述冻结文件的原相对路径和来源清单。它便于查看结果，
但不等于完整复现包；需要代码与输入语料时请使用 `rerankhuts_icde2027.zip`。
原根目录的肿瘤学语料、问题集、报告和来源信息已迁至 `data/oncology/`，
具体路径及使用说明见根目录 `guide.md`。仓库来源清单位于
`metadata/MANIFEST.json`，发布状态位于 `metadata/release_status.json`；
三者同时进入完整包、代码分包和结果分包，原始输入数据只进入完整包。
每个 ZIP 另在顶层生成 `MANIFEST.json`，记录该包所有文件的字节数与 SHA-256，
其中也包括仓库的 `metadata/MANIFEST.json`；两份清单分别用于来源追溯与包内容校验。
代码分包显式包含 `experiments/strengthening/study_plan.json` 与 `.gitattributes`；
结果分包包含新结果、主轨迹、研究计划和扩展指南，完整包另含全部输入数据。

代码仓库见 [GitHub](https://github.com/YuZhengYYDS/rerankhuts)。
交付包见 [icde2027-restructured-20261013 下载入口](https://github.com/YuZhengYYDS/rerankhuts/releases/tag/icde2027-restructured-20261013)。
60 世界人工语义审核已完成；独立的外部真实场景复现尚未完成。
