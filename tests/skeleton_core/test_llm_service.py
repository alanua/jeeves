from __future__ import annotations

import pytest

from tools.skeleton_core import llm_service
from tools.skeleton_core.llm_service import LLMServicePanic


def test_required_env_fails_closed_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(llm_service, "_load_dotenv_once", lambda: None)

    with pytest.raises(LLMServicePanic):
        llm_service._required_env("OPENAI_API_KEY")


def test_query_openai_blocks_empty_prompt() -> None:
    with pytest.raises(LLMServicePanic):
        llm_service.query_openai("")


def test_query_gemini_blocks_empty_prompt() -> None:
    with pytest.raises(LLMServicePanic):
        llm_service.query_gemini("")
