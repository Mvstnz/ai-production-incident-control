# Current test report

Only current ordinary manufacturing examples are represented. Missing runs are not inferred.

| Check | Observed result |
| --- | --- |
| Unit tests | 112 tests; 0 failures; 0 errors |
| PostgreSQL API | 34 passed, 2 warnings in 42.58s on the guided-dashboard update |
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
| hosted-gemini | PASS: one real model invocation; WF03 execution 120 |
| guided-dashboard | TypeScript/Vite build, German guided cases, public entry and mobile navigation passed |

Hosted action execution IDs: 90, 109, 105, 98, 111, 107.

Statistical live model evaluation: NOT_RUN; zero calls in the 50-case deterministic fixture evaluation. Separately, one [hosted live Gemini smoke run](../../evidence/workflow-runs/hosted-gemini.json) passed. [Current GitHub acceptance](https://github.com/Mvstnz/ai-production-incident-control/actions/runs/34223684112) passed for application commit 8520a59. Email effects are captured in PostgreSQL or local Mailpit. See [hosting](hosting.md) for commands, workflow IDs, access, service limits and rollback boundaries.
