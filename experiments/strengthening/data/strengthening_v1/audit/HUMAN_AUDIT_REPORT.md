# 60-world Human Semantic Audit

Two human reviewers completed the semantic audit of the 60-world sample and both approved the reviewed annotations. The completion status and common approval outcome were confirmed by the author on 2026-11-06.

## Scope

| Item | Count |
| --- | ---: |
| Sampled worlds | 60 |
| Human reviewers | 2 |
| Paired question variants | 120 |
| Required facts in the sampled worlds | 183 |
| World-reviewer completion entries | 120 |

The reviewed world identifiers and paired collection identifiers are those in [human_audit_packet.jsonl](human_audit_packet.jsonl). Each world has two URL-grouping variants with the same ordered document texts.

## Audit criteria

The audit follows the four criteria of the original review template.

| Criterion | Material checked |
| --- | --- |
| Text and fact-table consistency | Questions and original document statements against the required facts and values. |
| Complete assertion spans | Subject, revision, predicate and value binding within the marked support intervals, including question and answer jointly for QA renderings. |
| Temporal and version status | Current, obsolete and contradictory assertions against the dated world facts. |
| Source policy | Explicit allowed-source rules and URL hosts for both paired variants. |

## Result

| Reviewer label | Worlds covered | Overall outcome |
| --- | ---: | --- |
| R1 | 60 | Approved |
| R2 | 60 | Approved |

The reported reviewer outcomes agree on acceptance of the reviewed annotations. R1 and R2 are anonymous labels used in this documentation.

## Record provenance

[human_audit_completed.csv](human_audit_completed.csv) is a completion register prepared from the author's confirmation. It expands the confirmed sample-wide completion and common approval outcome to the 60 world identifiers and two reviewer slots. The four criterion fields and actual completion dates are left empty because the original per-criterion forms and dates were not supplied with that confirmation. The confirmation date records when the completion was reported, rather than when the reviews took place. Original reviewer forms can be retained alongside this register.

The machine-readable completion event is recorded in [human_audit_completion.json](human_audit_completion.json). File identities for the frozen data and original review materials are recorded in [source_manifest.json](source_manifest.json).

## Saved detailed checks

The supplied dimension-level [review A/B records](reviews/README.md) are retained
separately with their original model-based source labels. Their world IDs, required
facts and source citations are checked against the frozen sample; they are not
identified as the original human reviewer forms.

## Source materials

- [Original audit packet](human_audit_packet.jsonl): the 60 sampled worlds, fact tables and paired question identifiers.
- [Original blank template](human_audit_template.csv): the original reviewer-slot layout and four audit criteria.
- [Original corpus](../corpus.jsonl), [questions](../questions.jsonl), [world truth](../truth.jsonl) and [frozen specification](../specification.json): the underlying repository dataset.

The sampling packet and blank template retain their original bytes. Pending fields in the sampling packet record its preparation-time state; the completion event above records the subsequently confirmed audit status. Historical experiment manifests retain their original execution-time status.
