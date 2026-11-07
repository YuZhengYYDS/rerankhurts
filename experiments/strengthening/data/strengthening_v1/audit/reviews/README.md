# Saved dimension-level reviews

[Review A](WORLD_REVIEW_RESULTS_A.md) and [Review B](WORLD_REVIEW_RESULTS_B.md)
are the two supplied reviews of the same 60-world sample. Each covers
120 paired questions, 183 required facts and four dimensions per world. Their
source labels and contents are preserved unchanged.

The evidence indexes contain 361 and 501 citations, respectively. The review
verification script checks the sampled world IDs, paired question/collection IDs,
claim bindings, character spans, URLs and quoted text against the frozen dataset.
QA quotations may display a source newline as a space; verification allows only
whitespace normalization for this display change.

The separate author-confirmed human completion report is
[HUMAN_AUDIT_REPORT.md](../HUMAN_AUDIT_REPORT.md). These saved model-based records
are not identified as the original human reviewer forms.

```bash
python scripts/check_world_review_records.py --output build/verification/world_reviews.json
```
