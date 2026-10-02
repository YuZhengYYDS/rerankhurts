# Historical COLING research tools

This directory contains the original corpus, question, evaluation and packaging
tools, reorganized from the repository root. The completed ICDE experiments use
`experiments/`, their reanalysis uses `validation/` and `scripts/`, and the clean
manuscript is in `paper/`. See the root README for those supported workflows.

## Invocation and data paths

Invoke a selected maintained historical tool as a module **from the repository
root**, for example `python -m legacy.run_p3_matrix --dry-run`. Module imports use
the explicit `legacy` package. Data, `.env`, and historical output paths continue
to resolve against the repository root; moving a tool has not moved its inputs.
The drivers launch other historical modules with `-m legacy.<name>` and launch
the frozen retrieval/scoring scripts at their original root paths.

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
  `run_view_analyses.py`, `llm_judge.py`.
- Analysis and figures: `analyze_results.py`, `combine_revision_results.py`,
  `make_figures.py`, `make_heatmaps.py`, `make_main_table.py`,
  `make_revision_tables.py`, `curate_paper_assets.py`.
- Annotation packet preparation: `build_annotation_template.py`,
  `prepare_human_eval_packets.py`. Preparing a packet does not create human labels.
- Historical packaging: `archive_results.py`, `build_revision_assets.py`,
  `package_emnlp_results.py`, `sanitize_release.py`. These retain their historical
  output conventions; use the current packaging command in the root README for
  the ICDE deliverable. Code copies preserve the `legacy/` package structure.

## Frozen root compatibility files

Five scripts remain at their original root paths with unchanged bytes because
`validation/results/input_manifest.json` identifies them as audit inputs:

- `generate_normalized_questions.py`
- `paper_support_analysis.py`
- `run_rag_eval.py`
- `score_retrieval.py`
- `summarize_supplement_results.py`

The E0 audit dynamically loads the normalizer at its root path, and the query
normalization tests import two of these modules directly. Replacing them with
wrappers would change the recorded hashes. Frozen datasets, experiment code,
run identities, evaluation results and table inputs also retain their paths and
bytes. Existing inference resume requires the original command and settings.

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
every moved file's original path/hash, destination/hash, and whether its original
bytes were preserved. Path adaptations apply only to the maintained tools above.
