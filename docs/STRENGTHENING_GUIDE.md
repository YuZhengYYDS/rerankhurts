# Strengthening study: execution and verification

This guide covers `strengthening_v1`: fictional administrative records used to
study URL concentration, scoring visibility and evidence packing. The original
automated phases completed on October 2: 89,280 inference/evaluation records,
720 model answers and 576 online requests, excluding eight warm-ups. This is a
controlled benchmark, distinct from clinical validation. Current v25 methods and
results are in `paper/sections/03_protocol.tex` and `04_evaluation.tex`.

## Verify delivered artifacts first

Use the full repository/archive with its directory structure. The code-only ZIP
does not contain all inputs and traces; combining convenience code/result ZIPs
does not guarantee a complete original dataset. The paper ZIP is for compilation.

```bash
pixi run --locked strengthen-verify --require-complete
pixi run --locked verify
pixi run --locked test
# Standard-library strengthening check without Pixi:
python scripts/check_strengthening_files.py --require-complete
```

These checks verify saved identities, record sets and source references without
model caches. `--allow-in-progress` accepts pending new work without representing
it as completed. Integrity verification is separate from scientific rescoring
and semantic review.

## Fixed dataset and independent units

Inputs are in `experiments/strengthening/data/strengthening_v1/`. Seeds
`20261002`, `20261003`, `20261004` each generate 20 development and 100 test worlds:
360 independent worlds, including 60 development and 300 test worlds. Two variants
per world give 720 isolated 80-chunk task collections, with 57,600 chunks total.
The variants preserve question, ordered text, facts and publisher hosts while
changing twelve URL assignments. Both stay in the same split.

Development documents use prose/list templates. Test includes 150 held-out QA
document worlds. This changes document rendering across worlds, not same-world
templates or independent question families. Inference sees public corpus/question
fields and explicit source restrictions; world facts, metadata and claim labels
remain evaluation-only. The independent parser reconstructs assertions from text.

Frozen SHA-256 values:

```text
specification.json  90daa40eec2c4603bebb5918f1e77b21b7d59f9df659edb55deb84d793b8143b
corpus.jsonl         b882dc31e8ed9a96df520f5e5b6423a64f3e17fa4770ab3840385dddd5b8ccb5
questions.jsonl      71303669f245110cffb695dcb9d779e9896d1c353d58109485aa6c54510b77d7
metadata.jsonl       c43eb0ec083bbfa5e0672201a7a0e44374437266a0a12e506dced462cf3622b2
truth.jsonl          c4022335d4a79a7863b3f89df62b5d0e3e50e85b65a6ba60b1babd680287fdb7
claims.jsonl         2cbab46699b2ae34424e1a13c77139aaba1d3ce45168886d6a326bd4c1947451
```

The specification also fixes generator code, study plan and splits. A changed
protocol, model, device setting or input needs a new identity/output directory,
not rewritten old hashes.

## Locked environment and model snapshots

```bash
pixi install --locked -e default
pixi install --locked -e gpu
pixi run --locked -e gpu strengthen-models --include-answer-model
pixi run --locked -e gpu strengthen-models --include-answer-model --verify-only
```

The GPU environment supplies PyTorch, Transformers, Sentence Transformers and
tokenizers. The tokenizer-only oracle evaluation uses the same dependency group.
Use a separate identity for `--device cpu`. Weights are excluded from release
archives, downloaded explicitly, and subsequently read from `.cache/models/`.

| Component | Frozen model revision |
| --- | --- |
| `BAAI/bge-small-en-v1.5` | `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` |
| `BAAI/bge-reranker-v2-m3` | `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e` |
| `cross-encoder/ms-marco-MiniLM-L6-v2` | `233902d25c440f23af6f7d6e94d2946bac0bee0a` |
| `google-bert/bert-base-uncased`, evidence tokenizer only | `86b5e0934494bd15c9632b12f734a8a67f723594` |
| `Qwen/Qwen2.5-1.5B-Instruct`, answer model | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |

The 128/512 scoring limits are experimental interventions, not claims about each
model's maximum native context. Download verification records exact model-file hashes.

## Reproduce into separate directories

The delivered dataset and audit packet already exist. Generation refuses conflicting
bytes. If generating an entirely new work copy, run the default independent audit
once to create its packet, then use separate destinations for further audits.

```bash
pixi run --locked strengthen-generate
pixi run --locked strengthen-audit --output build/reproduction/data_audit
pixi run --locked -e gpu strengthen-run --output build/reproduction/strengthening_run
pixi run --locked -e gpu strengthen-evaluate --run build/reproduction/strengthening_run --output build/reproduction/strengthening_results
pixi run --locked -e gpu strengthen-answers --run build/reproduction/strengthening_run --output build/reproduction/strengthening_results/answers
pixi run --locked -e gpu strengthen-timing --run build/reproduction/strengthening_run --output build/reproduction/strengthening_results/timing
pixi run --locked strengthen-analyze --results build/reproduction/strengthening_results
pixi run --locked python -m experiments.strengthening.figures --results build/reproduction/strengthening_results
pixi run --locked strengthen-verify --run build/reproduction/strengthening_run --results build/reproduction/strengthening_results --require-complete
```

