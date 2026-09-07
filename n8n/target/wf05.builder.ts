const stage0 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Purpose", "position": [-160, -270], "parameters": {"content": "## WF05 · Risk Explanation and Action Plan\nVersioned risk policy → allowed SOP actions → verified exact drafts → immutable plan and approval/outbox. Simulated AI explicitly disclosed.\n\nSynthetic data · simulated AI · local sandbox only.", "height": 190, "width": 700}}, output: [{}]});

const stage1 = trigger({type: "n8n-nodes-base.executeWorkflowTrigger", version: 1.2, config: {"name": "Workflow Input", "position": [270, 200], "parameters": {"inputSource": "passthrough"}}, output: [{}]});

const stage2 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Plan Context", "position": [540, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return $input.all().map(i=>({json:{...i.json,execution_id:$execution.id,workflow_id:$workflow.id}}));"}}, output: [{}]});

const stage3 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Evaluate Risk Policy", "position": [810, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/risk/evaluate", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ {impact:$json.impact} }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage4 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Draft Allowed Actions", "position": [1080, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/plans/draft", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ {impact:$('Plan Context').first().json.impact,risk:$json,incident_id:$('Plan Context').first().json.incident_id,revision:$('Plan Context').first().json.revision} }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage5 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Commit Versioned Plan", "position": [1350, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/plans", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ {...$('Plan Context').first().json,risk:$('Evaluate Risk Policy').first().json,plan:$json} }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage6 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Target Configuration BLOCKED", "position": [-160, -720], "parameters": {"content": "## BLOCKED — inactive / unpublished\nConfigure authorized Operations and ERP HTTPS endpoints and missing APIC credentials before any separately authorized execution.\n\nhttps://configure-apic-ops.invalid and https://configure-apic-erp.invalid are deliberately non-routable configuration placeholders. Preserve every endpoint path. Dynamic wakeup URLs must be backend-validated for the authorized n8n host and protected by APIC Webhook Intake.\n\nWorkflow settings (Asia/Bangkok, caller policy, retention and shared WF09 error routing) are pending: no documented SDK creation settings; update is blocked by the approval gate. WF09 must remain unpublished. No runtime test has run.", "width": 980, "height": 390, "color": 3}}, output: [{}]});

export default workflow("apic-portfolio-wf05", "APIC | WF05 | Risk Explanation and Action Plan")
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
