# Original Oncology execution source

These are the unchanged preparation, supplementary inference, full scoring and
delivery scripts from `oncology_coverage_run_20261103`, with the copied original
factorial backend/protocol. They retain original absolute server paths and runtime
assumptions as execution provenance; they are not the portable entry points.

For repository-relative verification, use `../verify_tokenizer_intervals.py` with
the pinned local tokenizer, then `../rescore.py`. The first reconstructs exact
token-prefix character bounds and the second recomputes annotated coverage. The
original source snapshot shows the full source-run sequence, including unknown-token
checks and grouped bootstrap analysis. No neural inference is required for either
current verification command.
