# Workflow inventory

Local state: published, graph readback matched source. Target state: created/read back, inactive, configuration blocked; zero target execution IDs. Readback is not an execution test.

| Workflow | Local n8n ID | Target n8n ID | Target state |
|---|---|---|---|
| APIC / WF01 / Email Intake | `APICWF0100000001` | [`chlrLWx22aB9AELo`](https://mvstnz1.app.n8n.cloud/workflow/chlrLWx22aB9AELo) | Inactive / runtime NOT_RUN |
| APIC / WF02 / API and Form Intake | `APICWF0200000001` | [`BGz4AwLb1Y6S4Zfv`](https://mvstnz1.app.n8n.cloud/workflow/BGz4AwLb1Y6S4Zfv) | Inactive / runtime NOT_RUN |
| APIC / WF03 / Normalize Verify and Correlate | `APICWF0300000001` | [`6tHziLEHudpdk5hk`](https://mvstnz1.app.n8n.cloud/workflow/6tHziLEHudpdk5hk) | Inactive / runtime NOT_RUN |
| APIC / WF04 / ERP Impact Analysis | `APICWF0400000001` | [`JidtBtBq79j2UeUU`](https://mvstnz1.app.n8n.cloud/workflow/JidtBtBq79j2UeUU) | Inactive / runtime NOT_RUN |
| APIC / WF05 / Risk Explanation and Action Plan | `APICWF0500000001` | [`DaGeYQsYvTTBkzpA`](https://mvstnz1.app.n8n.cloud/workflow/DaGeYQsYvTTBkzpA) | Inactive / runtime NOT_RUN |
| APIC / WF06 / Human Approval | `APICWF0600000001` | [`oBliSIngBBWlmj17`](https://mvstnz1.app.n8n.cloud/workflow/oBliSIngBBWlmj17) | Inactive / runtime NOT_RUN |
| APIC / WF07 / Action Execution | `APICWF0700000001` | [`NwyqBStHsct30JQZ`](https://mvstnz1.app.n8n.cloud/workflow/NwyqBStHsct30JQZ) | Inactive / runtime NOT_RUN |
| APIC / WF08 / SLA Dispatch and Recovery | `APICWF0800000001` | [`K8yUTKNLA2WyHJUU`](https://mvstnz1.app.n8n.cloud/workflow/K8yUTKNLA2WyHJUU) | Inactive / runtime NOT_RUN |
| APIC / WF09 / Error and Dead Letter Handler | `APICWF0900000001` | [`KF1ttQVhDbDHBDmY`](https://mvstnz1.app.n8n.cloud/workflow/KF1ttQVhDbDHBDmY) | Inactive / runtime NOT_RUN |
| APIC / WF10 / Daily Management Digest | `APICWF1000000001` | [`anfiXs99aCeeg1g4`](https://mvstnz1.app.n8n.cloud/workflow/anfiXs99aCeeg1g4) | Inactive / runtime NOT_RUN |

Local probe: `APICPROBE0000001`, executed successfully. Target probe: `Fm2mFkzgF0jwFJEA`, created/read back and manually executed successfully with the bound Gemini credential (execution `3`); it remains inactive/unpublished. This isolated credential check does not remove the target core workflows' Operations/ERP connectivity blocker. Neither probe is one of the ten core workflows.

The local graph source is `n8n/workflows/`; sanitized persisted exports are `n8n/exports/local/`. Actual cloud exports and SDK builders are `n8n/target/`. See [target deployment](target-deployment.md) for missing credentials, configuration and graph drift.

Actual local execution references are recorded in [E2E evidence](../../evidence/workflow-runs/local-e2e.json), [resilience evidence](../../evidence/workflow-runs/resilience.json) and the [browser verification](../../evidence/test-results/browser.json).
