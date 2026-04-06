from __future__ import annotations

import time

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext, AgentResult
from app.agents.registry import AgentRegistry
from app.core.exceptions import PolicyViolationError, ProviderError
from app.db.models import Trace
from app.memory.repository import MemoryRepository
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
        self._agent_registry = AgentRegistry()

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
        memory_repo = MemoryRepository(db)

        # --- Policy pre-flight ---
        self._policy.enforce_self_modification(message)
        # Pre-flight check for 'shell' crash removed to allow structured denial later.

        # --- Task classification ---
        task_type = classify_task(message)

        # --- Session memory (DB-backed) ---
        history = await memory_repo.get_recent_history(session_id, limit=10)

        # --- Ensure DB session row exists ---
        await memory_repo.ensure_session(session_id, user_id)

        # --- Persist user message ---
        await memory_repo.add_message(session_id, "user", message)

        # --- Select agent ---
        task_str = task_type.value
        if task_str == "complex":
            target_agent = "planner"
        elif task_str == "research":
            target_agent = "research"
        else:
            target_agent = "executor"

        registry_warning = None
        try:
            agent = self._agent_registry.get_agent(target_agent)
            agent_name = target_agent
        except ValueError as e:
            if "registered as a placeholder" in str(e):
                agent_name = "executor"
                agent = self._agent_registry.get_agent(agent_name)
                # Keep warning for later injection into response
                registry_warning = f"{target_agent} agent not implemented; fell back to executor"
            else:
                raise

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

        # --- Handle explicit tool intent ---
        from app.tools.handler import ToolHandler
        from app.tools.registry import ToolRegistry
        
        tool_handler = ToolHandler(self._policy, ToolRegistry())
        tool_calls, warning = await tool_handler.handle_tool_intent(message, allow_tools)
        
        if warning:
            if registry_warning:
                registry_warning += f" | {warning}"
            else:
                registry_warning = warning

        fallback_used = False
        warnings: list[str] = []
        if registry_warning:
            warnings.append(registry_warning)
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
            for w in result.warnings:
                warnings.append(w)
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
        await memory_repo.add_message(session_id, "assistant", answer)

        # --- Persist trace ---
        summary_payload = {"calls": tool_calls} if tool_calls else None
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
                tool_calls_summary=summary_payload,
            )
        )

        await db.commit()

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
            "tool_calls": tool_calls,
            "latency_ms": round(latency_ms, 2),
            "warnings": warnings,
        }