The 124 targeted configurations comprise 28 main budget/cap cells and 96 selected
mechanism/model/source-policy comparisons. This is not a full Cartesian product.
The run manifest records the exact settings. Inference saves task-level compressed
traces and resumes only an identical identity. A separate `--limit 2` smoke run
retains the full expected denominator; evaluation needs `--allow-partial` and the
analysis refuses to treat it as complete.

The original answer study uses 60 test worlds, two variants and six conditions:
720 answers. The timing study uses 24 worlds, one variant each and four conditions:
96 first-pass plus 480 steady requests, excluding eight warm-ups. Timing refuses
to append to existing request logs; an interrupted session must be restarted
separately rather than combined. Keep the machine awake or use a continuously
available server for uninterrupted execution.

## Rescore saved traces without neural inference

After obtaining/verifying the pinned tokenizer:

```bash
pixi run --locked -e gpu strengthen-evaluate --output build/reanalysis/strengthening
pixi run --locked strengthen-analyze --results build/reanalysis/strengthening --answers experiments/strengthening/results/strengthening_v1/answers --timing experiments/strengthening/results/strengthening_v1/timing
```

These outputs stay in `build/`. Full figure regeneration expects consistent
answer/timing directories under the selected complete result tree; the command
above can read the separately supplied downstream directories for analysis.
For current stage, packing, Oncology and matched-answer follow-up tools, see
[V25_ARTIFACT_GUIDE.md](V25_ARTIFACT_GUIDE.md).

## Endpoint and inference definitions

- `U_sim`: all required current facts have complete support in delivered original
  spans. Fragments can jointly cover an assertion, but missing non-whitespace
  characters prevent complete assertion credit. This is not human utility.
- `G_final`: at least one delivered token belongs to a designated URL. It need
  not agree with `U_sim`.
- `admissible_U_sim`, `C_sim`, `nonempty`: complete support from allowed sources,
  nonempty all-source compliance, and nonempty output, respectively. Empty output
  is not compliant; source-policy contrasts use constrained tasks.
- Conflict and obsolete exposure are separate from positive support. Current
  counterfactuals use the consortium publisher by construction.
- `score_visible_*` refers to scoring-view original text, separately from final
  evidence budgets. `score_single_call_visible_*` requires a complete assertion
  in at least one complete scoring input.
- Stage support distinguishes candidate absence, cap/filter removal and packing
  loss. Pure reordering does not delete full-text membership.
- `feasibility.csv` gives necessary oracle-relaxation bounds for packing geometry.
  Passing is not a guarantee of actual attainment; infeasible cases stay in the
  primary population denominator.

Both primary tests are post-minus-pre `U_sim` at 512/2048 tokens: dense pool 64,
M3, cap two, prefix packing, prefix512 dense/CE views, no refill/filter. Average
the paired variants within each world, use 5,000 seed-stratified world bootstrap
replicates and 20,000 world sign flips under null sign exchangeability. Holm
covers these two tests; named exploratory families use BH. Degenerate empirical
intervals do not establish population equivalence.

`complete_correct` checks normalized fictional truth. `complete_grounded_correct`
also requires cited evidence to contain complete, current, admissible support.
It is not citation-by-citation precision and does not separately penalize every
extra irrelevant citation. `schema_valid` checks JSON key/nesting structure.
Closed-book and wrong-world conditions are explicit no-support controls.

First-pass requests start with resident models and indexes; they are not cold
startup or model-loading measurements. Online timing includes fresh query encoding,
retrieval, CE, cap/filter/packing and in-memory trace construction; it excludes
initialization, offline indexing, answer generation and disk serialization. Shared
factorial component diagnostics do not replace these requests. Request quantiles
are not sums of component quantiles. Repeats are averaged within worlds for pairing.

## Results, reviews and previous studies

Frozen traces stay in `experiments/runs/strengthening_v1/`; evaluated records,
feasibility, primary/exploratory/subgroup comparisons, support flows, controls,
answers, timing and figure/source manifests stay in
`experiments/strengthening/results/strengthening_v1/`.

The author confirmed completion and approval by two human reviewers for the
60-world semantic sample. Its completion report/register preserve that confirmation
basis; the original individual forms were not supplied. The two detailed saved
review files A/B are model-based and separately indexed in
`data/strengthening_v1/audit/reviews/README.md`. Original parser/run statuses
retain their execution-time values. This dataset review is separate from E1/E2
human evidence utility and independent external replication.

The historical E3 and pilot files remain unchanged, including tied, null and
reversed selection outcomes. `legacy_null_audit.json` is replay, not new inference.
Historical release assets retain their dates; the repository's private visibility
does not by itself provide public EAB artifact access.

```bash
pixi run --locked package --split --verify
pixi run --locked verify-package
```

Packages exclude environments, model caches/weights and compiler scratch. The full
package includes original datasets, run manifests/status/traces and independent
evaluation/downstream records needed for cache-free integrity verification.
