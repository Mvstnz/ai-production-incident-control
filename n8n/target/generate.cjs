const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const ROOT = __dirname;
const OPS = 'https://configure-apic-ops.invalid';
const ERP = 'https://configure-apic-erp.invalid';
const ORDER = ['wf09','wf07','wf06','wf05','wf04','wf03','wf01','wf02','wf10','wf08'];
const clone = value => JSON.parse(JSON.stringify(value));
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const allowedCredentials = new Set(['APIC Operations Service','APIC ERP Read','APIC Webhook Intake','APIC Demo Form','Google Gemini(PaLM) Api account']);
function literal(value, key = '') {
  if (Array.isArray(value)) return '[' + value.map(x => literal(x)).join(', ') + ']';
  if (value && typeof value === 'object') return '{' + Object.entries(value).map(([k,v]) => JSON.stringify(k) + ': ' + literal(v,k)).join(', ') + '}';
  if (typeof value === 'string' && key !== 'jsCode' && value.startsWith('=')) return 'expr(' + JSON.stringify(value.slice(1)) + ')';
  return JSON.stringify(value);
}
function build(source, ids = {}) {
  const expected = clone(source);
  if (expected.settings.errorWorkflow) expected.settings.errorWorkflow = ids[expected.settings.errorWorkflow] || 'CONFIGURE_TARGET_WF09';
  const unresolved = [];
  for (const n of expected.nodes) {
    if (n.credentials?.googlePalmApi) n.credentials.googlePalmApi = {name:'Google Gemini(PaLM) Api account'};
    if (n.type === 'n8n-nodes-base.httpRequest') n.parameters.url = n.parameters.url.replaceAll('http://ops-api:8000',OPS).replaceAll('http://mock-erp:8001',ERP);
    if (n.type === 'n8n-nodes-base.executeWorkflow') {
      const dependency = n.parameters.workflowId.value;
      assert(ORDER.includes(dependency), 'Unknown workflow dependency');
      n.parameters.workflowId.value = ids[dependency] || 'CONFIGURE_TARGET_' + dependency.toUpperCase();
      if (!ids[dependency]) unresolved.push(dependency);
    }
  }
  const note = {
    name: 'Target Configuration BLOCKED', type: 'n8n-nodes-base.stickyNote', typeVersion: 1,
    position: [-160, -720],
    parameters: {
      content: '## BLOCKED — inactive / unpublished\nConfigure authorized Operations and ERP HTTPS endpoints and missing APIC credentials before any separately authorized execution.\n\n' + OPS + ' and ' + ERP + ' are deliberately non-routable configuration placeholders. Preserve every endpoint path. Dynamic wakeup URLs must be backend-validated for the authorized n8n host and protected by APIC Webhook Intake.\n\nWorkflow settings (Asia/Bangkok, caller policy, retention and shared WF09 error routing) are pending: no documented SDK creation settings; update is blocked by the approval gate. WF09 must remain unpublished. No runtime test has run.',
      width: 980, height: 390, color: 3
    }
  };
  expected.nodes.push(note);
  const vars = Object.fromEntries(expected.nodes.map((n,i)=>[n.name,'stage'+i]));
  const statements = expected.nodes.map(n => {
    const config = {};
    for (const [k,v] of Object.entries(n)) if (!['id','type','typeVersion','credentials','webhookId'].includes(k)) config[k] = v;
    let configText = literal(config);
    if (n.credentials) {
      const credentials = Object.entries(n.credentials).map(([type,c]) => {
        assert(allowedCredentials.has(c.name), 'Unexpected credential name');
        return JSON.stringify(type) + ': newCredential(' + JSON.stringify(c.name) + ')';
      }).join(', ');
      configText = configText.slice(0,-1) + ', credentials: {' + credentials + '}}';
    }
    const factory = ['webhook','formTrigger','executeWorkflowTrigger','scheduleTrigger','errorTrigger','manualTrigger'].some(t=>n.type === 'n8n-nodes-base.'+t) ? 'trigger' : 'node';
    return 'const '+vars[n.name]+' = '+factory+'({type: '+JSON.stringify(n.type)+', version: '+n.typeVersion+', config: '+configText+', output: [{}]});';
  });
  let graph = 'export default workflow('+JSON.stringify('apic-portfolio-'+source.key)+', '+JSON.stringify(source.name)+')';
  for (const n of expected.nodes) graph += '\n  .add('+vars[n.name]+')';
  for (const [name,types] of Object.entries(expected.connections)) {
    for (const [type,outputs] of Object.entries(types)) {
      assert.equal(type,'main','Only observed main connections supported');
      outputs.forEach((targets,out)=>targets.forEach(target=>{
        assert.equal(target.type,'main');
        const destination = vars[target.node]+(target.index ? '.input('+target.index+')' : '');
        graph += out ? '\n  .add('+vars[name]+'.output('+out+').to('+destination+'))' : '\n  .add('+vars[name]+').to('+destination+')';
      }));
    }
  }
  return {code: statements.join('\n\n')+'\n\n'+graph+';\n', expected, unresolved:[...new Set(unresolved)]};
}
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])]));
  return value;
}
function edges(connections) {
  return Object.entries(connections).flatMap(([from,types])=>Object.entries(types).flatMap(([type,outputs])=>outputs.flatMap((targets,out)=>(targets||[]).map(t=>[from,type,out,t.node,t.type,t.index])))).sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)));
}
function inspect(expected, actual) {
  const errors = [];
  const check = (name,condition) => {if (!condition) errors.push(name);};
  check('active must be false', actual.active === false);
  check('published version must be null', actual.activeVersionId === null);
  check('workflow name', actual.name === expected.name);
  const actualByName = new Map(actual.nodes.map(n=>[n.name,n]));
  for (const n of expected.nodes) {
    const a = actualByName.get(n.name);
    check('node exists: '+n.name,!!a);
    if (!a) continue;
    check('node type/version: '+n.name,a.type === n.type && a.typeVersion === n.typeVersion);
    check('node parameters: '+n.name, JSON.stringify(canonical(a.parameters)) === JSON.stringify(canonical(n.parameters)));
    check('node position: '+n.name,JSON.stringify(a.position) === JSON.stringify(n.position));
    for (const k of ['disabled','onError','retryOnFail','maxTries','waitBetweenTries','alwaysOutputData','executeOnce']) if (k in n) check('node execution setting: '+n.name+'/'+k,a[k] === n[k]);
  }
  check('exact original graph edges',JSON.stringify(edges(expected.connections))===JSON.stringify(edges(actual.connections)));
  const extras = actual.nodes.filter(n=>!expected.nodes.some(e=>e.name === n.name));
  check('no extra executable nodes', extras.every(n=>n.type==='n8n-nodes-base.stickyNote'));
  const credentialBindings = expected.nodes.filter(n=>n.credentials).map(n=>({
    node:n.name, required:n.credentials, returned:actualByName.get(n.name)?.credentials || {},
    status:Object.entries(n.credentials).every(([type,credential])=>actualByName.get(n.name)?.credentials?.[type]?.name===credential.name)?'CONFIGURED':'BLOCKED_MISSING_CREDENTIAL'
  }));
  return {valid:errors.length===0, errors, source_node_count:expected.nodes.length-1, requested_node_count:expected.nodes.length,
    returned_node_count:actual.nodes.length, edge_count:edges(expected.connections).length,
    code_runtime_strings_preserved:expected.nodes.filter(n=>n.type==='n8n-nodes-base.code').every(n=>actualByName.get(n.name)?.parameters.jsCode===n.parameters.jsCode),
    auth_parameters_preserved:expected.nodes.every(n=>['authentication','genericAuthType','incomingAuthentication'].every(k=>!(k in n.parameters)||actualByName.get(n.name)?.parameters[k]===n.parameters[k])),
    extra_sticky_notes:extras.map(n=>n.name), credential_requirements:credentialBindings};
}
function refreshSource(key) {
  assert(ORDER.includes(key),'Pass one workflow key, e.g. wf03');
  const repo = path.resolve(ROOT,'../..');
  const snapshotPath = path.join(ROOT,'source-snapshot.json');
  const snapshot = JSON.parse(fs.readFileSync(snapshotPath,'utf8'));
  const localFlows = Object.fromEntries(ORDER.map(k=>[k,JSON.parse(fs.readFileSync(path.join(repo,'n8n/workflows',k+'.json'),'utf8'))]));
  const localIdMap = Object.fromEntries(Object.entries(localFlows).map(([k,w])=>[w.id,k]));
  const local = localFlows[key];
  const normalized = {key,name:local.name,settings:{...local.settings,...(local.settings.errorWorkflow?{errorWorkflow:localIdMap[local.settings.errorWorkflow]}:{})},
    nodes:local.nodes.map(({id,credentials,...n})=>({...n,...(credentials?{credentials:Object.fromEntries(Object.entries(credentials).map(([type,c])=>[type,{name:c.name}]))}:{}),
      parameters:n.type==='n8n-nodes-base.executeWorkflow'?{...n.parameters,workflowId:{...n.parameters.workflowId,value:localIdMap[n.parameters.workflowId.value]}}:n.parameters})),connections:local.connections};
  const index=snapshot.findIndex(item=>item.key===key); assert(index>=0,'Workflow missing from source snapshot');
  snapshot[index]=normalized;
  fs.writeFileSync(snapshotPath,JSON.stringify(snapshot,null,2)+'\n');
  return normalized;
}
if (require.main === module) {
  if (process.argv[2] === '--refresh-source') {
    const refreshed=refreshSource(process.argv[3]);
    console.log(JSON.stringify({key:refreshed.key,status:'SOURCE_SNAPSHOT_REFRESHED',nodeCount:refreshed.nodes.length}));
    process.exit(0);
  }
  const snapshot = JSON.parse(fs.readFileSync(path.join(ROOT,'source-snapshot.json'),'utf8'));
  const idsFile = path.join(ROOT,'ids.json');
  const ids = fs.existsSync(idsFile) ? JSON.parse(fs.readFileSync(idsFile,'utf8')) : {};
  const key = process.argv[2];
  assert(ORDER.includes(key),'Pass one workflow key, e.g. wf09');
  const generated = build(snapshot.find(w=>w.key===key),ids);
  fs.writeFileSync(path.join(ROOT,key+'.builder.ts'),generated.code);
  fs.writeFileSync(path.join(ROOT,key+'.expected.json'),JSON.stringify(generated.expected,null,2)+'\n');
  console.log(JSON.stringify({key,code:generated.code,unresolved:generated.unresolved,sha256:hash(generated.code)}));
}
module.exports = {build,inspect,hash,canonical,edges,ORDER,refreshSource};
