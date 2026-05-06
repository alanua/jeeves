"""Local offline project profile evaluator for Skeleton flow selection."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.capabilities import (
    DANGEROUS_DEFAULT_MARKERS,
    SAFE_FORBIDDEN_MARKERS,
    capability_flow,
    known_capability_names,
)

ProfileStatus = Literal[
    "ready",
    "blocked_unknown_capability",
    "blocked_unsafe_default",
    "unknown_needs_review",
]
RiskLevel = Literal["GREEN", "YELLOW", "ORANGE", "RED", "UNKNOWN"]


class ProjectSkeletonProfileInput(BaseModel):
    """Public-safe project profile input."""

    model_config = ConfigDict(extra="ignore")

    project: str = ""
    type: str = ""
    default_risk: RiskLevel = "UNKNOWN"
    allowed_skeleton_capabilities: list[str] = Field(default_factory=list)
    project_needs: list[str] = Field(default_factory=list)
    test_commands: list[str] = Field(default_factory=list)
    forbidden_by_default: list[str] = Field(default_factory=list)
    runtime_change_requires_explicit_approval: bool = True


class ProjectSkeletonProfilePacket(BaseModel):
    """Deterministic project development-flow packet."""

    model_config = ConfigDict(extra="forbid")

    project: str
    profile_status: ProfileStatus
    allowed_skeleton_capabilities: list[str] = Field(default_factory=list)
    development_flow: list[str] = Field(default_factory=list)
    recommended_next_gate: str | None = None
    risk_level: RiskLevel
    forbidden_by_default: list[str] = Field(default_factory=list)
    runtime_change_requires_explicit_approval: bool
    project_needs: list[str] = Field(default_factory=list)
    missing_capability_signals: list[str] = Field(default_factory=list)
    recommended_skeleton_skill_backlog: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    merge_allowed: bool = False
    deploy_allowed: bool = False


def _normalized_items(items: list[str]) -> list[str]:
    return [item.strip() for item in items if item.strip()]


def _unknown_capabilities(capabilities: list[str]) -> list[str]:
    known = known_capability_names()
    return sorted({capability for capability in capabilities if capability not in known})


def _unsafe_defaults(items: list[str]) -> list[str]:
    unsafe = []
    for item in items:
        normalized = item.strip().casefold()
        if normalized in DANGEROUS_DEFAULT_MARKERS:
            unsafe.append(item)
    return sorted(set(unsafe))


def _safe_forbidden_items(items: list[str]) -> list[str]:
    safe = []
    for item in items:
        normalized = item.strip().casefold()
        if normalized in SAFE_FORBIDDEN_MARKERS:
            safe.append(item)
    return sorted(set(safe))


def _missing_profile_fields(packet: ProjectSkeletonProfileInput) -> list[str]:
    missing = []
    if not packet.project.strip():
        missing.append("project")
    if not packet.type.strip():
        missing.append("type")
    if packet.default_risk == "UNKNOWN":
        missing.append("default_risk")
    if not packet.allowed_skeleton_capabilities:
        missing.append("allowed_skeleton_capabilities")
    return missing


def _missing_capability_signals(packet: ProjectSkeletonProfileInput) -> list[str]:
    known = known_capability_names()
    allowed = set(packet.allowed_skeleton_capabilities)
    signals = []
    for need in _normalized_items(packet.project_needs):
        if need not in known and need not in allowed:
            signals.append(need)
    return sorted(set(signals))


def _backlog(signals: list[str]) -> list[str]:
    return [f"Add a reviewed Skeleton capability for {signal}" for signal in signals]


def _recommended_next_gate(flow: list[str]) -> str | None:
    if "pr-review-gate" in flow:
        return "pr-review-gate"
    if flow:
        return flow[-1]
    return None


def build_project_skeleton_profile(
    packet: ProjectSkeletonProfileInput,
) -> ProjectSkeletonProfilePacket:
    """Build a local/offline project Skeleton profile packet."""
    allowed = _normalized_items(packet.allowed_skeleton_capabilities)
    forbidden = _normalized_items(packet.forbidden_by_default)
    unknown = _unknown_capabilities(allowed)
    unsafe_defaults = _unsafe_defaults(forbidden)
    missing_fields = _missing_profile_fields(packet)
    signals = _missing_capability_signals(packet)
    blockers: list[str] = []

    blockers.extend(f"Unknown Skeleton capability: {capability}" for capability in unknown)
    blockers.extend(f"Unsafe default grants authority: {item}" for item in unsafe_defaults)
    blockers.extend(f"Missing required profile field: {field}" for field in missing_fields)

    if unsafe_defaults:
        status: ProfileStatus = "blocked_unsafe_default"
    elif unknown:
        status = "blocked_unknown_capability"
    elif missing_fields:
        status = "unknown_needs_review"
    else:
        status = "ready"

    flow = capability_flow(packet.type, allowed) if status == "ready" else []

    return ProjectSkeletonProfilePacket(
        project=packet.project,
        profile_status=status,
        allowed_skeleton_capabilities=allowed,
        development_flow=flow,
        recommended_next_gate=_recommended_next_gate(flow),
        risk_level=packet.default_risk,
        forbidden_by_default=_safe_forbidden_items(forbidden),
        runtime_change_requires_explicit_approval=packet.runtime_change_requires_explicit_approval,
        project_needs=_normalized_items(packet.project_needs),
        missing_capability_signals=signals,
        recommended_skeleton_skill_backlog=_backlog(signals),
        blockers=sorted(set(blockers)),
        merge_allowed=False,
        deploy_allowed=False,
    )


def build_project_skeleton_profile_from_json(raw_json: str) -> ProjectSkeletonProfilePacket:
    """Validate local JSON text and build a project Skeleton profile packet."""
    return build_project_skeleton_profile(ProjectSkeletonProfileInput.model_validate_json(raw_json))
