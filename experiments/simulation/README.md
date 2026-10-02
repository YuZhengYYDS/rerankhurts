# Controlled synthetic evidence-selection pilot

This experiment tests how a retrieval configuration selected by designated-page
retention differs from one selected by complete fact coverage in a controlled
synthetic environment. It supplies an exact, inspectable content oracle for
fictional documents while executing the actual dense retriever and cross-encoder.
It complements the historical E0 audit and the oncology E3 experiment; it does
not replace independent human annotation, the human-only E2 gate, or an external
medical benchmark.

The contract was frozen before model execution, with generation and analysis
seed **20260928**. The current dataset is `pilot_v2`. A pre-analysis semantic
audit found that the initial release counterclaim did not always negate the
actual required safeguard. The initial run was interrupted after six tasks;
only progress counters had been examined. Version 2 replaces that sentence with
an explicit negation of the world's exact safeguard, preserving the worlds,
questions, split, IDs, source assignments, and claim placement. The invalidated
version is not an experimental result. See `AMENDMENTS.md` for that validity
correction. The v2 model backend and independent evaluator have now completed
all **2,400 task-configuration records**, with recorded input/code/model hashes.
The full test suite has 73 passing tests, and exact-command resume is verified.

## Observed selection result

For the primary open-evidence 512-token comparison, all ten configurations tie
at 0.60 development complete-fact coverage. The frozen structural tie rule
selects pool-16 dense retrieval without a cap. The page-retention selector
chooses pool-16 m3 without a cap, also a coverage maximizer on development data.
Held-out coverage is 22/40 (0.55) for the coverage-selected configuration and
27/40 (0.675) for the retention-selected configuration. The difference is
-0.125, with a paired test-world 95% bootstrap interval of [-0.25, 0].

Thus, the difference in selected identities is tie-dependent and does not show
a strict conflict between the two development objectives. The pilot does not
support the hypothesis that retention-driven selection reduces held-out fact
coverage. Development bootstrap selects the primary dense coverage candidate
in 61.10% of resamples and the m3 candidate in 38.90%, illustrating instability.
The exploratory 2,048-token contrast is -0.025 (interval [-0.075, 0]), again
with overlapping development maximizers. These conditional intervals do not
jointly integrate development-selection uncertainty or establish equivalence.

Machine-readable results are in `results/pilot_v2/selection.json` and
`results/pilot_v2/summary.csv`; `budget_feasibility.json` preserves the structural
ceiling analysis without changing the denominators. The scientific figure is
regenerated with `pixi run --locked python scripts/plot_simulation.py`.

## Scope and experimental units

The pilot contains 60 fictional cohort worlds, ten in each of six stress
scenarios: `aligned`, `distributed`, `alternative_source`, `stale_version`,
`near_match`, and `late_evidence`. Each world supplies one information need in
two forms: an open-evidence question and a question with an explicit source
restriction. This produces 120 tasks but **60 independent simulation units**;
the paired forms are not two independent information needs.

The text describes fictional oncology record-review workflows, such as routing,
review intervals, and release identity checks. It provides no actual drug or
treatment recommendation. Documents use fictional `*.invalid` addresses and
multiple source families. Required facts are fixed before document plans and
text rendering. Each world has complete valid support available in the corpus,
including support from an allowed source for its constrained question.

The scenarios vary structural conditions: support distributed across chunks,
support on an alternative page, obsolete versions, explicit counterclaims,
similar but different cohorts, repeated chunks from one URL, and support late
in a chunk. A near-match cohort is a distractor, not automatically a contradiction
of the target cohort. A designated gold page need not be sufficient or be the
only supporting source. These are controlled conditions, not measured
frequencies of failures in clinical material.

The long-evidence condition has a deliberate budget boundary. In all ten
`late_evidence` worlds, the earliest complete valid release claim requires a
chunk prefix of 817--1,048 tokens under the pinned budget tokenizer. Complete
coverage is therefore impossible at 512 tokens even with an ideal ranking.
There are four such development worlds and six test worlds, giving overall
512-token coverage ceilings of 0.80 and 0.85, respectively. These are structural
upper bounds, not measured model performance. Report this condition separately
when interpreting coverage failures.

No winning configuration is stipulated. Null, reversed, tied, and scenario-specific
results are retained. Neither document generation nor model/configuration choices
may be revised in response to test outcomes. A later redesigned benchmark must
have a new version and a separate analysis rather than overwrite this pilot.

