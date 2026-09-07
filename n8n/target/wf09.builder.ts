const stage0 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Purpose", "position": [-160, -270], "parameters": {"content": "## WF09 · Error and Dead Letter Handler\nReal automatic Error Trigger and explicit test/subworkflow input. Redact raw supplier text and credentials; bounded retry stays in DB. No self-error recursion.\n\nSynthetic data · simulated AI · local sandbox only.", "height": 190, "width": 700}}, output: [{}]});

const stage1 = trigger({type: "n8n-nodes-base.errorTrigger", version: 1, config: {"name": "Automatic Execution Error", "position": [270, 200], "parameters": {}}, output: [{}]});

const stage2 = trigger({type: "n8n-nodes-base.executeWorkflowTrigger", version: 1.2, config: {"name": "Workflow Input", "position": [540, 200], "parameters": {"inputSource": "passthrough"}}, output: [{}]});

const stage3 = trigger({type: "n8n-nodes-base.webhook", version: 2.1, config: {"name": "Protected Error Harness", "position": [810, 200], "parameters": {"httpMethod": "POST", "path": "apic-error", "authentication": "headerAuth", "responseMode": "lastNode", "options": {"allowedOrigins": "http://127.0.0.1:5173"}}, credentials: {"httpHeaderAuth": newCredential("APIC Webhook Intake")}}, output: [{}]});

const stage4 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Safe Error Metadata", "position": [1080, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "const e=$input.first().json.body||$input.first().json; const err=e.execution?.error||{}; const status=Number(e.status_code||err.httpCode||err.statusCode||err.context?.httpCode)||null; const delay=Number(e.retry_after||err.context?.retryAfter)||null; return [{json:{scope_id:e.scope_id||null,job_id:e.job_id||null,execution_id:String(e.execution?.id||e.execution_id||$execution.id),workflow_id:e.workflow?.id||e.workflow_id||$workflow.id,status_code:status,retry_after:delay,error_class:e.error_class||(status && status<500 && status!==429?'PERMANENT':'TRANSIENT'),message:e.error_class==='PERMANENT'?'Permanent workflow configuration failure':'Workflow execution failed; inspect authorized runtime logs'}}];"}}, output: [{}]});

const stage5 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Record Error and Classify Retry", "position": [1350, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/errors", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage6 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Target Configuration BLOCKED", "position": [-160, -720], "parameters": {"content": "## BLOCKED — inactive / unpublished\nConfigure authorized Operations and ERP HTTPS endpoints and missing APIC credentials before any separately authorized execution.\n\nhttps://configure-apic-ops.invalid and https://configure-apic-erp.invalid are deliberately non-routable configuration placeholders. Preserve every endpoint path. Dynamic wakeup URLs must be backend-validated for the authorized n8n host and protected by APIC Webhook Intake.\n\nWorkflow settings (Asia/Bangkok, caller policy, retention and shared WF09 error routing) are pending: no documented SDK creation settings; update is blocked by the approval gate. WF09 must remain unpublished. No runtime test has run.", "width": 980, "height": 390, "color": 3}}, output: [{}]});

export default workflow("apic-portfolio-wf09", "APIC | WF09 | Error and Dead Letter Handler")
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
