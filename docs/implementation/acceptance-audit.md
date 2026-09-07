# Acceptance evidence audit

Evidence reviewed on 7 September 2026 at approximately 12:19 UTC. This is a
read-only assessment of recorded results, not a new test run or an update of the
acceptance matrix. At this cutoff, `acceptance/acceptance-matrix.json` still has
the planning note and all 36 entries marked `NOT_RUN`, despite substantial newer
evidence. The final matrix needs reconciliation with that evidence.

The unit output records **100 passed in 0.27 seconds**. The API output records
**23 passed in 45.96 seconds**, with two upstream deprecation warnings. API tests
use genuine PostgreSQL and local Mailpit, but an in-process ERP TestClient; their
synthetic workflow references are not n8n execution IDs. The local runtime report
records ten successful cases with actual n8n references. The resilience report
has eight successful normal cases and a failed Wait-registration/restart case.
New tests described below are **NOT_RUN** until a subsequent output records them.

## Evidence index

| Label | Exact artifact / source |
|---|---|
| UNIT | [`evidence/test-results/domain.txt`](../../evidence/test-results/domain.txt), tests in [`tests/unit/test_domain.py`](../../tests/unit/test_domain.py) |
| API | [`api-integration-output.txt`](api-integration-output.txt), [`backend-verification.md`](backend-verification.md), tests in [`tests/integration/test_api.py`](../../tests/integration/test_api.py) |
| E2E | [`evidence/workflow-runs/local-e2e.json`](../../evidence/workflow-runs/local-e2e.json), assertions in [`scripts/test_runtime.py`](../../scripts/test_runtime.py) |
| RESILIENCE | [`evidence/workflow-runs/resilience.json`](../../evidence/workflow-runs/resilience.json), assertions in [`scripts/test_resilience.py`](../../scripts/test_resilience.py) |
| EVAL | [`evidence/evaluations/fixture-v1-report.json`](../../evidence/evaluations/fixture-v1-report.json) and frozen [`fixtures/evaluation-v1.json`](../../fixtures/evaluation-v1.json) |
| SCAN | [`evidence/test-results/secret-scan.json`](../../evidence/test-results/secret-scan.json), `files_checked: 214`, no findings in its stated scope |
| TARGET | [`evidence/workflow-runs/target-deployment.json`](../../evidence/workflow-runs/target-deployment.json), [`target-deployment.md`](target-deployment.md) |
| UI | Actual PNGs under [`evidence/screenshots`](../../evidence/screenshots), including overview, incident, approval, reliability, viewer and local n8n execution 11 |

`LOCAL_TESTED` below applies only to the described boundary. `PARTIAL` means a
relevant executed test exists but leaves part of the exact criterion unproved.
`NOT_RUN`, `FAILED` and `BLOCKED` are never acceptance passes. Target execution is
not inferred from local results.

## Criterion-by-criterion findings

