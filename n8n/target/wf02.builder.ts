const stage0 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Purpose", "position": [-160, -270], "parameters": {"content": "## WF02 · API and Form Intake\nAuthenticated intake → durable event/job transaction → 202 → asynchronous analysis. Idempotency lives in PostgreSQL, not this execution.\n\nSynthetic data · simulated AI · local sandbox only.", "height": 190, "width": 700}}, output: [{}]});

const stage1 = trigger({type: "n8n-nodes-base.webhook", version: 2.1, config: {"name": "Authenticated Intake", "position": [270, 200], "parameters": {"httpMethod": "POST", "path": "apic-intake", "authentication": "headerAuth", "responseMode": "responseNode", "options": {"allowedOrigins": "http://127.0.0.1:5173"}}, credentials: {"httpHeaderAuth": newCredential("APIC Webhook Intake")}}, output: [{}]});

const stage2 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Canonical Envelope", "position": [540, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "const e=$input.first().json.body; if(!e || JSON.stringify(e).length>65536) throw new Error('INVALID_ENVELOPE_SIZE'); return [{json:e}];"}}, output: [{}]});

const stage3 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Commit Source Event", "position": [810, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/source-events", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage4 = node({type: "n8n-nodes-base.respondToWebhook", version: 1.5, config: {"name": "Durable Acceptance", "position": [1080, 200], "parameters": {"respondWith": "json", "responseBody": expr("{{ $json }}"), "options": {"responseCode": 202}}}, output: [{}]});

const stage5 = node({type: "n8n-nodes-base.executeWorkflow", version: 1.3, config: {"name": "Start Analysis", "position": [1350, 200], "parameters": {"source": "database", "workflowId": {"__rl": true, "mode": "id", "value": "6tHziLEHudpdk5hk"}, "mode": "each", "options": {"waitForSubWorkflow": false}}}, output: [{}]});

const stage6 = trigger({type: "n8n-nodes-base.formTrigger", version: 2.6, config: {"name": "Authenticated Supplier Form", "position": [0, 700], "parameters": {"authentication": "basicAuth", "formTitle": "Report a supplier delay", "formDescription": "Synthetic demo only. Enter confirmed availability; proposed delivery is never treated as confirmed.", "formFields": {"values": [{"fieldLabel": "Purchase order", "fieldName": "purchase_order", "fieldType": "text", "requiredField": true}, {"fieldLabel": "PO position", "fieldName": "purchase_order_item", "fieldType": "text", "requiredField": true}, {"fieldLabel": "Material", "fieldName": "material", "fieldType": "text", "requiredField": true}, {"fieldLabel": "Open quantity (pcs)", "fieldName": "quantity", "fieldType": "text", "requiredField": true}, {"fieldLabel": "Confirmed available at (ISO timestamp with offset)", "fieldName": "available_at", "fieldType": "text", "requiredField": true}]}, "responseMode": "lastNode", "options": {"path": "apic-supplier-form", "respondWithOptions": {"values": {"respondWith": "text", "formSubmittedText": "Report durably recorded. Check the Operations dashboard for verified assessment or clarification."}}}}, credentials: {"httpBasicAuth": newCredential("APIC Demo Form")}}, output: [{}]});

const stage7 = node({type: "n8n-nodes-base.code", version: 2, config: {"name": "Form Envelope", "position": [1890, 200], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": "const d=$json; return [{json:{schema_version:'1.0',scope_id:'928d1daf-6ffe-54e4-8cf3-5d4032986821',source:'FORM',source_account_id:'apic-authenticated-form',source_id:'form-'+$execution.id,received_at:$now.toISO(),correlation_id:'00000000-0000-4000-8000-'+String($execution.id).padStart(12,'0'),sender:'operator@example.test',subject:'Structured supplier delay',content_text:'Authenticated structured supplier form',payload:{incident_type:'SUPPLIER_DELAY',purchase_order:d.purchase_order,purchase_order_item:d.purchase_order_item,material:d.material,confirmed_supply_schedule:[{quantity:Number(d.quantity),available_at:d.available_at,status:'CONFIRMED'}],reason:'Supplier form report'}}}];"}}, output: [{}]});

const stage8 = node({type: "n8n-nodes-base.httpRequest", version: 4.5, config: {"name": "Commit Form Source Event", "position": [2160, 200], "parameters": {"method": "POST", "url": "https://configure-apic-ops.invalid/internal/source-events", "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": true, "specifyBody": "json", "jsonBody": expr("{{ $json }}"), "options": {"timeout": 15000}}, credentials: {"httpHeaderAuth": newCredential("APIC Operations Service")}}, output: [{}]});

const stage9 = node({type: "n8n-nodes-base.executeWorkflow", version: 1.3, config: {"name": "Start Form Analysis", "position": [2430, 200], "parameters": {"source": "database", "workflowId": {"__rl": true, "mode": "id", "value": "6tHziLEHudpdk5hk"}, "mode": "each", "options": {"waitForSubWorkflow": false}}}, output: [{}]});

const stage10 = node({type: "n8n-nodes-base.stickyNote", version: 1, config: {"name": "Target Configuration BLOCKED", "position": [-160, -720], "parameters": {"content": "## BLOCKED — inactive / unpublished\nConfigure authorized Operations and ERP HTTPS endpoints and missing APIC credentials before any separately authorized execution.\n\nhttps://configure-apic-ops.invalid and https://configure-apic-erp.invalid are deliberately non-routable configuration placeholders. Preserve every endpoint path. Dynamic wakeup URLs must be backend-validated for the authorized n8n host and protected by APIC Webhook Intake.\n\nWorkflow settings (Asia/Bangkok, caller policy, retention and shared WF09 error routing) are pending: no documented SDK creation settings; update is blocked by the approval gate. WF09 must remain unpublished. No runtime test has run.", "width": 980, "height": 390, "color": 3}}, output: [{}]});

export default workflow("apic-portfolio-wf02", "APIC | WF02 | API and Form Intake")
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
  .add(stage4).to(stage5)
  .add(stage6).to(stage7)
  .add(stage7).to(stage8)
  .add(stage8).to(stage9);
