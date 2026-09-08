"""Scan exactly Git-eligible files without logging any matched secret value."""
from pathlib import Path
import subprocess,json,re
ROOT=Path(__file__).resolve().parents[1]
result=subprocess.run(['rtk','proxy','git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT,capture_output=True,check=True)
files=sorted(set(x for x in result.stdout.decode().split('\0') if x))
secrets=[]
env=ROOT/'.env'
if env.exists():
    public_keys={'PROFILE','EXTERNAL_ACTIONS_ENABLED','AI_MODE','LLM_MODEL','LLM_MAX_CALLS'}
    secrets += [value.encode() for line in env.read_text().splitlines() if '=' in line
                for key,value in [line.split('=',1)] if key not in public_keys and len(value)>=20]
for name in ('credentials.json','n8n-owner.json','hosted-credentials.json'):
    path=ROOT/'.local'/name
    if path.exists():
        doc=json.loads(path.read_text());secrets += [u['password'].encode() for u in doc.get('users',[doc]) if u.get('password')]
for name in ('hosted-env.json','hosting-access.json'):
    path=ROOT/'.local'/name
    if path.exists():
        data=json.loads(path.read_text())
        for key,value in data.items():
            if isinstance(value,str) and len(value)>=20 and any(part in key.upper() for part in ('PASSWORD','SECRET','TOKEN','DATABASE','KEY')):
                secrets.append(value.encode())
issues=[];checked=0
for name in files:
    p=ROOT/name
    if not p.is_file():continue
    data=p.read_bytes();checked+=1
    if any(s and s in data for s in secrets):issues.append({'file':name,'kind':'LOCAL_SECRET_VALUE'})
    if re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',data):issues.append({'file':name,'kind':'PRIVATE_KEY'})
    if name=='.env' or name.startswith('.local/'):issues.append({'file':name,'kind':'PRIVATE_PATH_TRACKED'})
report={'check':'Git-eligible repository and exports exact-local-secret/private-key scan','status':'PASS' if not issues else 'FAIL','files_checked':checked,'issues':issues,'limits':'Exact known local secrets and private-key markers; not a universal secret detector. Screenshots separately visually reviewed.'}
dest=ROOT/'evidence/test-results/secret-scan.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report));raise SystemExit(bool(issues))
