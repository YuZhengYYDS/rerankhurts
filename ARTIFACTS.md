# Reproduction and artifact guide

This public repository provides the code, inputs, recorded traces and analysis outputs for the RAG evidence-delivery study. The paper itself is not distributed here. The study is an ICDE 2027 Experiment, Analysis, and Benchmark (EAB) submission; the venue requires all artifacts needed to reproduce its results. **The repository is not yet a complete independently auditable EAB package:** the authors report that two human reviewers completed the 60-world semantic audit, but their original reviewer records have not been supplied here. See [Remaining work](#remaining-work) before relying on this repository as a complete submission artifact.

## Material map

| Evidence or result | Inputs, code, and recorded outputs |
| --- | --- |
| Controlled 360-world benchmark and paired design | [Frozen data, truth and spans](experiments/strengthening/data/strengthening_v1/), [generator and independent audit](experiments/strengthening/), [study plan](experiments/strengthening/study_plan.json), [run traces](experiments/runs/strengthening_v1/) and [evaluation outputs](experiments/strengthening/results/strengthening_v1/). These contain 720 paired tasks and 89,280 configuration records. |
| Stage and packing comparisons | [Stage reanalysis](experiments/supplements/stage_reanalysis_v1/) and [packing reanalysis](experiments/supplements/packing_reanalysis_v1/), including scripts, matched summaries and case evidence. |
| Exploratory oncology annotated-support comparison | [Coverage package](experiments/supplements/oncology_coverage_v1/): revised questions, 377 required facts, source occurrences, delivered-interval maps, 155 trace references, saved results and offline rescorer. The 152 reused traces are in [the E3 run](experiments/runs/e3_m3/); the three new-question traces are in the package. The [corpus](data/oncology/corpus/corpus_chunks_v2.jsonl) contains 7,124 chunks. |
| 512-token answer and request-cost studies | [Recorded answers](experiments/strengthening/results/strengthening_v1/answers/) and [timing requests](experiments/strengthening/results/strengthening_v1/timing/), with manifests, configurations and summaries. |
| Matched 2048-token answer follow-up | [2048-token follow-up](experiments/supplements/answers_2048_120_v1/): 240 recorded response files for 120 tasks, saved evidence and verification; [generation](experiments/strengthening/downstream_2048.py) and [analysis](experiments/strengthening/analyze_answers_2048.py) source snapshots. |
| Pilot selection comparison | [Pilot outputs](experiments/simulation/results/pilot_v2/) and [simulation code and protocol](experiments/simulation/). |
| 60-world review material | [Audit packet and original template](experiments/strengthening/data/strengthening_v1/audit/); [two model-based reviews](experiments/strengthening/data/strengthening_v1/audit/reviews/) are included with their original source labels. **These are not the two human reviewers' original records.** |

The oncology annotation snapshot identifies Codex assistant as the annotation author and is marked `domain_adjudicated: false` and `clinical_gold_eligible: false`; seven questions explicitly carry pending domain-adjudication status. The authors subsequently reported that expert review has been completed, but the corresponding records are not yet in this repository. The snapshot must not be treated as independently verified expert-adjudicated clinical gold without those records. The [metadata update record](validation/oncology_metadata_update_20261107.json) documents removal of an older human-review status field; it does not itself establish expert review.

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

On 2026-11-10 these checks passed in local Python environments. They check file identities, trace membership, saved endpoints, support spans, transitions and/or model-review evidence bindings as described by each script. They **do not** rerun inference or establish that the human reviewers carried out the audit. Oncology rescoring uses saved tokenizer-to-original-text intervals; [an additional check](experiments/supplements/oncology_coverage_v1/README.md) can reconstruct those intervals with the pinned tokenizer snapshot. The oncology scorer reproduced 155 × 20 outcomes, 377 required facts and 1,241 source occurrences. The answer verifier checked 240 response hashes across 120 tasks.

## Re-execution and environment

The [strengthening guide](experiments/strengthening/README.md) describes model snapshots, data generation, retrieval, reranking, answer generation, timing and analysis commands. The [E3 guide](experiments/README.md) describes the source-retention run; the [2048-token guide](experiments/supplements/answers_2048_120_v1/README.md) distinguishes the recovered Linux execution snapshot from portable offline verification. `pixi.toml` and `pixi.lock` define the locked Windows/Linux environments; GPU inference, hardware-specific timing, model downloads and any original server-path assumptions are separate from the offline checks. We did not rerun neural models or validate a fresh locked environment for this update. Outputs from new runs must use separate directories rather than overwrite frozen records.

Original corpus and other third-party materials retain their own source terms; see [the oncology source metadata](data/oncology/sources/) and [LICENSE](LICENSE). Source provenance and exact model or tokenizer revisions are recorded in the respective frozen manifests. The oncology annotations were prepared with prior results known; they are not evidence of a blinded evaluation.

## Remaining work

1. Add the original records from both human reviewers and any adjudication for the 60-world semantic audit, and the oncology expert-review records reported by the authors. The authors' confirmation and the two model-based reviews must not be represented as original human reviewer forms. Correct manuscript claims if the underlying records cannot substantiate them.
2. Independently audit the complete package against every manuscript table, figure and result, including execution environments, model availability and third-party data reuse conditions. Existing checks above cover specific recorded outputs; they are not a proof that all results can be reproduced from scratch.
3. Historical documents and manifests may mention the removed manuscript or old private-delivery state. The current source-tree manifest is [metadata/MANIFEST.json](metadata/MANIFEST.json); frozen experiment manifests and logs retain their historical identities.

The repository is public, but the authors should verify the complete artifact and submit its public URL in CMT before the ICDE deadline. Do not claim the package is complete while required evidence is missing.
