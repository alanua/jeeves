"""Minimal read-only LLM connectivity service for Skeleton Core.

Sprint 10 scope:
- load API keys from environment / dotenv
- fail closed if keys are missing
- provide synchronous ping-grade query helpers
- do not write files
- do not print secrets
- do not grant execution powers
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


class LLMServicePanic(RuntimeError):
    """Fail-closed LLM service panic."""


_DOTENV_LOADED = False


def _load_dotenv_once() -> None:
    global _DOTENV_LOADED

    if _DOTENV_LOADED:
        return

    # Do not print paths or values. Load common runner locations only.
    candidates = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path("/home/agent/agent-dev/.env"),
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            load_dotenv(dotenv_path=candidate, override=False)

    # Also allow python-dotenv's default discovery as a fallback.
    load_dotenv(override=False)

    _DOTENV_LOADED = True


def _required_env(name: str) -> str:
    _load_dotenv_once()
    value = os.environ.get(name, "").strip()
    if not value:
        raise LLMServicePanic(f"missing_required_env:{name}")
    return value


def query_openai(prompt: str, model: str = "gpt-4o") -> str:
    """Query OpenAI once and return text output.

    Read-only network call. No files are written.
    """

    if not prompt.strip():
        raise LLMServicePanic("empty_openai_prompt")

    from openai import OpenAI

    api_key = _required_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=32,
    )

    text = getattr(response, "output_text", "") or ""
    text = text.strip()

    if not text:
        raise LLMServicePanic("empty_openai_response")

    return text


def query_gemini(prompt: str, model: str = "gemini-2.5-pro") -> str:
    """Query Gemini once and return text output.

    Read-only network call. No files are written.
    """

    if not prompt.strip():
        raise LLMServicePanic("empty_gemini_prompt")

    from google import genai

    api_key = _required_env("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    text = getattr(response, "text", "") or ""
    text = text.strip()

    if not text:
        raise LLMServicePanic("empty_gemini_response")

    return text
