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
