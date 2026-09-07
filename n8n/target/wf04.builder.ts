const stage0 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Purpose", "position": [-160, -270], "parameters": {"content": "## WF04 · ERP Impact Analysis\nRead one immutable ERP snapshot → pure baseline/incident allocation → persist evidence. No formula duplication in n8n.\n\nSynthetic data · simulated AI · local sandbox only.", "height": 190, "width": 700}}, output: [{}]});

const stage1 = trigger({type: "n8n-nodes-base.executeWorkflowTrigger", version: 1.2, config: {"name": "Workflow Input", "position": [270, 200], "parameters": {"inputSource": "passthrough"}}, output: [{}]});

const stage2 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Impact Context", "position": [540, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return $input.all().map(i=>({json:{...i.json,execution_id:$execution.id,workflow_id:$workflow.id}}));"}}, output: [{}]});

const stage3 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Read Immutable ERP Snapshot", "position": [810, 200], "parameters": {"url": expr("{{ 'https://configure-apic-erp.invalid/erp/v1/snapshots/'+$json.snapshot_id+'?scope_id='+$json.scope_id }}"), "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC ERP Read")}}, output: [{}]});

const stage4 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Calculate Temporal Impact", "position": [1080, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/impact/evaluate", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ {snapshot:$json,facts:$('Impact Context').first().json.facts} }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage5 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Persist Impact Evidence", "position": [1350, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/impact/save", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ {...$('Impact Context').first().json,impact:$json} }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage6 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Target Configuration BLOCKED", "position": [-160, -720], "parameters": {"content": "## BLOCKED — inactive / unpublished\nConfigure authorized Operations and ERP HTTPS endpoints and missing APIC credentials before any separately authorized execution.\n\nhttps://configure-apic-ops.invalid and https://configure-apic-erp.invalid are deliberately non-routable configuration placeholders. Preserve every endpoint path. Dynamic wakeup URLs must be backend-validated for the authorized n8n host and protected by APIC Webhook Intake.\n\nWorkflow settings (Asia/Bangkok, caller policy, retention and shared WF09 error routing) are pending: no documented SDK creation settings; update is blocked by the approval gate. WF09 must remain unpublished. No runtime test has run.", "width": 980, "height": 390, "color": 3}}, output: [{}]});

export default workflow("apic-portfolio-wf04", "APIC | WF04 | ERP Impact Analysis")
  .add(stage0)
  .add(stage1)
  .add(stage2)
  .add(stage3)
  .add(stage4)
  .add(stage5)
  .add(stage6)
  .add(stage1).to(stage2)
  .add(stage2).to(stage3)
  .add(stage3).to(stage4)
  .add(stage4).to(stage5);
