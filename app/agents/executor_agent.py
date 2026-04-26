from __future__ import annotations

import structlog

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.core.config import settings
from app.llm.base import GenerateOptions, Message
from app.llm.router import LLMRouter

log = structlog.get_logger(__name__)

_SYSTEM_PROMPT = """You are Jeeves, a helpful and precise AI assistant.
You answer questions clearly and concisely. You do not make up information.
If you are unsure, say so. You do not take actions outside of your conversation context."""


class ExecutorAgent(BaseAgent):
    """
    General-purpose executor agent.

    Handles all task types in the first vertical slice.
    Builds a message list from history + current message, calls the LLM router,
    and returns a structured AgentResult.
    """

    def __init__(self, llm_router: LLMRouter | None = None) -> None:
        self._router = llm_router or LLMRouter()

    @property
    def name(self) -> str:
        return "executor"

    def can_handle(self, task_type: str) -> bool:
        # The executor handles everything in Stage 1.
        return True

    async def execute(self, context: AgentContext) -> AgentResult:
        messages: list[Message] = []

        # Include recent session history for continuity
        for turn in context.history:
            messages.append(Message(role=turn["role"], content=turn["content"]))

        # Append current user message
        messages.append(Message(role="user", content=context.message))

        opts = GenerateOptions(temperature=0.7, max_tokens=2048)

        try:
            mode = settings.default_mode
            resp, fallback_used = await self._router.generate(
                messages=messages,
                system_prompt=_SYSTEM_PROMPT,
                options=opts,
                mode=mode,
                task_type=context.task_type,  # type: ignore[arg-type]
            )
        except Exception as exc:
            log.error(
                "executor_agent.generate_failed", error=str(exc), request_id=context.request_id
            )
            raise

        return AgentResult(
            agent_name=self.name,
            answer=resp.content,
            tool_calls=[],
            warnings=[],
            extra={
                "provider": resp.provider,
                "model": resp.model,
                "fallback_used": fallback_used,
                "prompt_tokens": resp.prompt_tokens,
                "completion_tokens": resp.completion_tokens,
            },
        )
