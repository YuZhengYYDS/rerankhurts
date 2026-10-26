# Historical COLING research tools

This directory contains the original corpus, question, evaluation and packaging
tools, reorganized from the repository root. The completed ICDE experiments use
`experiments/`, their reanalysis uses `validation/` and `scripts/`, and the clean
manuscript is in `paper/`. See the root README for those supported workflows.

## Invocation and data paths

Invoke a selected maintained historical tool as a module **from the repository
root**, for example `python -m legacy.run_p3_matrix --dry-run`. Module imports use
the explicit `legacy` package. Oncology data now lives under `data/oncology/`:
`corpus/` holds corpora, `questions/` holds question sets, `reports/` holds
construction and screening CSVs, and `sources/` holds `data_sources.json` and
`urls.txt`. Builders write new datasets and reports into those same groups.
`.env` and historical result folders still resolve against the repository root.
`metadata/` holds the release manifest and status. The shared location policy is
in `rerankhuts/paths.py`; historical input overrides use `legacy/paths.py`.
Exact former root filenames remain usable as relative input overrides, including
`QUESTIONS_FILE=questions.jsonl`. Explicit custom absolute and relative paths
remain usable. Source configuration retains its original `"path": "urls.txt"`
bytes; the corpus builder resolves that alias to `data/oncology/sources/urls.txt`.
The drivers launch all historical tools with `-m legacy.<name>`. The five former
root scripts also have dispatcher/Pixi tasks: `legacy-normalize`, `legacy-eval`,
`legacy-score`, `legacy-analysis`, and `legacy-summarize`. These commands use the
original environment variables and accept no extra command-line options.

The migration received static Python compilation, import/path checks and frozen
file hash verification. Historical pipelines were not executed. Some workflows
require the original `result_revision/` inputs or the original COLING paper tree,
which are not present in this release. Data builders can replace datasets, and
the LLM question/judge tools can make paid API calls when explicitly invoked.
Neither is part of output reanalysis.

`requirements.txt` preserves the original unpinned dependency list for provenance.
It is not the locked ICDE environment specification: use the root `pixi.toml`
and `pixi.lock` for the current workflows. The original corpus builder also uses
`datasets`; the Pixi environments do not claim to support every historical tool.

## Tool groups

- Corpus and questions: `build_corpus.py`, `build_expanded_benchmark.py`,
  `build_grounded_questions.py`, `annotate_questions.py`,
  `finalize_expanded_benchmark.py`, `purge_leaky_questions.py`,
  `verify_expanded_questions.py`.
- Historical experiment drivers: `run_p3_matrix.py`, `run_p4_expanded.py`,
  `run_view_analyses.py`, `run_rag_eval.py`, `llm_judge.py`.
- Question normalization: `generate_normalized_questions.py`.
- Analysis and figures: `analyze_results.py`, `combine_revision_results.py`,
  `make_figures.py`, `make_heatmaps.py`, `make_main_table.py`,
  `make_revision_tables.py`, `curate_paper_assets.py`, `score_retrieval.py`,
  `paper_support_analysis.py`, `summarize_supplement_results.py`.
- Annotation packet preparation: `build_annotation_template.py`,
  `prepare_human_eval_packets.py`. Preparing a packet does not create human labels.
- Historical packaging: `archive_results.py`, `build_revision_assets.py`,
  `package_emnlp_results.py`, `sanitize_release.py`. These retain their historical
  result-folder conventions and include data plus the path helpers; use the
  current packaging command in the root README for the ICDE deliverable. Code copies preserve the `legacy/` package structure.

## Original source snapshots

All maintained historical Python tools now live in this package; the repository
root contains no Python compatibility shims. Their data defaults resolve under
`data/oncology/`, and their result outputs remain in the historical result folders.

The five former root scripts are retained byte for byte under
`archive/code_20261022/`. They are provenance snapshots, not runnable entry
points. The original `validation/results/input_manifest.json` remains intact:
the frozen checker resolves only those five historical root paths to the
snapshots and checks their original hashes and sizes. Maintained versions here
have the necessary package imports and repository-root path calculations.

The E0 audit loads `legacy/generate_normalized_questions.py` for the wording
transformation and records both that source and the historical snapshots when
writing a fresh reanalysis manifest. Frozen datasets retain their bytes at the new data locations. Historical
manifest strings, experiment code, run identities and evaluation results remain
unchanged; integrity readers translate only the exact recorded root aliases.
Existing inference resume requires the original command and settings.

## Archival files

`archive/` contains six original files preserved byte for byte for provenance,
without adaptation or execution:

- `_chain_validated9.sh`, `_rerun_judges.sh`: reference the former
  `d:/Pycharm/DeepSeekLLM` checkout and historical logs.
- `init_projec.py`: creates files, including `.env`, at import time.
- `inspect_corpus.py`: expects the former `corpus_chunks.jsonl` input.
- `report_figures.py`, `build_case_study_table.py`: expect historical root CSVs
  absent from the current artifact.

They are not current command entry points. `migration_manifest.json` records
the earlier migration's original path/hash, destination/hash, and whether its
original bytes were preserved. The additional five root-script snapshots are
documented in `../archive/code_20261022/README.md`. Path adaptations apply only
to maintained tools.
