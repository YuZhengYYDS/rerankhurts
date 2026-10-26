# Re-ranking for oncology treatment QA — code and results

This guide describes the historical COLING workflow. Its tools are now under
`legacy/`; run module commands from the repository root. Current artifact and
manuscript instructions are in the root README.

Code, corpora, question sets and results for *Auditing Re-ranking for
Source-Aligned Evidence Retrieval in Oncology Treatment QA*. Quantitative tables
and plots are produced from stored run outputs; the two pipeline diagrams are
manually maintained conceptual illustrations and contain no measured values.

## What is being measured

Retrieval is scored at the **page** level against a single gold URL per
question: Recall@5/@10, MRR, nDCG@10, and whether the gold page survives into
the final top-4 evidence list the answer model is given. The gold URL marks the
authoritative source page for the question; it is not a claim that no other page
is clinically relevant, and the metrics should be read that way.

## Environment

The reference results were produced with:

| | |
|---|---|
| Python | 3.13 |
| torch | 2.11.0+cu128 (CUDA) |
| transformers | 5.5.3 |
| sentence-transformers | 5.4.0 |
| pandas | 3.0.2 |

`pip install -r legacy/requirements.txt` covers the dependencies. GPU is used for the
dense encoder and every cross-encoder; the pipeline also runs on CPU, slowly.
Model weights are downloaded from Hugging Face on first use
(`BAAI/bge-small-en-v1.5`, `cross-encoder/ms-marco-MiniLM-L-6-v2`,
`BAAI/bge-reranker-base`, `BAAI/bge-reranker-v2-m3`,
`ncbi/MedCPT-Cross-Encoder`).

### Answer generation and the judge

`run_rag_eval.py` (answer generation, the LLM re-ranker) and `llm_judge.py` (the
automatic judge) call an OpenAI-compatible chat endpoint. Copy `.env.example` to
`.env` and fill it in. The variable names are historical — any endpoint works.

**Retrieval metrics do not require an API endpoint.** Answer generation, the LLM
listwise re-ranker, and automatic judging do require the configured endpoint.
The stored per-question outputs support deterministic post-processing without
calling those models again.

## Data

| File | What it is |
|---|---|
| `data/oncology/sources/data_sources.json` | the corpus sources, read by `build_corpus.py` |
| `data/oncology/corpus/corpus_chunks_v1.jsonl` | the original corpus (6,785 chunks) |
| `data/oncology/corpus/corpus_chunks_v2.jsonl` | the expanded corpus (7,124 chunks), v1 plus new NCI/PDQ pages |
| `data/oncology/questions/questions.jsonl` | the original 100-question pool |
| `result/emnlp_full_results_20260427_gpu_final/paper_questions_validated.jsonl` | the 78 audited questions the original submission used |
| `data/oncology/questions/questions_expanded_full_prepurge.jsonl` | the expanded benchmark before the leak purge (187 items) |
| `data/oncology/questions/questions_expanded_full_validated.jsonl` | **the expanded benchmark used in the paper** (155 items) |
| `data/oncology/questions/questions_judge_sample_validated.jsonl` | the 40-question stratified sample used only for the repeated judge-stability check |

The expanded benchmark is 155, not the 187 the drafting round produced:
`purge_leaky_questions.py` removes 32 items whose text names its own gold
document ("...in the NCI PDQ melanoma treatment summary?"), which a keyword
system can win without retrieving. The script reads the pre-purge file and
writes the validated one, so the 187 → 155 step is a re-runnable step rather
than an unexplained difference; the removal is recorded item by item in
`data/oncology/reports/questions_expanded_leakfree_report.csv`. None of the
original 78 audited questions leak this way.

### The three result views

| View | Questions | Corpus | What it isolates |
|---|---|---|---|
| `orig78` | 78 audited | v1 | continuity with the original submission |
| `iso78` | 78 audited | v2 | the corpus expansion alone |
| `exp155` | 155 validated | v2 | the final benchmark |

Reporting all three separates the corpus effect from the question-set effect;
the revision changed both at once.

## Running it

One experiment, configured by environment variables:

```bash
QUESTIONS_FILE=result/emnlp_full_results_20260427_gpu_final/paper_questions_validated.jsonl \
RUN_EXPERIMENTS=baseline,rerank RUN_GENERATION=0 \
OUTPUT_RESULTS_FILE=result_revision/my_run.csv \
python -m rerankhuts legacy-eval
```

The batch drivers wrap that for the full matrices:

```bash
python -m legacy.run_p3_matrix --dry-run     # 78-question matrix and every sweep
python -m legacy.run_p4_expanded --dry-run   # expanded-benchmark and isolation batches
```

## Complete rebuild in the full working tree

```bash
python -m legacy.run_view_analyses           # per-view tables (orig78 / iso78 / exp155)
python -m legacy.build_revision_assets --publish --archive-note "<what changed>"
```

`build_revision_assets.py` chains the rest: `combine_revision_results.py` →
`score_retrieval.py` → `analyze_results.py` → `make_figures.py` →
`make_heatmaps.py` → `paper_support_analysis.py` →
`summarize_supplement_results.py` → `make_revision_tables.py` →
`curate_paper_assets.py`, then archives the round and publishes the paper
bundle. These commands require the full working tree, including
`result_revision/`, the per-view evaluation folders, and `results_archive/`.
Run `run_view_analyses.py` first: the re-ranker table reads its per-view tables.

