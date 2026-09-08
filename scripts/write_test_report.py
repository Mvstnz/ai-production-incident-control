"""Summarize only retained, observed test results."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
suite=ET.parse(ROOT/'evidence/test-results/domain-junit.xml').getroot().find('testsuite')
api=(ROOT/'docs/implementation/api-integration-output.txt').read_text(encoding='utf-8')
api_result=re.findall(r'\d+ passed[^\n]*',api)[-1].strip('= ')
lines=['# Current test report','','Only current ordinary manufacturing examples are represented. Missing runs are not inferred.','','| Check | Observed result |','| --- | --- |',f"| Unit tests | {suite.attrib['tests']} tests; {suite.attrib['failures']} failures; {suite.attrib['errors']} errors |",f'| PostgreSQL API | {api_result} |']
for name in ('local-e2e','resilience','acceptance-ordering'):
    p=ROOT/f'evidence/workflow-runs/{name}.json'
    if p.exists():
        report=read(str(p.relative_to(ROOT)));cases=report['tests']
        lines.append(f"| {name} | {sum(c['status']=='PASS' for c in cases)}/{len(cases)} passed |")
for name in ('rebootstrap','shared-showcase','secret-scan','browser','github-ci'):
    p=ROOT/f'evidence/test-results/{name}.json'
    if p.exists():lines.append(f"| {name} | {read(str(p.relative_to(ROOT))).get('status','See checks')} |")
for name in ('hosted-demo','hosted-actions'):
    report=read(f'evidence/workflow-runs/{name}.json')
    lines.append(f"| {name} | {report['status']} |")
lines+=['','Hosted action execution IDs: '+', '.join(a['execution_id'] for a in read('evidence/workflow-runs/hosted-actions.json')['actions'])+'.','','Live model evaluation: NOT_RUN; zero calls in the 50-case deterministic fixture evaluation. Email effects are captured in PostgreSQL or local Mailpit. See [hosting](hosting.md) for commands, workflow IDs, access, service limits and rollback boundaries.']
(ROOT/'docs/implementation/test-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
