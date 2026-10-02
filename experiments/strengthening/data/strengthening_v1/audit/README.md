# Human audit packet: source locations and pending review

This packet contains 60 latent worlds with both paired collections and blank reviewer slots A/B. Selection used generation seed, rendering family, and scenario, without model configurations, predictions, or outcomes. **No human opinions have been supplied and no human review is complete.** `report.json` and `claims_reparsed.jsonl` are automatic parser outputs, not reviewer judgments.

Keep this directory with its parent dataset directory. The files needed for review are:

- [human_audit_packet.jsonl](human_audit_packet.jsonl): sampled world IDs, both question/collection IDs, full dated fact tables, and pending status.
- [human_audit_template.csv](human_audit_template.csv): two empty reviewer records per sampled world.
- [../corpus.jsonl](../corpus.jsonl): actual original document text and URLs. Repository-relative path: `experiments/strengthening/data/strengthening_v1/corpus.jsonl`.
- [../questions.jsonl](../questions.jsonl): questions and explicit allowed source prefixes. Repository-relative path: `experiments/strengthening/data/strengthening_v1/questions.jsonl`.
- [../truth.jsonl](../truth.jsonl): all world fact tables; each packet entry already includes its relevant table.
- [../specification.json](../specification.json): frozen file hashes and design.

The packet's `documents_file` value `../corpus.jsonl` is relative to this `audit/` directory, not the repository root or the reviewer's working directory. For each packet row, select corpus rows whose `collection_id` occurs in that row's `collection_ids`; each collection has 80 ordered chunks. Select the two question rows by `qids`. Do not substitute excerpts from model traces for the original corpus.

Reviewers should work independently and record their own `reviewer_id`, judgments, comments, and completion time in separate copies of the template. Check whether text agrees with the fact table, whether marked assertions fully bind subject/revision/predicate/value, whether obsolete versus current conflicting assertions are distinguishable, and whether explicit source policy matches URL hosts. In QA renderings, the full assertion includes both question and answer; a nearby entity header or isolated answer cannot replace the required binding. Inspect both variants to confirm unchanged ordered text and source hosts despite URL grouping changes. Record missing, ambiguous, or unexpected assertions as problems rather than forcing agreement with the automatic parser.

The task is a data-semantic audit, not an assessment of model success. Keep model outcomes and configuration identities hidden during independent review. After both genuine reviews are available, preserve the original opinions and document any adjudication separately. Do not fill blank reviewer cells with automatic checks or claim inter-reviewer agreement from uncompleted forms.
