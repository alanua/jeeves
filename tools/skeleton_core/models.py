"""Decision models for the ChatGPT Exoskeleton core CLI."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(StrEnum):
    """Skeleton task risk level."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"


class RouteTarget(StrEnum):
    """Execution route selected by the Skeleton gate."""

    CHATGPT_ONLY = "CHATGPT_ONLY"
    RUNNER_GREEN = "RUNNER_GREEN"
    RUNNER_YELLOW = "RUNNER_YELLOW"
    RUNNER_ORANGE = "RUNNER_ORANGE"
    BLOCKED_RED = "BLOCKED_RED"


class EvidencePolicy(StrEnum):
    """Evidence sources allowed for later review, without calling them in this CLI."""

    NONE = "NONE"
    MANUAL_EVIDENCE_ALLOWED = "MANUAL_EVIDENCE_ALLOWED"
    GEMINI_EVIDENCE_ALLOWED = "GEMINI_EVIDENCE_ALLOWED"
    ANTIGRAVITY_EVIDENCE_ALLOWED = "ANTIGRAVITY_EVIDENCE_ALLOWED"
    PRIVATE_EVIDENCE_REQUIRES_REVIEW = "PRIVATE_EVIDENCE_REQUIRES_REVIEW"


class TaskPacket(BaseModel):
    """User task normalized into a Skeleton decision packet."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    project: str = Field(default="skeleton", min_length=1)
    requested_by: str = Field(default="oleksii", min_length=1)
    evidence_policy: EvidencePolicy = EvidencePolicy.NONE


class RouteDecision(BaseModel):
    """Routing decision for a task packet."""

    model_config = ConfigDict(extra="forbid")

    risk_level: RiskLevel
    route_target: RouteTarget
    evidence_policy: EvidencePolicy
    blocked_reason: str | None = None
