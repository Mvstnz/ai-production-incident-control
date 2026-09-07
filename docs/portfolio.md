# Portfolio narrative

AI Production Incident Control demonstrates a controlled response to synthetic
manufacturing incidents. An incoming supplier message, machine report or quality
form becomes a verified fact revision, a reproducible impact assessment, a
human-approved response and an auditable action trail.

The useful product outcome is traceability: an operator can see which facts
were supplied, which ERP relationships support them, how the incident worsens
the original plan and exactly what a manager is approving. The system does not
claim real customers, production deployment, proven financial savings or
statistical risk prediction.

## Demonstration storyline

1. Open a synthetic Supplier Delay run. The source explicitly offers an early
   partial delivery without confirming it. Show that the assessment preserves
   the confirmed baseline and displays the offer separately.
2. Inspect the result: 38 units of requirement, 14 available units and 24 units
   short at need; three production orders reviewed, two additionally affected.
   The unique affected open positions total EUR 126,400. The versioned demo
   policy calculates 88 / CRITICAL.
3. Inspect the six risk factors and original-versus-revised completion times.
   Explain that open-order exposure is not predicted lost revenue.
4. Open the exact supplier email approval. The recipient, subject, body,
   revision and plan hash are visible before decision. A production manager
   approves the CRITICAL response; viewer access cannot substitute for a role.
5. Inspect the actual local adapter result and workflow execution reference.
   The incident remains monitoring after the mail, because supplier contact
   does not establish material receipt.
6. Submit the confirmed 10-plus-30 revision. Total supply stays 40. Shortage
   becomes 14; only one production order remains affected, for EUR 54,400 and
   69 / HIGH. Explain why older unexecuted approvals cannot authorize this
   changed plan.
7. Show the machine fixture's measured 8/16-hour gap and qualified alternative,
   then the quality fixture's verified inspection/lot/shipment trace and
   manager-approved synthetic block. Do not imply either proposal acts on real
   equipment or performs a recall.

Only demonstrate steps for which the current acceptance report records an
observed result. If a workflow, approval race, adapter or screen has not run,
identify that status plainly instead of presenting planned behavior as a live
success. Use genuine application and canvas screenshots from the evidence
directory; never replace missing execution evidence with a drawn mockup.

## Interview explanation

**Why n8n?** The visible workflow describes the orchestration boundaries,
branching, approval wait and recovery process. It makes integration behavior
inspectable. The backend owns atomic transactions and reusable business rules
because those require concurrency protection and focused tests.

**Why keep AI out of scoring?** A language model can assist interpretation and
writing, while dates, quantities, financial totals and severity need source
evidence and deterministic rules. The demo provider is explicitly simulated AI;
the recorded fixture evaluation is not a live-model quality claim.

**How are duplicate effects controlled?** The database persists transport and
business identities, plan versions, action keys and receipts. The worker
revalidates current approval before dispatch. Unknown write outcomes stop for
reconciliation. This avoids pretending a content hash alone guarantees exactly
one email under every provider failure.

**Why these scores?** They are versioned demonstration priorities. The factor
thresholds are business assumptions, with boundary tests, rather than empirical
probabilities. The Hero and machine examples exercise the same policy without
hardcoded final scores.

**What changes for a real ERP?** Replace synthetic snapshot/command adapters with
authorized integration contracts, map genuine resource and calendar semantics,
verify provider idempotency and reconciliation, and validate security,
operations and approval policy with the responsible organization. Existing
credentials do not themselves authorize production writes or external messages.

## Authorship and evidence

This implementation was developed with AI assistance. The portfolio should
explain the chosen domain model, orchestration/state split, approval protocol and
failure tradeoffs transparently; it should not claim unaided authorship.
n8n, FastAPI, PostgreSQL, React and other dependencies retain their own authorship
and licenses.

[Architecture](architecture.md), [data model](data-model.md),
[security controls](security.md) and [limitations](limitations.md) provide the
supporting technical explanation. [Domain tests](../evidence/test-results/domain.txt)
and [evaluation evidence](../evidence/evaluations/README.md) contain bounded local
results. Workflow manifests and observed execution evidence determine what can
be called locally or target tested; the target connector/network blockers remain
visible.
