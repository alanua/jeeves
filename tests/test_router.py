from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import DefaultMode
from app.core.exceptions import ProviderError
from app.llm.base import Message, ProviderResponse
from app.llm.router import LLMRouter
from app.orchestration.task_classifier import TaskType, classify_task

# --- Task classifier ---

def test_classify_coding_task():
    assert classify_task("Write a Python function to sort a list") == TaskType.coding


def test_classify_research_task():
    assert classify_task("Summarize the latest research on neural networks") == TaskType.research


def test_classify_short_task_is_simple():
    assert classify_task("Hello there") == TaskType.simple


def test_classify_general_task():
    result = classify_task("Tell me about the history of the Roman Empire in detail and do not omit anything about it")
    assert result in (TaskType.general, TaskType.complex, TaskType.research)


# --- LLM Router ---

@pytest.mark.asyncio
async def test_router_uses_ollama_by_default():
    mock_resp = ProviderResponse(
        content="hello", model="llama3", provider="ollama"
    )
    router = LLMRouter()
    with patch.object(router._ollama, "generate", new_callable=AsyncMock, return_value=mock_resp):
        resp, fallback = await router.generate(
            messages=[Message(role="user", content="hi")],
            mode=DefaultMode.local_first,
        )
    assert resp.provider == "ollama"
    assert fallback is False


@pytest.mark.asyncio
async def test_router_falls_back_to_openrouter_on_ollama_failure():
    mock_fallback = ProviderResponse(
        content="from cloud", model="gpt-4o-mini", provider="openrouter"
    )
    router = LLMRouter()
    with (
        patch.object(
            router._ollama,
            "generate",
            new_callable=AsyncMock,
            side_effect=ProviderError("timeout"),
        ),
        patch.object(
            router._openrouter,
            "generate",
            new_callable=AsyncMock,
            return_value=mock_fallback,
        ),
        patch("app.core.config.settings.enable_cloud_fallback", new=True),
        patch("app.core.config.settings.openrouter_api_key", new="sk-test"),
    ):
        resp, fallback = await router.generate(
            messages=[Message(role="user", content="hi")],
            mode=DefaultMode.local_first,
        )
    assert resp.provider == "openrouter"
    assert fallback is True


@pytest.mark.asyncio
async def test_router_raises_when_all_fail():
    router = LLMRouter()
    with (
        patch.object(
            router._ollama,
            "generate",
            new_callable=AsyncMock,
            side_effect=ProviderError("timeout"),
        ),
        patch("app.core.config.settings.enable_cloud_fallback", new=False),
        pytest.raises(ProviderError),
    ):
        await router.generate(
            messages=[Message(role="user", content="hi")],
            mode=DefaultMode.local_first,
        )
