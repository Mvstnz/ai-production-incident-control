const stage0 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Purpose", "position": [-160, -270], "parameters": {"content": "## WF03 · Normalize Verify and Correlate\nClaim due job → extract supported fixture or structured facts → verify ERP identity → correlate immutable revision. Unknown input requires manual review.\n\nSynthetic data · simulated AI · local sandbox only.", "height": 190, "width": 700}}, output: [{}]});

const stage1 = trigger({type: "n8n-nodes-base.executeWorkflowTrigger", version: 1.2, config: {"name": "Workflow Input", "position": [270, 200], "parameters": {"inputSource": "passthrough"}}, output: [{}]});

const stage2 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Execution Context", "position": [540, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return $input.all().map(i=>({json:{...i.json,execution_id:$execution.id,workflow_id:$workflow.id}}));"}}, output: [{}]});

const stage3 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Claim Analysis Job", "position": [810, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/jobs/claim", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ {job_id:$json.job_id,owner:'n8n:'+$execution.id,limit:1,execution_id:$execution.id,workflow_id:$workflow.id} }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage4 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Claimed Job", "position": [1080, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return ($input.first().json.items||[]).map(j=>({json:{...j,execution_id:$execution.id,workflow_id:$workflow.id}}));"}}, output: [{}]});

const stage5 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Load Source and Snapshot", "position": [1350, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/jobs/context", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage6 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Fixture or Structured Extraction", "position": [1620, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/extract", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ {envelope:$json.envelope,snapshot:$json.snapshot} }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage7 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Bind Extraction", "position": [1890, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "return [{json:{...$('Load Source and Snapshot').first().json,extraction:$input.first().json}}];"}}, output: [{}]});

const stage8 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Verify and Correlate Revision", "position": [2160, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/incidents/correlate", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage9 = node({type: "n8n-nodes-base.if", version: 2.3, config: {"name": "Current Verified Revision", "position": [2430, 200], "parameters": {"conditions": {"options": {"caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2}, "conditions": [{"id": "bf122387-85b6-574b-96e6-b4345942f94e", "leftValue": expr("{{ !$json.skip_analysis && $json.status!=='MANUAL_REVIEW' }}"), "rightValue": true, "operator": {"type": "boolean", "operation": "true", "singleValue": true}}], "combinator": "and"}, "options": {}}}, output: [{}]});

const stage10 = node({type: "n8n-nodes-base.executeWorkflow", version: 1.3, config: {"name": "ERP Impact Analysis", "position": [2700, 200], "parameters": {"source": "database", "workflowId": {"__rl": true, "mode": "id", "value": "JidtBtBq79j2UeUU"}, "mode": "each", "options": {"waitForSubWorkflow": true}}}, output: [{}]});

const stage11 = node({type: "n8n-nodes-base.executeWorkflow", version: 1.3, config: {"name": "Risk and Action Plan", "position": [2970, 200], "parameters": {"source": "database", "workflowId": {"__rl": true, "mode": "id", "value": "DaGeYQsYvTTBkzpA"}, "mode": "each", "options": {"waitForSubWorkflow": true}}}, output: [{}]});

const stage12 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Complete Analysis Job", "position": [3240, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/jobs/complete", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage13 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Target Configuration BLOCKED", "position": [-160, -720], "parameters": {"content": "## BLOCKED — inactive / unpublished\nConfigure authorized Operations and ERP HTTPS endpoints and missing APIC credentials before any separately authorized execution.\n\nhttps://configure-apic-ops.invalid and https://configure-apic-erp.invalid are deliberately non-routable configuration placeholders. Preserve every endpoint path. Dynamic wakeup URLs must be backend-validated for the authorized n8n host and protected by APIC Webhook Intake.\n\nWorkflow settings (Asia/Bangkok, caller policy, retention and shared WF09 error routing) are pending: no documented SDK creation settings; update is blocked by the approval gate. WF09 must remain unpublished. No runtime test has run.", "width": 980, "height": 390, "color": 3}}, output: [{}]});

export default workflow("apic-portfolio-wf03", "APIC | WF03 | Normalize Verify and Correlate")
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
  .add(stage1).to(stage2)
  .add(stage2).to(stage3)
  .add(stage3).to(stage4)
  .add(stage4).to(stage5)
  .add(stage5).to(stage6)
  .add(stage6).to(stage7)
  .add(stage7).to(stage8)
  .add(stage8).to(stage9)
  .add(stage10).to(stage11)
  .add(stage11).to(stage12)
  .add(stage9).to(stage10)
  .add(stage9.output(1).to(stage12));
