# Recorded strengthening inputs and source

These three files preserve the exact specification, study plan and audit source
used by the recorded inference and scoring identities. Their state fields describe
the time of that recorded run. Current review status is recorded separately:

The completed 60-world human review is documented in the linked completion record.
The snapshots describe the earlier inference run.

- [Completed 60-world A/B human review](../../experiments/strengthening/data/strengthening_v1/audit/reviews/completion.json).
- [Completed Oncology expert review](../../experiments/supplements/oncology_coverage_v1/reviews/).

The maintained study plan and dataset specification link the completed review.
The integrity checker resolves historical hashes to these unchanged bytes and
checks that the current specification differs only in review metadata.
The maintained audit command writes only to new output directories.
