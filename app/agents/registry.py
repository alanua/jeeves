from app.agents.base import BaseAgent
from app.agents.executor_agent import ExecutorAgent


class AgentRegistry:
    def __init__(self):
        self._agents = {
            "executor": ExecutorAgent(),
            "planner": None, # Placeholder
            "research": None, # Placeholder
        }

    def get_agent(self, name: str) -> BaseAgent:
        agent = self._agents.get(name)
        if agent is None:
            if name in self._agents:
                raise ValueError(f"Agent '{name}' is registered as a placeholder but not fully implemented.")
            raise ValueError(f"Agent '{name}' not found in registry.")
        return agent
