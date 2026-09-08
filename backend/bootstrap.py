"""python -m backend.bootstrap: migrations and idempotent synthetic seed."""
import json
import os
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from backend.db import transaction, uid
from backend.security import passwords
from backend.seed import ROOT, seed_scope
from backend.datasets import dataset_name, demo_clock

DEFAULT_SCOPE = str(uuid5(NAMESPACE_URL,"apic-portfolio/default-demo/fictional-v2"))


def main():
    with transaction(migration=True) as conn:
        conn.execute("SELECT pg_advisory_xact_lock(hashtext('apic:migrations'))")
        conn.execute("CREATE SCHEMA IF NOT EXISTS ops")
        conn.execute("CREATE TABLE IF NOT EXISTS ops.schema_migrations(version text PRIMARY KEY,applied_at timestamptz NOT NULL DEFAULT now())")
        for path in sorted((ROOT/"database"/"migrations").glob("*.sql")):
            if not conn.execute("SELECT 1 FROM ops.schema_migrations WHERE version=%s",(path.name,)).fetchone():
                conn.execute(path.read_text(encoding="utf-8"))
                conn.execute("INSERT INTO ops.schema_migrations(version) VALUES (%s)",(path.name,))
        creds = Path(os.getenv("APIC_CREDENTIALS_FILE",str(ROOT/".local"/"credentials.json")))
        content=json.loads(creds.read_text())
        users=content.get("users",[])
        if isinstance(users,dict):
            users=[{"username":key,"role":key,**(value if isinstance(value,dict) else {"password":value})} for key,value in users.items()]
        if not users:
            raise RuntimeError("Bootstrap requires generated users in APIC_CREDENTIALS_FILE")
        for user in users:
            if not conn.execute("SELECT 1 FROM ops.users WHERE username=%s",(user["username"],)).fetchone():
                conn.execute("INSERT INTO ops.users VALUES (%s,%s,%s,%s)",(uid(),user["username"],passwords.hash(user["password"]),user["role"]))
        admin=conn.execute("SELECT id FROM ops.users WHERE role='admin' LIMIT 1").fetchone()
        conn.execute("INSERT INTO ops.scopes(id,name,owner_id,clock_at) VALUES (%s,'APIC · Invented manufacturing world',%s,%s) ON CONFLICT DO NOTHING",(DEFAULT_SCOPE,admin["id"],demo_clock()))
        conn.execute("INSERT INTO ops.memberships SELECT %s,id FROM ops.users ON CONFLICT DO NOTHING",(DEFAULT_SCOPE,))
        seed_scope(conn,DEFAULT_SCOPE)
        roles={r["rolname"] for r in conn.execute("SELECT rolname FROM pg_roles").fetchall()}
        if "apic_app" in roles:
            conn.execute("GRANT USAGE ON SCHEMA ops,erp TO apic_app; GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA ops TO apic_app; GRANT SELECT ON erp.snapshots TO apic_app; REVOKE UPDATE,DELETE ON ops.audit_events FROM apic_app")
        if "apic_erp" in roles:
            conn.execute("GRANT USAGE ON SCHEMA ops,erp TO apic_erp; GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA erp TO apic_erp; GRANT SELECT ON ops.scopes,ops.incident_actions,ops.action_plans,ops.incidents,ops.approvals,ops.failures TO apic_erp; GRANT UPDATE(erp_revision) ON ops.scopes TO apic_erp")
    print(json.dumps({"status":"bootstrapped","default_scope_id":DEFAULT_SCOPE,"synthetic":True}))


if __name__ == "__main__":
    main()
