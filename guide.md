# 仓库使用指南

审稿与复现入口见 [ARTIFACTS.md](ARTIFACTS.md)。这份指南说明实验数据、代码和运行结果的位置。论文文件与旧稿归档不包含在当前仓库中。仓库的日常命令都从根目录执行。

## 1. 从哪里开始

| 要做什么 | 入口 |
| --- | --- |
| 查找原始语料、问题集和数据来源 | [data/oncology/](data/README.md) |
| 查看实验完成状态 | [metadata/release_status.json](metadata/release_status.json) 或 `pixi run --locked status` |
| 查看源码结构 | [docs/CODE_GUIDE.md](docs/CODE_GUIDE.md) |
| 查看结果与指标来源 | [docs/RESULTS_GUIDE.md](docs/RESULTS_GUIDE.md) |
| 校验冻结文件、重做分析 | 下文的“常用命令” |

## 2. 目录结构

```text
data/oncology/
  corpus/                    原始与扩展语料 JSONL
  questions/                 问题集 JSONL
  sources/                   来源配置与 URL 列表
  reports/                   数据构建、清理和筛查 CSV 报告

metadata/                    仓库清单、状态和目录迁移记录
rerankhuts/                  统一命令入口和公共路径解析
experiments/                 实验实现、冻结输入、模型运行记录和评分结果
validation/                  独立审计程序及校验报告
scripts/                     分析、论文构建、打包和完整性校验工具
legacy/                      历史数据构建、评估和结果整理工具
archive/                     原始代码的历史快照与记录
docs/                        按主题展开的文档
tests/                       测试
build/                       本机编译、重新分析和新运行的输出
```

根目录保留 `README.md`、`guide.md`、`LICENSE`、`pixi.toml`、`pixi.lock` 和 Git/环境配置。JSON、JSONL、CSV、URL 列表及 Python 工具均在对应子目录中。

## 3. 数据文件在哪里

| 目录 | 文件与用途 |
| --- | --- |
| `data/oncology/corpus/` | `corpus_chunks_v1.jsonl`（6,785 个块）、`corpus_chunks_v2.jsonl`（7,124 个块） |
| `data/oncology/questions/` | `questions.jsonl`（100 题）；`questions_expanded_full_prepurge.jsonl`（清理前 187 题）；`questions_expanded_full_validated.jsonl`（清理后 155 题）；`questions_judge_sample_validated.jsonl`（40 题样本） |
| `data/oncology/sources/` | `data_sources.json`、`urls.txt`，用于记录和读取语料来源 |
| `data/oncology/reports/` | `corpus_expansion_report.csv`、`questions_expanded_leakfree_report.csv`，以及后续数据构建报告 |

这些文件在迁移时保留原字节和哈希。已发布的运行记录可能仍记载迁移前的根目录文件名；维护中的校验器通过 [固定路径映射](rerankhuts/paths.py) 定位文件，并继续校验原来的哈希与运行身份。

受控仿真和扩展实验各有自己的版本化数据目录，分别位于 `experiments/simulation/data/` 和 `experiments/strengthening/data/`。它们与上述肿瘤语料属于不同工作负载。

## 4. 安装环境与常用命令

依赖与环境定义见 `pixi.toml` 和 `pixi.lock`；锁定平台为 Windows 和 Linux。

```bash
pixi install --locked
pixi run --locked workflow --help
pixi run --locked status
```

| 命令 | 用途与输出 |
| --- | --- |
| `pixi run --locked verify` | 校验已发布的冻结输入、代码身份和轨迹；报告写入 `build/verification/` |
| `pixi run --locked test` | 在当前环境运行测试 |
| `pixi run --locked e0` | 历史结果审计，输出 `build/reanalysis/e0/` |
| `pixi run --locked analyze-e3` | 已发布 E3 结果的分析，输出 `build/reanalysis/e3/` |
| `pixi run --locked interactions-e3` | 已发布 E3 的交互比较，输出同一分析目录 |

查看真实调用命令：

```bash
pixi run --locked workflow --dry-run e3
```

重新执行 E3 使用 `pixi run --locked -e gpu e3`。它读取迁移后的语料和问题集，默认输出为 `build/runs/e3/`；已发布的冻结运行位于 `experiments/runs/e3_m3/`，供校验和分析读取。数据路径属于运行身份的一部分，因此迁移后的新运行使用独立输出目录。继续已有运行时，输入路径、参数和运行身份须匹配。

历史工具入口为 `legacy-normalize`、`legacy-eval`、`legacy-score`、`legacy-analysis` 和 `legacy-summarize`。它们的环境变量、输入选择和行为见 [legacy/README.md](legacy/README.md)。

## 5. 清单、历史记录与输出

- [metadata/MANIFEST.json](metadata/MANIFEST.json)：当前源代码树文件的大小与 SHA-256 清单；冻结实验及 Release 自带历史清单另行保留。
- [metadata/release_status.json](metadata/release_status.json)：稿件、作者和实验完成状态。
- [metadata/data_layout.json](metadata/data_layout.json)：本次数据文件迁移的路径与校验记录。
- [archive/](archive/)：历史代码快照；原先的论文归档已经移除。

历史论文构建、打包及部分校验脚本仍可能依赖已移除的论文文件；运行前需先更新这些脚本及清单。实验分析输出使用 `build/` 或明确指定的新目录。

作者确认已完成 60 个 world 的人工语义审核，但审核记录尚待上传；新版 377 条肿瘤事实标注及对应实验结果见 [oncology coverage](experiments/supplements/oncology_coverage_v1/)。作者表示肿瘤专家已逐条复核 377 项判断；[AI辅助审核表](experiments/supplements/oncology_coverage_v1/reviews/)已公开，表格本身没有专家签名或独立人工确认。仓库目前公开，补充材料需在用于复现和评审前核对完整性。
