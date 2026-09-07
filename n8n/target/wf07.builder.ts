const stage0 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Purpose", "position": [-160, -270], "parameters": {"content": "## WF07 · Action Execution\nAtomic claim rechecks exact current authorization. Adapter supports only local effects; accepted-but-timed-out write is UNKNOWN_OUTCOME and cannot blindly retry. Notification never resolves incident.\n\nSynthetic data · simulated AI · local sandbox only.", "height": 190, "width": 700}}, output: [{}]});

const stage1 = trigger({type: "n8n-nodes-base.executeWorkflowTrigger", version: 1.2, config: {"name": "Workflow Input", "position": [270, 200], "parameters": {"inputSource": "passthrough"}}, output: [{}]});

const stage2 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Action Context", "position": [540, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return $input.all().map(i=>({json:{...i.json,execution_id:$execution.id,workflow_id:$workflow.id}}));"}}, output: [{}]});

const stage3 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Claim Authorized Action", "position": [810, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/actions/claim", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage4 = node({type: "n8n-nodes-base.if", version: 2.3, config: {"name": "May Execute Exact Payload", "position": [1080, 200], "parameters": {"conditions": {"options": {"caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2}, "conditions": [{"id": "b2442fd3-5663-5882-a86c-6c51ae9afa2a", "leftValue": expr("{{ $json.can_execute===true }}"), "rightValue": true, "operator": {"type": "boolean", "operation": "true", "singleValue": true}}], "combinator": "and"}, "options": {}}}, output: [{}]});

const stage5 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Execute Controlled Sandbox Adapter", "position": [1350, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/actions/execute", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ {scope_id:$('Action Context').first().json.scope_id,action_id:$json.action_id,claim_token:$json.claim_token,execution_id:$execution.id,workflow_id:$workflow.id} }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage6 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Known Action Outcome", "position": [1620, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return $input.all().map(i=>({json:{action_id:i.json.action_id,status:i.json.status,provider_reference:i.json.provider_reference||null}}));"}}, output: [{}]});

const stage7 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Target Configuration BLOCKED", "position": [-160, -720], "parameters": {"content": "## BLOCKED — inactive / unpublished\nConfigure authorized Operations and ERP HTTPS endpoints and missing APIC credentials before any separately authorized execution.\n\nhttps://configure-apic-ops.invalid and https://configure-apic-erp.invalid are deliberately non-routable configuration placeholders. Preserve every endpoint path. Dynamic wakeup URLs must be backend-validated for the authorized n8n host and protected by APIC Webhook Intake.\n\nWorkflow settings (Asia/Bangkok, caller policy, retention and shared WF09 error routing) are pending: no documented SDK creation settings; update is blocked by the approval gate. WF09 must remain unpublished. No runtime test has run.", "width": 980, "height": 390, "color": 3}}, output: [{}]});

export default workflow("apic-portfolio-wf07", "APIC | WF07 | Action Execution")
  .add(stage0)
  .add(stage1)
  .add(stage2)
  .add(stage3)
  .add(stage4)
  .add(stage5)
  .add(stage6)
  .add(stage7)
  .add(stage1).to(stage2)
  .add(stage2).to(stage3)
  .add(stage3).to(stage4)
  .add(stage4).to(stage5)
  .add(stage5).to(stage6);