Each completed round is frozen under `results_archive/<date>_<time>_<label>/`
with a `MANIFEST.md` naming what backs which draft; see
`results_archive/README.md`. The live working directory `result_revision/` is
scratch — file names repeat every round, so only the archive says which numbers
a draft used.

## Evaluation caveats

These are binding on how the numbers may be described.

- **The answer-quality scores are automatic, not human.** `llm_judge.py` grades
  with an LLM. Every row it writes carries
  `annotation_source="llm_judge_automatic"` and
  `valid_for_human_eval_claim=False`, and the results must be reported as
  automatic LLM-judge scores.
- **Evidence relevance is distinct-source, not four-chunk, evaluation.** The
  relevance command de-duplicates each final window by URL and scores one
  representative excerpt per delivered source page. The released run has 1,085
  question--system outputs and 3,352 distinct-source judgments; system means
  first average sources within a question and then weight all 155 questions
  equally.
- **The judge is not perfectly reproducible.** `llm_judge.py stability` grades
  the same answers three times. On the 40-question sample, repeating the
  identical prompt at temperature 0 reproduces 97.9 %–99.6 % of grades exactly
  (it is not deterministic), and reversing the evidence order preserves pairwise
  ordering 85.4 %–97.9 % of the time. Grades that move almost always move by one
  point. That noise floor is comparable to the gaps between systems, which is
  why answer-quality differences here should not be read as a ranking.
- **Latency figures are one machine's.** The timing columns are wall-clock on
  the machine that ran them and are comparable between rows of the same batch,
  not across batches run with different settings.

## Layout

| Path | |
|---|---|
| `legacy/run_rag_eval.py` | the pipeline: retrieval, fusion, re-ranking, generation |
| `legacy/build_corpus.py`, `build_expanded_benchmark.py` | corpus and question construction |
| `legacy/purge_leaky_questions.py` | the 187 → 155 leak removal |
| `legacy/score_retrieval.py`, `analyze_results.py` | retrieval and answer-level metrics |
| `legacy/llm_judge.py` | the automatic judge (`answer`, `relevance`, `stability`) |
| `legacy/paper_support_analysis.py`, `curate_paper_assets.py`, `make_*.py` | tables and figures |
| `legacy/build_revision_assets.py`, `run_view_analyses.py` | the rebuild drivers |
| `legacy/archive_results.py`, `sanitize_release.py` | freezing a round and stripping local paths |

The repository also contains scratch scripts from earlier rounds that are not
part of any pipeline (for example `report_figures.py`, whose input CSVs are no
longer present). They are kept for provenance and are not on any path above.

## What ships in this release

The maintained historical scripts are grouped under `legacy/` and resolve
default data paths under `data/oncology/`. New corpus/question files and
construction reports use its `corpus/`, `questions/` and `reports/` subfolders;
source configuration and URL lists use `sources/`. `.env` and historical result
folders still resolve against the repository root. Exact former root filenames
are accepted as relative input aliases, and custom path overrides remain usable.
Release metadata is under `metadata/`. Historical package/archive copies include
the shared path helpers and preserve the relative data layout. Use
`python -m rerankhuts legacy-eval` or `python -m legacy.<module>` from that root.
The original five root-script bytes are preserved under `archive/code_20261022/`
for integrity checks; use the maintained package modules to run tools.

| Path | |
|---|---|
| `results/figures/` | every figure in the paper |
| `results/tables/` | every table in the paper, as the CSV it was rendered from |
| `results/per_question/` | the run log behind each of those tables |
| `results/RESULT_INDEX.md` | what the last rebuild regenerated, and what it did not |
| `results/PROVENANCE.md` | the archive round these files were published from |
| `LICENSE` | MIT, for the code; see the data note below |

### The per-question logs are reduced

A raw log is one row per question per mode carrying the chunk ids, URLs, titles
and scores of all five pipeline stages. At a pool of 100 that is ~1.5 MB of list
columns per question, and the full set is 838 MB -- past what GitHub will take,
and mostly repeated between stages. `results/per_question/` keeps the columns
that decide every reported number: `ranking_urls` (matched against the gold URL
for MRR and nDCG@10), `final_urls` (for the top-4 hit rate), the per-stage
counts, the timings, and the abstention flag. It drops the per-stage id, title
and score lists, which no table or figure reads.

The reduction is metric-preserving, and that is checkable: recomputing nDCG@10,
MRR, Recall@10 and the final hit rate from the reduced logs reproduces
`results/tables/rev_table_rerankers.csv` to four decimals on all three views
(for example, expanded-benchmark nDCG@10 of 0.8736 / 0.8428 / 0.9024 / 0.9797 for
the non-re-ranked baseline, MiniLM-L6, bge-reranker-v2-m3 and the source-aware
diagnostic). A full-fidelity log is written by any run of `run_rag_eval.py`; the
reduction is applied only on the way into this release.

## License and anonymity

The code is MIT-licensed (`LICENSE`). The corpora are derived from public
sources and keep their own terms: NCI/PDQ pages and the oncology textbook are
U.S. Government works, and the PubMed records are abstract text plus citation
metadata used under the NLM terms of use. The questions, the gold-page
assignments and the LLM-judge scores are ours and ship under the same MIT terms
as the code.

This release carries no author names, affiliations or machine paths, so it can
be used for double-blind review. If you are reading it during review, it is the
artifact referenced in the paper's Artifact Availability section.
