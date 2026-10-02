# ICDE audit protocol and experiment entry points

This directory implements a new **source-retention audit** on the supplied data.
It does not turn the legacy questions into independent information needs, infer
clinical support from a URL, or fill in human labels. `G` means designated-page
retention. `U`, source compliance `C`, and answer support `A` remain unavailable
until their required labels/protocols exist. No answer generation is performed.

## Run and recompute

From the repository root, after installing the locked Pixi GPU environment:

```powershell
pixi run --locked -e gpu python -m pytest -q tests/test_protocol.py
pixi run --locked -e gpu python -m experiments.run_factorial --device cuda --limit 2 --output experiments/runs/smoke
pixi run --locked -e gpu e3
```

The `e3` task supplies the three immutable model/tokenizer revisions recorded
by the shipped full run. Do not omit these revisions when resuming through the
lower-level module: its legacy default is `main`, which has a different run identity.
The first invocation downloads public model snapshots; no paid API is used.
On an 8 GB CUDA GPU the default reranker uses FP16, eager attention and batches
of 8, after unloading the dense model. Reduce `--rerank-batch-size 4` **before
starting a new run directory** if memory is insufficient. CPU runs use FP32 and
must explicitly request `--device cpu`. They have a different timing regime.

Resume an interrupted run with the exact original command. A run manifest pins
the actual model commit SHAs and refuses changed code, inputs, arguments or
library versions. If such a change is intentional, choose a new output folder.
Per-question trace files and per-input scoring caches are written atomically.
Changing the question limit requires a new output folder.

Recompute tables without downloading or loading models:

```powershell
pixi run --locked python -m experiments.run_factorial --output experiments/runs/e3_m3 --summarize-only
pixi run --locked analyze-e3
pixi run --locked interactions-e3
```

The two analysis tasks copy their inputs and write recomputed outputs under
`build/reanalysis/e3/`, keeping the shipped run files unchanged. `analyze-e3`
produces 16 paired contrasts and the paper figure; `interactions-e3` produces
the distinct eight-interaction diagnostic. They are not duplicate implementations.

`summary.csv`, `per_question.csv` and `status.json` are generated from trace
files. `factorial_diagnostics.json` contains all eight cap-by-reranker `G`
interactions for the two pools and budgets, with exploratory pointwise 95%
page-group bootstrap intervals. They are not confirmatory, multiplicity-adjusted
tests and cannot establish an interaction in human evidence utility.
This lower-level interaction diagnostic complements the main paired contrasts
and figures from `scripts/analyze_factorial.py`; both default to seed 20260924
and 5000 group-bootstrap replicates. The two files answer different contrasts
and must not be treated as independent replications.

## Frozen operator and metric definitions

* **Input:** frozen `corpus_chunks_v2.jsonl` (all supplied rows) and
  `questions_expanded_full_validated.jsonl`. Data and code SHA-256 values are
  recorded. Every corpus row is retained, including legacy ID collisions;
  collided IDs receive `::row` plus a stable zero-based corpus row number.
  Traces also retain `original_chunk_id` and `corpus_row`. The manifest gives
  collision and exact-duplicate counts, so this is not implicit deduplication.
* **Retrieval:** `BAAI/bge-small-en-v1.5`, FP32 normalized embeddings, cosine
  scores, maximum sequence length 512 and no query prefix (matching the legacy
  input format). Every question has one maximum 64-candidate list. Pools of
  16 and 64 are prefixes of that same list. Exact ties retain corpus order.
* **Source cap:** at most two chunks per normalized URL; stable filtering
  within the raw pool, with no replenishment from outside that pool. URL
  normalization lowercases scheme/host, removes fragments/trailing slashes,
  and keeps query parameters (which can encode versions).
* **Reranking:** scalar raw logits from `BAAI/bge-reranker-v2-m3`, input pair
  `(question, chunk text)`, tokenizer truncation to 512 total pair tokens.
  Actual and pre-truncation pair token counts are logged. Equal scores retain
  first-stage order. The no-reranker cells use the original dense ordering.
