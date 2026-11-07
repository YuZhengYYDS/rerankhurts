# Paired stage reanalysis

Run `python -m rerankhuts stage-reanalysis` from the repository root.
The analysis reads the frozen 89,280-row evaluated dataset, matches pre-cap2 and
post-cap2 within each question, and reproduces the saved transition table at
512 and 2048 tokens (600 tasks from 300 worlds per budget).

`results/paired_transition_summary.csv` separates packing-input support states
from final delivered support states. `case_evidence.json` records two execution
examples, each with four settings, exact original quotes and delivered intervals.
The script checks these against the original corpus and compressed traces.
Absolute paths in the historical export identify its original execution location;
the executable resolves current paths from the repository root and question ID.

The counts describe where support disappears. They do not independently assign
a unique upstream cause. No model is rerun and original files are unchanged.
See [the artifact guide](../../../docs/V25_ARTIFACT_GUIDE.md).
