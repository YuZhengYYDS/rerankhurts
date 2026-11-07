# Matched 2048-token answer follow-up

`raw/` contains the recovered original 240 response JSON files, frozen manifest,
completed status, prepared evidence and source-run verification records. `results/`
contains the published per-answer scores, summaries and world-paired contrasts.
These cover exactly the original answer study's 120 questions from 60 test worlds,
comparing uncapped M3 and post-cap2 M3 at 2048 tokens.

Run the standard-library check from the repository root:

```bash
python experiments/supplements/answers_2048_120_v1/verify.py
```

It validates all 240 recorded response hashes, embedded message/token hashes,
sample membership, saved per-answer endpoints and endpoint summary means. No model
is loaded. Statistical interval settings and results remain in the saved analysis
manifest and contrast tables.

The recovered inference and analysis implementations are at
`experiments/strengthening/downstream_2048.py` and `analyze_answers_2048.py`.
Their bytes retain the recorded source hashes. The inference implementation uses
Linux `fcntl` locking. Its original protection snapshot expects the pre-migration root `MANIFEST.json`
and original delivery layout; this source is retained to document that execution,
not substituted for the current offline verification command. A neural rerun must
use the recorded original snapshot and separate outputs, never the shipped
`raw/` directory. The original implementation and test are retained, with the
test skipped on platforms that lack `fcntl`. The standard-library verification
above runs on Windows and Linux.