* **Twenty unique cells:** two pools × two budgets × five operator sequences:
  no cap/no reranker; cap/no reranker; no cap/m3; cap→m3; m3→cap. The two
  no-reranker cap orders are identical, so 24 nominal cells become 20.
* **Evidence budget:** a common `google-bert/bert-base-uncased` tokenizer is
  pinned separately from the ranking models. It gives every condition the
  same budget accounting. Chunk IDs are encoded without added start/end
  tokens, separated by one tokenizer SEP ID, and concatenated in rank order.
  The last chunk is prefix-truncated to fit 512 or 2048 tokens; longer chunks
  are never skipped in favor of later chunks. Traces store the exact token
  stream, delivered decoded text and partial-chunk status. This measures
  evidence tokens, excluding question, metadata, generation prompt and answer.
  No claim is made that these are all input tokens of an unexecuted generator.
* **Page metrics:** `G_final=1` if any delivered chunk contributes at least one
  token from any designated gold URL. This intentionally does not establish
  support. Ranking MRR and nDCG@10 use the complete post-operator ranking
  before budget packing, stably collapsed to unique URLs. Binary URL gains
  use all gold URLs for IDCG, including unretrieved gold. Missing retrieved
  gold yields zero; the runner rejects questions lacking gold labels.
  These definitions differ from legacy first-gold/chunk-position nDCG.
* **Stage loss:** first absent designated page across candidate generation,
  pre-cap, reranker membership, post-cap and budget is counted once. Pure
  reordering cannot lose membership, but can change budget delivery. These
  labels are URL diagnostics and must not be called evidence-support loss.

The inputs are existing page-informed questions; this experiment is not E4
external replication. An apparent `G` benefit cannot validate H1 or H2 about
human utility. The strong “misleading pipeline selection” title remains gated
on independent E1/E2 evidence.

## Timing and reproducibility limits

Torch synchronization brackets GPU work. One excluded query warmup precedes
retrieval measurements; one excluded pair warmup precedes reranking. Online
retrieval includes query encoding, score computation and top-64 selection.
Reranker measurements include CPU pair tokenization/instrumentation, transfers,
inference and score extraction. URL filtering, score sorting and packing are
measured on the CPU. Offline corpus tokenization/encoding and model loading are
excluded from online totals; available offline timings are recorded separately.

To keep the local experiment tractable, each distinct query/input-list rerank
operation is measured once. Off-cap and post-cap share the same inference;
different budgets also share it. Pre-cap is executed on its own input list,
so its reduced inference cost is measured rather than guessed. Reported p50/p95
are percentiles of **shared-component sums**, not 20 independently measured
end-to-end services. Cache resumption retains the original measured inference
time and logs `cache_hit`; it never interprets a cache lookup as zero inference
cost. There are no repeated-run uncertainty estimates, concurrent-load tests,
or production throughput claims. E5 is therefore only partially covered.

Seeds, deterministic Torch algorithms, disabled TF32, model SHAs, exact model
file hashes, package versions, GPU/CPU/platform, code hashes, pair lengths,
candidate IDs, stage ranks and evidence tokens are recorded. Cross-hardware
floating-point variation remains possible. `manifest.json` defines the run;
`model_files/` hashes downloaded model/tokenizer files. `cache/` and model
weights can be omitted from a published artifact when the exact download and
recompute instructions are retained. Keep `traces/`, manifest, summary and
per-question results for audit and table regeneration.

## Independent annotation and E2 gate

First obtain independent information needs with stable `qid` and `group_id`;
questions should precede selection of their reference pages. The following
command creates a **blank** expert fact-rubric template:

```powershell
pixi run --locked python -m experiments.annotation prepare --questions independent_questions.jsonl --output experiments/annotations/pilot
```

