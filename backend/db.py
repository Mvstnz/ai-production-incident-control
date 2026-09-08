"""Short PostgreSQL transactions; no SQLite fallback and no n8n table access."""
import hashlib
import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


def uid():
    return str(uuid4())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=lambda x:x.isoformat() if hasattr(x,"isoformat") else str(x))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def js(value):
    return Jsonb(json.loads(canonical(value)))


@contextmanager
def transaction(erp=False, migration=False):
    key = "MIGRATION_DATABASE_URL" if migration else "ERP_DATABASE_URL" if erp else "DATABASE_URL"
    url = os.environ.get(key) or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(f"Required configuration {key} is missing")
    # Supabase transaction pooling cannot retain prepared statements across transactions.
    with psycopg.connect(url, row_factory=dict_row, connect_timeout=8, prepare_threshold=None) as conn:
        with conn.transaction():
            yield conn


def now(conn, scope_id):
    row = conn.execute("SELECT clock_at FROM ops.scopes WHERE id=%s", (scope_id,)).fetchone()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(404, "Scope not found")
    return row["clock_at"]


def utcnow():
    return datetime.now(timezone.utc)


def audit(conn, scope_id, event, object_id, actor="service:n8n", data=None, correlation_id=None):
    conn.execute("""INSERT INTO ops.audit_events
        (id,scope_id,event,object_id,actor,data,correlation_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (uid(), scope_id, event, str(object_id), actor, js(data or {}), correlation_id))


def outbox(conn, scope_id, key, kind, payload):
    conn.execute("""INSERT INTO ops.outbox_events (id,scope_id,event_key,kind,payload)
        VALUES (%s,%s,%s,%s,%s) ON CONFLICT(scope_id,event_key) DO NOTHING""",
        (uid(), scope_id, key, kind, js(payload)))
