#!/usr/bin/env bash
cd "d:/Pycharm/DeepSeekLLM" || exit 1
IN=result_revision/p4_expanded_judge_answers.csv
{
  echo "=== ANSWER JUDGE START ==="
  python llm_judge.py answer --input "$IN" \
      --out result_revision/p4_judge_answer_eval.csv --workers 6
  echo "ANSWER_EXIT=$?"
  echo "=== RELEVANCE JUDGE START ==="
  python llm_judge.py relevance --input "$IN" \
      --out result_revision/p4_judge_relevance_eval.csv --workers 6 --top-k 4
  echo "RELEVANCE_EXIT=$?"
  echo "=== ALL JUDGE DONE ==="
} > result_revision/_judge_rerun.log 2>&1
