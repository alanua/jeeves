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
        request_id="test",
        message="Please write a complex long term plan that takes multiple steps",
        session_id="test-session-124",
        user_id="user1",
        allow_tools=False,
        preferred_mode=None,
        metadata={},
        db=db_session
    )
    
    # It should fall back to executor and emit a warning
    assert res["selected_agent"] == "executor"
    assert any("planner agent not implemented; fell back to executor" in w for w in res["warnings"])
