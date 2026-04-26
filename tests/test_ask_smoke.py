from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.llm.base import ProviderResponse

MOCK_RESPONSE = ProviderResponse(
    content="The capital of France is Paris.",
    model="llama3",
    provider="ollama",
    prompt_tokens=10,
    completion_tokens=12,
)


@pytest.mark.asyncio
async def test_ask_returns_answer(client):
    """
    /ask smoke test with Ollama provider mocked.
    Verifies the full request-response cycle without a real LLM.
    """
    with patch(
        "app.llm.providers.ollama_provider.OllamaProvider.generate",
        new_callable=AsyncMock,
        return_value=MOCK_RESPONSE,
    ):
        resp = await client.post(
            "/ask",
            json={"message": "Tell me a joke"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "The capital of France is Paris."
    assert data["selected_agent"] == "executor"
    assert data["selected_provider"] == "ollama"
    assert data["fallback_used"] is False
    assert isinstance(data["latency_ms"], float)
    assert data["request_id"]


@pytest.mark.asyncio
async def test_ask_with_session_id_preserved(client):
    """Session ID provided by caller is echoed back in trace."""
    with patch(
        "app.llm.providers.ollama_provider.OllamaProvider.generate",
        new_callable=AsyncMock,
        return_value=MOCK_RESPONSE,
    ):
        resp = await client.post(
            "/ask",
            json={
                "message": "Hello",
                "session_id": "test-session-abc",
            },
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ask_fallback_triggered(client):
    """
    When Ollama fails, the system should fall back to OpenRouter.
    Both providers are mocked — Ollama raises, OpenRouter succeeds.
    """
    from app.core.exceptions import ProviderError

    openrouter_response = ProviderResponse(
        content="Fallback answer.",
        model="openai/gpt-4o-mini",
        provider="openrouter",
        prompt_tokens=8,
        completion_tokens=5,
    )

    with (
        patch(
            "app.llm.providers.ollama_provider.OllamaProvider.generate",
            new_callable=AsyncMock,
            side_effect=ProviderError("Ollama timeout"),
        ),
        patch(
            "app.llm.providers.openrouter_provider.OpenRouterProvider.generate",
            new_callable=AsyncMock,
            return_value=openrouter_response,
        ),
        patch(
            "app.core.config.settings.openrouter_api_key",
            new="sk-test-key",
        ),
        patch(
            "app.core.config.settings.enable_cloud_fallback",
            new=True,
        ),
    ):
        resp = await client.post("/ask", json={"message": "Tell me something"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["fallback_used"] is True
    assert data["selected_provider"] == "openrouter"


@pytest.mark.asyncio
async def test_ask_all_providers_fail_returns_error(client):
    """
    When all providers fail and fallback is disabled, /ask returns a graceful error message.
    """
    from app.core.exceptions import ProviderError

    with (
        patch(
            "app.llm.providers.ollama_provider.OllamaProvider.generate",
            new_callable=AsyncMock,
            side_effect=ProviderError("Ollama down"),
        ),
        patch(
            "app.core.config.settings.enable_cloud_fallback",
            new=False,
        ),
    ):
        resp = await client.post("/ask", json={"message": "Will this work?"})

    assert resp.status_code == 200
    data = resp.json()
    assert "[Error]" in data["answer"] or "[Policy" in data["answer"]
    assert len(data["warnings"]) > 0


@pytest.mark.asyncio
async def test_ask_unauthorized_in_prod(client):
    """
    Without a token, /ask should return 401 when not in development mode.
    """
    from httpx import ASGITransport, AsyncClient

    from app.core.config import AppEnv
    from app.main import app

    with patch("app.core.config.settings.app_env", new=AppEnv.production):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as anon_client:
            resp = await anon_client.post("/ask", json={"message": "Unauth request"})
            assert resp.status_code == 401
            assert "Missing Authorization" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_ask_authorized_with_invalid_token(client):
    """
    With an invalid token, /ask should return 401.
    """
    from httpx import ASGITransport, AsyncClient

    from app.core.config import AppEnv
    from app.main import app

    with patch("app.core.config.settings.app_env", new=AppEnv.production):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={"Authorization": "Bearer BAD_TOKEN"},
        ) as bad_client:
            resp = await bad_client.post("/ask", json={"message": "Bad token request"})
            assert resp.status_code == 401
            assert "Invalid API key" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_ask_session_history_continuity(client):
    """
    Verifies that a follow-up request correctly hydrates historical session messages
    from the database and injects them into the provider message list.
    """
    mock_generate = AsyncMock(return_value=MOCK_RESPONSE)

    with patch("app.llm.providers.ollama_provider.OllamaProvider.generate", mock_generate):
        # First request
        resp1 = await client.post(
            "/ask", json={"message": "First message", "session_id": "test-continuity-1"}
        )
        assert resp1.status_code == 200

        # Second request on the same session
        resp2 = await client.post(
            "/ask", json={"message": "Second message", "session_id": "test-continuity-1"}
        )
        assert resp2.status_code == 200

    assert mock_generate.call_count == 2

    second_call_args = mock_generate.call_args_list[1]
    kwargs = second_call_args.kwargs
    messages = kwargs.get("messages", second_call_args.args[0] if second_call_args.args else [])

    roles_contents = [(m.role, m.content) for m in messages]

    assert ("user", "First message") in roles_contents
    assert ("assistant", MOCK_RESPONSE.content) in roles_contents
    assert ("user", "Second message") in roles_contents
