# Matched 2048-token answer follow-up: English report

This companion summarizes the saved follow-up outputs without changing the original report or execution source. The experiment reuses the original 120 questions from 60 test worlds and compares uncapped M3 with post-cap2 M3 at a 2048-token evidence budget. Each condition has 120 actual responses.

## Saved endpoint means

| Condition | Complete correct | Complete grounded correct | Field accuracy | Grounded field accuracy |
| --- | ---: | ---: | ---: | ---: |
| m3_off_prefix | 26.67% | 11.67% | 47.36% | 22.92% |
| m3_post_prefix | 25.00% | 10.00% | 49.44% | 21.67% |

## World-paired contrasts

All differences are post-cap2 minus uncapped M3. Values below are percentage points; intervals are seed-stratified world bootstrap 95% intervals, not marginal error bars.

| Endpoint | Difference (pp) | 95% interval (pp) | BH-adjusted q |
| --- | ---: | --- | ---: |
| complete_correct | -1.67 | [-5.83, +2.50] | 0.690365 |
| complete_grounded_correct | -1.67 | [-4.17, +0.00] | 0.671233 |
| field_accuracy | +2.08 | [-2.22, +6.74] | 0.671233 |
| grounded_field_accuracy | -1.25 | [-4.31, +1.74] | 0.671233 |

The additional conditions do not increase the number of independent worlds. The original analysis specifies 5,000 bootstrap repetitions, 20,000 sign flips and BH adjustment within the four-endpoint follow-up family. The sign-flip assumption is exchangeability of world differences under the null, rather than randomized policy assignment.

## Provenance and verification

The original response JSON files, messages and token records are in `raw/responses/`. The raw manifest/status preserve the generation identity; `results/` contains the saved scored records and analysis tables. `python experiments/supplements/answers_2048_120_v1/verify.py` checks the 240 response hashes, frozen sample membership, message/token hashes, saved endpoints and summary means without loading a model.

The recovered execution source retains its original Linux locking and legacy protection-layout assumptions. Use the documented current offline verification for this repository layout. No new inference or answer scoring is introduced by this English companion.
