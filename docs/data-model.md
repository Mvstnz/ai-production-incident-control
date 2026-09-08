# Data model

PostgreSQL stores all application business state. The application database has
`ops` and `erp` schemas; n8n uses a separate database and role. The application
never reads or patches n8n's internal tables. The actual migration is
[`001_initial.sql`](../database/migrations/001_initial.sql).

Internal entities use UUIDs. ERP business identifiers, such as `DEMO-PO-8264/10` and
`DEMO-SO-FRAME-42/20`, remain readable strings. A synthetic `scope_id` accompanies business
entities and composite foreign keys so that relationships do not silently cross
demo scopes. Users receive explicit scope memberships; membership and command
role are separate checks.

## Operations aggregates

| Aggregate | Persisted purpose and identity |
|---|---|
| `users`, `sessions`, `memberships`, `scopes` | Password hashes, hashed session/CSRF tokens, server-side roles, scope membership and business clock |
| `source_events` | Original synthetic envelope, authenticated integration context, payload hash and review state; unique scope/channel/account/source ID |
| `analysis_jobs` | One durable job per source, current step, four-attempt bound, due time, lease, claim token, execution/workflow references |
| `incidents` | Business object, active episode, current revision/status, severity and current assessment pointer |
| `incident_revisions`, `incident_sources` | Immutable normalized facts/evidence and source-to-revision relationships |
| `impact_assessments`, `incident_impacts` | Immutable snapshot-bound calculation and unique affected sales-line values |
| `risk_assessments` | Policy version and calculated factors, score or missing-data result |
| `action_plans`, `approvals`, `incident_actions` | Exact versioned plan/hash, per-role approval decisions and separately claimed action state |
| `outbox_events`, `wait_registrations` | Unique work/wakeup/SLA keys, delivery leases and internal n8n resume references |
| `provider_receipts`, `erp.command_receipts` | Evidence of sandbox effects, stable action identity and ERP payload hash |
| `audit_events`, `workflow_errors` | Append-only business history and redacted runtime/retry/dead-letter information |
| `digests`, `failures` | Scope/date/channel-unique reports and explicit synthetic failure injection |
| `evaluation_runs`, `evaluation_results` | Schema support for model/dataset run metadata; checked-in fixture evaluation currently writes versioned evidence files |

## Synthetic ERP aggregates

| Area | Tables |
|---|---|
| Procurement | suppliers, supplier materials, materials, purchase orders/items and revisioned supply schedules |
| Material coverage | inventory lots/reservations, production orders and material requirements |
| Capacity | machines, capabilities, capacity calendar and production operations |
| Customer impact | customers, sales orders/items and quantity-based production-to-sales allocations |
| Quality trace | shipments/items, lot allocations and verified inspections |
| Read/write evidence | immutable snapshots, approved command receipts and versioned synthetic fixture data |

The Mock ERP is deliberately a small simulator. Its snapshot builder combines
versioned seed data with selected current ERP rows; it is not a complete ERP
query or planning implementation. Snapshot metadata includes schema version,
snapshot ID, scope, ERP revision, incident type and analysis time. Detailed reads
require the snapshot ID. Snapshot creation uses a repeatable-read transaction;
domain validation rejects explicitly incomplete or mixed metadata.

Quality resolution uses a separate disposition record in the snapshot, preserving
the original failed inspection. `quality_dispositions` contains disposition ID,
lot, inspection, verified flag, result, evidence and decision time. Only a
verified `RELEASED` disposition tied to that inspection and lot, with released
inventory and no shipped allocation, demonstrates restored quality coverage.

## Separate state machines

An incident can be analyzing, awaiting approval, executing a response,
monitoring, in manual review, resolved or closed. Approval rejection and an
adapter error do not resolve the business incident.

Approvals have `PENDING`, `APPROVED`, `REJECTED`, `EXPIRED` and `SUPERSEDED` states.
Modification creates a new plan version rather than editing approved content.
Actions have their own readiness, in-progress, success, retry, failure,
cancellation and `UNKNOWN_OUTCOME` states. Jobs separately track pending,
running, retry-scheduled, successful and dead-letter work.

## Integrity and calculation conventions

- The active-incident index prevents duplicate active episodes for the same
  scope/type/business key. Transaction advisory locks serialize correlation.
- A deferred supply constraint checks that confirmed arrivals in a revision do
  not exceed the open PO quantity. A split replaces the original arrival.
- Snapshot, fact revision, impact and risk rows reject updates. Audit rejects
  updates and deletion, and the runtime role lacks those audit privileges.
- Scope foreign keys cover revision, source, impact, plan, approval and action
  relationships. Action and outbox keys provide persistent deduplication.
- Numeric resource quantities use fixed precision in SQL and Decimal in the
  engine. Financial values use integer cents. These are open-order values,
  never statistically predicted revenue loss.
- A production order may serve multiple sales positions, and a position may be
  supplied by multiple production orders. The domain supports explicit
  quantity-based mapping; the Hero fixture uses the simpler direct mapping.
- A sales position is affected when its modeled complete readiness is worsened
  by the incident and exceeds its customer due date. The full open position is
  counted once, including across multiple current incidents in the dashboard.

Database constraints, domain validation and server authorization have different
roles. Their existence is implementation evidence; concurrency, recovery and
scope-isolation pass claims require the corresponding observed integration tests.
