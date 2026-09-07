# Limitations and acceptance boundaries

`CODEX_BUILD_SPEC.md` is the authoritative acceptance contract. An implementation
file is not a passed test. `IMPLEMENTED`, `LOCAL_TESTED`, `TARGET_TESTED`,
`BLOCKED` and `NOT_RUN` describe different evidence levels. Consult the current
acceptance matrix and `evidence/` for final scenario status; these notes do not
upgrade an unexecuted test.

## Connected sandbox blockers

The authorized n8n MCP endpoint is
`https://mvstnz1.app.n8n.cloud/mcp-server/http`. Connector discovery and creation
of the unpublished project probe `Fm2mFkzgF0jwFJEA` succeeded. All ten core
workflows were subsequently created and read back; their actual IDs and
inactive states are in [the inventory](implementation/workflow-inventory.md).
Automatic approval
review rejected execute and update operations with: `MCP tool call requires
approval, but approval policy is never`. This is a concrete tool-approval
restriction, not a successfully tested workflow or an inferred n8n permission.
No alternative transport is used to bypass that rejection.

The cloud instance cannot resolve local Compose names such as `ops-api` or
`mock-erp`. Target application execution requires an authorized reachable HTTPS
Operations/ERP route and purpose-specific credentials. No public tunnel,
firewall opening or paid infrastructure was created. The cloud instance's exact
release was not exposed by the discovered connector; local image versions do
not prove target compatibility.

Creation and graph readback do not satisfy the requirement for executed target workflows.
Local publication/import and local execution evidence must remain separate from
AC31 target acceptance.

## AI evaluation

`LIVE_EVAL_NOT_RUN`: no authorized configured live-model credential, model and
call/cost budget were available for the recorded evaluation. Real email and
Slack delivery are also untested and disabled.

The fixture evaluation has 50 frozen synthetic cases, 30 development and 20
holdout. It verifies deterministic normalization and safe review decisions, not
general free-text intelligence. Mandatory-review recall is 100% in the recorded
run, while automatic processing is 33.3% development and 40% holdout. Type
accuracy is 86.7% and 90%; the live-model 95% target is not demonstrated. The
full result includes denominators, field matches, latency and zero provider
calls in [evaluation evidence](../evidence/evaluations/README.md).

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
base profile. Public hosting, load testing, backup restoration, disaster
recovery, security certification and real-user production operation are outside
the current evidence.
