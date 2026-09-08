import hashlib
import hmac
import os
import re
import secrets
from collections import defaultdict, deque
from datetime import timedelta
from time import monotonic

from argon2 import PasswordHasher
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from backend.db import transaction, utcnow

passwords = PasswordHasher()
attempts = defaultdict(deque)


def hashed(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def token(request, header, env):
    configured = os.getenv(env, "")
    supplied = request.headers.get(header, "")
    if len(configured) < 24 or not hmac.compare_digest(configured, supplied):
        raise HTTPException(401, "Invalid service credential")


def service(request: Request):
    token(request, "x-service-token", "SERVICE_TOKEN")


def origin(request):
    allowed = os.getenv("DASHBOARD_ORIGIN", "http://127.0.0.1:5173").split(",")
    if request.headers.get("origin") not in allowed:
        raise HTTPException(403, "Origin is not allowed")


def user(request: Request):
    rate_limit(request,"user-api",300)
    raw = request.cookies.get("apic_session", "")
    if not raw:
        raise HTTPException(401, "Login required")
    with transaction() as conn:
        found = conn.execute("""SELECT u.id,u.username,u.role,s.csrf_hash FROM ops.sessions s
            JOIN ops.users u ON u.id=s.user_id WHERE s.token_hash=%s AND s.expires_at>%s""",
            (hashed(raw), utcnow())).fetchone()
    if not found:
        raise HTTPException(401, "Session expired")
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin(request)
        if not hmac.compare_digest(found["csrf_hash"], hashed(request.headers.get("x-csrf-token", ""))):
            raise HTTPException(403, "CSRF verification failed")
    return found


def scope(conn, actor, scope_id):
    from uuid import UUID
    try: scope_id=UUID(str(scope_id))
    except (ValueError,TypeError): raise HTTPException(422,"A valid scope UUID is required")
    row = conn.execute("""SELECT s.* FROM ops.scopes s JOIN ops.memberships m ON m.scope_id=s.id
        WHERE s.id=%s AND m.user_id=%s""", (scope_id, actor["id"])).fetchone()
    if not row:
        raise HTTPException(403, "Scope access denied")
    return row


def role(actor, *roles):
    """Allow listed roles while treating authenticated admins as app superusers."""
    if actor["role"] != "admin" and actor["role"] not in roles:
        raise HTTPException(403, "Role is not permitted for this command")


def safe_message(value):
    text = str(value)[:2000]
    text = re.sub(r"(?i)(bearer\s+|(?:token|password|secret|authorization)[=: ]+)[^\s,;]+", r"\1[redacted]", text)
    text = re.sub(r"https?://[^\s]+", "[url redacted]", text)
    return text


class BodyLimitMiddleware:
    """Bound streamed payloads as well as Content-Length, before parsing/auth."""
    def __init__(self, app, limit=131072):
        self.app, self.limit = app, limit

    async def __call__(self, scope_, receive, send):
        if scope_["type"] != "http":
            return await self.app(scope_, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > self.limit:
                return await JSONResponse({"error_code":"PAYLOAD_TOO_LARGE","message":"Request exceeds 128 KiB","retryable":False},413)(scope_,receive,send)
            if not message.get("more_body"):
                break
        delivered = False
        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type":"http.request","body":bytes(body),"more_body":False}
            return await receive()
        await self.app(scope_, replay, send)


def rate_limit(request, bucket="login", limit=15):
    key = (bucket, request.client.host if request.client else "unknown")
    q, current = attempts[key], monotonic()
    while q and q[0] < current-60:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(429, "Rate limit exceeded", headers={"Retry-After":"60"})
    q.append(current)
