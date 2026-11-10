# Packing recovery and loss reanalysis

Run `python -m rerankhuts packing-reanalysis` from the repository root.
The original inference/evaluation records fix dense pool 64, M3, post-cap2,
prefix512 scoring views and no refill/source filter. Only packing changes among
prefix truncation, whole-chunk skipping and query-ranked windows.

- `results/packing_loss_recovery.csv`: conditional on complete support before
  packing but incomplete delivery with prefix packing (243 tasks at 512 tokens;
  73 at 2048), counts any missing fact restored, other facts lost and complete
  support restored. These columns overlap and must not be added.
- `results/packing_all_test_transitions.csv`: gains and losses of complete
  support across all 600 tasks, with the population denominator.
- `results/packing_paired_records.csv`: the 2,400 question-level paired records.
- `results/packing_marginals.csv`: complete support, partial coverage and page
  retention for each packing/budget setting.

The script reproduces these numbers and checks unchanged pre-packing stage
records, published marginals and three trace pairs. It writes only to a new
directory under `build/`. Human semantic review of the 60-world audit sample
has been completed. No extra paper table or model run is introduced.
