"""Document observed workflow IDs from the local and target readback manifests."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
local=json.loads((ROOT/'n8n/manifest.json').read_text())
target=json.loads((ROOT/'n8n/target/manifest.json').read_text())
bykey={w['key'].upper():w for w in target['workflows']}
lines=['# Workflow inventory','','Local state: published, graph readback matched source. Target state: created/read back, inactive, configuration blocked; zero target execution IDs. Readback is not an execution test.','','| Workflow | Local n8n ID | Target n8n ID | Target state |','|---|---|---|---|']
for w in local['workflows']:
    t=bykey[w['key'].upper()]
    lines.append(f"| {w['name'].replace('|','/')} | `{w['id']}` | [`{t['id']}`]({t['url']}) | Inactive / runtime NOT_RUN |")
lines+=['','Local probe: `APICPROBE0000001`, executed successfully. Target probe: `Fm2mFkzgF0jwFJEA`, created/read back, execution blocked. Neither is one of the ten core workflows.','','The local graph source is `n8n/workflows/`; sanitized persisted exports are `n8n/exports/local/`. Actual cloud exports and SDK builders are `n8n/target/`. See [target deployment](target-deployment.md) for missing credentials, configuration and graph drift.','','Actual local execution references are recorded in [E2E evidence](../../evidence/workflow-runs/local-e2e.json), [resilience evidence](../../evidence/workflow-runs/resilience.json) and the [browser verification](../../evidence/test-results/browser.json).']
(ROOT/'docs/implementation/workflow-inventory.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Observed local and target workflow inventory written.')
