"""Vercel entrypoint. n8n still owns orchestration; the ERP keeps its own auth."""
from backend.main import app
from backend.erp import app as erp_app
from fastapi import APIRouter

# Preserve the existing /erp/v1 contracts and their separate service credentials.
app.include_router(APIRouter(routes=[route for route in erp_app.routes if route.path.startswith('/erp/')]))
