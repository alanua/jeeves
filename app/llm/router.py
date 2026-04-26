from __future__ import annotations

import structlog

from app.core.config import DefaultMode, settings
from app.core.exceptions import ProviderError
from app.llm.base import BaseProvider, GenerateOptions, Message, ProviderResponse
from app.llm.providers.ollama_provider import OllamaProvider
from app.llm.providers.openrouter_provider import OpenRouterProvider
from app.orchestration.task_classifier import TaskType

log = structlog.get_logger(__name__)


class LLMRouter:
    """
    Routes generation requests to the appropriate provider.

    Strategy:
    - local_first: try Ollama, fall back to OpenRouter if enabled and Ollama fails
    - cloud_first: try OpenRouter, fall back to Ollama
    - cheapest: alias for local_first
    - strongest: alias for cloud_first

    Provider selection is config-driven. Fallback is opt-in via ENABLE_CLOUD_FALLBACK.
    """

    def __init__(self) -> None:
        self._ollama = OllamaProvider()
        self._openrouter = OpenRouterProvider()

        from app.llm.providers.mock_provider import MockProvider

        self._mock = MockProvider()

    def _preferred_order(self, mode: DefaultMode, task_type: TaskType) -> list[BaseProvider]:
        """Return providers in preference order for the given mode."""
        if settings.mock_provider_enabled:
            return [self._mock]
        if mode in (DefaultMode.local_first, DefaultMode.cheapest):
            return [self._ollama, self._openrouter]
        if mode in (DefaultMode.cloud_first, DefaultMode.strongest):
            return [self._openrouter, self._ollama]
        return [self._ollama, self._openrouter]

    async def generate(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
        options: GenerateOptions | None = None,
        mode: DefaultMode | None = None,
        task_type: TaskType = TaskType.general,
    ) -> tuple[ProviderResponse, bool]:
        """
        Attempt generation with preferred provider, falling back if allowed.

        Returns:
            (response, fallback_used)
        """
        effective_mode = mode or settings.default_mode
        providers = self._preferred_order(effective_mode, task_type)

        primary = providers[0]
        fallbacks = providers[1:]

        try:
            resp = await primary.generate(messages, system_prompt, options)
            log.info(
                "llm.generate.success",
                provider=primary.name,
                model=resp.model,
                task_type=task_type,
            )
            return resp, False
        except ProviderError as exc:
            log.warning(
                "llm.generate.primary_failed",
                provider=primary.name,
                error=str(exc),
            )

        if not settings.enable_cloud_fallback:
            raise ProviderError(
                f"Primary provider '{primary.name}' failed and cloud fallback is disabled"
            )

        for fallback in fallbacks:
            # Skip OpenRouter if no API key configured
            if fallback.name == "openrouter" and not settings.openrouter_api_key:
                log.warning(
                    "llm.generate.fallback_skipped", provider=fallback.name, reason="no_api_key"
                )
                continue
            try:
                resp = await fallback.generate(messages, system_prompt, options)
                log.info(
                    "llm.generate.fallback_success",
                    provider=fallback.name,
                    model=resp.model,
                    task_type=task_type,
                )
                return resp, True
            except ProviderError as exc:
                log.warning(
                    "llm.generate.fallback_failed",
                    provider=fallback.name,
                    error=str(exc),
                )

        raise ProviderError("All providers failed to generate a response")
