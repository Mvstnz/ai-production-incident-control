const stage0 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Purpose", "position": [-160, -270], "parameters": {"content": "## WF06 · Human Approval\nA Wait wakeup is technical only. After waiting, reload the DB decision and revalidate exact plan/version/hash/role before any action. Parent analysis is already complete.\n\nSynthetic data · simulated AI · local sandbox only.", "height": 190, "width": 700}}, output: [{}]});

const stage1 = trigger({type: "n8n-nodes-base.executeWorkflowTrigger", version: 1.2, config: {"name": "Workflow Input", "position": [270, 200], "parameters": {"inputSource": "passthrough"}}, output: [{}]});

const stage2 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Approval Context", "position": [540, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return $input.all().map(i=>({json:{...i.json,execution_id:$execution.id,workflow_id:$workflow.id}}));"}}, output: [{}]});

const stage3 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Load Authoritative Approvals", "position": [810, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/approvals/context", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage4 = node({type: "n8n-nodes-base.if", version: 2.3, config: {"name": "Pending Human Decision", "position": [1080, 200], "parameters": {"conditions": {"options": {"caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2}, "conditions": [{"id": "556da52b-1faa-5c2f-8ba8-8f00abd69ab1", "leftValue": expr("{{ $json.status==='PENDING' }}"), "rightValue": true, "operator": {"type": "boolean", "operation": "true", "singleValue": true}}], "combinator": "and"}, "options": {}}}, output: [{}]});

const stage5 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Register Protected Continuation", "position": [1350, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/approvals/register-wait", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ {...$('Approval Context').first().json,resume_url:$execution.resumeUrl} }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage6 = node({type: "n8n-nodes-base.wait", version: 1.1, config: {"name": "Wait for Approval Wakeup", "position": [1620, 200], "parameters": {"resume": "webhook", "httpMethod": "POST", "incomingAuthentication": "headerAuth", "responseMode": "onReceived", "limitWaitTime": true, "limitType": "afterTimeInterval", "resumeAmount": 30, "resumeUnit": "seconds", "options": {"noResponseBody": true}}, credentials: {"httpHeaderAuth": newCredential("APIC Webhook Intake")}}, output: [{}]});

const stage7 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Revalidate Decision and Plan", "position": [1890, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/approvals/revalidate", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $('Approval Context').first().json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage8 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Authorized Action References", "position": [2160, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "const c=$('Approval Context').first().json; return ($json.ready_action_ids||[]).map(id=>({json:{scope_id:c.scope_id,action_id:id}}));"}}, output: [{}]});

const stage9 = node({type: "n8n-nodes-base.executeWorkflow", version: 1.3, config: {"name": "Execute Approved Action", "position": [2430, 200], "parameters": {"source": "database", "workflowId": {"__rl": true, "mode": "id", "value": "NwyqBStHsct30JQZ"}, "mode": "each", "options": {"waitForSubWorkflow": true}}}, output: [{}]});

const stage10 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Target Configuration BLOCKED", "position": [-160, -720], "parameters": {"content": "## BLOCKED — inactive / unpublished\nConfigure authorized Operations and ERP HTTPS endpoints and missing APIC credentials before any separately authorized execution.\n\nhttps://configure-apic-ops.invalid and https://configure-apic-erp.invalid are deliberately non-routable configuration placeholders. Preserve every endpoint path. Dynamic wakeup URLs must be backend-validated for the authorized n8n host and protected by APIC Webhook Intake.\n\nWorkflow settings (Asia/Bangkok, caller policy, retention and shared WF09 error routing) are pending: no documented SDK creation settings; update is blocked by the approval gate. WF09 must remain unpublished. No runtime test has run.", "width": 980, "height": 390, "color": 3}}, output: [{}]});

export default workflow("apic-portfolio-wf06", "APIC | WF06 | Human Approval")
  .add(stage0)
  .add(stage1)
  .add(stage2)
  .add(stage3)
  .add(stage4)
  .add(stage5)
  .add(stage6)
  .add(stage7)
  .add(stage8)
  .add(stage9)
  .add(stage10)
  .add(stage1).to(stage2)
  .add(stage2).to(stage3)
  .add(stage3).to(stage4)
  .add(stage5).to(stage6)
  .add(stage6).to(stage7)
  .add(stage7).to(stage8)
  .add(stage8).to(stage9)
  .add(stage4).to(stage5)
  .add(stage4.output(1).to(stage7));
