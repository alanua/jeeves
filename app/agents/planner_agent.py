from __future__ import annotations

import structlog

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.core.config import settings
from app.llm.base import GenerateOptions, Message
from app.llm.router import LLMRouter

log = structlog.get_logger(__name__)

_PLANNER_SYSTEM_PROMPT = """\
You are Jeeves, a planning-focused AI assistant.
Your job is to help the user produce a clear, concise, actionable plan.

When responding:
- Output a numbered list of concrete steps
- Each step should be specific and actionable
- Keep each step short (one sentence preferred)
- Do not claim to execute the steps yourself
- Do not pretend to browse the internet or access external systems
- If you are uncertain about a step, say so explicitly
- End with a brief summary of the overall approach

Do not write long prose. Structure is your primary output."""


class PlannerAgent(BaseAgent):
    """
    Planner agent.

    Produces structured, step-oriented plans using a planning-specific system prompt.
    Calls the LLM router directly with its own framing rather than proxying ExecutorAgent.
    """

    def __init__(self, llm_router: LLMRouter | None = None) -> None:
        self._router = llm_router or LLMRouter()

    @property
    def name(self) -> str:
        return "planner"

    def can_handle(self, task_type: str) -> bool:
        return task_type == "complex"

    async def execute(self, context: AgentContext) -> AgentResult:
        log.info("planner_agent.execute", request_id=context.request_id)

        messages: list[Message] = []
        for turn in context.history:
            messages.append(Message(role=turn["role"], content=turn["content"]))
        messages.append(Message(role="user", content=context.message))

        opts = GenerateOptions(temperature=0.5, max_tokens=2048)

        try:
            mode = settings.default_mode
            resp, fallback_used = await self._router.generate(
                messages=messages,
                system_prompt=_PLANNER_SYSTEM_PROMPT,
                options=opts,
                mode=mode,
                task_type=context.task_type,  # type: ignore[arg-type]
            )
        except Exception as exc:
            log.error(
                "planner_agent.generate_failed", error=str(exc), request_id=context.request_id
            )
            raise

        return AgentResult(
            agent_name=self.name,
            answer=resp.content,
            tool_calls=[],
            warnings=["Planner: output is structured planning framing, not execution."],
            extra={
                "provider": resp.provider,
                "model": resp.model,
                "fallback_used": fallback_used,
                "prompt_tokens": resp.prompt_tokens,
                "completion_tokens": resp.completion_tokens,
            },
        )
