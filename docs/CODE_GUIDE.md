# 代码导览与维护约束

## 从哪个入口开始

在仓库根目录使用 `pixi run --locked workflow --help`。入口位于
`rerankhuts/cli.py`，通过当前 Pixi Python 的子进程调用既有程序，明确设置
仓库工作目录并传递参数，不使用 shell 拼接命令。

入口将模型执行、既有结果核验、重新分析、论文构建和打包分为独立动作。
`--dry-run` 放在动作前可查看命令；例如
`pixi run --locked workflow --dry-run e3`。实际模型执行选 gpu 环境，编译选 paper。

## 当前实验代码

- `experiments/protocol.py`：配置枚举、稳定排序、每 URL cap、token-prefix 打包、URL 指标、实验身份与检查。
- `experiments/run_factorial.py`：E3 的模型加载、共享候选与分数缓存、计时、轨迹和恢复。
- `experiments/simulation/generate.py`：事实先于文本的虚构世界生成；固定 split、oracle 和 specification。
- `experiments/simulation/backend.py`：受控仿真实际模型运行；不读取 oracle 标签。
- `experiments/simulation/evaluate.py`：独立检查已交付文本、事实跨度、源约束、选择规则和 bootstrap。
- `experiments/annotation.py`、`analyze_selection.py`：尚未开展的人工标注/效用研究工具，有标签来源守卫。

新扩展模块位于 `experiments/strengthening/`，详细接口见其
[README](../experiments/strengthening/README.md) 和 [扩展指南](STRENGTHENING_GUIDE.md)：

- `generate.py`、`study_plan.json`：冻结360世界、配对URL干预、split与研究计划。
- `audit_data.py`：独立解析原文断言并核对世界真值；生成60世界的空白人工审核包。
- `protocol.py`、`backend.py`：124个定向配置、真实模型推断、评分视野、打包、来源策略与恢复；推断不读取oracle。
- `evaluate.py`：核对实际交付token与原文区间，独立计事实覆盖、合规、冲突、阶段支持及预算界。
- `analyze.py`：配对世界统计、主比较Holm校正、探索族BH校正及下游结果分析。
- `downstream.py`：实际Qwen回答、无支持控制与独立证据忠实评分。
- `timing.py`：重新计算query/pair分数的在线请求测时，不拼接中断的测量session。
- `figures.py`：从完成且来源一致的分析产物生成论文图和图清单。

E3、`simulation`和`strengthening`三个 inference backend 保留独立版本，以保持各自
已完成实验的代码身份；不要简单合并后继续写入旧 run。两个同名 factorial 分析也有不同用途：

- `scripts/analyze_factorial.py` 输出 16 个配对对比、分组统计和论文热图。
- `experiments/analyze_factorial.py` 输出 8 个 pre/post cap 交互。

统一入口先核验固定输入，再将四个分析输入复制到 `build/reanalysis/e3/`。
重算产物与已发布结果分开，二者不是独立重复实验。

## 校验代码

- `scripts/check_frozen_files.py`：标准库离线检查记录的源代码、输入数据、结果和轨迹哈希。
- `scripts/check_strengthening_files.py`：标准库离线核验新数据、89,280条轨迹记录、独立评估、720个回答和576个计时请求的来源与完整性。
- `validation/check_e3.py`：不导入原 scorer，复核 3,100 条轨迹的结构、稳定排序、预算、指标与 FP16 敏感性。
- `validation/audit_metrics.py`：47 个历史日志的 E0 重算，保留 12 个已解释的原始错误。
- `validation/audit_simulation_endpoint_pairs.py`：独立复算论文中的 G/U 四格配对频数。
- `scripts/verify_release.py`：验证 ZIP 的成员路径、大小、SHA-256 和包内清单。

`verify` 不需要模型权重或网络；它检查旧E0/E3和`pilot_v2`的已保存文件与token轨迹。
新研究使用 `pixi run --locked strengthen-verify --require-complete` 单独核验，也不需要模型缓存。
完整oracle重算分别使用 `sim-evaluate` 和 `strengthen-evaluate`，其tokenizer依赖在gpu环境；
哈希完整性检查与重新计分是不同动作。

## 为什么根目录仍有五个旧脚本

这些文件被 E0 输入清单固定记录，保持原路径、原字节：

- `generate_normalized_questions.py`
- `paper_support_analysis.py`
- `run_rag_eval.py`
- `score_retrieval.py`
- `summarize_supplement_results.py`

根目录 corpus/question JSONL 也被数据清单和 run identity 引用。移动它们后即使内容
相同，也可能改变恢复使用的路径身份。其余可维护旧工具归入 `legacy/`，只用于
原研究流程；历史 scratch/过时输入工具位于 `legacy/archive/`。

## 修改后的验证顺序

1. 运行 `pixi run --locked test`；若新测试需要模型/tokenizer 扩展依赖，使用 gpu 环境。
2. 运行 `pixi run --locked verify` 和 `pixi run --locked strengthen-verify --require-complete`，确认新旧冻结实验身份与结果未被意外修改。
3. 修改论文表格时，先重算并核对结果，再执行 `paper-tables` 和 paper 环境中的 `paper`。
4. 执行 `package --split --verify`。环境、缓存、模型权重和编译文件只留本地。

如果科学协议确实需要更改，应创建新版本/新输出目录，重新执行受影响实验，
并明确区分新旧结果；不能更新旧 manifest 来伪装为原来的运行。
