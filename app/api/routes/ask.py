from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.ids import generate_request_id
from app.db.session import get_db
from app.orchestration.orchestrator import Orchestrator
from app.schemas.ask import AskRequest, AskResponse

log = structlog.get_logger(__name__)

router = APIRouter()

# Module-level orchestrator — stateless, safe to share across requests
_orchestrator = Orchestrator()
security = HTTPBearer(auto_error=False)


def verify_api_key(credentials: HTTPAuthorizationCredentials | None = Security(security)) -> str | None:
    if not credentials:
        from app.core.config import AppEnv
        if settings.app_env == AppEnv.development:
            log.info("ask.auth_bypassed", reason="development_mode")
            return "dev-bypass"
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )
    return credentials.credentials


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
) -> AskResponse:
    """
    Submit a task to Jeeves.

    The system will classify the task, select a provider (local or cloud),
    run the executor agent, and return the answer with trace metadata.
    """
    request_id = generate_request_id()
    session_id = request.session_id or str(uuid.uuid4())

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id, session_id=session_id)

    log.info(
        "ask.received",
        message_len=len(request.message),
        preferred_mode=request.preferred_mode,
        allow_tools=request.allow_tools,
    )

    result = await _orchestrator.handle(
        request_id=request_id,
        message=request.message,
        session_id=session_id,
        user_id=request.user_id,
        allow_tools=request.allow_tools,
        preferred_mode=request.preferred_mode.value if request.preferred_mode else None,
        metadata=request.metadata,
        db=db,
    )

    return AskResponse(**result)
