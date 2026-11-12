# E0: independent audit of frozen results

For the completed 360-world strengthening study, use
`pixi run --locked strengthen-verify --require-complete` from the repository root.
Its offline checker is `scripts/check_strengthening_files.py`; the
[strengthening guide](../docs/STRENGTHENING_GUIDE.md) describes its data, traces,
independent scoring, answers and request timing. Two rounds of human review
are complete for the sampled 60 worlds; see the [human review records](../experiments/strengthening/data/strengthening_v1/audit/reviews/). The historical E0 audit below documents the frozen-output checks.

Run from the repository root (standard library only):

```powershell
python validation/audit_metrics.py
python -m unittest discover -s tests -p test_metrics_audit.py -v
```

This is recomputation from saved URL rankings, **not a new model run**. It
imports the released question wording transformation, but none of the original
metric scorers. It performs exact URL matching after trimming whitespace.
It makes no human evaluation, content support, source compliance, or clinical
quality claim.

`results/e0_audit.json` is the machine-readable report. `input_manifest.json`
contains SHA-256 hashes of the corpora, question sets, logs, compared tables,
and relevant code. The main generated outputs are:

- `recomputed_metrics.csv`: all 47 retrieval logs, 14,062 query/system records,
  with original chunk-rank metrics and separately named distinct-page metrics.
- `published_table_checks.csv`: 417 individual published cells checked. The
  405 cells outside the normalization table agree at recorded precision.
- `corrected_supp_query_normalization_overall.csv`: replacement normalization
  table with the original column names, generated from logs with preserved IDs.
- `normalization_join_diagnosis.csv`: the 7 rewritten questions in each of 3
  modes whose labels the historical text join lost. The report also reproduces
  the 12 erroneous original summary cells by applying the historical join.
- `rank_transitions.csv`: separate full-ranking, top-10, and top-4 conventions.
- `true_top4_transitions.csv`: actual delivery losses and rescues.
- `cross_run_comparison.csv`: the original 78 queries compared across the two
  frozen expanded-corpus runs.
- `paired_bootstrap_sensitivity.csv`: descriptive question and gold-page
  cluster bootstrap intervals (5,000 resamples, seed 42).
- `log_inventory.csv` and `logged_configurations.csv`: trace availability and
  per-file/per-mode recorded configuration.

The audit exits nonzero for malformed rows or unexplained cell discrepancies.
It exits zero for the 12 documented historical normalization defects **only if
their old values are reproduced by the faulty join**; their `pass` values remain
false. This is not a claim that all historical cells are correct. Original
`results/tables/` files are retained as frozen provenance. Use the corrected
normalization CSV above for the revised manuscript.

## What changes in the manuscript

1. The historical "nDCG@10" is a first-gold **chunk-position** discounted score:
   `1/log2(rank+1)` for the first gold chunk at rank at most 10, otherwise zero.
   Only the first hit contributes; implicit IDCG is 1. Historical Recall@k is
   Hit@k, and MRR uses the complete ranking. All present questions have one
   designated gold page; that does not justify this definition for multiple
   accepted pages. Distinct-page nDCG is provided separately, with stable URL
   deduplication and IDCG from every annotated gold page, including missing ones.
   Ten pages and ten chunks have different budget semantics.
2. Base and MiniLM on the original 78 questions reproduce 0.869555 and 0.770301
   first-gold discount, with identical final gold-page hit 70/78. The equality
   conceals two losses (q32 and q34, rank 1 to 5) and two rescues (q12, 6 to 4;
   q45, 6 to 3). Historical examples q58, 5 to 12, and q9, 8 to 12, are ranking
   degradations, not losses from a top-4 context.
3. LLM scoring on the isolated 78-query run yields 0.863121; the original-query
   slice of the 155-query run yields 0.877316. Twelve URL orders and four first
   gold ranks differ. These are distinct stored outputs. Both file hashes are
   available, but historical request/run IDs and timestamps are absent. Do not
   merge them as a single result or infer a repeated-run distribution.