## Frozen development and test split

Whole worlds are assigned deterministically to 20 development groups and 40
test groups before any model scores are inspected. Both question forms stay in
the same split. The 20 development worlds are as evenly distributed across six
scenarios as integer counts permit: two scenarios have four and four have three;
their test counts are six and seven, respectively. The seeded assignment and
actual counts belong in `specification.json`.

Development and test use different lexical rendering families, with no shared
cohort entities or documents between worlds. All documents are present in the
retrieval corpus: holding out a world from configuration selection does not
remove its supporting evidence from retrieval. This is a predefined synthetic
rendering shift, not evidence of transfer to an independent real domain. The
shared scenario rules and generator still delimit the evaluation population.

## Data boundary and expected files

Generated data live under `experiments/simulation/data/pilot_v2/`:

- `corpus.jsonl` contains `chunk_id`, `url`, and `text`. Identifiers are opaque;
  kinds and fact IDs are not rendered into the text. Version and source
  information needed to interpret a claim is present in the text itself.
- `questions.jsonl` contains the question plus IDs, split, policy, scenario,
  designated URLs, and construction metadata. **Only the question text is a
  model input.** The metadata supports grouping and evaluation.
- `oracle.jsonl` is evaluator-only. For each question it contains required fact
  IDs, allowed URL prefixes, and exact character spans for valid, contradictory,
  or obsolete claims. Every complete span includes the relevant subject,
  context, value, and version. Several spans may support the same fact.
- `specification.json` records the frozen design, seed, counts, assignments,
  rendering choices, and data provenance.

The model backend must whitelist `question` and document `text` when constructing
inputs. It must not serialize entire question records or read oracle fields into
model prompts, embeddings, candidate scores, source bonuses, or ranking decisions.
An explicit source requirement written in a constrained question is legitimate
input; its gold URL and oracle admissibility labels are not. Tests should inspect
the actual model-input construction, not rely on filenames to prevent leakage.

Simulation runs use the separate output directory
`experiments/runs/simulation_pilot_v2/`; evaluator outputs go to
`experiments/simulation/results/pilot_v2/`. Expected artifacts include a run manifest,
completion status, per-task and per-configuration metrics, stage traces and
scores, actual delivered token streams, frozen selector decisions, ties,
held-out contrasts and intervals, and development selection frequencies. The
evaluator writes `per_record.csv`, `summary.csv`, `selection.json`,
`budget_feasibility.json`, and `status.json`. A smoke
run uses a different directory and cannot be substituted for the full experiment.

## Measurements from delivered content

The evaluator uses the pinned budget tokenizer's offset mapping against the
original chunk text. A fact counts only when at least one **complete valid claim
span** survives in the actual delivered token prefix. Merely retaining a chunk,
its URL, or the start of a proposition does not establish support. Duplicate
spans do not earn repeated fact credit. Token normalization, whitespace, special
tokens, and final partial chunks must be handled by the same recorded token
convention used during packing.

The frozen endpoints are:

- `G_final`: at least one delivered token comes from a designated page, using
  the existing source-retention convention.
- `U_sim`: every required fact has a complete delivered valid-support span.
  This is binary **simulator-defined complete fact coverage**.
- Coverage fraction: the proportion of distinct required facts with valid
  delivered support.
- Contradiction and obsolete exposure: separately recorded complete delivered
  spans with those statuses. Valid coverage can coexist with these exposures;
  `U_sim=1` does not silently resolve a conflict.
- Source-admissible complete coverage for constrained tasks: each required fact
  has delivered valid support from an allowed source.
- `C_sim` for constrained tasks: the delivered context is nonempty and every
  delivered chunk URL satisfies the predefined source policy. An uninformative
  chunk from a disallowed source still violates this particular all-chunks rule.

`U_sim` is not the paper's human-adjudicated ordinal sufficiency label. It does
not measure whether a person could safely interpret conflicting information,
whether a clinician would find the package sufficient, or whether a generated
answer uses the evidence. There is no answer generator or answer-quality `A`
endpoint in this pilot. Oracle labels remain explicitly synthetic and must be
rejected by the human-only E2 validation gate.

## Models and frozen configuration selection

