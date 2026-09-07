"""Record an actual GitHub Actions run, including the exact tested revision."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
run_id=sys.argv[1]
result=subprocess.run(['rtk','proxy','gh','run','view',run_id,'--json','databaseId,url,headSha,status,conclusion,jobs,startedAt,updatedAt'],cwd=ROOT,text=True,capture_output=True,check=True)
run=json.loads(result.stdout)
report={'status':'PASS' if run['conclusion']=='success' else 'FAIL' if run['status']=='completed' else 'NOT_RUN',
        'repository':'Mvstnz/ai-production-incident-control','profile':'FRESH_GITHUB_UBUNTU_RUNNER',
        'recorded_at':datetime.now(timezone.utc).isoformat(),'run':run,
        'limits':'This is a fresh local sandbox on GitHub, not a target-cloud n8n execution or live model evaluation.'}
destination=ROOT/'evidence/test-results'/(sys.argv[2] if len(sys.argv)>2 else 'github-ci.json')
destination.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'run_id':run_id,'tested_commit':run['headSha'],'url':run['url']}))
