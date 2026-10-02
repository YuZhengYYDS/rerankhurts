# ICDE adaptation: evidence and execution boundaries

This project implements the user's ICDE/VLDB adaptation memorandum. The memorandum
is a research design, not a record of completed experiments.

## E0: frozen-output reproducibility

Recompute historical ranking and final-page-retention metrics from the released
per-question CSV files. Keep historical scoring semantics separate from the new
unique-URL metric. Reduced historical logs do not contain the raw candidate IDs;
they cannot validate early-stage evidence retention or reproduce neural inference.

## E1 and E2: human evidence utility

The supplied release explicitly contains no completed human evaluation. Existing
LLM-judge scores are automatic evaluations. Independent information needs,
domain-qualified support annotations, set-level sufficiency, adjudication and
group-disjoint development/test evaluation are required for the memorandum's
human-utility claims. Blank annotation packets are inputs to that work, not results.

## E3: new operator experiment

The new runner uses one maximal dense-retrieval ranking for each query, pools of
16/64, no URL cap/cap before reranking/cap after reranking, no reranker/m3, and
512/2048 evidence tokens. Equivalent no-reranker cap positions are merged, giving
20 unique configurations. Every query saves full stage identities and the exact
delivered evidence token stream. Results measure designated-page retention (G),
not human evidence utility (U). New inference is distinguishable from E0 replay.

## E4 and E5

Splits of the existing 155 questions are not independent external replication.
Hardware and component inference timings describe the current local execution.
Cached component times are not independent end-to-end benchmarks of all pipelines.
External workloads, human U/C/A, realistic load and formal generalization claims
remain outside the evidence supplied by the existing release.

## Controlled synthetic extension

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
not claimed. All synthetic labels remain separate from the human-only E2 gate.

## Reporting rule

The title and abstract must not claim that retrieval metrics mislead deployment
selection until independent human evidence supports that assertion. Submission
readiness and completed experiments must be reported separately from executable
infrastructure and proposed protocols.
