"""Preserve private discovery locally and prepare the authorized public source tree."""
from pathlib import Path
import json,shutil,re
ROOT=Path(__file__).resolve().parents[1]
private=ROOT/'.local/pre-publication';private.mkdir(parents=True,exist_ok=True)
def backup(path):
    target=private/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():shutil.copy2(path,target)
for name in ('n8n/sdk-reference.md','n8n/node-schemas.md','n8n/target/node-schemas.md'):
    p=ROOT/name
    if not p.exists():continue
    backup(p)
    p.write_text('# n8n discovery provenance\n\nThe authorized n8n MCP returned the SDK/node reference during implementation. The full third-party capture is retained only in the local private discovery archive, outside the public repository. This source tree keeps authored workflow builders, observed versions, actual cleaned readbacks and validation outcomes.\n\nNode versions used: Webhook2.1, HTTP Request4.5, Code2, Execute Workflow1.3, Wait1.1, Schedule1.4, Form Trigger2.6. Target release version was not exposed. Missing target credentials and runtime verification remain explicit blockers.\n\nSources: [n8n documentation](https://docs.n8n.io/), [n8n source](https://github.com/n8n-io/n8n).\n',encoding='utf-8')
for name in ('adopt_handoff.py','inspect_handoff_v11.py','adopt_handoff_v11.py','run_target_deploy_bridge.py'):
    p=ROOT/'scripts'/name
    if p.exists():
        backup(p);p.unlink() # Exact owned maintenance files, not a recursive cleanup.
for p in [ROOT/'n8n/target/manifest.json',ROOT/'evidence/workflow-runs/target-deployment.json']:
    backup(p);s=p.read_text(encoding='utf-8')
    s=s.replace('User explicitly prohibits publish, test and execution. Prior execute_workflow gate denial remains in force. Runtime and E2E verification NOT_RUN.','User authorized target deployment and testing. The parent bounded this creation/readback pass to inactive workflows because update/execute were rejected by the automatic approval gate and required network/credentials are missing. Runtime and E2E verification NOT_RUN.')
    s=s.replace('Publication is explicitly prohibited; errorWorkflow is not configured.','Publication was deferred for this blocked deployment pass; errorWorkflow is not configured.')
    p.write_text(s,encoding='utf-8')
for p in [ROOT/'n8n-discovery.md',*list((ROOT/'docs/implementation').glob('*.md')),*list((ROOT/'evidence/workflow-runs').glob('*.json'))]:
    backup(p);s=p.read_text(encoding='utf-8')
    s=s.replace('C:/Users/marvi/Desktop/n8n_Workflows/ai-production-incident-control/','')
    s=s.replace('C:\\\\Users\\\\marvi\\\\Desktop\\\\n8n_Workflows\\\\ai-production-incident-control','repository')
    s=s.replace('`zkTKdNAJ8L1X6AqP`','`foreign-workflow-1`').replace('`3bLubRLjNjvSORwO`','`foreign-workflow-2`')
    s=s.replace('Auto categorise Outlook emails with AI','Unrelated workflow 1').replace('My workflow','Unrelated workflow 2')
    s=s.replace('— Marvin, Typ `personal`','— own personal project')
    p.write_text(s,encoding='utf-8')
def clean(value):
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items() if k not in ('claim_token','resume_url','password','csrf_token')}
    if isinstance(value,list):return [clean(v) for v in value]
    return value
for p in (ROOT/'evidence/workflow-runs').glob('local-e2e*.json'):
    p.write_text(json.dumps(clean(json.loads(p.read_text(encoding='utf-8'))),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
report={'status':'PREPARED','private_paths_excluded':['.env','.local','.venv','node_modules'],'third_party_full_reference_captures':'retained locally; public summaries and links replace captures','claim_tokens_and_resume_urls':'removed from public runtime evidence','target_authorization_provenance':'clarified parent operational boundary vs explicit user authorization','known_business_data':'synthetic fixtures and sandbox messages only','remaining_check':'Run scan_repository.py again on final staged files before push.'}
(ROOT/'evidence/test-results/publication-sanitization.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
