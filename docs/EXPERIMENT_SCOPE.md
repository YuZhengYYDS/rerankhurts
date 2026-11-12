# ICDE adaptation: evidence and execution boundaries

This document maps the ICDE/VLDB adaptation memorandum to the delivered
evidence and experiment entry points.

The 2026-10-13 manuscript restructuring presents the 360-world study as the main
experiment, followed by oncology and pilot evidence as context. It does not rerun
experiments or change computational code, experimental data, or statistical
results; the table-builder adjustment changes caption wording only. Automated
experiment completion remains dated 2026-10-02.

## E0: frozen-output reproducibility

Recompute historical ranking and final-page-retention metrics from the released
per-question CSV files. Keep historical scoring semantics separate from the new
unique-URL metric. Reduced historical logs do not contain the raw candidate IDs;
they cannot validate early-stage evidence retention or reproduce neural inference.

## E1 and E2: human evidence utility

Human semantic review of the sampled 60 worlds has been completed. This audit
checks annotation correctness, assertion completeness, temporal/revision status,
and source-policy consistency. Independent information needs, domain-qualified
support annotations, set-level
sufficiency, adjudication and group-disjoint development/test evaluation are
required for the memorandum's human-utility claims. LLM-judge scores are recorded
as automatic evaluations.

## E3: new operator experiment

The new runner uses one maximal dense-retrieval ranking for each query, pools of
16/64, no URL cap/cap before reranking/cap after reranking, no reranker/m3, and
512/2048 evidence tokens. Equivalent no-reranker cap positions are merged, giving
20 unique configurations. Every query saves full stage identities and the exact
delivered evidence token stream. Results measure designated-page retention (G),
not human evidence utility (U). New inference is distinguishable from E0 replay.

## E4 and E5 in the original release

Splits of the existing 155 questions are not independent external replication.
Hardware and component inference timings describe the current local execution.
Cached component times are not independent end-to-end benchmarks of all pipelines.
External workloads, human U/C/A, realistic load and formal generalization claims
remain outside the evidence supplied by those original experiments. The new
strengthening protocol below adds actual answer-model evaluation and separate
request timing; it does not turn synthetic tasks into external real-world data.

## September 28 controlled pilot: pilot_v2

The September 28 revision adds a controlled simulation route. It is a
separate synthetic experiment using fictional registry workflows with known
fact spans, not human E1/E2 and not real-world E4. The actual retrieval/reranking
pipeline runs on 60 worlds, paired open/constrained questions and 780 chunks.
An independent evaluator measures complete delivered fact coverage (`U_sim`),
source admissibility and contradiction/obsolete exposure. Frozen development
selection and held-out testing apply only to this generated population.

The primary selector uses open questions at 512 tokens. The denominator
retains the long-evidence worlds whose necessary facts are structurally beyond
that budget; their limitation is reported independently of model performance.
Constrained selection, generated answer quality and clinical usefulness are
not claimed from this pilot. Its development ties, zero-effect comparisons and
reverse selector result remain in the artifact when new experiments are added.
All synthetic labels remain separate from the human-only E2 gate.

## October 2 strengthening study: strengthening_v1

The new [study plan](../experiments/strengthening/study_plan.json) fixes 360
independent fictional worlds across three seeds: 60 development and 300 test
worlds, including 150 test worlds with a held-out QA document rendering. Each
world contributes two tasks in separate 80-chunk tenant collections. The paired
intervention changes URL concentration while preserving ordered document text,
questions, facts and source hosts. Duplicate intensity and support structure
vary between worlds. This estimates mechanisms within a designed synthetic
mixture, not their frequency in a deployment population.

The inference backend consumes public corpus and question files only. An
independent parser checks rendered assertions against dated world facts and
scores complete assertions in verified delivered intervals. Fact coverage,
designated-URL retention, admissible coverage, contradictions, obsolete evidence
and source compliance are separate endpoints. Source hosts and contradiction
status are related by construction; current revisions are explicit in questions.
The QA holdout concerns document rendering, not a separate family of user questions.

The 124 configurations form a targeted matrix of cap placement, budgets,
retrievers, cross-encoders, scoring visibility, packing, refill and source-policy
placement. They are not a full Cartesian product. The automated portions of all
four phases are complete as of 2026-10-02: 89,280 inference records and independent
evidence evaluations, 720 actual answers, and 576 timed requests. Eight warm-up
requests are excluded from timing results. Inference, evaluation, answers and
timing each have a separate completed status record.

The completed answer experiment covers 60 test worlds, both variants and six
conditions, for 720 actual local Qwen responses. Four evidence conditions are accompanied
by closed-book and wrong-world controls; exact fictional correctness, grounding
and abstention are scored separately. The completed latency session covers 24 worlds,
one variant per world and four configurations: 96 first-pass and 480 steady
requests, plus eight excluded warm-ups. Requests recompute query embeddings and
reranker scores with resident models; offline indexing, model loading, generation
and serialization are outside the measured boundary. First-pass is not a cold
machine or model-loading benchmark.

Primary inference averages the two variant-specific post-minus-pre differences
within each test world. The two prespecified contrasts use dense pool 64, M3,
cap two, no refill, no source filter, prefix512 dense/CE views, prefix packing,
and budgets 512/2048. Seed-stratified world bootstrap intervals and world sign
flips preserve this clustering; Holm adjustment covers the two primary contrasts,
with BH adjustments within exploratory families. Null, reverse and structurally
infeasible cases remain in the analysis. Degenerate intervals do not establish
equivalence.

The human semantic audit of the 60-world sample is complete. Audit materials are
located in `../experiments/strengthening/data/strengthening_v1/audit/`.
Automatic parser results, tests, model outputs and hash verification are recorded
separately from human review. The semantic audit does not establish clinical
sufficiency or replace human evidence-utility evaluation.
Input/run/result paths, exact commands and completion gates are documented in
[STRENGTHENING_GUIDE.md](STRENGTHENING_GUIDE.md).

## Delivery materials

The restructured manuscript delivery reference is
[icde2027-restructured-20261013](https://github.com/YuZhengYYDS/rerankhuts/releases/tag/icde2027-restructured-20261013).

## Reporting rule

Claims about source retention and synthetic coverage must name their workload
and evaluation unit. Claims about human utility or deployment selection require
corresponding independent evidence. Submission readiness and completed
experiments must be reported separately from executable infrastructure,
in-progress runs and proposed protocols.
