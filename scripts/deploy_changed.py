"""Redeploy only named owned local workflows, with a prior supported-CLI export."""
import sys,json
from bootstrap import ROOT,run,compose,wait,wait_published_webhook
from n8n_io import backup_owned
run('proxy',sys.executable,'scripts/build_workflows.py')
manifest=json.loads((ROOT/'n8n/manifest.example.json').read_text())
requested=set(sys.argv[1:])
assert requested and requested<={w['key'] for w in manifest['workflows']}
backup_owned([w for w in manifest['workflows'] if w['key'] in requested])
for w in manifest['workflows']:
    if w['key'] not in requested:continue
    compose('exec','-T','n8n','n8n','import:workflow',f"--input=/project/n8n/workflows/{w['file']}")
    compose('exec','-T','n8n','n8n','publish:workflow',f"--id={w['id']}")
compose('restart','n8n','n8n-runners')
wait('http://127.0.0.1:5678/healthz')
wait_published_webhook()
