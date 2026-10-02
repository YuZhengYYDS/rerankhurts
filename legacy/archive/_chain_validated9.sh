#!/usr/bin/env bash
# Wait for the P4 judge phase to release the GPU, then rebuild the nine-mode
# validated batch on one BM25 function.
cd "d:/Pycharm/DeepSeekLLM" || exit 1
n=0
while ! grep -q "JUDGE_EXIT" result_revision/_rerun155_judge.log 2>/dev/null; do
  n=$((n+1))
  if [ "$n" -gt 240 ]; then echo "WAIT_TIMEOUT after 40min"; break; fi
  sleep 10
done
echo "=== judge phase finished (waited $((n*10))s) ==="
python run_p3_matrix.py --only supp_strong_baselines_validated --no-skip \
  > result_revision/_rerun_validated9.log 2>&1
echo "VALIDATED9_EXIT=$?" >> result_revision/_rerun_validated9.log
