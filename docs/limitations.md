# Limitations and acceptance boundaries

`CODEX_BUILD_SPEC.md` is the authoritative acceptance contract. An implementation
file is not a passed test. `IMPLEMENTED`, `LOCAL_TESTED`, `TARGET_TESTED`,
`BLOCKED` and `NOT_RUN` describe different evidence levels. Consult the current
acceptance matrix and `evidence/` for final scenario status; these notes do not
upgrade an unexecuted test.

## Connected sandbox

Vercel serves the dashboard and authenticated APIs; Supabase stores state in private schemas. All ten n8n cloud workflows are published. Three current examples and six approved actions were executed; see [hosting](implementation/hosting.md).

The n8n instance is a trial. Continued availability depends on that account. Hosted recovery uses immediate wakeups and an hourly fallback. There is no availability SLA.

## AI evaluation

**LIVE_EVAL_NOT_RUN**: the deployed configuration uses deterministic fixture extraction and zero model calls. The 50 frozen development/holdout cases measure those decisions, not general model accuracy. See [fixture evaluation](../evidence/evaluations/fixture-v2-report.json) for exact outcomes and denominators.

## Business-model scope

- Single-level material requirements, FIFO-style temporal backlog with explicit
  priority, and fixed calendar-day remaining lead time; no full BOM explosion,
  shift/holiday planning or general MRP/APS optimization.
- A qualified alternative is a verified proposal, not a reserved resource until
  an approved mock command executes. Whole operations are scheduled; arbitrary
  partial-operation splitting is not modeled.
- Full open sales-line values are counted when affected, once per unique line.
  These are exposure indicators, not estimated losses, saved money or causal
  predictions validated against real operations.
- ERP data is synthetic. The snapshot builder combines fixture baselines and
  selected current rows; it is not an SAP/Comarch adapter or a general ERP
  replication layer.
- Quality reports require verified inspection evidence. Blocking a shipment is
  not resolution. Already shipped lots go to escalation/review; the product does
  not perform recalls or replace safety systems.
- Resolution requires a verified reassessment and manager decision. The quality
  domain accepts a separate verified release disposition tied to the original
  inspection/lot, supported by nonempty evidence, a valid decision time and
  released inventory. Already shipped trace still requires review. This pure
  rule is unit-tested. The separate quality disposition and authorized ERP
  command are also exercised in the real PostgreSQL API suite; a connected
  production quality-release integration has not been tested.
- Demo scopes provide synthetic-run isolation, not a claim of fully hardened
  multi-tenant SaaS, SSO, authorization delegation or multi-region operations.

## Delivery and operations

There is no universal exactly-once guarantee. Local action keys and receipts
support idempotent effects, but an SMTP timeout after acceptance leaves an
unknown outcome. That state needs reconciliation; a message ID alone is not
provider-enforced idempotency. A notification or ticket never proves the
underlying incident was fixed.

Four automatic analysis attempts, leases, an outbox and recovery schedules are
implemented design mechanisms. Their restart/race behavior counts as passed
only when separately exercised. The n8n Wait clock is independent of the demo
business clock. Redis/queue mode is optional and not part of the demonstrated
base profile. Load testing, backup restoration, disaster
recovery, security certification and real-user production operation are outside
the current evidence.
