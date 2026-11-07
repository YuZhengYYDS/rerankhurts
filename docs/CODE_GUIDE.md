# Code guide and maintenance rules

## Entry point

Use `pixi run --locked workflow --help` from the repository root. The dispatcher
in `rerankhuts/cli.py` invokes existing programs as argument vectors, sets the
repository working directory and forwards options without shell concatenation.
Model inference, verification, reanalysis, compilation and packaging are separate
actions. Put `--dry-run` before the action, for example
`pixi run --locked workflow --dry-run e3`.

## Experiment implementations

| Module | Responsibility |
| --- | --- |
| `experiments/protocol.py` | E3 configurations, stable ranking, URL caps, token-prefix packing, URL metrics and run identities |
| `experiments/run_factorial.py` | E3 model loading, shared candidates/scores, traces, timing diagnostics and resume checks |
| `experiments/simulation/generate.py` | Pilot facts-first world generation, frozen split, oracle and specification |
| `experiments/simulation/backend.py` | Pilot model inference without oracle labels |
| `experiments/simulation/evaluate.py` | Independent delivered-span/source-policy evaluation and pilot selection statistics |
| `experiments/annotation.py`, `analyze_selection.py` | Human evidence-utility protocol tools with label-provenance guards; separate from dataset-semantic review |

The [strengthening module](../experiments/strengthening/README.md) contains:

- `generate.py`, `study_plan.json`: 360 worlds, paired URL intervention and splits.
- `audit_data.py`: independent assertion parsing and world-fact checks; preparation
  of the original 60-world review packet and blank templates.
- `protocol.py`, `backend.py`: 124 targeted configurations, model inference,
  scoring views, packing, source policy and resume identities, without oracle input.
- `evaluate.py`: verification of delivered tokens/original intervals; fact support,
  admissibility, conflicts, stage transitions and feasibility bounds.
- `analyze.py`: world-paired comparisons, Holm/BH adjustment and downstream analysis.
- `downstream.py`: pinned Qwen answers, evidence controls and grounding evaluation.
- `downstream_2048.py`, `analyze_answers_2048.py`: recovered historical follow-up
  execution/analysis code, retained with its recorded identity and Linux locking.
- `timing.py`: independent online requests that recompute query/pair scores.
- `figures.py`: original benchmark figures from completed, provenance-bound results.

The three original inference backends remain separate to preserve run identities.
Do not merge their implementations and continue writing to an old run. Two
factorial analysis programs also have distinct scopes: `scripts/analyze_factorial.py`
produces 16 E3 contrasts; `experiments/analyze_factorial.py` produces eight cap-order
interactions. The dispatcher verifies original inputs and copies only the four
analysis input files to `build/reanalysis/e3/`. Reanalysis is not independent inference.

## Current supplementary tools

See [V25_ARTIFACT_GUIDE.md](V25_ARTIFACT_GUIDE.md) for input/output mappings.
The stage and packing scripts read original evaluated records. Oncology
`rescore.py` uses the saved character-boundary map; `verify_tokenizer_intervals.py`
can independently reconstruct those boundaries using the pinned tokenizer JSON.
The source snapshot retains the original preparation, inference and full-scoring
scripts. `scripts/plot_v25_complementary.py` uses the final Oncology results;
`scripts/plot_completed_results.py` remains a historical redraw tool.

`scripts/check_world_review_records.py` checks the supplied review A/B records,
their source labels and evidence indexes against the frozen 60-world sample.
It verifies record consistency, not the authorship of a human assessment.

## Verification tools

- `scripts/check_frozen_files.py`: standard-library hashes and identities for
  recorded E0/E3/pilot code, data, results and traces.
- `scripts/check_strengthening_files.py`: the main 89,280-record study, independent
  evaluation, 720 answers and 576 timing requests; no model cache required.
- `validation/check_e3.py`: 3,100 trace records, ranking stability, budgets, metrics
  and FP16 sensitivity, without importing the original scorer.
- `validation/audit_metrics.py`: E0 replay of 47 historical logs, retaining the
  12 documented original errors.
- `validation/audit_simulation_endpoint_pairs.py`: independent pilot G/U cell counts.
- `scripts/verify_release.py`: archive members, safe paths, sizes and hashes.

Integrity verification and scientific rescoring are different operations. Full
oracle rescoring uses the tokenizer dependencies in the `gpu` environment;
offline integrity checks do not download models or load weights.

## Historical paths and source preservation

Maintained tools live in `rerankhuts/`, `experiments/` and `scripts/`. Historical
root tools moved to `legacy/`, with these compatibility commands:

| Original tool, now in `legacy/` | Dispatcher command |
| --- | --- |
| `generate_normalized_questions.py` | `legacy-normalize` |
| `run_rag_eval.py` | `legacy-eval` |
| `score_retrieval.py` | `legacy-score` |
| `paper_support_analysis.py` | `legacy-analysis` |
| `summarize_supplement_results.py` | `legacy-summarize` |

These commands keep their original environment-variable configuration and do not
forward command-line arguments. `.env`, cache and output paths resolve from the
root; Oncology inputs default to `data/oncology/`. Other legacy tools use explicit
package names, for example `python -m legacy.<module>`.

The byte-preserved pre-migration sources remain in `archive/code_20261022/`.
Historical E0 manifests retain their original paths and digests; verification
resolves only the five known archived root tools and fails if an archive is
missing or changed. It never falls back to the maintained implementation.
E0 reanalysis records both the archived source and maintained function identities.

`rerankhuts/paths.py` resolves the known original Oncology root filenames to
`data/oncology/` and the metadata relocations. It preserves original hashes and
does not reinterpret same-named files in unrelated directories. New E3 execution
passes the relocated corpus/question paths and a fresh `build/runs/e3/` destination.
The frozen backend bytes are unchanged; direct invocation requires explicit input
and output paths. Obsolete scratch tools in `legacy/archive/` are not current entry points.

## Validation after changes

1. Run relevant tests; select the `gpu` environment for tokenizer/model-library tests.
2. Verify the original frozen identities and main strengthening artifacts.
3. Recompute affected analyses into new `build/` directories, then compile/check
   the manuscript if its inputs changed.
4. Verify packaging selection and generated releases as appropriate.

Protocol changes require a new version and separate outputs. Do not rewrite old
manifests to make changed experiments appear to be the original run.
