from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    """All information an agent needs to produce a response."""
    request_id: str
    session_id: str
    user_id: str | None
    message: str
    allow_tools: bool
    task_type: str
    history: list[dict[str, str]] = field(default_factory=list)  # [{role, content}, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """The output of a single agent execution."""
    agent_name: str
    answer: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Minimal contract every agent must satisfy.

    Agents are stateless — all context is passed in per-call.
    State persistence is the orchestrator's responsibility.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier."""

    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """Return True if this agent can handle the given task type."""

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Run the agent and return its result."""
