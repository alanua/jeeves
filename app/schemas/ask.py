from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PreferredMode(str, Enum):
    local_first = "local_first"
    cloud_first = "cloud_first"
    cheapest = "cheapest"
    strongest = "strongest"


class AskRequest(BaseModel):
    message: str = Field(
        ..., min_length=1, max_length=32_000, description="The user's task or question"
    )
    session_id: str | None = Field(None, description="Conversation session identifier")
    user_id: str | None = Field(None, description="Optional user identifier")
    preferred_mode: PreferredMode | None = Field(
        None, description="Provider selection strategy override"
    )
    allow_tools: bool = Field(False, description="Allow tool use for this request")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary caller metadata")


class AskResponse(BaseModel):
    request_id: str
    answer: str
    selected_agent: str
    selected_provider: str
    selected_model: str
    fallback_used: bool
    tool_calls: list[dict[str, Any]]
    latency_ms: float
    warnings: list[str]
