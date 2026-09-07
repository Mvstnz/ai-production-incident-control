# Backend and PostgreSQL verification

Status: **LOCAL_TESTED**, synthetic data only. No target-n8n or live-LLM result is claimed by these API tests.

Run from the repository root:

```powershell
rtk proxy python -m backend.run_integration
```

The runner uses the existing project's PostgreSQL and Mailpit services, provisions the separate `apic_integration` PostgreSQL database idempotently, applies migrations, and runs API tests. Secrets stay in process environment. It does not enqueue work in the demo database or n8n. Its own test scopes have work and membership removed during teardown; append-only audit history and immutable snapshots remain. The default demonstration scope is not reset.

Observed result: **24 passed** in **34.71 seconds**, with two upstream TestClient deprecation warnings. Exact output: `api-integration-output.txt`.

The tested boundaries are FastAPI TestClient â†’ genuine PostgreSQL and ERP FastAPI TestClient â†’ genuine PostgreSQL. SMTP tests actually connect to Compose Mailpit. ERP-command tests call the genuine ERP API in process; they are not evidence of n8n execution. Runtime workflow tests and actual n8n execution IDs belong to the separate end-to-end report.

The suite verifies supplier baseline 24/88/CRITICAL and confirmed split 14/69/HIGH, immutable revision history, ten concurrent source duplicates, mail/form business deduplication, unknown/injection review, user/service separation, Origin/CSRF/rate limits, scope access and scoped foreign keys, stale/replayed/early/modified/rejected/expired approvals, approved SMTP dispatch without incident resolution, accepted-provider timeout without resend, four total retry attempts with Retry-After, digest/SLA uniqueness, machine/quality fixtures, unauthorized ERP rejection, approved rescheduling and quality blocking, separate Quality release approval and verified disposition before resolution, append-only audit, body/time validation, scoped reset, and database failure without false acceptance.

A runtime regression revealed that a generic n8n Error Trigger lost the ERP Retry-After response header. `/internal/jobs/context` now persists the genuine status and retry due time before propagating the HTTP error. A focused regression test confirms the 30-second provider delay and verifies that later generic error reporting cannot consume another attempt or shorten that delay. n8n still orchestrates the eventual retry.

The selected n8n version adds an opaque `signature` query parameter to Wait URLs. Registration accepts exactly that parameter, binds the path to the actual execution ID and configured origin, and rejects duplicate parameters, redirect parameters, fragments, userinfo and other paths. The signature remains internal. Recovery marks obsolete completed-plan wakeups delivered instead of leaving them pending indefinitely.

Database migrations include relational ERP entities, decimal quantities, integer cents, composite scope foreign keys, source and active-incident uniqueness, job/action leases, immutable snapshots/revisions/assessments/plan payloads, a transactional outbox, append-only audit triggers, confirmed-supply and reservation aggregate constraints. Bootstrap grants `apic_app` no ERP writes and no audit UPDATE/DELETE; `apic_erp` receives only its integration rights. The migration owner is used only by bootstrap/test setup. Parent runtime tests separately check the actual least-privilege service roles.

SLA policy is versioned in `config/sla-policy.v1.json`. Local follow-up uses Mondayâ€“Friday 08:00â€“17:00 Bangkok and omits public holidays. SLA reminders and action follow-ups become idempotent local sandbox-notification records. Scope clock advancement does not change n8n's real clock.

Quality release is a separate manager proposal (`POST /api/incidents/{id}/quality-release-plan`) followed by the normal exact-plan approval and ERP action path. The original failed inspection remains immutable. Resolution requires a current ERP revision with verified disposition or restored resource coverage; a sent message alone is insufficient.

Known boundaries: SMTP has no general exactly-once guarantee; uncertain acceptance remains `UNKNOWN_OUTCOME` and requires reconciliation. Local API tests use synthetic `api-test-*` workflow references, never fabricated n8n execution IDs. The process-local rate limiter is sufficient for the single-instance demo and is not a distributed limiter. The API has no real ERP/LLM/provider adapter enabled.

## Final acceptance edge suite

The final runner collects all of tests/integration. Actual result: 30 passed, 2 dependency deprecation warnings in 152.87 seconds against real isolated PostgreSQL. This includes precise ambiguous-PO/missing-year review, tampered-draft replacement, unverified-quality review, a calculated LOW external mail approval gate, and two-incident sales-value union. See api-integration-output.txt for every executed test name.