| ID | Audited evidence level | Exact existing test / observation | Remaining gap at cutoff |
|---|---|---|---|
| AC01 | PARTIAL | E2E runs the current Compose stack, real PostgreSQL/APIs and published n8n. Local M0 probe executions `1`, `2` succeeded. | No recorded fresh isolated checkout/volume/bootstrap result. A planned GitHub CI job is not an executed first-start test. Root owns the pending clean-run evidence. |
| AC02 | PARTIAL | M0 probe retained the same `APICPROBE0000001` through reimport/restart; executions `1`, `2`. `scripts/test_rebootstrap.py` exists. | No recorded final full-stack second-bootstrap report at cutoff. Need ten workflow IDs, seeds, persistent secrets, jobs/actions and retained state compared before/after. Root owns this run. |
| AC03 | LOCAL_TESTED | UNIT `test_hero[scenario=0]`; API `test_supplier_baseline_split_and_immutable_history`; E2E `hero_baseline_and_proposed_partial`, execution `377`, shortage 24, value 12640000 cents, 88 CRITICAL. Runtime assertions include demand 38, available 14, reviewed 3, affected 2. | No gap in the recorded local Hero calculation. Target remains separate. |
| AC04 | LOCAL_TESTED | UNIT `test_unconfirmed_offer_is_separate_and_replaces_quantity`; E2E `hero_baseline_and_proposed_partial` verifies confirmed Hero totals while proposals/what-if remain present. EVAL case `APIC-EVAL-v1-01`. | No local domain gap; the what-if result is hypothetical and must not be counted in dashboard totals. |
| AC05 | LOCAL_TESTED | UNIT `test_hero[scenario=1]`, `test_unconfirmed_offer_is_separate_and_replaces_quantity`; API supplier baseline/split test; E2E `confirmed_split_replaces_supply_and_revises`, execution `388`, shortage 14, one affected MO, 5440000 cents, 69 HIGH. Unit asserts confirmed supply remains 40. | No gap in the recorded local split calculation. |
| AC06 | PARTIAL | API `test_concurrent_transport_deduplication`; E2E `parallel_deduplication_and_cross_channel_correlation`: ten requests, one source event/job, same incident revision; executions `392`, `397`, `414`. | Concurrent ingestion and correlation are proved. The concurrency case does not itself approve/dispatch and count provider effects; separate replay/delivery tests exercise effect deduplication. Avoid claiming the exact combined concurrent-delivery scenario ran. |
| AC07 | LOCAL_TESTED | API `test_mail_form_same_facts_links_source_without_revision`; UNIT `test_email_and_structured_facts_have_same_business_identity`; E2E `parallel_deduplication_and_cross_channel_correlation` records three linked sources and revision 1, including mail and form. | No local correlation gap. |
| AC08 | LOCAL_TESTED | API `test_supplier_baseline_split_and_immutable_history` asserts two revisions/plans and superseded old approvals. E2E split execution `388`; RESILIENCE stale-approval case exercises revision replacement. | No local revision-history gap. |
| AC09 | PARTIAL: exact UNIT/EVAL, general runtime review | UNIT `test_ambiguous_dates_are_review`; EVAL `APIC-EVAL-v1-08` returns a missing-year reason; `APIC-EVAL-v1-27` and `-50` return `Purchase-order item is ambiguous in ERP`. E2E `ambiguous_input_requires_clarification`, execution `442`, reviews unsupported free text. | Runtime case name is broader than its assertions: it does not set multiple ERP PO candidates or the exact missing-year schedule. New API edge tests cover those inputs but are NOT_RUN until recorded. |
| AC10 | LOCAL_TESTED | UNIT `test_own_reservation_is_protected_without_double_subtraction`, `test_lot_inventory_excludes_blocked_and_foreign_reservations`, parameterized inconsistency tests; API `test_own_inventory_reservation_is_preserved_in_snapshot`. | Own-reservation API and blocked-lot unit boundaries are covered; no dedicated n8n blocked-lot scenario recorded. |
| AC11 | PARTIAL | UNIT `test_sales_line_union_and_full_open_position_convention`, `test_non_one_to_one_production_sales_mapping`, `test_aggregate_rejects_conflict_and_scopes_excludes_history`. | API `test_digest_sla_and_current_value_dedup` creates only one incident; its name does not prove two current incidents share a sales position in dashboard aggregation. New actual two-incident API test is NOT_RUN. |
| AC12 | LOCAL_TESTED at API/fixture boundary | API `test_unknown_and_injection_are_manual_review`; UNIT `test_unknown_free_text_and_prompt_injection_never_automated`; EVAL `-13` and `-39` return prompt-injection review. | No live-model tool/recipient behavior is claimed. Recorded fixture/API path refuses processing. |
| AC13 | PARTIAL | UNIT `test_forged_draft_numbers_are_replaced_and_low_email_still_needs_approval` rejects `1000 units ... LOW` and returns grounded `88 / CRITICAL`. | This unit helper does not alone prove persistence and dispatch reject a tampered workflow draft. New API plan-gate/claim test is NOT_RUN; no live model was invoked. |
| AC14 | LOCAL_TESTED | API `test_approval_replay_stale_and_early_wait` returns 409 on second approval. E2E `approval_replay_early_decision_and_delivery` records approval replay 409, SMTP action execution `381`, one attempt, unchanged IDs/attempts/provider IDs after repeat recovery. | This is observed sandbox idempotency, not an exactly-once claim for arbitrary providers. |
| AC15 | PARTIAL | API `test_approval_replay_stale_and_early_wait` approves first, then registers a synthetic Wait URL and finds persisted APPROVED/wakeup. E2E delivery test succeeds. | E2E does not assert actual Wait-readiness ordering. The real Wait-registration/restart test currently fails; successful ordinary delivery must not stand in for the precise early-wakeup race. |
| AC16 | LOCAL_TESTED | API `test_reject_modify_expire_no_dispatch[REJECT/MODIFY/EXPIRE]`; RESILIENCE `rejected_plan_never_dispatches_supplier_email`, `modified_plan_requires_new_exact_approval`, `expired_plan_prevents_late_approval`. Modified exact mail executed at `503`; expired approval returns 409. | No local gap for the recorded rejection/modification/expiry cases. |
| AC17 | LOCAL_TESTED | RESILIENCE `superseded_approval_rejected_after_new_revision`, executions `517`, `521`, old approval HTTP 409 and old unexecuted actions cancelled; API revision-history/replay tests support it. | No local stale-approval gap. |
| AC18 | LOCAL_TESTED | API `test_auth_csrf_scope_and_mutated_roles`, `test_approval_replay_stale_and_early_wait`: viewer plus forged role denied, GET decision 405, repeated POST 409. E2E `runtime_auth_csrf_scope_boundaries` returns 403 for viewer. | Screenshot presence adds no missing authorization guarantee; server tests are the evidence. |
| AC19 | LOCAL_TESTED | API `test_unknown_outcome_ticket_effect_at_most_once`, `test_real_sandbox_smtp_success_and_unknown_outcome`; E2E `accepted_write_timeout_does_not_resend`, executions `449`, `450`, known provider IDs with UNKNOWN_OUTCOME and stable attempts after recovery. | No live external-provider reconciliation is claimed. |
| AC20 | LOCAL_TESTED | API `test_job_retry_four_attempts_retry_after_and_dlq`, `test_context_preserves_provider_retry_after_before_generic_error_trigger`; RESILIENCE 503 case ends DEAD_LETTER after four attempts (`545`, `556`, `569`, `617`), 429 case recovers (`679`, `720`). | Earlier failed attempts remain history; use the actual latest successful regression evidence, not source code alone. |
| AC21 | PARTIAL | API `test_database_failure_no_false_acceptance` injects a failing transaction function and observes 503 without source-event ID. | This is not a real database shutdown/restart/redelivery test. `database_outage_no_false_202_and_safe_redelivery` exists but no result at cutoff; API agent owns the disruptive runtime phase. |
| AC22 | FAILED / implementation under correction | RESILIENCE `registered_wait_and_committed_approval_outbox_survive_n8n_restart` records FAIL: `real Wait registration`, deadline exceeded, empty registrations. | No real Wait restart or committed-outbox restart pass can be claimed from this run; it failed before acquiring the required initial state. API agent owns correction/retest. |
| AC23 | LOCAL_TESTED | API `test_digest_sla_and_current_value_dedup`; RESILIENCE `SLA_stages_are_unique_and_never_auto_approve` records the same notification IDs after repeated recovery and no automatic approval, executions `638`, `655`. | No local repeated-stage gap. |
| AC24 | LOCAL_TESTED | UNIT `test_machine_gap_and_qualified_unreserved_alternative` plus invalid-alternative/calendar tests; API `test_machine_quality_and_privileged_erp_reject` and `test_authorized_erp_commands_and_separate_quality_disposition`; E2E `machine_approved_mock_erp_reschedule`, assessment `418`, reschedule `425`, score 52 HIGH. | Whole-operation synthetic scheduling only; no real machine control. |
| AC25 | LOCAL_TESTED | UNIT `test_verified_quality_trace_requires_manager_approval`; API quality/privileged-command tests; E2E `quality_trace_and_quality_manager_approval` asserts block WAITING_APPROVAL before decision, quality-manager approval, verified override and block execution `439` (assessment `434`). | No automatic block or recall is claimed. |
| AC26 | PARTIAL | UNIT `test_unverified_quality_is_urgent_review`; EVAL `-23`, `-24`, `-47` return urgent manual review rather than a fabricated failed inspection. | Exact unverified-inspection input has not traversed the API persisted-source/action gate in recorded output. New API edge test is NOT_RUN. |
| AC27 | LOCAL_TESTED | API `test_real_sandbox_smtp_success_and_unknown_outcome` asserts MONITORING after SMTP success; E2E delivery execution `381` records `incident_status: MONITORING`. | Sending is not resolution. Separate verified resolution/disposition has API evidence but is not needed to imply an automatic resolve. |
| AC28 | LOCAL_TESTED | API `test_digest_sla_and_current_value_dedup` compares full digest body to KPI. E2E `daily_digest_is_idempotent` returns the same digest ID/body twice and matching KPI value through published webhook. | Runtime report does not retain a WF10 execution ID in this case; API/HTTP result and persisted report ID are present. Do not invent an execution reference. |
| AC29 | LOCAL_TESTED | API `test_scoped_reset_keeps_other_scope_and_audit`; RESILIENCE `reset_only_changes_owned_synthetic_scope` compares a second scope's incident/revision/impact/sources unchanged. | No unrelated n8n resources are part of reset. Scope isolation is demonstrated; broader production reset behavior is outside scope. |
| AC30 | LOCAL_TESTED: bounded scan | SCAN reports PASS for 214 Git-eligible files, exact known local secrets and private-key markers, zero findings. | This is not a universal secret detector. Any later file change/publication needs a current scan, and image content needs the root's visual review. |
| AC31 | BLOCKED / target runtime NOT_RUN | TARGET records all ten created/read-back inactive workflows, zero execution IDs, no credentials bound. | Update/execute autoapproval restriction, authorized reachable HTTPS APIs, target credentials and current graph drift remain. Creation/readback is not target E2E acceptance. |
| AC32 | LOCAL_TESTED fixture report; LIVE NOT_RUN | EVAL records dataset hash/version 1.0, fixture-v1, extraction-v1.0, 30 development/20 holdout, all decision/field denominators, latency and zero provider calls. | Type accuracy is 26/30 and 18/20; automatic rates 10/30 and 8/20. No live-model quality gate is passed; `LIVE_EVAL_NOT_RUN` remains explicit. |
| AC33 | LOCAL_TESTED at domain/immutability boundary | UNIT `test_mixed_or_incomplete_snapshots` and invalid/missing-risk tests; API `test_immutable_snapshot_and_cross_scope_foreign_key`; EVAL `-26`, `-49` review mixed revisions. | No recorded dedicated malformed/mixed snapshot passed through the full n8n assessment-save boundary. Do not equate immutability alone with every inconsistent-data case. |
| AC34 | LOCAL_TESTED | API `test_auth_csrf_scope_and_mutated_roles`, `test_immutable_snapshot_and_cross_scope_foreign_key`, body-limit/rate-limit tests; E2E `runtime_auth_csrf_scope_boundaries`: missing CSRF and nonmember reads denied. | No distributed/production security certification is claimed. |
| AC35 | PARTIAL | UNIT `test_forged_draft_numbers_are_replaced_and_low_email_still_needs_approval` verifies purchasing remains required after the test changes risk to LOW. | That test does not calculate a genuine LOW incident or call server action claims. New API edge case calculates LOW from a tiny verified delay/exposure and must prove claim rejection before approval; currently NOT_RUN. |
| AC36 | PARTIAL / final browser check pending | UI artifacts show real dashboard screens and a real local n8n execution canvas. E2E APIs expose persisted execution IDs and assessment values. | Screenshots alone are not an asserted same-incident/same-revision UI-to-canvas reconciliation. Root owns the browser comparison, reload/mobile final check and final screenshot evidence. |

