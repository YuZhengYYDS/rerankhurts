# Strengthening study: reproducible workload and workflow

This directory implements the prospectively specified experiments in [study_plan.json](study_plan.json). It contains the 360-world synthetic workload and separate inference, evidence evaluation, answer generation, and latency measurement. Earlier replay and pilot data, code, and results remain separate. This document describes the design and commands; it does not report experimental outcomes.

As of 2026-10-02, the automated portions of all four phases are complete: 89,280 main inference records and independent evidence evaluations, 720 actual model answers, and 576 online request measurements, with eight warm-ups excluded. Each stage has its own completed status record. The 60-world human review remains pending, and external real-world replication has not been performed. The baseline and strengthening core are verified in the private repository; the restructured paper's four delivery archives correspond to this [Release download location](https://github.com/YuZhengYYDS/rerankhuts/releases/tag/icde2027-restructured-20261013). Its assets and upload verification receipt determine publication status. Private delivery does not complete the separate EAB requirement for openly accessible artifacts.

The 2026-10-13 manuscript restructuring places this study at the center of the paper. `main.tex` directly includes the methods under Benchmark and Experimental Design; `strengthening.tex` contains only the main results. This revision does not rerun experiments or change computational code, experimental data, or statistical results; the table-builder adjustment affects caption wording only. The frozen workflow below retains its October 2 completion provenance.

## Data and independent units

The frozen dataset is [data/strengthening_v1](data/strengthening_v1). Seeds `20261002`, `20261003`, and `20261004` each generate 20 development and 100 test worlds: **360 independent worlds**, with **720 paired tasks** and **57,600 chunks**. Each task searches its own 80-chunk tenant collection. A latent world, including both variants, belongs to exactly one split. Statistical inference uses worlds, not chunks, tasks, or configurations as independent observations.

The two variants have identical questions, ordered document texts, fact values, and source hosts. Exactly 12 registry URL assignments change from separate pages to a shared designated page. This intervention changes URL concentration. The number of replicated chunks, chosen from 0, 4, and 12, is a separate between-world factor and stays constant within each pair. Shared text embeddings and scores may be reused without mixing searchable collections.

Worlds require two, three, or four exclusive facts. The six designed scenarios are a single complete chunk, complementary chunks on one URL, complementary chunks across URLs, equivalent complete support sets, obsolete/current conflicting assertions, and varying support position. Support positions and document lengths are drawn from the frozen ranges; worlds are never accepted or discarded on the basis of model scores, effect direction, or significance. Having complete support somewhere in a collection does not guarantee that a particular retrieval, cap, or budget can retain it.

Development uses prose and list renderings. Test includes those families plus 150 worlds rendered as held-out question/answer text. The held-out grammar is checked for structural correctness but is not used for model tuning. Open and constrained source policies are balanced by design, with the same policy in both variants. These mixture weights describe the simulator, not real deployment prevalence.

## Input boundary and semantic oracle

The inference backend reads two public JSONL files with strict schemas:

- `corpus.jsonl`: `chunk_id`, `collection_id`, `url`, `text`.
- `questions.jsonl`: `qid`, `collection_id`, `question`, `allowed_url_prefixes`.

Neural retrieval and reranking receive question and document text. Collection IDs restrict retrieval; URLs implement explicit source policies and per-URL caps. Neither oracle labels nor split/scenario labels enter these models.

Evaluation-only files are `truth.jsonl` (one dated fact table per world), `metadata.jsonl` (task/group/split/template/policy/factors and designated URLs), and `claims.jsonl` (generator claim offsets and labels). `specification.json` freezes their hashes, dimensions, generator hash, and study-plan snapshot. The generated specification records that an independent audit is required; its later outcome belongs in `audit/report.json`, not in a rewritten specification.

The independent parser in [audit_data.py](audit_data.py) does not import the generator. `parse_claims(text)` returns complete subject/version/predicate/value assertions and original character intervals; `classify(truth, claim)` independently assigns semantic status against the fact table. The evaluator reparses text rather than awarding credit from `claims.jsonl`. In the QA rendering, a complete support span includes both the question binding the subject/version/predicate and its answer. An isolated answer value earns no support. Wrong-subject `-Annex` records are irrelevant; superseded-version statements are obsolete; a different current value of an exclusive predicate is contradictory.

`U_sim` is one exactly when all required facts have complete valid support in the delivered text. `fact_coverage` is the fraction of unique required facts supported. Duplicate assertions do not increase coverage. Admissible support, contradiction exposure, obsolete exposure, and nonempty source-policy compliance (`C_sim`) are separate measurements. A contradictory statement does not silently negate valid coverage. `G_final` records whether a delivered segment belongs to a designated gold URL; a URL match alone provides no fact credit, and alternative supporting URLs can provide fact credit without a gold-URL match. These endpoints are synthetic oracle measurements, not human judgments or clinical utility.

The renderer samples current and old values from the same value distributions. Every assertion binds its own entity and revision, including distractors. Questions specify the requested current revision; the temporal scenario therefore tests version-conditioned retrieval and evidence exposure, not autonomous inference of which revision is current. Current contradictory assertions occur at the consortium host, so source filtering and truth status are structurally related in this workload. The answer prompt exposes publisher origins for source-policy use, omitting role-revealing URL paths such as `archive` and `disputed`; source labels still map to the original trace records. Generalization to arbitrary or unlabeled publisher reliability requires other data.

