from pathlib import Path
import subprocess,json,hashlib,re
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def command(*args):return subprocess.run(['rtk','proxy',*args],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
images={}
for name in ('postgres:17.6','n8nio/n8n:2.37.10','n8nio/runners:2.37.10','axllent/mailpit:v1.27.4','python:3.12.10-slim','node:24.12.0-bookworm-slim','nginx:1.28.0-alpine'):
    try:images[name]=json.loads(command('docker','image','inspect',name,'--format','{{json .RepoDigests}}'))
    except subprocess.CalledProcessError:
        metadata=command('docker','buildx','imagetools','inspect',name)
        digest=re.search(r'^Digest:\s+(sha256:[a-f0-9]{64})',metadata,re.MULTILINE)
        images[name]={'registry_digest':digest.group(1) if digest else None,'source':'docker buildx imagetools inspect; pinned build-stage tag'}
report={'captured_at':datetime.now(timezone.utc).isoformat(),'profile':'DEMO_LOCAL','n8n':'2.37.10','target_n8n_release':None,'target_note':'Node schema versions exposed; target release not exposed by MCP.','docker_engine':command('docker','version','--format','{{.Server.Version}}'),'host_node':command('node','--version'),'host_python':command('python','--version'),'rtk':command('rtk','--version'),'images':images,'locks':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('backend/requirements.lock.txt','package-lock.json')},'node_versions':{'webhook':2.1,'formTrigger':2.6,'httpRequest':4.5,'executeWorkflow':1.3,'wait':1.1,'scheduleTrigger':1.4,'code':2}}
(ROOT/'versions.lock').write_text(json.dumps(report,indent=2)+'\n');print('Runtime versions and lock hashes captured.')
