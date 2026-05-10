from __future__ import annotations

import os

import pytest

from tools.skeleton_core.yellow_runnerd import _check_live_env


def test_live_env_missing_key_blocks_before_queue_consumption(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_LIVE_MODE", raising=False)

    with pytest.raises(RuntimeError, match="missing_gemini_api_key_env_for_yellow_runnerd"):
        _check_live_env("live")


def test_live_env_with_key_sets_live_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "AIza" + "x" * 35)
    monkeypatch.delenv("GEMINI_API_LIVE_MODE", raising=False)

    _check_live_env("live")

    assert os.environ["GEMINI_API_LIVE_MODE"] == "true"


def test_mock_env_does_not_require_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    _check_live_env("mock")
