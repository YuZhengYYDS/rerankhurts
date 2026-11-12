# Completed 60-world human reviews

Two rounds of human semantic review, [A](WORLD_REVIEW_RESULTS_A.md) and
[B](WORLD_REVIEW_RESULTS_B.md), are complete for the same 60-world sample.
Each covers 120 paired questions, 183 required facts and four dimensions per world.
The [completion record](completion.json) links the sampled worlds and both review files.

The evidence indexes contain 361 and 501 citations, respectively. Verification
checks world membership, paired question/collection IDs, required facts,
claim bindings, character spans, URLs and quoted source text. QA quotations
allow whitespace normalization when a source newline is displayed as a space.

```bash
python scripts/check_world_review_records.py --output build/verification/world_reviews.json
```
