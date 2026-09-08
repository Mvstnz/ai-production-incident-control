# Current test report

Only current ordinary manufacturing examples are represented. Missing runs are not inferred.

| Check | Observed result |
| --- | --- |
| Unit tests | 112 tests; 0 failures; 0 errors |
| PostgreSQL API | 34 passed, 2 warnings in 44.77s |
| local-e2e | 10/10 passed |
| resilience | 10/10 passed |
| acceptance-ordering | 2/2 passed |
| rebootstrap | PASS |
| shared-showcase | PASS |
| secret-scan | PASS |
| browser | PASS |
| github-ci | PASS |
| hosted-demo | TARGET_TESTED |
| hosted-actions | TARGET_TESTED |

Hosted action execution IDs: 90, 109, 105, 98, 111, 107.

Live model evaluation: NOT_RUN; zero calls in the 50-case deterministic fixture evaluation. Email effects are captured in PostgreSQL or local Mailpit. See [hosting](hosting.md) for commands, workflow IDs, access, service limits and rollback boundaries.