4. "NoDedup" with reranking gives 0.808257, whereas Base without a cap gives
   0.869555. They have different second-stage configurations. Rerank depth 24
   with retrieval pool 100 gives 0.753147; retrieval pool 24 with full post-cap
   reranking gives 0.770301. The implementation appends the unreranked tail.
5. Full-ranking Base hits all 78 queries. Full-ranking "both missing" is zero;
   the 3 SmallPool residual cases are losses only for the candidate. Top-4
   both-missing for MiniLM is 6/78. Always state the cutoff.
6. The LLM prompt presents candidates jointly and requests a 0--2 score for
   each chunk (first 500 characters), then uses stable sorting. Describe this
   precisely as joint-context ordinal chunk scoring. It is not a prompt that
   directly outputs a permutation. The historical code uses temperature 0 and
   silently returns zero scores on request/parse failure; the release cannot
   recover the frequency of these fallbacks.
7. Query normalization was incorrectly scored by joining annotations on both
   qid and changed question text. All 234 logged queries match the released
   deterministic rewrite; 7 distinct rewrites previously lost annotations.
   Correct Base/MiniLM discounted scores are 0.853279/0.753283 (formerly
   0.824848/0.717974); final hits are 69/78 and 70/78. The parent task fixed
   the production join; all 12 corrected production values agree with this
   independent audit to 1e-12.

## Limits that remain

The reduced release contains ranking/final URL strings and stage counts, but
omits raw candidate IDs, candidate-stage URLs, final chunk IDs, final evidence
text, and model responses. Initial stage-retention figures cannot be independently
rebuilt from these reduced logs. Matching URL multisets cannot verify shared
chunk-level candidates. Four chunks is not a measured token budget.

The original 78 questions cover 6 designated pages. The 155-question expansion
covers 20 designated pages and includes all original questions plus questions
constructed with source information. It is not an independent external test.
All present judge labels declare `llm_judge_automatic`; no human labels are
present. E1 human utility calibration and E2 independent utility-based selection
cannot be concluded from this audit. Page-cluster intervals are descriptive and
do not resolve independent sampling or multiple-comparison concerns.

Historical latency also depends on the run: the main baseline log's MiniLM
rerank average is approximately 120.2 ms, versus 14.6 ms in the reranker-family
log with the same URL metric. Keep cost and quality paired within each run;
missing historical hardware/model revision information prevents a unified
hardware-controlled cost conclusion.

## New E3 run verification

After the 155-question factorial run has completed, run:

```powershell
python validation/check_e3.py --run experiments/runs/e3_m3
```

This independent standard-library check reads the saved full traces and the
hash-matched original corpus. It checks common candidate prefixes, canonical
row identities, cap/rerank order, exact evidence token streams and budgets,
partial chunks, distinct-page metrics, and budget monotonicity. It produces
`results/e3_integrity.json` and `results/e3_score_sensitivity.csv`.

The sensitivity analysis keeps pre-cap membership fixed and reorders those
chunks using their saved no-cap scores. Separate FP16 inference batches can
produce slightly different scores for the same query/chunk pair. The report
counts affected rankings, delivered chunk IDs, and final G values without
executing a model again. This is an exploratory numerical sensitivity analysis;
its counterfactual order has no newly measured latency or human utility.

The two-question checker/analyzer smoke-test outputs are excluded from the
publication inputs and kept only in `build/factorial_analysis_smoke/`.

The completed 155-question run passes all 3,100 configuration-record checks.
Among 8,635 query/chunk scores compared once per query and pool, 1,549 differ
across pre-cap/no-cap input batches, with maximum absolute logit difference
0.015625. Reusing no-cap scores changes 15 of 310 pre-cap full orderings but
changes no delivered chunk-ID list and no final G value across all 620
query/pool/budget sensitivity cases.
