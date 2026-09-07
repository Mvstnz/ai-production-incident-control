# Implementation progress

Authoritative handoff: CODEX_BUILD_SPEC.md v1.1, M0–M7 and AC01–AC36. Branch main. Public GitHub publication is explicitly authorized and in progress.

| Milestone | Status | Observed gate |
|---|---|---|
| M0 Discovery & Contracts | IMPLEMENTED / LOCAL_TESTED | Full specification and ADRs read; contracts fixed; actual MCP discovery and own target probe readback. Target execution blocked. |
| M1 Infrastructure & Domain | LOCAL_TESTED | Real PostgreSQL, separate databases/roles, persistent Compose stack, 100 domain tests and 30 API integration tests. Repeat bootstrap preserves all observed identities and secrets. |
| M2 Intake → Assessment | LOCAL_TESTED | Published local n8n intake, correlation, impact and plan stages; actual Hero/split/dedup execution evidence. |
| M3 Approval → Action → Recovery | LOCAL_TESTED | Exact approvals, roles, UNKNOWN_OUTCOME, real 429/503 and four-attempt DLQ passed. Actual signed Wait restart, offline approval/outbox persistence and database outage/redelivery passed. Resilience suite: 10/10. |
| M4 Complete Use Cases | LOCAL_TESTED | Supplier88/69, machine52 with approved reschedule, quality hard override with approved synthetic block. |
| M5 Product Demo | LOCAL_TESTED | Four real API-backed views; guided Hero and approval delivered once. Viewer isolation, scope reload, mobile Enter/Escape/focus and desktop layout passed. Actual dashboard action matches n8n execution 670. |
| M6 Connected Sandbox | BLOCKED | Ten target workflows created and read back. Zero target execution IDs. Update/execute gate, target HTTPS endpoints and four credentials remain missing. |
| M7 Quality & Portfolio | LOCAL_TESTED / CI PENDING | 50 fixture evaluation cases; live NOT_RUN. Sanitized runtime exports, screenshots, test evidence, README, handover and actual repeat bootstrap complete. Public source publication and fresh GitHub CI verification are the final steps. |

Evidence locations: evidence/workflow-runs/local-e2e.json, resilience.json, target-deployment.json; evidence/test-results/domain.txt; docs/implementation/backend-verification.md. Original failures are preserved. No unexecuted test is passed. Final criterion status is maintained in acceptance/acceptance-matrix.json.
