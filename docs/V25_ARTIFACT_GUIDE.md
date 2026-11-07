# v25 manuscript and supporting artifacts

The active manuscript is [paper/main.pdf](../paper/main.pdf), with the matching
author-supplied LaTeX export in [paper/](../paper/). It has 12 body pages, 13 total
pages, 12 figures and five tables. The AI acknowledgment and references start on
page 13. The v25 import preserves the manuscript's scientific prose and numbers;
the one Unicode range dash in `question--configuration` uses LaTeX syntax for
portable font rendering.

The original input datasets, model identities, traces and statistical outputs
remain at their existing paths. The following versioned additions supply the
subsequent analyses. Historical run manifests retain their execution-time state.

| Manuscript evidence | Inputs and executable analysis | Saved output |
| --- | --- | --- |
| Main benchmark, primary contrasts, Figs. 4-8 and Table IV | `experiments/strengthening/data/strengthening_v1/`, `experiments/runs/strengthening_v1/`, original independent evaluators | `experiments/strengthening/results/strengthening_v1/` |
| Paired stage transitions in IV-B | `experiments/supplements/stage_reanalysis_v1/analyze.py`; original `per_record.csv` and trace examples | `experiments/supplements/stage_reanalysis_v1/results/` |
| Packing restoration and additional losses in IV-C; Fig. 6(a) context | `experiments/supplements/packing_reanalysis_v1/analyze.py`; original `per_record.csv`, `summary.csv`, run manifest and three trace pairs | `experiments/supplements/packing_reanalysis_v1/results/` |
| Original 512-token answer study in Fig. 9 | `experiments/strengthening/downstream.py` | `experiments/strengthening/results/strengthening_v1/answers/` |
| Matched 2048-token answer follow-up in Fig. 9 | `experiments/strengthening/downstream_2048.py`, `analyze_answers_2048.py`; exact original 120-question sample | `experiments/supplements/answers_2048_120_v1/` including 240 raw responses |
| Request timing in Fig. 10 | `experiments/strengthening/timing.py`; resident-model requests | `experiments/strengthening/results/strengthening_v1/timing/` |
| Oncology page outcomes, Fig. 11(a), and annotated coverage, Table V | `experiments/supplements/oncology_coverage_v1/rescore.py`; frozen Oncology corpus, final question/annotation snapshot and indexed traces | `experiments/supplements/oncology_coverage_v1/results/` |
| Pilot selection, Fig. 11(b) | `experiments/simulation/` | `experiments/simulation/results/pilot_v2/` |
| Saved dimension-level reviews A/B | Original 60-world sample; `scripts/check_world_review_records.py` | `experiments/strengthening/data/strengthening_v1/audit/reviews/` |
| 60-world semantic audit | Original corpus, paired questions, world facts, packet and four-criterion template | `experiments/strengthening/data/strengthening_v1/audit/HUMAN_AUDIT_REPORT.md` and completion records |

## Offline reanalysis

Run from the repository root in the locked default environment:

```bash
pixi run --locked stage-reanalysis
pixi run --locked packing-reanalysis
pixi run --locked oncology-coverage
python experiments/supplements/answers_2048_120_v1/verify.py
```

The first three commands write to separate new directories under
`build/reanalysis/` and refuse an existing destination. Pass `--output
build/reanalysis/<new-name>` for another run. They neither load models nor edit
saved results. Stage and packing computations use task-level descriptive pairs;
the original primary inferential unit remains the world.

Oncology rescoring uses the saved original-character boundary map. Its 1,241
quoted annotation occurrences are checked against original corpus text, and all
155 trace hashes and 3,100 saved coverage outcomes are reconciled. `rescore.py` does not regenerate tokenizer offsets. The separate
`verify_tokenizer_intervals.py --tokenizer <local-snapshot>` command reconstructs
and checks them from the pinned tokenizer JSON, without a neural model. The source run checks remain in the saved records; the original full scoring
scripts are preserved in `oncology_coverage_v1/source_snapshot/`. Coverage means coverage of the
annotated support sets: OR over alternative support sets and AND over the parts
required within each set.

## Input versions and execution provenance

The Oncology cohort has 155 question identifiers and 20 configurations. The
final input file is `oncology_coverage_v1/inputs/questions_revised.jsonl` and the
annotation hashes are in `annotations/rubric_freeze.json`. It reuses the original
traces for 152 unchanged questions; q124, q141 and q297 use saved supplementary
traces for their revised question scopes. `inputs/trace_index.json` maps every
question to its exact repository file and SHA-256. No original Oncology input
or trace is replaced. Original and supplementary timing values come from
different hardware and are not pooled into a common latency measurement.

The annotations and coverage outputs retain the source run's review metadata.
They measure annotated original-span support, not clinical correctness or
exhaustive semantic absence. The 60-world human semantic audit is a separate
dataset check: its report records the author's confirmation that two reviewers
completed the sample and approved it. The completion register is not a substitute
for unavailable original per-criterion reviewer forms. The two completed detailed review files are linked under
`audit/reviews/`, with their dimension-level judgments and evidence indexes.

RAGChecker and RAGAS provide related evaluation context. This revision adds no
comparison experiment and makes no claim of a new fact-coverage metric.

## Current Fig. 11 and language companions

`python scripts/plot_v25_complementary.py` redraws both panels from the final
Oncology snapshot and frozen pilot results into a new `build/` directory. Its
Oncology counts are 20 / 167 / 2,913; the historical redraw script retains the
original 20 / 171 / 2,909 snapshot. The command leaves supplied paper assets intact.

Maintained guides, new review indexes and explanatory reports are English.
Archived Chinese guides, original report/code strings, source quotations and frozen
metadata retain their original bytes. English companions cover the follow-up
result report and the Oncology question-version notes.

## Compilation and packaging

```bash
pixi run --locked -e paper paper
python scripts/check_manuscript.py
pixi run --locked package --split --verify
```

The manuscript checker counts body pages separately from exempt material and
compares compiled table labels with the supplied source. The results archive
includes the versioned supplements and their inputs, code and provenance. The
code-only archive omits data, as before; use the full archive for complete
reproduction. Current verification is recorded in
`validation/repository_update_20261107.json` and the subsequent
`validation/repository_followup_20261107.json`. Older validation files describe
their dated snapshots.
