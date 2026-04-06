from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class GenerateOptions:
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int | None = None


@dataclass
class ProviderResponse:
    content: str
    model: str
    provider: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    raw: dict = field(default_factory=dict)


class BaseProvider(ABC):
    """Abstract interface all LLM providers must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier, e.g. 'ollama' or 'openrouter'."""

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model this provider uses."""

    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
        options: GenerateOptions | None = None,
    ) -> ProviderResponse:
        """Generate a completion from the given message history."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable and functional."""
