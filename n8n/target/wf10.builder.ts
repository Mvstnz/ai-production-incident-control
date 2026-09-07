const stage0 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Purpose", "position": [-160, -270], "parameters": {"content": "## WF10 · Daily Management Digest\nOne digest per scope, Bangkok business date and channel. KPI union of unique sales positions, no double-counted exposure or invented savings.\n\nSynthetic data · simulated AI · local sandbox only.", "height": 190, "width": 700}}, output: [{}]});

const stage1 = trigger({type: "n8n-nodes-base.scheduleTrigger", version: 1.4, config: {"name": "Daily at 08 Bangkok", "position": [270, 200], "parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "0 8 * * *"}]}}}, output: [{}]});

const stage2 = trigger({type: "n8n-nodes-base.executeWorkflowTrigger", version: 1.2, config: {"name": "Workflow Input", "position": [540, 200], "parameters": {"inputSource": "passthrough"}}, output: [{}]});

const stage3 = trigger({type: "n8n-nodes-base.webhook", version: 2.1, config: {"name": "Protected Digest Test", "position": [810, 200], "parameters": {"httpMethod": "POST", "path": "apic-digest", "authentication": "headerAuth", "responseMode": "lastNode", "options": {"allowedOrigins": "http://127.0.0.1:5173"}}, credentials: {"httpHeaderAuth": newCredential("APIC Webhook Intake")}}, output: [{}]});

const stage4 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Digest Context", "position": [1080, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "const d=$input.first().json.body||$input.first().json; return [{json:{scope_id:d.scope_id||null,execution_id:$execution.id,workflow_id:$workflow.id}}];"}}, output: [{}]});

const stage5 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Commit Consistent Sandbox Digest", "position": [1350, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/digest", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage6 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Target Configuration BLOCKED", "position": [-160, -720], "parameters": {"content": "## BLOCKED — inactive / unpublished\nConfigure authorized Operations and ERP HTTPS endpoints and missing APIC credentials before any separately authorized execution.\n\nhttps://configure-apic-ops.invalid and https://configure-apic-erp.invalid are deliberately non-routable configuration placeholders. Preserve every endpoint path. Dynamic wakeup URLs must be backend-validated for the authorized n8n host and protected by APIC Webhook Intake.\n\nWorkflow settings (Asia/Bangkok, caller policy, retention and shared WF09 error routing) are pending: no documented SDK creation settings; update is blocked by the approval gate. WF09 must remain unpublished. No runtime test has run.", "width": 980, "height": 390, "color": 3}}, output: [{}]});

export default workflow("apic-portfolio-wf10", "APIC | WF10 | Daily Management Digest")
  .add(stage0)
  .add(stage1)
  .add(stage2)
  .add(stage3)
  .add(stage4)
  .add(stage5)
  .add(stage6)
  .add(stage1).to(stage4)
  .add(stage2).to(stage4)
  .add(stage3).to(stage4)
  .add(stage4).to(stage5);
