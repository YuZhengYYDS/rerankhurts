# Protocol amendment log

## 2026-09-28 — pilot_v1 invalidated before outcome analysis

Independent semantic inspection found that the generated release-safeguard counterclaim did not necessarily negate the world's actual safeguard. A generic statement permitting release without an identity check or reviewer sign-off is not the logical opposite of every possible required workflow safeguard.

The two-question engineering smoke run had completed. A provisional full inference run was interrupted after six of 120 tasks, before inspecting selection outcomes or any comparative performance values. No outcome was used to change the data, scenarios, configuration set, split, endpoint or tie rule.

pilot_v2 corrects the affected statement to explicitly negate its world's actual safeguard. Dedicated tests and a second semantic review are required before executing it. The original frozen design in PROTOCOL.md still applies; paths named pilot_v1 in that original contract refer to the superseded provisional dataset. All delivered simulation results use pilot_v2. Invalid v1 data and partial traces are retained separately in local task scratch, excluded from the release, and must not be pooled with v2.

This is a validity correction, not an additional independent replication or a performance-based retry.
