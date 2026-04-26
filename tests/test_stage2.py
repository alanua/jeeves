from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.executor_agent import ExecutorAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.registry import AgentRegistry
from app.agents.research_agent import ResearchAgent
from app.llm.base import ProviderResponse
from app.memory.repository import MemoryRepository
from app.tools.registry import ToolRegistry

_MOCK_RESPONSE = ProviderResponse(
    content="Mock answer.",
    model="llama3",
    provider="ollama",
    prompt_tokens=5,
    completion_tokens=10,
)


def test_agent_registry():
    registry = AgentRegistry()
    agent = registry.get_agent("executor")
    assert isinstance(agent, ExecutorAgent)

    planet_agent = registry.get_agent("planner")
    assert isinstance(planet_agent, PlannerAgent)

    research_agent = registry.get_agent("research")
    assert isinstance(research_agent, ResearchAgent)

    with pytest.raises(ValueError, match="not found"):
        registry.get_agent("nonexistent")


@pytest.mark.asyncio
async def test_tool_shell_denial():
    registry = ToolRegistry()
    shell_tool = registry.get_tool("shell")
    result = await shell_tool.execute()
    assert not result.success
    assert "disabled" in result.error


@pytest.mark.asyncio
async def test_memory_repository(db_session):
    repo = MemoryRepository(db_session)
    session_id = "test-session-123"

    await repo.ensure_session(session_id)
    await repo.add_message(session_id, "user", "hello")
    await repo.add_message(session_id, "assistant", "world")

    history = await repo.get_recent_history(session_id, limit=10)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "world"


@pytest.mark.asyncio
async def test_orchestrator_planner_route(db_session):
    """Planner route returns selected_agent=planner with planning-framed warning."""
    from app.orchestration.orchestrator import Orchestrator

    with patch(
        "app.llm.providers.ollama_provider.OllamaProvider.generate",
        new_callable=AsyncMock,
        return_value=_MOCK_RESPONSE,
    ):
        orch = Orchestrator()
        res = await orch.handle(
            request_id="test-planner",
            message="Please write a complex long term plan that takes multiple steps",
            session_id="test-session-planner",
            user_id="user1",
            allow_tools=False,
            preferred_mode=None,
            metadata={},
            db=db_session,
        )

    assert res["selected_agent"] == "planner"
    assert any("Planner: output is structured planning framing" in w for w in res["warnings"])

    from sqlalchemy import select

    from app.db.models import Trace

    stmt = select(Trace).where(Trace.request_id == "test-planner")
    trace = (await db_session.execute(stmt)).scalar_one_or_none()
    assert trace is not None
    assert trace.selected_agent == "planner"
    assert trace.tool_calls_summary is None


@pytest.mark.asyncio
async def test_orchestrator_research_route(db_session):
    """Research route returns selected_agent=research with research-framed warning."""
    from app.orchestration.orchestrator import Orchestrator

    with patch(
        "app.llm.providers.ollama_provider.OllamaProvider.generate",
        new_callable=AsyncMock,
        return_value=_MOCK_RESPONSE,
    ):
        orch = Orchestrator()
        res = await orch.handle(
            request_id="test-research",
            message="Please research the top papers from the last decade",
            session_id="test-session-research",
            user_id="user1",
            allow_tools=False,
            preferred_mode=None,
            metadata={},
            db=db_session,
        )

    assert res["selected_agent"] == "research"
    assert any("Research: output is based on training data only" in w for w in res["warnings"])


@pytest.mark.asyncio
async def test_orchestrator_tool_shell_denial(db_session):
    """tool:shell with allow_tools=True returns structured denial, no execution."""
    from app.orchestration.orchestrator import Orchestrator

    with patch(
        "app.llm.providers.ollama_provider.OllamaProvider.generate",
        new_callable=AsyncMock,
        return_value=_MOCK_RESPONSE,
    ):
        orch = Orchestrator()
        res = await orch.handle(
            request_id="test-shell",
            message="tool:shell whoami",
            session_id="test-session-shell",
            user_id="user1",
            allow_tools=True,
            preferred_mode=None,
            metadata={},
            db=db_session,
        )

    assert len(res["tool_calls"]) == 1
    assert res["tool_calls"][0]["tool"] == "shell"
    assert res["tool_calls"][0]["status"] == "denied"
    assert "disabled in configuration" in res["tool_calls"][0]["reason"]
    assert any("disabled in configuration" in w for w in res["warnings"])

    from sqlalchemy import select

    from app.db.models import Trace

    stmt = select(Trace).where(Trace.request_id == "test-shell")
    trace = (await db_session.execute(stmt)).scalar_one_or_none()
    assert trace is not None
    assert trace.tool_calls_summary is not None
    assert trace.tool_calls_summary["calls"][0]["tool"] == "shell"
