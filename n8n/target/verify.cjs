const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {build,inspect,hash,canonical,edges,ORDER} = require('./generate.cjs');
const root = __dirname;
const repo = path.resolve(root,'../..');
const read = file => JSON.parse(fs.readFileSync(file,'utf8'));
const snapshot = read(path.join(root,'source-snapshot.json'));
const ids = read(path.join(root,'ids.json'));
const evidencePath = path.join(repo,'evidence/workflow-runs/target-deployment.json');
const evidence = read(evidencePath);
const canonicalText = value => JSON.stringify(canonical(value));
assert.equal(snapshot.length,10);
assert.equal(Object.keys(ids).length,10);
assert.equal(new Set(Object.values(ids)).size,10);
const localIdMap = Object.fromEntries(snapshot.map(s=>[read(path.join(repo,'n8n/workflows',s.key+'.json')).id,s.key]));
const checks = [];
for (const source of snapshot) {
  const key = source.key;
  const result = build(source,ids);
  assert.deepEqual(result.unresolved,[],key+' unresolved dependencies');
  const builderPath = path.join(root,key+'.builder.ts');
  assert.equal(fs.readFileSync(builderPath,'utf8'),result.code,key+' builder reproducibility');
  fs.writeFileSync(path.join(root,key+'.expected.json'),JSON.stringify(result.expected,null,2)+'\n');
  const exportPath = path.join(root,key+'.json');
  const exportedBytes = fs.readFileSync(exportPath);
  const workflow = JSON.parse(exportedBytes);
  const inspected = inspect(result.expected,workflow);
  assert.equal(inspected.valid,true,key+' '+inspected.errors.join(', '));
  assert.equal(workflow.id,ids[key]);
  assert.equal(workflow.activeVersionId,null);
  assert.equal(workflow.active,false);
  assert.equal(workflow.settings.errorWorkflow,undefined);
  assert.equal(workflow.nodes.filter(n=>n.name==='Target Configuration BLOCKED').length,1);
  const configuredCredentialNodes=workflow.nodes.filter(n=>n.credentials && Object.keys(n.credentials).length);
  assert.equal(configuredCredentialNodes.length,key==='wf03'?1:0);
  if(key==='wf03') assert.equal(configuredCredentialNodes[0].credentials.googlePalmApi?.name,'Google Gemini(PaLM) Api account');
  for (const n of workflow.nodes) {
    if(n.type==='n8n-nodes-base.executeWorkflow') assert(Object.values(ids).includes(n.parameters.workflowId.value),key+' local/unresolved target reference');
    if(n.type==='n8n-nodes-base.httpRequest') {
      assert(!n.parameters.url.includes('http://ops-api:8000'));
      assert(!n.parameters.url.includes('http://mock-erp:8001'));
      assert(n.parameters.url.includes('https://configure-apic-') || n.parameters.url==='={{ $json.resume_url }}',key+' unknown target origin');
    }
  }
  const serialized = JSON.stringify(workflow);
  for(const forbidden of ['pinData','shared','owner','scopes','APICWF','apicOpsService01','apicErpRead0001','apicWebhook001','apicForm000001','apicGemini0001']) assert(!serialized.includes('"'+forbidden+'"') && !serialized.includes('APICWF') && !serialized.includes('apicOpsService01'),key+' forbidden export metadata');
  const localPath = path.join(repo,'n8n/workflows',key+'.json');
  const localBytes = fs.readFileSync(localPath);
  const local = JSON.parse(localBytes);
  const normalized = {key,name:local.name,settings:{...local.settings,...(local.settings.errorWorkflow?{errorWorkflow:localIdMap[local.settings.errorWorkflow]}:{})},
    nodes:local.nodes.map(({id,credentials,...n})=>({...n,...(credentials?{credentials:Object.fromEntries(Object.entries(credentials).map(([type,c])=>[type,{name:c.name}]))}:{}),
    parameters:n.type==='n8n-nodes-base.executeWorkflow'?{...n.parameters,workflowId:{...n.parameters.workflowId,value:localIdMap[n.parameters.workflowId.value]}}:n.parameters})),connections:local.connections};
  const drift = canonicalText(normalized)!==canonicalText(source);
  if (drift) {
    const pending = build(normalized,ids);
    const pendingDir = path.join(root,'pending');
    fs.mkdirSync(pendingDir,{recursive:true});
    fs.writeFileSync(path.join(pendingDir,key+'.builder.ts'),pending.code);
    fs.writeFileSync(path.join(pendingDir,key+'.expected.json'),JSON.stringify(pending.expected,null,2)+'\n');
    fs.writeFileSync(path.join(pendingDir,key+'.drift.json'),JSON.stringify({key,status:'BLOCKED_UPDATE',target_id:ids[key],source_snapshot_sha256:hash(canonicalText(source)),current_source_sha256:hash(localBytes),current_builder_sha256:hash(pending.code),changed_nodes:normalized.nodes.filter(n=>canonicalText(n)!==canonicalText(source.nodes.find(s=>s.name===n.name)??null)).map(n=>n.name),connections_changed:canonicalText(normalized.connections)!==canonicalText(source.connections),target_updated:false},null,2)+'\n');
  }
  const record = evidence.workflows.find(w=>w.key===key);
  const currentValidationPath=path.join(root,key+'.validation.json');
  if(fs.existsSync(currentValidationPath)) record.sdk_validation=read(currentValidationPath);
  assert.equal(record.sdk_validation.valid,true);
  assert.equal(record.readback_nodes_validation.valid,true);
  assert.equal(record.execution_search.count,0);
  assert.equal(record.execution_search.estimated,false);
  assert.equal(record.precreation_search.data.filter(w=>w.name===source.name).length,0);
  assert.equal(evidence.final_inventory.data.filter(w=>w.name===source.name).length,1);
  const hashes = {
    builder_sha256:hash(result.code),
    export_sha256:hash(exportedBytes),
    current_source_file_sha256:hash(localBytes),
    source_snapshot_sha256:hash(canonicalText(source)),
    expected_graph_sha256:hash(canonicalText(result.expected)),
    readback_graph_sha256:hash(canonicalText({nodes:workflow.nodes,connections:workflow.connections}))
  };
  Object.assign(record,{version_id:workflow.versionId,active:workflow.active,active_version_id:workflow.activeVersionId,
    hashes,source_drift:drift,readback_comparison:inspected,
    pending_update:drift?{status:'BLOCKED_UPDATE',builder_file:'n8n/target/pending/'+key+'.builder.ts',details:read(path.join(root,'pending',key+'.drift.json')),sdk_validation:fs.existsSync(path.join(root,'pending',key+'.validation.json'))?read(path.join(root,'pending',key+'.validation.json')):null}:null,
    dependencies:result.expected.nodes.filter(n=>n.type==='n8n-nodes-base.executeWorkflow').map(n=>({node:n.name,target_id:n.parameters.workflowId.value,wait_for_subworkflow:n.parameters.options?.waitForSubWorkflow})),
    missing_settings:Object.fromEntries(Object.entries(record.settings_requested).filter(([k,v])=>canonicalText(workflow.settings[k]??null)!==canonicalText(v)))
  });
  if (record.pending_update) {
    const p = record.pending_update;
    p.validation_matches_builder = p.sdk_validation?.builder_sha256 === p.details.current_builder_sha256;
    p.sdk_status = p.validation_matches_builder && p.sdk_validation?.validation.valid ? 'VALIDATED_NOT_DEPLOYED' : 'NOT_RUN_CURRENT_BUILDER';
  }
  checks.push({key,id:ids[key],valid:true,source_drift:drift,node_count:workflow.nodes.length,edge_count:edges(workflow.connections).length,credential_bindings:configuredCredentialNodes.length,...hashes});
}
const sourceDrift = checks.filter(c=>c.source_drift).map(c=>c.key);
const summary = {
  status:sourceDrift.length?'LOCAL_TESTED_WITH_SOURCE_DRIFT':'LOCAL_TESTED',command:'rtk proxy node n8n/target/verify.cjs',
  checked_at:new Date().toISOString(),workflow_count:10,passed_readback_comparisons:10,
  total_source_nodes:checks.reduce((n,c)=>n+c.node_count-1,0),
  total_target_nodes:checks.reduce((n,c)=>n+c.node_count,0),
  total_edges:checks.reduce((n,c)=>n+c.edge_count,0),
  source_drift:sourceDrift,duplicate_names:0,missing_target_references:0,credential_bindings:checks.reduce((n,c)=>n+c.credential_bindings,0),
  runtime_executions:0,target_test_status:'NOT_RUN',checks
};
evidence.local_verification=summary;
if(sourceDrift.length && !evidence.blockers.some(b=>b.id==='SOURCE_DRIFT')) evidence.blockers.push({id:'SOURCE_DRIFT',status:'BLOCKED',workflows:sourceDrift,detail:'Concurrent local source changed after deployment snapshot; target graph preserves the captured snapshot. Update remains forbidden.'});
const manifest={
  schema_version:'1.0',project:'apic-portfolio',repository:evidence.repository,target:evidence.target,
  status:'BLOCKED',implementation_status:'IMPLEMENTED',target_test_status:'NOT_RUN',execution_ids:[],
  expected_create_order:evidence.expected_create_order,actual_create_order:evidence.actual_create_order,
  creation_order_deviation:evidence.creation_order_deviation,
  configuration_placeholders:{ops_origin:'https://configure-apic-ops.invalid',erp_origin:'https://configure-apic-erp.invalid'},
  credential_requirements:[
    {name:'APIC Operations Service',type:'httpHeaderAuth',header:'X-Service-Token',status:'MISSING'},
    {name:'APIC ERP Read',type:'httpHeaderAuth',header:'X-ERP-Token',status:'MISSING'},
    {name:'APIC Webhook Intake',type:'httpHeaderAuth',status:'MISSING'},
    {name:'APIC Demo Form',type:'httpBasicAuth',status:'MISSING'},
    {name:'Google Gemini(PaLM) Api account',type:'googlePalmApi',status:'CONFIGURED',scope:'WF03 live branch; isolated credential probe passed'}
  ],
  note:'Credential header names must be matched to the approved backend deployment; no values or target credential IDs exist.',
  workflows:evidence.workflows.map(({key,id,name,url,active,active_version_id,version_id,status,implementation_status,configuration_status,target_test_status,source_file,builder_file,export_file,hashes,source_drift,dependencies,settings_requested,settings_observed,missing_settings,readback_comparison,sdk_validation,readback_nodes_validation})=>({
    key,id,name,url,active,active_version_id,version_id,status,implementation_status,configuration_status,target_test_status,execution_ids:[],
    source_file,builder_file,export_file,hashes,source_drift,dependencies,
    settings_requested,settings_observed,missing_settings,
    validation:{sdk:sdk_validation.valid,readback_nodes:readback_nodes_validation.valid,readback_graph:readback_comparison.valid,code_runtime_strings_preserved:readback_comparison.code_runtime_strings_preserved,auth_parameters_preserved:readback_comparison.auth_parameters_preserved,warnings:sdk_validation.warnings||[]},
    pending_update:evidence.workflows.find(w=>w.key===key).pending_update,
    blockers:evidence.blockers.filter(b=>(b.id!=='AUTH_SCHEMA_DISCREPANCY'||key==='wf06') && (b.id!=='SOURCE_DRIFT'||source_drift)).map(b=>b.id)
  })),
  blockers:evidence.blockers,local_verification:{...summary,checks:undefined},rollback:evidence.rollback
};
fs.writeFileSync(evidencePath,JSON.stringify(evidence,null,2)+'\n');
fs.writeFileSync(path.join(root,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
fs.writeFileSync(path.join(root,'local-verification.json'),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify({...summary,checks:undefined}));
