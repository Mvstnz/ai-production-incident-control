const stage0 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Purpose", "position": [-160, -270], "parameters": {"content": "## WF08 · SLA Dispatch and Recovery\nEvery 60 seconds claim bounded due work. Recover leases, outstanding decisions and outbox; deduplicate each SLA stage. Business clock does not alter n8n Wait time.\n\nSynthetic data · simulated AI · local sandbox only.", "height": 190, "width": 700}}, output: [{}]});

const stage1 = trigger({type: "n8n-nodes-base.scheduleTrigger", version: 1.4, config: {"name": "Every Minute", "position": [270, 200], "parameters": {"rule": {"interval": [{"field": "minutes", "minutesInterval": 1}]}}}, output: [{}]});

const stage2 = trigger({type: "n8n-nodes-base.webhook", version: 2.1, config: {"name": "Protected Recovery Test", "position": [540, 200], "parameters": {"httpMethod": "POST", "path": "apic-recovery", "authentication": "headerAuth", "responseMode": "onReceived", "options": {"allowedOrigins": "http://127.0.0.1:5173"}}, credentials: {"httpHeaderAuth": newCredential("APIC Webhook Intake")}}, output: [{}]});

const stage3 = trigger({type: "n8n-nodes-base.executeWorkflowTrigger", version: 1.2, config: {"name": "Workflow Input", "position": [810, 200], "parameters": {"inputSource": "passthrough"}}, output: [{}]});

const stage4 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Recovery Context", "position": [1080, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return [{json:{execution_id:$execution.id,workflow_id:$workflow.id}}];"}}, output: [{}]});

const stage5 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Recover Due Work and SLA", "position": [1350, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/recovery", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage6 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Due Jobs", "position": [1620, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return ($json.jobs||[]).map(x=>({json:x}));"}}, output: [{}]});

const stage7 = node({type: "n8n-nodes-base.executeWorkflow", version: 1.3, config: {"name": "Dispatch WF03", "position": [1890, 200], "parameters": {"source": "database", "workflowId": {"__rl": true, "mode": "id", "value": "6tHziLEHudpdk5hk"}, "mode": "each", "options": {"waitForSubWorkflow": false}}}, output: [{}]});

const stage8 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Due Approval Plans", "position": [2160, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return ($json.plans||[]).map(x=>({json:x}));"}}, output: [{}]});

const stage9 = node({type: "n8n-nodes-base.executeWorkflow", version: 1.3, config: {"name": "Dispatch WF06", "position": [2430, 200], "parameters": {"source": "database", "workflowId": {"__rl": true, "mode": "id", "value": "oBliSIngBBWlmj17"}, "mode": "each", "options": {"waitForSubWorkflow": false}}}, output: [{}]});

const stage10 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Due Actions", "position": [2700, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return ($json.actions||[]).map(x=>({json:x}));"}}, output: [{}]});

const stage11 = node({type: "n8n-nodes-base.executeWorkflow", version: 1.3, config: {"name": "Dispatch WF07", "position": [2970, 200], "parameters": {"source": "database", "workflowId": {"__rl": true, "mode": "id", "value": "NwyqBStHsct30JQZ"}, "mode": "each", "options": {"waitForSubWorkflow": false}}}, output: [{}]});

const stage12 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Due Wakeups", "position": [3240, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return ($json.wakeups||[]).map(x=>({json:x}));"}}, output: [{}]});

const stage13 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Send Protected Wakeup", "position": [3510, 200], "parameters": {"method": "POST", "url": expr("{{ $json.resume_url }}"), "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {"timeout": 5000, "response": {"response": {"neverError": true, "fullResponse": true}}}}, credentials: {"httpHeaderAuth": newCredential("APIC Webhook Intake")}}, output: [{}]});

const stage14 = node({type: "n8n-nodes-base.if", version: 2.3, config: {"name": "Wakeup Accepted", "position": [3780, 200], "parameters": {"conditions": {"options": {"caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2}, "conditions": [{"id": "71109397-bfcf-5ffc-aea3-03b78e4148c1", "leftValue": expr("{{ $json.statusCode>=200 && $json.statusCode<300 }}"), "rightValue": true, "operator": {"type": "boolean", "operation": "true", "singleValue": true}}], "combinator": "and"}, "options": {}}}, output: [{}]});

const stage15 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Acknowledge Wakeup", "position": [4050, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/outbox/ack", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ {scope_id:$('Due Wakeups').item.json.scope_id,event_id:$('Due Wakeups').item.json.event_id} }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage16 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Target Configuration BLOCKED", "position": [-160, -720], "parameters": {"content": "## BLOCKED — inactive / unpublished\nConfigure authorized Operations and ERP HTTPS endpoints and missing APIC credentials before any separately authorized execution.\n\nhttps://configure-apic-ops.invalid and https://configure-apic-erp.invalid are deliberately non-routable configuration placeholders. Preserve every endpoint path. Dynamic wakeup URLs must be backend-validated for the authorized n8n host and protected by APIC Webhook Intake.\n\nWorkflow settings (Asia/Bangkok, caller policy, retention and shared WF09 error routing) are pending: no documented SDK creation settings; update is blocked by the approval gate. WF09 must remain unpublished. No runtime test has run.", "width": 980, "height": 390, "color": 3}}, output: [{}]});

export default workflow("apic-portfolio-wf08", "APIC | WF08 | SLA Dispatch and Recovery")
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
  .add(stage11)
  .add(stage12)
  .add(stage13)
  .add(stage14)
  .add(stage15)
  .add(stage16)
  .add(stage5).to(stage6)
  .add(stage5).to(stage8)
  .add(stage5).to(stage10)
  .add(stage5).to(stage12)
  .add(stage6).to(stage7)
  .add(stage8).to(stage9)
  .add(stage10).to(stage11)
  .add(stage12).to(stage13)
  .add(stage13).to(stage14)
  .add(stage14).to(stage15)
  .add(stage1).to(stage4)
  .add(stage2).to(stage4)
  .add(stage3).to(stage4)
  .add(stage4).to(stage5);
