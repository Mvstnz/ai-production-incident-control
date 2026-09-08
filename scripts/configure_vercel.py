"""Upload only runtime environment variables through Vercel's documented API."""
import json
import subprocess
from pathlib import Path
import re
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parents[1]


def main():
    project=json.loads((ROOT/'.vercel/project.json').read_text())
    env=json.loads((ROOT/'.local/hosted-env.json').read_text())
    body=[{'key':key,'value':value,'type':'sensitive','target':['production','preview']} for key,value in env.items() if key!='MIGRATION_DATABASE_URL']
    if len(sys.argv)>1: body=[row for row in body if row['key'] in sys.argv[1:]]
    payload=ROOT/'.local/vercel-env-payload.json'
    payload.write_text(json.dumps(body),encoding='utf-8')
    def upload(row):
        command=['rtk','proxy','npx','--yes','vercel@59.11.7','env','add',row['key'],'production','--scope','pattaya-pimps','--force']
        if any(word in row['key'] for word in ('TOKEN','SECRET','DATABASE')): command.append('--sensitive')
        response=subprocess.run(command,cwd=ROOT,input=row['value'],capture_output=True,text=True,encoding='utf-8')
        if response.returncode:
            safe=response.stderr
            for value in env.values():
                if len(value)>8: safe=safe.replace(value,'[redacted]')
            print(safe[:1200])
            raise RuntimeError('Vercel rejected environment variable '+row['key'])
        print('Configured '+row['key'],flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool: list(pool.map(upload,body))
    print(f'Configured {len(body)} protected runtime variables. Migration credentials stay local.')


if __name__=='__main__': main()
