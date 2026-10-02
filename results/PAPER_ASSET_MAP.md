# Paper Asset Map

## Main-paper quantitative sources

- Table 1: `paper_table_main_baselines.csv`
  Validated-78 retrieval leaderboard.
- Table 2: `rev_table_rerankers.csv`
  Six second-stage variants across orig78, iso78, and exp155.
- Table 3: `rev_table_inversion.csv`, `rev_table_judge.csv`, `rev_table_judge_ci.csv`, and `rev_table_spearman.csv`
  Automatic answer quality, question-balanced distinct-source relevance, confidence intervals, and system-level rank correlations.

## Generated figures

- `fig_main_retrieval.png` and `fig_answer_rates.png`: main performance summaries.
- `fig_stage_retention_validated.png`: stage-wise gold-page retention.
- `fig_heatmap_retrieval_ndcg.png` and `fig_heatmap_insufficient.png`: non-duplicated topic-level heatmaps with canonical labels.

## Manually maintained conceptual diagrams

- `RAG 检索到生成的简化流程图.png`
- `黄金证据保留丢失机制图.png`
  These illustrations contain no measured values and are not regenerated from CSVs.
- No valid manual answer-level evaluation is available.
  Automatic answer scores may be reported only with their automatic provenance.
- No valid manual graded-relevance evaluation is available.
  Automatic distinct-source relevance may be reported only as LLM-judge output.

## Appendix

- `accuracy_cost_pareto_clean.csv`: numerical source table for the clean Pareto figure
- `rev_table_benchmark.csv`: benchmark sizes across the three result views
- `rev_table_inversion.csv`: aligned retrieval, relevance, and answer metrics
- `rev_table_judge.csv`: automatic answer and question-balanced relevance summaries
- `rev_table_judge_ci.csv`: automatic answer-score confidence intervals
- `rev_table_relevance_by_source.csv`: distinct-source relevance by source category
- `rev_table_rerankers.csv`: re-ranker comparison across the three result views
- `rev_table_spearman.csv`: system-level rank correlations
- `paper_table_main_baselines.csv`
- `paper_table_model_upgrades.csv`
- `rev_table_judge_rates.csv`
- `rev_table_source_ablation_ci.csv`
- `rev_table_subset_split.csv`

## Human Eval

- `HUMAN_EVAL_STATUS.md`: whether the current annotation files are valid for paper use
- `rev_table_judge.csv`: automatic LLM-judge scores, not human annotation (every row carries `valid_for_human_eval_claim = False`); cite it only as an automatic evaluation.

## Curated Folder

- `paper_assets_curated/`: compact folder containing only paper-ready tables, figures, and key appendix summaries
