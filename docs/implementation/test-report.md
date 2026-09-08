# Executed test report

The matrix is an index of retained evidence. Fixture tests, local runtime and connected-cloud execution are separate. No unexecuted test is passed.

| Boundary | Actual result | Command / evidence |
|---|---|---|
| Pure domain | 108 passed | `rtk proxy python -m pytest tests/unit -q`; domain-junit.xml |
| Real PostgreSQL API integration | 34 passed, 2 dependency warnings in 47.93s | `rtk proxy python -m backend.run_integration`; api-integration-output.txt |
| Published local n8n E2E | 10/10 passed after final redeploy | `rtk proxy python -X utf8 scripts/test_runtime.py` |
| Exact concurrent delivery / early approval ordering | 2/2 passed locally; actual Mailpit capture counted after repeated recovery | `rtk proxy python -X utf8 scripts/test_acceptance_ordering.py`; acceptance-ordering.json |
| Actual runtime resilience | 10/10 passed, earlier failures retained | `rtk proxy python -X utf8 scripts/test_resilience.py --phase normal`; disruptive phases below |
| Repeat full bootstrap | Passed, identities and secrets preserved | `rtk proxy python scripts/test_rebootstrap.py` |
| Shared viewer showcase | Three actual incident types; repeated seeding preserves IDs; viewer mutation 403 | `rtk proxy python scripts/test_showcase.py`; evidence/test-results/shared-showcase.json |
| Frontend build / typecheck | Passed | `rtk npm run build` |
| Real browser | Four views, exact approval, role/scope checks, responsive keyboard and same execution verified | evidence/test-results/browser.json |
| Fixture evaluation | 50 cases; 30 development / 20 holdout | evidence/evaluations/fixture-v1-report.json |
| Live LLM | NOT_RUN, zero calls/cost | Missing configured model/credential/call budget |
| Target cloud n8n | 10 created/read back, 0 executions | BLOCKED; target-deployment.json |

Fresh GitHub CI: PASS

## Recorded local execution IDs

| Scenario | Status | Recorded execution IDs |
|---|---|---|
| hero_baseline_and_proposed_partial | PASS | 1259 |
| approval_replay_early_decision_and_delivery | PASS | 1272, 1273 |
| confirmed_split_replaces_supply_and_revises | PASS | 1259, 1279 |
| parallel_deduplication_and_cross_channel_correlation | PASS | 1283, 1288, 1305 |
| machine_approved_mock_erp_reschedule | PASS | 1309, 1316, 1317 |
| quality_trace_and_quality_manager_approval | PASS | 1323, 1326, 1327 |
| ambiguous_input_requires_clarification | PASS | 1331 |
| accepted_write_timeout_does_not_resend | PASS | 1338, 1339 |
| daily_digest_is_idempotent | PASS | Not retained in this case; HTTP/persisted-result evidence only |
| runtime_auth_csrf_scope_boundaries | PASS | Not retained in this case; HTTP/persisted-result evidence only |
| rejected_plan_never_dispatches_supplier_email | PASS | 480, 490 |
| modified_plan_requires_new_exact_approval | PASS | 499, 502, 503 |
| expired_plan_prevents_late_approval | PASS | 509, 512 |
| superseded_approval_rejected_after_new_revision | PASS | 517, 521 |
| ERP_503_stops_after_four_attempts_in_DLQ | PASS | 545, 556, 569, 617 |
| SLA_stages_are_unique_and_never_auto_approve | PASS | 638, 655 |
| reset_only_changes_owned_synthetic_scope | PASS | Not retained in this case; HTTP/persisted-result evidence only |
| ERP_429_respects_retry_after_then_recovers | PASS | 679, 720 |
| registered_wait_and_committed_approval_outbox_survive_n8n_restart | PASS | 1183, 1195, 1205, 1208 |
| database_outage_no_false_202_and_safe_redelivery | PASS | 1215, 1217, 1219, 1220 |
| ten_concurrent_first_deliveries_then_one_sandbox_effect | PASS | 1552, 1553 |
| committed_approval_observed_before_any_wait_then_n8n_delivery | PASS | 1564, 1565 |

Each execution is in the local n8n instance, not the cloud target. Action records and browser evidence separately prove action670 succeeded once and left the incident in monitoring.

## Disruption commands

Run only with other local users idle; these stop/start this project’s own containers and restore them in finally blocks.

```sh
rtk proxy python -X utf8 scripts/test_resilience.py --phase restart --allow-interruption
rtk proxy python -X utf8 scripts/test_resilience.py --phase database --allow-interruption
```

Normal resilience includes real 429 Retry-After, bounded503 retries, rejection/modification/expiry, stale approval, repeated SLA and isolated reset. Restart persists an actual signed Wait and commits approval/outbox while n8n is stopped. Database outage proves no false202 and safe replay after restoration. The complete raw sanitized results are in evidence/workflow-runs/.

Two third-party deprecation warnings occurred in the API test client; the run passed. Load testing, live model accuracy and real external delivery are not covered.
