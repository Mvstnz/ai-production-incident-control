"""Remove work from historical API test scopes only; preserve append-only history."""
from backend.db import transaction


def main():
    count=0
    with transaction(migration=True) as conn:
        scopes=conn.execute("SELECT id FROM ops.scopes WHERE name='API integration test' AND synthetic=true").fetchall()
        for row in scopes:
            sid=row["id"]
            users=conn.execute("SELECT u.id FROM ops.users u JOIN ops.memberships m ON m.user_id=u.id WHERE m.scope_id=%s AND u.username IN (%s,%s,%s,%s,%s,%s)",(sid,*[r+"-"+str(sid)[:8] for r in ("viewer","operator","purchasing","production_manager","quality_manager","admin")])).fetchall()
            conn.execute("DELETE FROM ops.incidents WHERE scope_id=%s",(sid,))
            conn.execute("DELETE FROM ops.source_events WHERE scope_id=%s",(sid,))
            conn.execute("DELETE FROM ops.outbox_events WHERE scope_id=%s",(sid,))
            conn.execute("DELETE FROM ops.workflow_errors WHERE scope_id=%s",(sid,))
            conn.execute("DELETE FROM ops.memberships WHERE scope_id=%s",(sid,))
            conn.execute("UPDATE ops.scopes SET owner_id=NULL WHERE id=%s",(sid,))
            for account in users:
                conn.execute("DELETE FROM ops.sessions WHERE user_id=%s",(account["id"],))
                conn.execute("DELETE FROM ops.memberships WHERE user_id=%s",(account["id"],))
                conn.execute("DELETE FROM ops.users WHERE id=%s",(account["id"],))
            count+=1
    print(f"Cleaned work/memberships from {count} API integration test scopes; audit and immutable snapshots retained.")


if __name__=="__main__": main()
