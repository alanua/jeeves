from __future__ import annotations


class JeevesError(Exception):
    """Base exception for all Jeeves errors."""


class ProviderError(JeevesError):
    """Raised when an LLM provider fails."""


class PolicyViolationError(JeevesError):
    """Raised when a policy check denies an action."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class AgentError(JeevesError):
    """Raised when an agent encounters an unrecoverable error."""


class MemoryError(JeevesError):
    """Raised on memory read/write failures."""