The backend reuses the existing 20 configurations and pinned model/tokenizer
revisions: BGE-small-en-v1.5 retrieval; no re-ranker or BGE-reranker-v2-m3;
candidate depth 16 or 64; cap disabled, before re-ranking, or afterward; and
evidence budgets 512 or 2,048. With no re-ranker, pre- and post-cap are equivalent
and only one is evaluated. Rankings and cross-encoder scores are computed by
the models, not supplied by the oracle. Preserve full stage IDs and token
streams. The original oncology runner and historical run identities remain
unchanged.

The **primary endpoint** is open-evidence selection at 512 tokens. Among its ten
configurations, select one by mean development `G_final` and one by mean
development `U_sim`, with equal weight per information need. Report all tied
maxima. Both selectors use the same frozen structural tie rule, ascending by:
no re-ranker before re-ranker; pool; cap order `off`, `pre`, `post`; then
configuration ID. This rule does not use measured latency or test performance.

Freeze both choices before evaluating the 40 test worlds. The test contrast is
the mean `U_sim` of the development-U-selected configuration minus that of the
development-G-selected configuration. Report the choices, their test scores,
the paired difference, and a group-bootstrap percentile 95% interval from 5,000
draws with seed 20260928. This interval describes the fixed selected pair on
resampled test worlds. Development-bootstrap selection frequencies are a
separate stability analysis; they do not turn that interval into an estimate
covering every source of selection uncertainty.

The 2,048-token contrast is exploratory. Constrained-task `U_sim`, admissible
coverage, and `C_sim` are descriptive: this pilot does not implement or claim a
source-feasible selector. Report scenario counts and results to expose
heterogeneity, without searching for a favorable scenario after seeing the
aggregate outcome. A zero or reversed primary contrast is a valid result.

## Command interfaces

Run from the repository root in the Pixi environment. The committed task
definitions use the frozen default paths and model revisions:

```text
pixi run --locked sim-generate
pixi run --locked -e gpu sim-run
pixi run --locked -e gpu sim-evaluate
```

The evaluator needs no GPU inference, but uses the `gpu` environment because it
contains `transformers` and the pinned BERT tokenizer needed for exact offset
mapping. The default environment does not provide that tokenizer dependency.

The underlying module entry points are below. The defaults select the frozen
version 2 paths; `--help` lists explicit path overrides.

```text
pixi run --locked python -m experiments.simulation.generate --help
pixi run --locked -e gpu python -m experiments.simulation.backend --help
pixi run --locked -e gpu python -m experiments.simulation.evaluate --help

pixi run --locked python -m experiments.simulation.generate
pixi run --locked -e gpu python -m experiments.simulation.backend --device cuda --rerank-batch-size 8
pixi run --locked -e gpu python -m experiments.simulation.evaluate
```

The generator uses seed 20260928 and the frozen `pilot_v2` specification. Model
execution uses the existing SHA-pinned revisions and records code/input hashes.
Evaluation reads the complete run's delivered prefixes; it must not perform new
retrieval or replace missing model outputs with oracle rankings. Before using
results, validate split separation, available support, exact spans, truncation,
alternative support, duplicate handling, obsolete and contradictory exposure,
and rejection by the human-only gate. Preserve unsuccessful run status instead
of treating partial output as a completed benchmark.

## Relation to prior evaluation work and limits

[ARES](https://aclanthology.org/2024.naacl-long.20/) trains lightweight evaluation
models using synthetic training examples and combines their predictions with a
small human-annotated set through prediction-powered inference. It evaluates
context relevance, answer faithfulness, and answer relevance. Our deterministic
span oracle does not reproduce that calibration procedure or remove its need
for human evidence.

[RGB](https://arxiv.org/abs/2309.01431) organizes an English/Chinese RAG benchmark
around noise robustness, negative rejection, information integration, and
counterfactual robustness, evaluating the behavior of language models using
retrieved information. It supplies context for controlled stress testing; this
retrieval-only pilot is neither an implementation of RGB nor an empirical
comparison against its systems. Controlled testbeds and synthetic evaluation
are existing approaches, not novelty claims made by this artifact.

The pilot can identify selection effects within its frozen worlds and verify
that those effects depend on delivered content rather than URL identity alone.
Its main validity risks are correlated templates, source cues that simplify
retrieval, a small development split with many tied configurations, span-oracle
bugs shared with the renderer, and synthetic assumptions about what counts as
a fact. Distinct held-out entities do not eliminate those risks. Inspecting
generated examples and testing the oracle establish internal consistency, not
human or clinical validity. Any later claim about real evidence usefulness,
medical safety, or general RAG behavior requires the corresponding independent
real-world evidence.
