from __future__ import annotations

import structlog

from app.llm.base import BaseProvider, GenerateOptions, Message, ProviderResponse

log = structlog.get_logger(__name__)


class MockProvider(BaseProvider):
    """
    A safe mock provider used for local testing when no external providers are reachable.
    """

    @property
    def name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return "mock-model"

    async def generate(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
        options: GenerateOptions | None = None,
    ) -> ProviderResponse:
        log.info("mock_provider.generate_called", message_count=len(messages))
        return ProviderResponse(
            content="This is a mock answer for testing.",
            model=self.default_model,
            provider=self.name,
            prompt_tokens=10,
            completion_tokens=10,
        )

    async def health_check(self) -> bool:
        return True
