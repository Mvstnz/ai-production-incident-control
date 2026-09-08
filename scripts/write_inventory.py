"""Render the inventory from actual local and cloud manifests."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
target=json.loads((ROOT/'n8n/target/manifest.json').read_text(encoding='utf-8'))
lines=['# Workflow inventory','','Published cloud graph readbacks. Execution evidence is recorded separately in hosting.md.','','| Workflow | Cloud ID | State |','| --- | --- | --- |']
for w in target['workflows']:
    lines.append(f"| {w['name'].replace('|','/')} | [{w['id']}]({w['url']}) | {'Published' if w['active'] else 'Unpublished'} |")
lines+=['','Actual cloud graphs: n8n/target/wf01.json through wf10.json. Local source graphs: n8n/workflows/. Local persisted readbacks: n8n/exports/local/. Credential values are excluded.']
(ROOT/'docs/implementation/workflow-inventory.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
