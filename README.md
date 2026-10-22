# RerankHuts：论文、代码与实验结果

论文：**What Survives the Context Budget? Source Retention and Fact Coverage in RAG**  
作者顺序：Zheng Yu、Jie Li、Boyang Wang、Jingbang Chen。Zheng Yu与Jie Li为共同第一作者；Jie Li与第三作者Boyang Wang均署名香港中文大学（深圳）；Jingbang Chen为通讯作者。作者单位及共同贡献标注已写入论文；全部12张图已插入正文。

建议下载完整包 **rerankhuts_icde2027.zip**，解压后进入唯一的 **rerankhuts/** 目录。完整包包含论文、代码、输入数据、冻结结果、完整轨迹和逐文件校验清单。独立代码包和结果包便于单独查看；完整复现使用完整包。

2026-10-02 扩展实验状态：四阶段的自动化部分已完成。`strengthening_v1` 包含 **720任务 × 124配置 = 89,280条主推断及独立评分记录**、**720个实际模型回答**、**576个在线请求测量**，另有8次warm-up不计入测量。各步骤均有独立的 `complete` 状态；60世界人工审核仍未进行，外部真实场景复现也未完成。操作与指标解释见 [扩展实验指南](docs/STRENGTHENING_GUIDE.md)。

2026-10-21 配图与整合完成：F1–F3/F12为已核验的概念图，F4/F10/F11用真实冻结数据生成科研绘图，F5–F9保留原矢量图。58段完整首句加粗、7个编号章节、12张图、4张表均保留。三张数据图附PDF/SVG/600dpiPNG、源数据、SHA-256及可重绘脚本；已通过仅含论文和脚本的隔离重绘。未新增模型实验或改动冻结统计。见[论文PDF](paper/main.pdf)、[本次修改说明](paper/revision_notes_20261021.md)、[构建和图源说明](paper/README.md)。正式提交前仍需开放artifact与作者ORCID等元数据。\n
## 先运行这三步

安装 [Pixi](https://pixi.prefix.dev/latest/installation/)，然后在仓库根目录执行：

```bash
pixi install --locked
pixi run --locked workflow --help
pixi run --locked verify
```

verify 使用现有文件校验哈希、E3 的 3,100 条轨迹和仿真配对统计，不调用模型或付费 API。首次安装环境需要网络；环境装好后该校验不需要网络。新校验报告写入 build/verification/，冻结实验目录保持不变。

## 代码在哪里

- [rerankhuts/](rerankhuts/)：维护中的统一命令入口；python -m rerankhuts 与 Pixi 的 workflow task 等价。
- [experiments/](experiments/README.md)：冻结的检索、重排、预算打包、指标定义与 E3 实验。
- [experiments/simulation/](experiments/simulation/README.md)：受控世界生成器、实际模型执行后端、独立事实跨度评分。
- [experiments/strengthening/](experiments/strengthening/README.md)：360世界扩展设计、独立语义审计、124配置推断、实际答案与在线测时。
- [validation/](validation/README.md)：独立审计、轨迹检查、配对频数复算及已发布核验报告。
- [scripts/](scripts/)：结果分析、论文构建、打包、包校验和冻结文件检查。
- [legacy/](legacy/README.md)：从根目录迁出的旧版语料构建、LLM 评估、结果整理工具。legacy/archive/ 保存依赖过时路径或输入的历史脚本。
- [tests/](tests/)：原实验协议、仿真 oracle、命令入口、文件完整性和打包测试。
- [paper/](paper/README.md)：干净、可独立编译的 IEEE 论文目录。
- [docs/CODE_GUIDE.md](docs/CODE_GUIDE.md)：模块职责、入口及维护约束。
- [docs/RESULTS_GUIDE.md](docs/RESULTS_GUIDE.md)：论文图表对应哪些数据、如何重新分析。
- [docs/STRENGTHENING_GUIDE.md](docs/STRENGTHENING_GUIDE.md)：新实验的固定输入、运行顺序、独立单位和分步完成检查。

根目录仍保留五个历史脚本和原始输入文件：它们的路径和字节哈希已被审计或实验身份固定。具体原因见代码指南；不要为了目录美观修改这些冻结文件。

## 环境选择

Pixi 锁定 default、gpu 和 paper 三个环境，均隔离在 .pixi/，不会打包。锁文件覆盖 Windows/Linux；本次实际验证平台为 Windows，GPU 为 RTX 5060 8 GB。

```bash
# 默认：离线结果核验、统计、打包
pixi install --locked

# GPU：实际检索/重排；仿真评分需要其 tokenizer 依赖
pixi install --locked -e gpu

# 论文：Tectonic 编译
pixi install --locked -e paper
```

当前实验不需要付费 API。legacy/ 中部分历史 LLM 脚本需要用户自己的 .env；它们不是默认复现流程。其历史依赖记录在 legacy/requirements.txt，未经当前三个环境完整验证。

## 常用入口

```bash
pixi run --locked status
pixi run --locked verify
pixi run --locked test
pixi run --locked e0
pixi run --locked analyze-e3
pixi run --locked interactions-e3
```

- e0：重新核对 47 个历史日志，输出 build/reanalysis/e0/。
- analyze-e3：重新生成 16 个配对对比及页面保留率图，输出 build/reanalysis/e3/。
- interactions-e3：另外八个 cap/re-ranker 交互，输出同一分析目录；它与上一个命令不是重复实现。
- 所有历史已发布结果仍保留原路径；重新分析不覆盖论文所引用的冻结结果。

查看真实执行命令而不运行：

```bash
pixi run --locked workflow --dry-run e3
```

## 执行或继续模型实验

```bash
pixi run --locked -e gpu e3
pixi run --locked -e gpu sim-run
pixi run --locked -e gpu sim-evaluate
```

e3 入口显式固定原实验的三个模型/tokenizer commit SHA；原底层模块的 main 默认值不用于这条入口。sim-run 同样使用其已固定版本。完整包已经包含已完成的逐题轨迹，重复同一命令会按原协议验证并继续；改变模型、数据、设备、批大小等条件必须使用新的输出目录，不能接续为原实验。

小规模试运行请明确使用新目录：

```bash
pixi run --locked -e gpu workflow e3 --limit 2 --output experiments/runs/smoke_new
```

sim-evaluate 将复算结果写到 build/reanalysis/simulation/。它校验实际交付 token 与完整事实跨度；缺少固定 tokenizer 文件时会下载这些文件，不必下载完整模型权重。已有 120 个任务轨迹对应 60 个独立世界，不能把重复配置当成独立样本。

## 扩展实验流程

新数据在 `experiments/strengthening/data/strengthening_v1/`，主轨迹在 `experiments/runs/strengthening_v1/`，评估、答案和测时产物在 `experiments/strengthening/results/strengthening_v1/`。三个种子各含20个开发世界与100个测试世界；两种来源集中度任务属于同一个世界，统计时不能算作两个独立样本。

```bash
# 核验已完成的各步骤与固定来源
pixi run --locked strengthen-verify --require-complete

# 模型准备和执行入口；完整的新目录复现命令见扩展实验指南
pixi run --locked -e gpu strengthen-models --include-answer-model
pixi run --locked -e gpu strengthen-run
pixi run --locked -e gpu strengthen-evaluate
pixi run --locked -e gpu strengthen-answers
pixi run --locked -e gpu strengthen-timing
pixi run --locked strengthen-analyze

# 在新的复现完成后，同样要求严格通过
pixi run --locked strengthen-verify --require-complete
```

主推断与回答可按固定身份续跑；独立测时不能拼接中断前后的session，已有请求文件时需另选输出目录。重算已发布结果时请按指南使用 `build/reanalysis/`，避免覆盖冻结产物。该流程保持本机运行，系统休眠时计算会暂停；持续运行需保持电脑唤醒。

## 论文与 ZIP

```bash
# 从已核验的旧E3与pilot_v2结果刷新相应表格
pixi run --locked paper-tables

# 编译，临时文件只写入 build/paper/
pixi run --locked -e paper paper

# 生成完整、论文、代码、结果四个包，并验证
pixi run --locked package --split --verify
pixi run --locked verify-package
```

dist/ 输出：

- rerankhuts_icde2027.zip：完整复现包，单一 rerankhuts/ 根目录。
- paper_icde2027_clean.zip：论文专用包，单一 paper/ 根目录。
- rerankhuts_icde2027_code.zip：代码、配置、文档和测试；不含完整语料/结果。
- rerankhuts_icde2027_results.zip：冻结结果、轨迹、审计及来源信息；不单独提供模型复现所需的全部代码和语料。
- manifest.json：完整包中源文件的逐文件大小和 SHA-256。
- sha256sums.json：压缩包及外部 manifest 的 SHA-256。

每个 ZIP 内也有 MANIFEST.json。打包按固定顺序、固定时间戳生成，排除环境、缓存、模型权重、凭据、编译临时文件和旧压缩包；verify-package 检查路径、条目集合、大小和哈希。结果包保留原相对路径，便于按来源核对。

扩展实验的独立评分、下游和测时均已完成；打包使用它们对应的统计、图和论文输入。其结果包包含新结果、完整轨迹、研究计划和阅读指南；代码包显式带上冻结 `study_plan.json` 与 `.gitattributes`。数据仍在完整包中，代码包与结果包的组合不替代完整复现包。

## 证据范围

E0 核验 417 个历史指标单元，405 个一致，12 个查询文本连接错误已解释并修正；原表仍作为历史记录保存。旧 E3 为 155 题 × 20 配置，共 3,100 条；`pilot_v2` 受控仿真为 120 任务 × 20 配置，共 2,400 条。新增89,280条主推断属于独立版本，不能覆盖或改写这些旧证据。

仿真是虚构注册管理场景的完整事实覆盖，不是人工临床效用。`pilot_v2` 主选择实验开发集十个配置的覆盖率全部并列 0.60；冻结选择规则在测试集得到 0.550 与 0.675，差值 -0.125，保留该反向结果。新实验另提供60世界的人工审核包，人工尚未完成。完整解释见 [实验范围](docs/EXPERIMENT_SCOPE.md) 与论文。

基线和扩展核心版本已推送并核验至指定的 [GitHub仓库](https://github.com/YuZhengYYDS/rerankhuts)，仓库为 **private**，需获授权后访问。2026-10-13历史四个交付包对应下载入口为 [icde2027-restructured-20261013 Release](https://github.com/YuZhengYYDS/rerankhuts/releases/tag/icde2027-restructured-20261013)，发布状态以该页实际附件及上传校验回执为准。后续正文配图更新以main分支为准。当前交付保持私有可见性，与ICDE EAB要求的开放artifact准备是两件事。

作者角色及全部正文配图已完成整合。正式提交前还需提供提交系统要求的 ORCID/联系信息，并准备公开可访问的复现artifact。2026-10-21重新核对投稿指南：正文须不超过12页，参考文献与AI内容致谢不计入，且不允许附录；其他CFP与日期保留2026-10-02核验记录，官方依据见 [论文说明](paper/README.md)。

代码许可见 LICENSE；第三方语料保留来源和相应条款，代码许可不替代原内容许可。

