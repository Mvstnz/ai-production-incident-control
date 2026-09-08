# Restore the earlier dashboard — 2026-09-08

The user rejected the guided redesign. The dashboard directory is restored from
`187078aab29acd1083685b97ed9912420240b633`: sidebar navigation, KPI cards, incident
register and the earlier detail/approval views. Its ordinary steel-rod, band-saw
and mounting-plate labels are retained. Earlier reference products are not restored.

The supplier email now uses readable dates, short paragraphs and an ordinary
dispatch-team signature. It distinguishes the confirmed 75-rod delivery on
16 November from an unconfirmed offer of 30 rods on 11 November, leaving 45 for
the final delivery if accepted. November 2026 is the fixed fictional planning
period. Supplier reply drafts ask for confirmation without including internal
risk scores or customer-order values.

Gemini stays enabled through the existing authenticated example dialog. Its
credential, model, budget, verification and n8n workflows are unchanged. Public
visitors remain read-only. No external supplier email is sent.

Local verification: production build and 112 unit tests pass; all 34 PostgreSQL
API integration tests pass. All 50 deterministic regression decisions pass in
[dataset version 3](../../evidence/evaluations/fixture-v3-report.json). This wording
revision retains the previous split; it is not a new unseen holdout or a live
model evaluation. The restored overview was also inspected in the browser.

The guided-dashboard report and screenshots describe a superseded release.
LinkedIn remains unpublished while the user reviews the restored application.

Hosted verification: application `0f681d1` is live on deployment
`dpl_6N84zW9cgUvqMsxZYsJgAa6gYovf`. Only the shared synthetic showcase was reset
through its owner-authorized API after an ignored local backup. Its audit trail
and all private workspaces were preserved. Three replacement assessments passed
with scores 83, 62 and 70; the new source mail and supplier reply are stored in
the public case, with fresh approvals pending. [HTTPS checks](../../evidence/workflow-runs/hosted-demo.json).

A real Gemini run with the rewritten mail also passed: 40 missing rods, two
affected orders, EUR 55,400 and the partial shipment still PROPOSED. The final
analysis stage records cloud workflow WF05, execution `154`; this is not the
Gemini-node execution ID. [Persisted live result](../../evidence/workflow-runs/hosted-gemini-readable-mail.json).
The runtime reported four of twenty reservations used after this check.

The complete [GitHub acceptance run](https://github.com/Mvstnz/ai-production-incident-control/actions/runs/34228754578)
passed, including clean bootstrap, repeat bootstrap, integration and n8n runtime
checks. Screenshots: [restored overview](../../evidence/screenshots/restored/overview.jpg)
and [readable source email](../../evidence/screenshots/restored/supplier-email.jpg).

Recovery baseline: redeploy application commit `0f681d1` or promote the verified
Vercel deployment above. The restoration is a new commit on `main`; Git history
was not rewritten. No schema or workflow rollback is required.
