# Demonstration walkthrough

1. Start Compose with `rtk proxy python scripts/bootstrap.py`. Sign in as production_manager using the generated local account. Choose **Run demo → Supplier delay**, which creates an isolated scope and enters the real WF01 webhook.
2. Observe the durable source event and job progress. Open the incident: 38 demand, 14 coverage, 24 shortage, three orders reviewed but only two affected, €126,400, score88. The allocation table shows the original and revised completion of each order.
3. Inspect the source, immutable snapshot, risk factor sources, SOP and exact plan. The proposed ten pieces remain outside the baseline; the what-if score69 is visibly hypothetical.
4. Review the approval inbox. The decision is bound to the exact recipient, message, action parameters, revision, version and hash. Enter a rationale and confirm the reviewed payload. Observe execution in Reliability and the local Mailpit inbox. The incident remains MONITORING.
5. Submit **Run confirmed split revision** from the assessment. The same incident receives a new revision; the previous evaluation remains visible, stale approvals cannot dispatch, and the current score becomes69 with€54,400 exposure.
6. Run the machine demo in a new scope. Inspect the qualified alternative and score52. Approve synthetic rescheduling with production_manager.
7. Sign in as quality_manager and run the quality demo. Inspect inspection/lot/shipment trace, then approve the exact quality block. A release requires a new evidence-backed proposal and a fresh approval. A message alone never resolves the case.
8. Use Reliability to inspect real job/Wait execution IDs, pending work, known failures and UNKNOWN_OUTCOME actions. Admin-only failure controls demonstrate bounded retries and ambiguous writes. Do not blindly retry an action whose provider outcome is unknown.

All figures are synthetic open-position values, not predicted losses or claimed savings. Simulated fixture evaluation and live LLM performance are separate; live has not run.

For repeatable automated demonstrations, run the HTTP acceptance scripts. They create their own scopes; select the resulting scope ID to inspect exactly the stored evidence. A demo reset is limited to the owner of that synthetic scope and preserves the immutable audit trail.
