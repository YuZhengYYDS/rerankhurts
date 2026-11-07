# Oncology annotated-support coverage

This snapshot contains the 155-question, 20-configuration results used for Table V
and the Oncology part of Fig. 11. It includes 377 annotated required facts and
1,241 exact source occurrences. The original corpus stays at
`data/oncology/corpus/corpus_chunks_v2.jsonl`.

Run `python -m rerankhuts oncology-coverage` from the repository root. Outputs
go to a new directory under `build/reanalysis/`; original inputs and outputs
are not overwritten. This offline command reproduces saved coverage using the
previously verified character-boundary map in
`inputs/delivered_original_intervals.csv`. It validates quote spans, trace
identities, delivered chunk/token records and every saved question-level coverage
outcome. Tokenizer offsets are an explicit saved input to `rescore.py`.

To independently reconstruct that input from the pinned tokenizer, run:

```bash
pixi run --locked -e gpu python experiments/supplements/oncology_coverage_v1/verify_tokenizer_intervals.py --tokenizer <local-snapshot-directory>
```

This command verifies the exact tokenizer JSON hash, token prefixes, original
character endpoints and all final token streams. It loads no neural model and
does not download files. The unchanged original full-scoring/inference source is
in [source_snapshot/](source_snapshot/README.md).

Files:

- `inputs/questions_revised.jsonl`: final 155 questions; [English metadata notes](inputs/QUESTION_VERSION_NOTES_EN.md) accompany the frozen version explanations.
- `annotations/truth.jsonl`, `claims.jsonl`, `rubric_freeze.json`: required facts,
  alternative support sets, exact source references and frozen input hashes.
- `inputs/trace_index.json`: executable repository-relative mapping for all 155
  traces. The original 152 unchanged-question traces are reused in place; the
  three supplemental traces are in `run_three/traces/`.
- `results/configuration_summary.csv`: all 20 configurations and Table V means.
- `results/per_question_coverage.csv`, `per_fact_coverage.csv`,
  `per_stage_coverage.csv`: question, fact and stage outcomes.
- `results/paired_contrasts.csv`, `same_page_different_fact_cases.csv`: paired
  configuration effects, source-group bootstrap intervals and divergence cases.
- `protocol.json`, `status.json`, `run_three/`, `results/validation.json` and
  `trace_provenance.json`: original processing/run records, preserved unchanged.

The source snapshot documents the input revisions and review status; see
[the artifact guide](../../../docs/V25_ARTIFACT_GUIDE.md) for the exact reuse/rerun
mapping. Do not pool hardware-specific timings or reinterpret annotated-span
coverage as clinical correctness or exhaustive support adjudication.
