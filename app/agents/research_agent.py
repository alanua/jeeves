from __future__ import annotations

import structlog

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.core.config import settings
from app.llm.base import GenerateOptions, Message
from app.llm.router import LLMRouter

log = structlog.get_logger(__name__)

_RESEARCH_SYSTEM_PROMPT = """\
You are Jeeves, a research-focused AI assistant.
Your job is to help the user synthesize information on a topic clearly and honestly.

When responding:
- Distinguish between what you know with confidence and what is uncertain
- Use phrases like "Based on my training data..." or "I'm not certain, but..." where appropriate
- Do not claim to browse the internet or access live sources
- Do not fabricate citations or paper titles
- If asked about recent events, note that your knowledge has a cutoff date
- Organize your response with a brief introduction, key points, and a conclusion
- Prefer accuracy over completeness — it is better to say less than to hallucinate

Structure your response clearly. Use headings or bullet points where helpful."""


class ResearchAgent(BaseAgent):
    """
    Research agent.

    Produces synthesis-oriented responses using a research-specific system prompt.
    Calls the LLM router directly with its own framing rather than proxying ExecutorAgent.
    """

    def __init__(self, llm_router: LLMRouter | None = None) -> None:
        self._router = llm_router or LLMRouter()

    @property
    def name(self) -> str:
        return "research"

    def can_handle(self, task_type: str) -> bool:
        return task_type == "research"

    async def execute(self, context: AgentContext) -> AgentResult:
        log.info("research_agent.execute", request_id=context.request_id)

        messages: list[Message] = []
        for turn in context.history:
            messages.append(Message(role=turn["role"], content=turn["content"]))
        messages.append(Message(role="user", content=context.message))

        opts = GenerateOptions(temperature=0.6, max_tokens=2048)

        try:
            mode = settings.default_mode
            resp, fallback_used = await self._router.generate(
                messages=messages,
                system_prompt=_RESEARCH_SYSTEM_PROMPT,
                options=opts,
                mode=mode,
                task_type=context.task_type,  # type: ignore[arg-type]
            )
        except Exception as exc:
            log.error("research_agent.generate_failed", error=str(exc), request_id=context.request_id)
            raise

        return AgentResult(
            agent_name=self.name,
            answer=resp.content,
            tool_calls=[],
            warnings=["Research: output is based on training data only — no live browsing."],
            extra={
                "provider": resp.provider,
                "model": resp.model,
                "fallback_used": fallback_used,
                "prompt_tokens": resp.prompt_tokens,
                "completion_tokens": resp.completion_tokens,
            },
        )