## Configuration and visibility contract

`protocol.build_configurations()` creates **124 unique configurations**: 28 budget/cap main configurations and 96 targeted comparisons. Budgets 256, 512, 1024, and 2048 have respectively 7, 55, 7, and 55 configurations. This is a targeted matrix, not the Cartesian product of all factor levels. Exact configurations are recorded in each backend manifest before inference.

The three retrieval/reranking model snapshots are:

- Dense encoder: `BAAI/bge-small-en-v1.5` at `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`.
- M3 cross-encoder: `BAAI/bge-reranker-v2-m3` at `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`.
- MiniLM cross-encoder: `cross-encoder/ms-marco-MiniLM-L6-v2` at `233902d25c440f23af6f7d6e94d2946bac0bee0a`.

Dense document views use sequence limits of 128 or 512 tokens, including special tokens, or overlapping windows with max query-cosine aggregation. Dense queries keep a 512-token limit. Cross-encoder views use a **joint question/document** limit of 128 or 512 tokens: question and special tokens reduce document capacity. Cross-encoder windows keep the complete question, slide over document tokens, and max-aggregate logits. These scoring limits are independent of the final evidence budget. MMR uses the fixed prefix-512 dense view. BM25 is collection-local; fusion uses reciprocal-rank fusion with constant 60.

The evidence budget uses `google-bert/bert-base-uncased` at `86b5e0934494bd15c9632b12f734a8a67f723594`, with no added special tokens inside segments and one SEP token between segments. It excludes the question, instructions, URL labels, and generated answer. Packing choices are prefix truncation, whole-chunk skipping, and query-only BM25 selection of nonoverlapping 192-token windows within each ranked chunk. Window packing retains chunk order; it is not an oracle or a global window reranker. Actual original character/token intervals and delivered token IDs are saved and independently checked.

The primary contrasts are M3 post-cap minus pre-cap at cap 2, dense pool 64, prefix packing, budget 512 or 2048, and no explicit source filter. Analysis averages paired-variant differences within worlds, uses seed-stratified world bootstrap intervals, and adjusts the two primary comparisons with Holm's method. Other comparisons are exploratory. Null, reversed, and budget-infeasible observations remain in the analysis; an all-zero empirical difference is not an equivalence claim.

## Commands and provenance

Run commands from the repository root with the checked-in Pixi lockfile. The `gpu` environment supplies the model/tokenizer libraries; `--device cpu` is available but retains the same model dependencies. Pinned model downloads are separate from inference and are stored under `.cache/models/`.

```powershell
pixi run --locked -e gpu strengthen-models --include-answer-model
pixi run --locked strengthen-audit --output build/strengthening/data_audit
pixi run --locked -e gpu strengthen-run
pixi run --locked -e gpu strengthen-evaluate
pixi run --locked -e gpu strengthen-answers
pixi run --locked -e gpu strengthen-timing
pixi run --locked strengthen-analyze --plots
```

The default inference directory is `experiments/runs/strengthening_v1`; evidence analysis defaults to `experiments/strengthening/results/strengthening_v1`, with `answers/` and `timing/` subdirectories for those experiments. `strengthen-models --verify-only --include-answer-model` hashes existing snapshots without network access. The runtime freezes code, models, packages, settings, study plan, and public input hashes. Resume refuses a changed identity; changed experiments require new output directories. Partial `--limit` runs are smoke tests and retain the full expected denominator.

When using a custom audit `--output`, read source documents from the dataset supplied by `--data` (the default is `experiments/strengthening/data/strengthening_v1`). The packet's `../corpus.jsonl` reference describes the shipped `data/strengthening_v1/audit/` layout and does not relocate the corpus into a custom output directory.

The dataset is already generated. To reproduce generation in a separate directory, use:

```powershell
pixi run --locked strengthen-generate --output build/strengthening/regenerated_v1 --seeds 20261002 20261003 20261004 --dev-per-seed 20 --test-per-seed 100
pixi run --locked strengthen-audit --data build/strengthening/regenerated_v1
```

Generation refuses to replace different frozen bytes. The automated audit verifies file hashes, schema, IDs, split boundaries, complete semantic spans, admissible support, equivalent support sets, and paired URL-only interventions. Tests exercise semantic errors and tampered inputs; run `pixi run --locked -e gpu python -m pytest tests/test_strengthening_data.py tests/test_strengthening_evaluation.py` for those checks. The backend has additional operator and input-boundary tests under `tests/`.

The separate answer experiment uses pinned `Qwen/Qwen2.5-1.5B-Instruct`, deterministic decoding, 60 preselected test worlds, both variants, four evidence configurations, and closed-book/no-support controls. Prompt and answer token costs use the answer tokenizer and are reported separately from evidence budgets. Latency measurements use fresh query encoding and reranker inference with resident models and offline indexes; model loading, offline indexing, answer generation, and serialization are excluded. Shared scoring timings in the main factorial run are diagnostics and must not be presented as independent online latency measurements.

## Human review status

The [human audit packet](data/strengthening_v1/audit/README.md) contains 60 worlds sampled by seed/template/scenario before inference, with two blank reviewer slots per world. **Human review has not been performed.** The automatic semantic audit does not populate reviewer judgments or complete the human E2 requirement. Genuine reviewers must independently inspect the source texts and fact tables, record their identities and observations, and resolve disagreements before any human-agreement claim is made.