## Focused API tests added after the evidence cutoff

[`tests/integration/test_acceptance_edges.py`](../../tests/integration/test_acceptance_edges.py)
uses the existing explicit PostgreSQL setup/helpers, with its own synthetic scope
per case. The cases are:

- `test_ambiguous_po_position_or_missing_year_enters_persisted_review`: actual
  multiple PO positions or an incomplete schedule date, persisted review and no
  action/approval creation.
- `test_tampered_draft_is_replaced_before_plan_persistence_and_dispatch`: a false
  numeric draft and foreign recipient cannot escape the server's grounded plan;
  supplier claim remains denied before approval.
- `test_unverified_quality_has_no_incident_action_or_approval`: an unverified ERP
  inspection results in durable urgent review, without an invented block.
- `test_genuinely_computed_low_supplier_mail_still_cannot_dispatch_unapproved`:
  LOW is derived from verified small exposure, low shortage, a one-day change,
  remote demand and an available alternative; no score is manually substituted.
- `test_dashboard_unions_same_sales_position_across_two_current_incidents`:
  supplier and machine assessments share a genuine scoped sales position; the
  KPI is compared with the union rather than the sum of incident values.

These tests are authored but **NOT_RUN in this audit**. No runtime or integration
runner was started while another agent's database disruption tests were active.
The current `backend.run_integration` runner explicitly names `test_api.py`; the
root must include the new file or collect the whole `tests/integration` directory
for the final authorized run. Only then can recorded gaps be upgraded.

## Final verification after the audit cutoff

All six added API edge cases were actually executed by the final whole-directory runner: 30/30 integration tests passed, including AC09/11/13/26/35. The actual resilience suite now has 10/10 passes including database outage (AC21) and signed Wait/restart/offline approval-outbox persistence (AC22); original failures remain in history. The complete repeat bootstrap passed (AC02). The browser report asserts the same incident/action and real n8n execution670 (AC36), plus reload/keyboard corrections. The current acceptance matrix supersedes the cutoff statuses above. Fresh GitHub CI (AC01) remains pending publication; target AC31 remains blocked.
