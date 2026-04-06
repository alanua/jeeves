from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ask, health
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import engine

configure_logging(settings.app_log_level)

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("jeeves.startup", env=settings.app_env, port=settings.app_port)
    # Schema is now managed purely by Alembic migrations during normal execution.
    # Test schemas can be isolated in test fixtures.
    yield
    log.info("jeeves.shutdown")
    await engine.dispose()


app = FastAPI(
    title="Jeeves",
    description="Local-first multi-agent orchestration system",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["ops"])
app.include_router(ask.router, tags=["core"])
