# Artifact versions

The [current main archive](https://github.com/YuZhengYYDS/rerankhurts/archive/refs/heads/main.zip)
contains the delivered code, data, recorded results and completed reviews:

- [60-world human review A/B and completion record](../experiments/strengthening/data/strengthening_v1/audit/reviews/).
- [Oncology expert judgments](../experiments/supplements/oncology_coverage_v1/reviews/).
- [Oncology facts, evidence and coverage results](../experiments/supplements/oncology_coverage_v1/).
- [Stage reanalysis](../experiments/supplements/stage_reanalysis_v1/) and [packing reanalysis](../experiments/supplements/packing_reanalysis_v1/).

The current inventory is [metadata/MANIFEST.json](../metadata/MANIFEST.json).
Run the commands in [VALIDATION.md](../docs/VALIDATION.md) after extraction.

The release tags `icde2027-strengthening-20261002` and
`icde2027-restructured-20261013`, and the `20260928/` archives, preserve their
original dated deliverables. These dates identify experiment and release versions.
The 60-world human audit and Oncology expert annotation were completed before
the ICDE paper submission; the completion records are linked above.
Recorded strengthening code and input identities are preserved in the
[historical snapshot](../archive/strengthening_recorded_inputs/).
