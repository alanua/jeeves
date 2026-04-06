from __future__ import annotations

import structlog

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.executor_agent import ExecutorAgent
from app.llm.router import LLMRouter

log = structlog.get_logger(__name__)


class PlannerAgent(BaseAgent):
    """
    Planner agent.

    For now, it acts as a concrete class but delegates all actual work to the standard ExecutorAgent
    while preserving its own 'planner' identity for the orchestration trace.
    """

    def __init__(self, llm_router: LLMRouter | None = None) -> None:
        self._executor = ExecutorAgent(llm_router)

    @property
    def name(self) -> str:
        return "planner"

    def can_handle(self, task_type: str) -> bool:
        return task_type == "complex"

    async def execute(self, context: AgentContext) -> AgentResult:
        log.info("planner_agent.execute.delegating", request_id=context.request_id)
        result = await self._executor.execute(context)
        # Ensure the selected_agent reflects the planner, not proxy
        result.agent_name = self.name
        # Note: warning is injected by the orchestrator in fallback, but here we are a real agent.
        # We can add a warning that it's a proxy for now, but keeping it minimal.
        result.warnings.append("Planner logic is currently delegated to base executor.")
        return result
