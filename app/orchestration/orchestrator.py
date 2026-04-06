from __future__ import annotations

import time

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext, AgentResult
from app.agents.executor_agent import ExecutorAgent
from app.core.exceptions import PolicyViolationError, ProviderError
from app.db.models import Message as DBMessage
from app.db.models import Session as DBSession
from app.db.models import Trace
from app.orchestration.task_classifier import classify_task
from app.policy.engine import PolicyEngine

log = structlog.get_logger(__name__)


class Orchestrator:
    """
    Main coordination point for a single /ask request.

    Responsibilities:
    - enforce pre-flight policy checks
    - classify the task
    - load session history from session memory
    - select and execute agent
    - persist messages and trace to DB
    - return a structured result to the API layer
    """

    def __init__(self) -> None:
        self._policy = PolicyEngine()
        self._executor = ExecutorAgent()

    async def handle(
        self,
        request_id: str,
        message: str,
        session_id: str,
        user_id: str | None,
        allow_tools: bool,
        preferred_mode: str | None,
        metadata: dict,
        db: AsyncSession,
    ) -> dict:
        start_ms = time.monotonic()

        # --- Policy pre-flight ---
        self._policy.enforce_self_modification(message)
        if allow_tools:
            # Stage 1: Explicitly log/enforce the policy bypass for tools
            # Even if they ask for tools, if they aren't enabled in config, crash.
            # E.g. Check 'shell' just to trigger the default deny.
            self._policy.enforce_tool_access("shell", allow_tools=allow_tools)

        # --- Task classification ---
        task_type = classify_task(message)

        # --- Session memory (DB-backed) ---
        from sqlalchemy import select
        stmt = (
            select(DBMessage)
            .where(DBMessage.session_id == session_id)
            .order_by(DBMessage.created_at.desc())
            .limit(10)
        )
        recent = (await db.scalars(stmt)).all()
        history = [{"role": msg.role, "content": msg.content} for msg in reversed(recent)]

        # --- Ensure DB session row exists ---
        existing = await db.get(DBSession, session_id)
        if existing is None:
            db_session = DBSession(id=session_id, user_id=user_id)
            db.add(db_session)

        # --- Persist user message ---
        db.add(DBMessage(session_id=session_id, role="user", content=message))

        # --- Select agent (always executor in Stage 1) ---
        agent = self._executor
        context = AgentContext(
            request_id=request_id,
            session_id=session_id,
            user_id=user_id,
            message=message,
            allow_tools=allow_tools,
            task_type=task_type.value,
            history=history,
            metadata=metadata,
        )

        fallback_used = False
        warnings: list[str] = []
        answer = ""
        provider = "unknown"
        model = "unknown"
        prompt_tokens = None
        completion_tokens = None
        success = True
        error_msg = None

        try:
            result: AgentResult = await agent.execute(context)
            answer = result.answer
            provider = result.extra.get("provider", "unknown")
            model = result.extra.get("model", "unknown")
            fallback_used = result.extra.get("fallback_used", False)
            prompt_tokens = result.extra.get("prompt_tokens")
            completion_tokens = result.extra.get("completion_tokens")
            warnings = result.warnings
        except PolicyViolationError as exc:
            success = False
            error_msg = exc.reason
            answer = f"[Policy Denied] {exc.reason}"
            warnings.append(error_msg)
        except ProviderError as exc:
            success = False
            error_msg = str(exc)
            answer = "[Error] All providers failed. Please check your configuration."
            warnings.append(error_msg)
        except Exception as exc:
            success = False
            error_msg = str(exc)
            answer = "[Error] An unexpected error occurred."
            warnings.append(error_msg)
            log.exception("orchestrator.unexpected_error", error=error_msg, request_id=request_id)

        latency_ms = (time.monotonic() - start_ms) * 1000

        # --- Persist assistant message ---
        db.add(DBMessage(session_id=session_id, role="assistant", content=answer))

        # --- Persist trace ---
        db.add(
            Trace(
                request_id=request_id,
                session_id=session_id,
                user_id=user_id,
                task_type=task_type.value,
                selected_agent=agent.name,
                selected_provider=provider,
                selected_model=model,
                fallback_used=fallback_used,
                latency_ms=round(latency_ms, 2),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                success=success,
                error=error_msg,
                tool_calls_summary=None,
            )
        )

        await db.commit()

        # Session memory is fully DB-backed now

        log.info(
            "orchestrator.done",
            request_id=request_id,
            session_id=session_id,
            task_type=task_type.value,
            agent=agent.name,
            provider=provider,
            model=model,
            fallback_used=fallback_used,
            latency_ms=round(latency_ms, 2),
            success=success,
        )

        return {
            "request_id": request_id,
            "answer": answer,
            "selected_agent": agent.name,
            "selected_provider": provider,
            "selected_model": model,
            "fallback_used": fallback_used,
            "tool_calls": [],
            "latency_ms": round(latency_ms, 2),
            "warnings": warnings,
        }
