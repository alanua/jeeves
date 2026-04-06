from __future__ import annotations

import httpx
import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import ProviderError
from app.llm.base import BaseProvider, GenerateOptions, Message, ProviderResponse

log = structlog.get_logger(__name__)


class OllamaProvider(BaseProvider):
    """
    Provider backed by a locally running Ollama instance.
    Uses the Ollama /api/chat HTTP endpoint.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self._base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self._model = model or settings.ollama_model_default
        self._timeout = timeout or settings.ollama_timeout_seconds

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def default_model(self) -> str:
        return self._model

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
        reraise=True,
    )
    async def generate(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
        options: GenerateOptions | None = None,
    ) -> ProviderResponse:
        opts = options or GenerateOptions()
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend({"role": m.role, "content": m.content} for m in messages)

        payload = {
            "model": self._model,
            "messages": payload_messages,
            "stream": False,
            "options": {
                "temperature": opts.temperature,
                "num_predict": opts.max_tokens,
            },
        }

        timeout = opts.timeout or self._timeout
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(f"{self._base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"Ollama HTTP error {exc.response.status_code}: {exc.response.text}") from exc
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            raise ProviderError(f"Ollama unreachable: {exc}") from exc

        msg = data.get("message", {})
        usage = data.get("usage", {})
        return ProviderResponse(
            content=msg.get("content", ""),
            model=data.get("model", self._model),
            provider=self.name,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            raw=data,
        )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self._base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
