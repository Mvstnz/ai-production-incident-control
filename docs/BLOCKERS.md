# Remaining blockers

## M6 / AC31 — BLOCKED_TARGET_CONNECTION

The authorized n8n MCP is connected. Ten APIC core workflows and an M0 probe were actually created and read back. This is partial target deployment, not connected acceptance.

| Blocker | Observed evidence | Required resolution |
|---|---|---|
| Tool approval policy | Automatic approval review rejected update_workflow and execute_workflow: `MCP tool call requires approval, but approval policy is never` | A session permitting the operations already requested by the user; no bypass of the gate |
| Backend connectivity | Cloud cannot reach Docker-only service names; no authorized HTTPS Operations/ERP deployment supplied | Authorized reachable HTTPS API deployment; configure origins and continuation allowlist |
| Target credentials | No credential metadata returned; four APIC purpose credentials remain unbound | Operations service, ERP read, protected intake/Wait Header Auth and form Basic Auth credentials |
| Target settings and graph updates | SDK creation omitted timezone/retention/caller/error routing; later runtime corrections remain undeployed | Export before permitted update; bind current graphs/settings/references and verify target Wait behavior |

All ten cloud workflows remain inactive/unpublished. Target execution IDs are empty. IDs and exact per-workflow readbacks are in `n8n/target/manifest.json`. The target release version was not exposed by MCP. Local success does not close these blockers. No public tunnel, firewall change, paid hosting, target secret upload or foreign workflow mutation was performed.

## Live model evaluation — NOT_RUN

No explicit paid-call budget or live provider credential was supplied. The deterministic 50-case fixture evaluation ran; live latency, cost and extraction quality were not measured. A live adapter and bounded evaluation require authorized configuration and validation. The application says simulated AI.

## Resolved prerequisites

The canonical v1.1 handoff was supplied, read and checked. Docker was restored and the local Compose stack runs. These are no longer access blockers. Remaining local test work is tracked honestly in the acceptance matrix and progress report.
