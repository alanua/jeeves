from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.llm.providers.ollama_provider import OllamaProvider
from app.llm.providers.openrouter_provider import OpenRouterProvider

log = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Basic liveness check. Returns immediately."""
    return {"status": "ok"}


@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Readiness check.
    Verifies DB connectivity. Provider health is informational — the app
    is still considered ready even if Ollama is down (cloud fallback may work).
    """
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        log.warning("ready.db_failed", error=str(exc))

    ollama_ok = await OllamaProvider().health_check()
    openrouter_ok = await OpenRouterProvider().health_check()

    providers = {
        "ollama": "ok" if ollama_ok else "unavailable",
        "openrouter": "ok" if openrouter_ok else "unavailable",
    }

    overall = "ready" if db_ok else "degraded"

    return {
        "status": overall,
        "database": "ok" if db_ok else "unavailable",
        "providers": providers,
    }


@router.get("/metrics")
async def metrics() -> dict[str, Any]:
    """
    Minimal structured stats endpoint.
    Returns configuration-level info. Extend with counters as telemetry matures.
    """
    return {
        "app_env": settings.app_env.value,
        "default_mode": settings.default_mode.value,
        "cloud_fallback_enabled": settings.enable_cloud_fallback,
        "tools_enabled": {
            "shell": settings.tool_shell_enabled,
            "filesystem": settings.tool_filesystem_enabled,
            "http_fetch": settings.tool_http_enabled,
        },
    }
