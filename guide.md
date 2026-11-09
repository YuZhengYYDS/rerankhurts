# 仓库使用指南

这份指南说明当前论文、实验数据、代码和运行结果的位置。仓库的日常命令都从根目录执行。

## 1. 从哪里开始

| 要做什么 | 入口 |
| --- | --- |
| 阅读当前论文 | [paper/main.pdf](paper/main.pdf) |
| 修改论文、上传 Overleaf | [paper/](paper/README.md)，主文件为 `main.tex` |
| 查找原始语料、问题集和数据来源 | [data/oncology/](data/README.md) |
| 查看实验完成状态 | [metadata/release_status.json](metadata/release_status.json) 或 `pixi run --locked status` |
| 查看源码结构 | [docs/CODE_GUIDE.md](docs/CODE_GUIDE.md) |
| 查看结果与指标来源 | [docs/RESULTS_GUIDE.md](docs/RESULTS_GUIDE.md) |
| 校验冻结文件、重做分析 | 下文的“常用命令” |

## 2. 目录结构

```text
paper/                       当前论文、参考文献、模板和配图

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
archive/                     原始代码和上一版论文的字节保留快照
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
| `pixi run --locked paper-tables` | 重新生成历史表格，输出 `build/reanalysis/tables/` |
| `pixi run --locked -e paper paper` | 编译当前论文，最终 PDF 写入 `paper/main.pdf`，临时文件写入 `build/paper/` |
| `python scripts/check_manuscript.py` | 检查段落首句、图表、页面和构建身份；报告位于 `validation/manuscript_checks.json` |
| `pixi run --locked package --split --verify` | 在 `dist/` 生成并校验完整、论文、代码和结果包 |

查看真实调用命令：

```bash
pixi run --locked workflow --dry-run e3
```

重新执行 E3 使用 `pixi run --locked -e gpu e3`。它读取迁移后的语料和问题集，默认输出为 `build/runs/e3/`；已发布的冻结运行位于 `experiments/runs/e3_m3/`，供校验和分析读取。数据路径属于运行身份的一部分，因此迁移后的新运行使用独立输出目录。继续已有运行时，输入路径、参数和运行身份须匹配。

历史工具入口为 `legacy-normalize`、`legacy-eval`、`legacy-score`、`legacy-analysis` 和 `legacy-summarize`。它们的环境变量、输入选择和行为见 [legacy/README.md](legacy/README.md)。

## 5. 清单、历史记录与输出

- [metadata/MANIFEST.json](metadata/MANIFEST.json)：当前仓库文件的大小与 SHA-256 清单；清单自身不参与自身哈希。
- [metadata/release_status.json](metadata/release_status.json)：稿件、作者和实验完成状态。
- [metadata/data_layout.json](metadata/data_layout.json)：本次数据文件迁移的路径与校验记录。
- [archive/README.md](archive/README.md)：旧稿、可编辑图源和历史代码快照的位置。

打包产生的每个 ZIP 仍有独立的根目录 `MANIFEST.json`，用于核对该压缩包的成员；它与源码仓库内的 `metadata/MANIFEST.json` 分开管理。

编译、重新分析和新实验输出使用 `build/` 或明确指定的新目录。当前论文的新版图在 `paper/figures/`；历史重绘工具的输出位于 `build/reanalysis/`。

图 1–3 的当前可编辑源文件位于 [paper/figures/drawio/](paper/figures/drawio/)，正文使用同目录上层的矢量 PDF 导出图。

上一版完整论文保存在 [archive/paper_20261027/](archive/paper_20261027/)。作者确认已完成 60 个 world 的人工语义审核，但审核记录尚待上传；新版 377 条肿瘤事实的标注及对应实验结果也待补充。仓库目前保持私有，投稿前请补齐材料并由作者公开仓库。
