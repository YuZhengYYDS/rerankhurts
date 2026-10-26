# 数据目录

肿瘤语料工作负载位于 `oncology/`：

| 子目录 | 内容 |
| --- | --- |
| `corpus/` | 原始与扩展语料 JSONL |
| `questions/` | 原始、清理前、清理后及 judge 样本问题集 |
| `sources/` | `data_sources.json` 和 `urls.txt` 来源配置 |
| `reports/` | 数据扩展、去泄漏与筛查 CSV 报告 |

迁移保留原文件字节。受控仿真与扩展实验的版本化输入分别位于 `../experiments/simulation/data/` 和 `../experiments/strengthening/data/`。常用入口与路径规则见 [根目录指南](../guide.md)。
