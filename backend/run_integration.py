"""Host runner: real PostgreSQL, separate apic_integration DB, no n8n test jobs.

Usage: python -m backend.run_integration
Requires the project's bootstrapped Compose PostgreSQL and Mailpit services.
Secrets are read from the ignored .env and passed in environment, never printed.
"""
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]


def run(args,env=None,input_=None,output_path=None):
    result=subprocess.run(["rtk","proxy","docker","compose",*args],cwd=ROOT,env=env,input=input_,text=True,capture_output=True)
    print(result.stdout,end="")
    print(result.stderr,end="",file=sys.stderr)
    if output_path:
        output_path.write_text("Execution: python -m backend.run_integration\nDatabase: apic_integration (PostgreSQL; separate from demo and n8n)\n"+result.stdout+result.stderr,encoding="utf-8")
    if result.returncode: raise SystemExit(result.returncode)
    return result.stdout+result.stderr


def main():
    env_file={}
    for line in (ROOT/".env").read_text().splitlines():
        if line and not line.startswith("#") and "=" in line:
            key,value=line.split("=",1);env_file[key]=value.strip().strip('"').strip("'")
    password=env_file["DB_OWNER_PASSWORD"]
    env={**os.environ,"DATABASE_URL":f"postgresql://apic_owner:{quote(password,safe='')}@postgres:5432/apic_integration"}
    env["MIGRATION_DATABASE_URL"]=env["DATABASE_URL"]
    run(["exec","-T","postgres","psql","-v","ON_ERROR_STOP=1","-U","apic_owner","-d","postgres"],input_="SELECT 'CREATE DATABASE apic_integration OWNER apic_owner' WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname='apic_integration')\\gexec\n")
    mounts=[]
    for name in ("backend","database","config","tests"):
        mounts += ["-v",f"{ROOT/name}:/app/{name}:ro"]
    common=["run","--rm","-e","DATABASE_URL","-e","MIGRATION_DATABASE_URL",*mounts,"bootstrap"]
    run([*common,"python","-m","backend.bootstrap"],env)
    destination=ROOT/"docs"/"implementation"/"api-integration-output.txt"
    run([*common,"python","-m","pytest","tests/integration/","-v","--tb=short","-p","no:cacheprovider"],env,output_path=destination)


if __name__=="__main__": main()