A domain expert supplies necessary facts, source policy, authorship and an
honest declaration that the rubric was frozen before viewing system outputs.
After running the fixed configurations on that cohort, export content-first
annotation packets:

```powershell
pixi run --locked python -m experiments.annotation export --run experiments/runs/independent_pilot --rubric experiments/annotations/pilot/rubric_frozen.jsonl --output experiments/annotations/pilot/packets
```

Two independent annotator folders have blank chunk support labels (0/1/2),
fact spans, conflict/outdated flags and **direct bundle-level** U (0/1/2).
System names, ranks, URL and gold flags are hidden in phase 1; source metadata
is provided separately in phase 2. The unmodified text can retain source
identity cues, a disclosed limitation. Partial chunks are distinct text items.
Never give annotators `coordinator_private/`. This pool contains final delivered
text only: add independent retrieved evidence and complete earlier-stage
labels before claiming coverage or support-loss mechanisms. Missing labels
remain unknown. An expert must adjudicate disagreements and agreement must be
reported; the scripts cannot provide medical judgments.

E2 consumes a manually adjudicated CSV with columns `qid,information_need_id,
group_id,config_id,token_budget,construction_source,source_policy,G,
url_ndcg_at_10,U,annotation_source,adjudication_record_id`.
Use `annotation_source=human_adjudicated`, U in {0,1,2},
`construction_source=independent_information_need`, and `source_policy=open`.
The endpoint is the proportion of bundles rated U=2. Every frozen configuration
must have a label on every question, at the same token budget. The specification
JSON contains `dev_groups`, `test_groups`, `configs`, full `tie_order`,
`primary_metric` (G or url_ndcg_at_10), `token_budget`, `delta`, `seed`,
`bootstrap_repetitions` (at least 1000), and
`frozen_before_test_inspection=true`. Freeze the scientific choices before
examining test labels; the field is an attestation, not proof of preregistration.
Only one open-evidence question instance per information need is accepted;
alternate phrasings cannot silently count as independent samples. Configurations
and group lists must be unique. At least two development and two test groups are
required for the bootstrap entry point, although two remains very imprecise.

The CLI also requires a provenance manifest with `kind=human_adjudication`, at
least two distinct `annotator_ids`, one `adjudicator_id`, and paths plus SHA-256
hashes under `rubric_file/rubric_sha256`,
`construction_manifest_file/construction_manifest_sha256`, and
`adjudication_records_file/adjudication_records_sha256`. Paths are relative to
the provenance manifest. These three archives use JSONL:

* The rubric records contain `qid`, nonempty `necessary_facts`, `rubric_author`
  and `frozen_before_system_output=true`.
* Construction records match each CSV row's `qid`, `information_need_id`,
  `group_id` and `construction_source`.
* Adjudication records contain unique `adjudication_record_id`, `qid`,
  `config_id`, adjudicated `U`, `adjudicator_id`, and `annotator_ratings` with
  at least two distinct named records of `annotator_id` and ordinal `U`.

Hashes and row-level consistency are checked before results are written. A CSV
merely renamed to `human_adjudicated` is insufficient. These structural checks
cannot certify human authorship, annotation quality or chronological freezing;
the archived originals and study records remain subject to human review.

```powershell
pixi run --locked python -m experiments.analyze_selection --labels adjudicated.csv --spec selection_spec.json --provenance annotation_provenance.json --output experiments/annotations/pilot/selection_result.json
```

The analysis chooses c_G and c_U on development groups, then evaluates their
paired test U difference with whole-group bootstrap intervals and development
selection frequencies. It rejects missing/automatic labels, incomplete cells,
overlapping groups and reused-question cohorts. `--allow-legacy-diagnostic`
explicitly downgrades the latter to a diagnostic; it does not establish formal
E2. Source-constrained selection needs a separately frozen feasibility rule and
is intentionally rejected by this open-evidence implementation. Few independent
groups limit precision; a wide interval is not evidence of equivalence.
