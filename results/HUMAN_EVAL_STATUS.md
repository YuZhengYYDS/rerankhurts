# Review records and answer/relevance metrics

## Completed human reviews

Two rounds of human semantic review, A and B, are complete for the sampled
60 worlds. See the [review records](../experiments/strengthening/data/strengthening_v1/audit/reviews/).

An oncology expert completed and confirmed all 377 fact-level judgments for
the 155-question annotation rubric. See the [expert-review workbook](../experiments/supplements/oncology_coverage_v1/reviews/).

## Legacy answer and relevance metrics

- [Answer metrics](per_question/p4_judge_answer_eval.csv) record scores for model-generated answers.
- [Relevance metrics](per_question/p4_judge_relevance_eval.csv) record distinct-source relevance scores.
- These legacy tables use the configured LLM judge. Their source fields and aggregation rules are preserved with the recorded scores.
