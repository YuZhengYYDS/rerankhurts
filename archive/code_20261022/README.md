# Original E0 source inputs (2026-10-22)

These five files preserve the exact bytes previously stored at the repository
root. They are source snapshots for the historical E0 audit:

- `generate_normalized_questions.py`
- `paper_support_analysis.py`
- `run_rag_eval.py`
- `score_retrieval.py`
- `summarize_supplement_results.py`

The historical `validation/results/input_manifest.json` still names their old
root paths and original SHA-256 values. `scripts/check_frozen_files.py` resolves
only those five names to this directory and verifies the original bytes and
sizes. A missing or changed snapshot fails verification.

Run maintained versions under `legacy/` using `python -m legacy.<module>` from
the repository root, or the five `legacy-*` tasks documented in
`docs/CODE_GUIDE.md`. These snapshots are not executable entry points: their
original relative paths reflect the old flat layout.
