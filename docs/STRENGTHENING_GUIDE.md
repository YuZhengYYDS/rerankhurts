# 扩展实验的运行、复核与结果读取

本指南对应 `strengthening_v1`。实验研究虚构行政档案中的来源集中度、评分可见范围和证据打包机制；不是临床数据验证。数据先生成并独立审计，再按冻结配置执行模型。2026-10-02四阶段自动化部分已完成：89,280条主推断及独立评分记录、720个实际模型回答、576个在线请求测量，另有8次warm-up不计入结果。各步骤分别记录 `complete`；复核仍应检查相应 `status.json`、来源哈希与完整性。

2026-10-13论文重构将该研究作为主研究，`main.tex` 在 Benchmark and Experimental Design 中直接载入方法，`strengthening.tex` 仅载入主结果。此次修改没有重跑实验，计算代码、数据和统计结果不变，表格生成器仅调整表注文字；下面的流程仍对应10月2日完成的冻结实验。

所有命令从仓库根目录执行。先从 [Pixi 官方文档](https://pixi.sh/latest/installation/) 安装 Pixi 并使 `pixi` 可在终端调用；使用仓库中的 `pixi.toml`、`pixi.lock`，不要将本机 `.pixi/` 复制给其他机器。代码和模型缓存可放在带空格或中文的路径中。

## 先验证已有交付包

完整复核使用 **完整 ZIP**，保留其目录结构。代码分包只供阅读和开发，缺少输入数据、模型轨迹及统计结果；代码 ZIP 与结果 ZIP 的组合也不保证包含所有原始输入。论文分包用于单独编译论文。需要原始数据和全部 provenance 时，使用完整包。

```text
pixi run --locked strengthen-verify --require-complete
pixi run --locked verify
pixi run --locked test
```

第一条专门核验新实验；第二条核验旧 E0/E3 与 `pilot_v2`。`strengthen-verify` 使用 Python 标准库检查已保存文件、精确记录集合、SHA-256 和原始来源引用，不需要模型缓存。已有 Python 时也可直接执行：

```text
python scripts/check_strengthening_files.py --require-complete
```

验证当前交付使用 `--require-complete`；`--allow-in-progress` 用于开发过程中检查新生成的运行目录。当前 60-world 的 A、B 两轮人工核查已完成，见[完成记录](../experiments/strengthening/data/strengthening_v1/audit/reviews/completion.json)。

## 固定的数据与独立单位

数据目录为 `experiments/strengthening/data/strengthening_v1/`。三个生成种子为 `20261002`、`20261003`、`20261004`，每个种子固定 20 个 development worlds、100 个 test worlds：共 **360 个独立世界、60 个开发世界、300 个测试世界**。

每个世界有两个来源集中度变体，共 720 个任务。每任务只检索自己的 80 个 chunk，合计 57,600 个 chunk。两个变体保留问题、按原顺序排列的文档文本、事实值和 publisher host，只改变十二个页面 URL 的归属。同一世界的所有任务保持在同一 split；两个变体不是两个独立样本。

开发文档采用 prose/list，测试包括 150 个未在开发中使用 QA 文档模板的世界。问题使用固定中性句式和与文档谓词不同的措辞。这是未见**文档模板**条件下的评估，不是同世界更换模板的实验，也不代表已经覆盖独立的多问题模板。

模型只接触 `corpus.jsonl` 的公开文本字段，以及 `questions.jsonl` 中的问题、collection 与显式来源约束。`truth.jsonl`、`metadata.jsonl`、`claims.jsonl` 是评估侧文件。独立 parser 从原文重建断言并核对世界事实，生成器的 `status` 标签不直接授予覆盖分数。

固定文件 SHA-256：

```text
specification.json  90daa40eec2c4603bebb5918f1e77b21b7d59f9df659edb55deb84d793b8143b
corpus.jsonl         b882dc31e8ed9a96df520f5e5b6423a64f3e17fa4770ab3840385dddd5b8ccb5
questions.jsonl      71303669f245110cffb695dcb9d779e9896d1c353d58109485aa6c54510b77d7
metadata.jsonl       c43eb0ec083bbfa5e0672201a7a0e44374437266a0a12e506dced462cf3622b2
truth.jsonl          c4022335d4a79a7863b3f89df62b5d0e3e50e85b65a6ba60b1babd680287fdb7
claims.jsonl         2cbab46699b2ae34424e1a13c77139aaba1d3ce45168886d6a326bd4c1947451
```

数据 specification 同时记录生成代码、研究计划、split 和文件哈希。不要为继续旧 run 而修改清单中的哈希。协议、代码、模型、设备设置或数据变化时，使用新的版本和输出目录。

## 安装隔离环境与固定模型

```text
pixi install --locked -e default
pixi install --locked -e gpu
pixi run --locked -e gpu strengthen-models --include-answer-model
pixi run --locked -e gpu strengthen-models --include-answer-model --verify-only
```

`gpu` 环境提供 PyTorch、Transformers、Sentence Transformers 和 fast tokenizer。独立 oracle 重算不运行神经模型，但其 tokenizer 依赖也在这个环境中。默认模型推断使用 CUDA；CPU 可通过 `--device cpu` 另建 run，不能与既有 CUDA 身份混用。模型权重不放进发布 ZIP，首次下载需要网络，之后从 `.cache/models/<组织--模型>/<revision>/` 本地读取。

模型来源和冻结 revision：

- Dense encoder：[BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)，`5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`。
- 主 cross-encoder：[BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)，`953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`。
- 复现 cross-encoder：[cross-encoder/ms-marco-MiniLM-L6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2)，`233902d25c440f23af6f7d6e94d2946bac0bee0a`。
- 证据预算 tokenizer：[google-bert/bert-base-uncased](https://huggingface.co/google-bert/bert-base-uncased)，`86b5e0934494bd15c9632b12f734a8a67f723594`；这里只使用 tokenizer，不将 BERT 当成答案模型。
- 实际答案模型：[Qwen/Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)，`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`。

以上链接是各发布者维护的模型仓库。实验采用的 128/512 评分范围是本研究的固定干预，不应解释为所有模型的最大原生上下文。下载脚本验证 revision 的解析结果，并记录实际模型文件哈希。

## 从零复现到新目录

下面把新推断和重算结果写到 `build/reproduction/`，保留已发布的 run 和结果。生成器遇到同名但字节不同的数据会拒绝覆盖。重新审计使用新的 output，避免重写已有的人工填写模板。

完整包已带 `data/strengthening_v1/audit/`。如果是在没有该目录的新工作副本中首次生成数据，应先运行一次不带 `--output` 的 `pixi run --locked strengthen-audit`，建立默认独立审计记录；之后再将复核输出写入 `build/`。

```text
pixi run --locked strengthen-generate
pixi run --locked strengthen-audit --output build/reproduction/data_audit
pixi run --locked -e gpu strengthen-run --output build/reproduction/strengthening_run
pixi run --locked -e gpu strengthen-evaluate --run build/reproduction/strengthening_run --output build/reproduction/strengthening_results
pixi run --locked -e gpu strengthen-answers --run build/reproduction/strengthening_run --output build/reproduction/strengthening_results/answers
pixi run --locked -e gpu strengthen-timing --run build/reproduction/strengthening_run --output build/reproduction/strengthening_results/timing
pixi run --locked strengthen-analyze --results build/reproduction/strengthening_results
pixi run --locked python -m experiments.strengthening.figures --results build/reproduction/strengthening_results
pixi run --locked strengthen-verify --run build/reproduction/strengthening_run --results build/reproduction/strengthening_results --require-complete
```

完整推断矩阵有 **124 个定向配置**，已完成 `720 × 124 = 89,280` 条记录，包含 28 个主预算/cap 格子和预先选定的机制、模型、来源策略子矩阵；它不是所有因素的完整笛卡尔积。精确配置见 `experiments/strengthening/protocol.py` 和 run 的 `manifest.json`。

`strengthen-run` 按题写入压缩轨迹，可在身份一致时使用原命令续跑。`--limit 2` 只用于 smoke，输出必须另选目录，状态保留完整分母并标为 partial。对这样的 smoke 做评估时显式加入 `--allow-partial`；分析程序拒绝把 partial 当成完整研究结果。

答案模型实验固定选择 60 个测试世界、保留两个变体，共 120 个任务 × 6 个条件 = 720 个回答。实际在线计时固定 24 个测试世界，每世界一个变体、四种配置：96 个 first-pass 请求和 480 个 steady 请求，另有 8 个不计入结果的 warm-up 请求。计时会拒绝续写已有 `requests.jsonl`；中断后应另建 session，不能拼接成一次连续试验。

本地程序在电脑系统休眠期间不继续计算。需要持续计算时保持机器唤醒，或将完整仓库、固定环境和输入部署到持续在线的计算机；唤醒后可按上述规则恢复推断，独立计时则重新开始一次 session。

## 只重算已保存结果

无需重跑模型即可检查固定轨迹。先下载/验证固定 tokenizer，然后执行：

```text
pixi run --locked -e gpu strengthen-evaluate --output build/reanalysis/strengthening
pixi run --locked strengthen-analyze --results build/reanalysis/strengthening --answers experiments/strengthening/results/strengthening_v1/answers --timing experiments/strengthening/results/strengthening_v1/timing
```

重新分析和旧结果的字节核验是不同动作。`strengthen-verify` 验证发布目录中的冻结文件；上面的重算输出保存在 `build/`。主研究图生成器默认读取所选结果目录中的 `answers/` 和 `timing/`；要重建包含答案与时延的全部图，应在完整复现目录按前一节顺序运行，或对完整发布结果执行图生成器。

## 指标与统计如何解释

- `U_sim`：实际交付的原文区间覆盖所有必需的当前有效事实。多个同一来源片段可以共同覆盖一条断言，但缺少非空白字符的残片不获得完整断言支持。它不是人工证据充分性标签。
- `G_final`：预算内保留了指定 URL 的至少一个交付 token。它可能为 1 而 `U_sim` 为 0，反之也可能成立。
- `admissible_U_sim`、`C_sim`、`nonempty`：分别表示允许来源上的完整事实覆盖、非空且全部交付来源合法、输出非空；空输出不算合规。来源过滤的统计对比使用 constrained 任务。
- `contradiction_exposure` 和 `obsolete_exposure`：与正向事实覆盖分开记录。虚构设计把当前反事实放在 consortium publisher，过滤收益应按此设计条件解释。
- `score_visible_*`：模型评分看到的原文范围，与最终证据预算分开。`score_single_call_visible_*` 要求一条完整断言出现在至少一个完整评分输入中。
- 阶段支持流区分候选不存在、cap 删除、过滤及最终预算删除；纯重排只改变顺序，不应改变完整候选集合的支持成员。
- `feasibility.csv`：针对 prefix、whole、window 几何给出 oracle relaxation 的必要可行性条件。未通过可以排除该条件下的完整覆盖；通过不证明实际检索/排序/打包能达到它。不可行任务仍保留在主分母中。

两个主比较均是 post-cap 减 pre-cap 的测试 `U_sim`：dense、pool 64、M3、cap=2、no refill、prefix packing、dense/CE prefix512、无来源过滤，分别使用预算 512 与 2048。同一世界先平均两个变体差异，再按生成种子分层做 5,000 次世界 bootstrap；20,000 次世界符号翻转使用零假设下的符号交换性假设。两项主比较采用 Holm，其余预先列出的探索族分别采用 BH。零差异和退化区间不表示已经证明总体等价。

下游 `complete_correct` 只判断规范化后的虚构真值；`complete_grounded_correct` 还要求所引用片段包含至少一组完整、当前且来源合法的支持。该指标不等于逐条引用的 precision，额外无关引用没有单独的逐条惩罚。`schema_valid` 检查 JSON 的键与嵌套键结构。Closed-book 和 wrong-world 是明确的无支持控制，不能被当成正常有证据条件。

`first_pass` 是模型和文档索引已准备好之后的首轮测量，**不是冷启动或模型加载时间**。正式 latency 边界包括真实 query encoding、检索、CE、cap/过滤/打包和内存轨迹构造，排除模型加载、离线文档编码/索引、答案生成及磁盘序列化。这里不复用 query embedding 或 pair-score 结果缓存。诊断矩阵中的共享组件计时不能替代它；request p50/p95 也不是组件分位数之和。重复请求先在世界内求均值后进入配对统计。

## 产物、人工审计与旧实验

模型轨迹保存在 `experiments/runs/strengthening_v1/`；独立测量与分析在 `experiments/strengthening/results/strengthening_v1/`：

- `per_record.csv`、`feasibility.csv`、`status.json`：逐任务配置指标、预算界和来源哈希。
- `primary_contrasts.csv`、`exploratory_contrasts.csv`、`subgroup_summary.csv`：主比较、完整探索族和模板/seed/scenario/variant 分层。
- `support_flow.csv`、`source_coverage_four_cells.csv`、`controls.json`、`redundant_support_control.json`：机制与控制检查。
- `answers/`、`timing/`：实际生成回答、完整 prompt/token 成本和独立在线请求记录；其状态与主 run 分开。
- `answer_contrasts.csv`、`answer_world_summary.csv`、`timing_world_contrasts.csv`：世界级下游比较。
- `analysis.json`、`figures/manifest.json`：分析设置、源文件哈希、图文件哈希与图注；图同时输出 PDF/PNG。

人工语义审计已完成，覆盖审核包中的 60 个世界，由两位人工审核者完成。审核材料位于 `data/strengthening_v1/audit/`。自动 parser、单元测试、哈希校验和模型回答属于自动检查，与人工审核判断分开记录。

仓库公开交付受控 360-world 主实验、Oncology 固定语料对照、pilot、回答和请求计时记录。发布包的内容与哈希由打包工具核验，当前审核完成记录见 `experiments/strengthening/data/strengthening_v1/audit/reviews/completion.json`。

旧 `experiments/runs/e3_m3/`、`experiments/simulation/data/pilot_v2/`、`experiments/runs/simulation_pilot_v2/` 和旧结果保持原版本。`legacy_null_audit.json` 只是从旧保存结果重算 pre/post 差异，不是重新运行旧模型，也不允许用新世界结果覆盖原有零效应、并列或反向选择结果。

完整打包和 ZIP 复核入口：

```text
pixi run --locked package --split --verify
pixi run --locked verify-package
```

发布包排除 `.pixi/`、`.cache/`、本地模型权重和 `build/`。最终完整包必须包含冻结数据、run manifest/status/轨迹、独立评估与下游产物，才能在无模型缓存的另一台机器上通过 `strengthen-verify --require-complete`。

审计命令只接受新的输出目录。复核已交付数据时，将 `--output` 指向新的 `build/` 子目录；已有人工审核记录及完成状态受到覆盖保护。冻结身份使用的原始计划和审计源码见 [历史来源快照](../archive/strengthening_review_state_20261113/README.md)。
