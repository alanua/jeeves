from app.agents.base import BaseAgent
from app.agents.executor_agent import ExecutorAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, BaseAgent] = {
            "executor": ExecutorAgent(),
            "planner": PlannerAgent(),
            "research": ResearchAgent(),
        }

    def get_agent(self, name: str) -> BaseAgent:
        agent = self._agents.get(name)
        if agent is None:
            raise ValueError(f"Agent '{name}' not found in registry.")
        return agent
