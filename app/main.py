from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.dashboard.router import router as dashboard_router
from app.security.auth import SecurityService
from app.security.middleware import SecurityMiddleware
from plugins.gowa.webhook import router as gowa_router
from plugins.n8n.api import router as n8n_api_router
from plugins.n8n.webhook import router as n8n_webhook_router

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
    lifespan=lifespan,
)
app.add_middleware(SecurityMiddleware)
app.state.security_service = SecurityService()
app.include_router(v1_router, prefix=settings.api_prefix)
app.include_router(dashboard_router)
app.include_router(gowa_router)
app.include_router(n8n_webhook_router)
app.include_router(n8n_api_router)
