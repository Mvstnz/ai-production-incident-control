# Environment report

The local Windows / PowerShell environment runs the isolated apic-portfolio Docker stack. Pinned application dependencies, runtime images and hashes are recorded in [versions.lock](../../versions.lock). The application was also built and tested on a fresh GitHub Ubuntu runner; the exact revision and result are recorded separately in the acceptance evidence.

[CODEX_BUILD_SPEC.md](../../CODEX_BUILD_SPEC.md) governs the 36 acceptance criteria. Current ordinary manufacturing fixtures replace all retired reference-product and invented-brand fixtures.

The authorized n8n connector operates against mvstnz1.app.n8n.cloud, project YS0S0X7u4Oc458ln. All ten APIC workflows are published, credentialed and read back with their published graphs matching the saved drafts. The cloud release number is not exposed and is not inferred from node schema versions.

The earlier connector approval blocker is resolved. Three hosted scenario assessments and six approved actions completed through the real cloud workflows. Their actual execution IDs are retained in [hosted analyses](../../evidence/workflow-runs/hosted-demo.json) and [hosted actions](../../evidence/workflow-runs/hosted-actions.json).

Vercel provides the public HTTPS dashboard and Operations/ERP endpoints. Supabase stores private application and synthetic ERP data. Purpose-specific server credentials connect n8n to those endpoints. See [hosting](hosting.md) for the live URL, service IDs, access boundaries, trial dependency and recovery instructions.
