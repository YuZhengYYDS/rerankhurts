# Reproduction and artifact guide

This public repository provides the code, inputs, recorded traces and analysis outputs for the RAG evidence-delivery study. The paper itself is not distributed here. The study is an ICDE 2027 Experiment, Analysis, and Benchmark (EAB) submission; the venue requires all artifacts needed to reproduce its results. This public repository provides the code, inputs, recorded traces and analysis outputs for the RAG evidence-delivery study. The paper itself is not distributed here. The study is an ICDE 2027 Experiment, Analysis, and Benchmark (EAB) submission; the venue requires all artifacts needed to reproduce its results. 

## Material map

| Evidence or result | Inputs, code, and recorded outputs |
| --- | --- |
| Controlled 360-world benchmark and paired design | [Frozen data, truth and spans](experiments/strengthening/data/strengthening_v1/), [generator and independent audit](experiments/strengthening/), [study plan](experiments/strengthening/study_plan.json), [run traces](experiments/runs/strengthening_v1/) and [evaluation outputs](experiments/strengthening/results/strengthening_v1/). These contain 720 paired tasks and 89,280 configuration records. |
| Stage and packing comparisons | [Stage reanalysis](experiments/supplements/stage_reanalysis_v1/) and [packing reanalysis](experiments/supplements/packing_reanalysis_v1/), including scripts, matched summaries and case evidence. |
| Exploratory oncology annotated-support comparison | [Coverage package](experiments/supplements/oncology_coverage_v1/): revised questions, 377 required facts, source occurrences, delivered-interval maps, 155 trace references, saved results and offline rescorer. The 152 reused traces are in [the E3 run](experiments/runs/e3_m3/); the three new-question traces are in the package. The [corpus](data/oncology/corpus/corpus_chunks_v2.jsonl) contains 7,124 chunks. |
| 512-token answer and request-cost studies | [Recorded answers](experiments/strengthening/results/strengthening_v1/answers/) and [timing requests](experiments/strengthening/results/strengthening_v1/timing/), with manifests, configurations and summaries. |
| Matched 2048-token answer follow-up | [2048-token follow-up](experiments/supplements/answers_2048_120_v1/): 240 recorded response files for 120 tasks, saved evidence and verification; [generation](experiments/strengthening/downstream_2048.py) and [analysis](experiments/strengthening/analyze_answers_2048.py) source snapshots. |
| Pilot selection comparison | [Pilot outputs](experiments/simulation/results/pilot_v2/) and [simulation code and protocol](experiments/simulation/). |
| 60-world review material | [Audit packet and original template](experiments/strengthening/data/strengthening_v1/audit/); [two reviews](experiments/strengthening/data/strengthening_v1/audit/reviews/) are included with their original source labels.  |

The authors report that an oncology expert personally completed and confirmed all 377 judgments. An [English review workbook](experiments/supplements/oncology_coverage_v1/reviews/) is available.

The oncology comparison is exploratory: its [rubric freeze](experiments/supplements/oncology_coverage_v1/annotations/rubric_freeze.json) records that prior outputs were known and the analysis was not blinded or preregistered. Missing an annotated span does not prove that semantically equivalent support is absent elsewhere, and the results do not establish clinical generalization.

## Offline checks

From the repository root, Python 3 runs the following without loading or rerunning neural models. Reanalysis commands write to a new `build/` directory and refuse to overwrite existing output directories; specify a fresh `--output` path if necessary.

```bash
# Frozen-input and historical-run integrity.
python3 scripts/check_frozen_files.py
python3 validation/check_e3.py --run experiments/runs/e3_m3 --output build/verification/e3
python3 validation/audit_simulation_endpoint_pairs.py --output build/verification/simulation_endpoint_pairs.json
python3 -m rerankhuts strengthen-verify --require-complete

# Recompute or reconcile the saved comparisons.
python3 -m rerankhuts stage-reanalysis
python3 -m rerankhuts packing-reanalysis
python3 -m rerankhuts oncology-coverage
python3 experiments/supplements/answers_2048_120_v1/verify.py
python3 scripts/check_world_review_records.py --output build/verification/world_reviews.json
```

On 2026-11-10 these checks passed in local Python environments. They check file identities, trace membership, saved endpoints, support spans, transitions and/or review evidence as described by each script. They **do not** rerun inference. Oncology rescoring uses saved tokenizer-to-original-text intervals; [an additional check](experiments/supplements/oncology_coverage_v1/README.md) can reconstruct those intervals with the pinned tokenizer snapshot. The oncology scorer reproduced 155 × 20 outcomes, 377 required facts and 1,241 source occurrences. The answer verifier checked 240 response hashes across 120 tasks.

## Re-execution and environment

The [strengthening guide](experiments/strengthening/README.md) describes model snapshots, data generation, retrieval, reranking, answer generation, timing and analysis commands. The [E3 guide](experiments/README.md) describes the source-retention run; the [2048-token guide](experiments/supplements/answers_2048_120_v1/README.md) distinguishes the recovered Linux execution snapshot from portable offline verification. `pixi.toml` and `pixi.lock` define the locked Windows/Linux environments; GPU inference, hardware-specific timing, model downloads and any original server-path assumptions are separate from the offline checks. We did not rerun neural models or validate a fresh locked environment for this update. Outputs from new runs must use separate directories rather than overwrite frozen records.

Original corpus and other third-party materials retain their own source terms; see [the oncology source metadata](data/oncology/sources/) and [LICENSE](LICENSE). Source provenance and exact model or tokenizer revisions are recorded in the respective frozen manifests. The oncology annotations were prepared with prior results known; they are not evidence of a blinded evaluation.


The repository is public, but the authors should verify the complete artifact and submit its public URL in CMT before the ICDE deadline. Do not claim the package is complete while required evidence is missing.
