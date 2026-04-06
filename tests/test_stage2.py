import pytest

from app.agents.executor_agent import ExecutorAgent
from app.agents.registry import AgentRegistry
from app.memory.repository import MemoryRepository
from app.tools.registry import ToolRegistry


def test_agent_registry():
    registry = AgentRegistry()
    agent = registry.get_agent("executor")
    assert isinstance(agent, ExecutorAgent)

    with pytest.raises(ValueError, match="not fully implemented"):
        registry.get_agent("planner")

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
async def test_orchestrator_deterministic_fallback(db_session, monkeypatch):
    from app.orchestration.orchestrator import Orchestrator
    
    # Mock Policy Engine so it doesn't fail on shell check if enabled
    class MockPolicy:
        def enforce_self_modification(self, msg): pass
        def enforce_tool_access(self, tool, allow_tools): pass
    
    # Mock LLM Router because we don't want to actually call the LLM
    from app.agents.base import AgentResult
    async def mock_execute(self, context):
        return AgentResult(
            agent_name="executor",
            answer="Mock response",
            tool_calls=[],
            warnings=[],
            extra={}
        )
    
    monkeypatch.setattr(ExecutorAgent, "execute", mock_execute)
    
    orch = Orchestrator()
    orch._policy = MockPolicy()
    
    # Test falling back on complex task (planner placeholder)
    res = await orch.handle(
        request_id="test1",
        message="Please write a complex long term plan that takes multiple steps",
        session_id="test-session-124",
        user_id="user1",
        allow_tools=False,
        preferred_mode=None,
        metadata={},
        db=db_session
    )
    
    assert res["selected_agent"] == "executor"
    assert any("planner agent not implemented; fell back to executor" in w for w in res["warnings"])

    # Verify trace was saved correctly with no tool summary
    from sqlalchemy import select

    from app.db.models import Trace
    stmt = select(Trace).where(Trace.request_id == "test1")
    trace = (await db_session.execute(stmt)).scalar_one_or_none()
    
    assert trace is not None
    assert trace.tool_calls_summary is None

@pytest.mark.asyncio
async def test_orchestrator_tool_shell_denial(db_session, monkeypatch):
    # Mock LLM Router to return successfully
    from app.agents.base import AgentResult
    from app.orchestration.orchestrator import Orchestrator
    async def mock_execute(self, context):
        return AgentResult(
            agent_name="executor",
            answer="I am an AI.",
            tool_calls=[],
            warnings=[],
            extra={}
        )
    monkeypatch.setattr(ExecutorAgent, "execute", mock_execute)
    
    orch = Orchestrator()
    # Explicitly test the orchestrator handles allow_tools=True and tool:shell input
    res = await orch.handle(
        request_id="test",
        message="tool:shell whoami",
        session_id="test-session-125",
        user_id="user1",
        allow_tools=True,
        preferred_mode=None,
        metadata={},
        db=db_session
    )
    
    assert res["answer"] == "I am an AI."
    assert len(res["tool_calls"]) == 1
    assert res["tool_calls"][0]["tool"] == "shell"
    assert res["tool_calls"][0]["status"] == "denied"
    assert "disabled in configuration" in res["tool_calls"][0]["reason"]
    assert any("disabled in configuration" in w for w in res["warnings"])
    
    # Verify trace was saved correctly
    from sqlalchemy import select

    from app.db.models import Trace
    stmt = select(Trace).where(Trace.request_id == "test")
    trace = (await db_session.execute(stmt)).scalar_one_or_none()
    
    assert trace is not None
    assert trace.tool_calls_summary is not None
    assert len(trace.tool_calls_summary["calls"]) == 1
    assert trace.tool_calls_summary["calls"][0]["tool"] == "shell"
