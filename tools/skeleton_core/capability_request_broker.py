"""Local/offline broker for converting project blockers into Skeleton skill requests."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CapabilityRequestStatus = Literal[
    "capability_request_ready",
    "capability_already_exists",
    "blocked_unsafe_capability",
    "unknown_needs_review",
]
RiskLevel = Literal["YELLOW", "RED", "UNKNOWN"]

UNSAFE_PATTERNS = {
    "live_executor": r"live executor|autonomous executor|execute live",
    "merge": r"\bmerge\b|auto-merge",
    "deploy": r"\bdeploy\b|deployment|release",
    "server": r"server ssh|\bssh\b|production server",
    "production_db": r"production db|production database|prod db",
    "secret": r"\.env|\bsecret\b|\bsecrets\b|\btoken\b|api key|apikey|credential|password",
    "runtime_change": r"runtime change|change runtime|modify runtime",
}


class CapabilityRequestInput(BaseModel):
    """Public-safe project capability request input."""

    model_config = ConfigDict(extra="ignore")

    project: str = ""
    repository: str = ""
    source_issue: int | None = None
    blocker_or_need: str = ""
    manual_steps_repeated: list[str] = Field(default_factory=list)
    desired_capability: str = ""
    safety_constraints: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    existing_capabilities: list[str] = Field(default_factory=list)


class CapabilityRequestPacket(BaseModel):
    """Structured Skeleton skill request packet."""

    model_config = ConfigDict(extra="forbid")

    status: CapabilityRequestStatus
    capability_name: str = ""
    source_project: str = ""
    source_repository: str = ""
    source_issue: int | None = None
    need_summary: str = ""
    risk_level: RiskLevel = "UNKNOWN"
    recommended_skeleton_issue_title: str = ""
    recommended_skeleton_issue_body: str = ""
    allowed_scope: list[str] = Field(default_factory=list)
    forbidden_scope: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    links_or_references: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    merge_allowed: bool = False
    deploy_allowed: bool = False
    next_safe_step: str


def _clean(value: str) -> str:
    return " ".join(value.strip().split())


def _clean_items(items: list[str]) -> list[str]:
    return [_clean(item) for item in items if _clean(item)]


def _slug(value: str) -> str:
    lowered = value.strip().casefold().replace("_", "-")
    return re.sub(r"[^a-z0-9-]+", "-", lowered).strip("-")


def _unsafe_text(packet: CapabilityRequestInput) -> str:
    """Text that represents requested capability, excluding safety constraints."""
    parts = [
        packet.project,
        packet.repository,
        packet.blocker_or_need,
        packet.desired_capability,
        "\n".join(packet.manual_steps_repeated),
        "\n".join(packet.evidence),
    ]
    return "\n".join(parts)


def _unsafe_blockers(packet: CapabilityRequestInput) -> list[str]:
    text = _unsafe_text(packet)
    blockers = []
    for name, pattern in UNSAFE_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            blockers.append(f"Unsafe capability request detected: {name}")
    return sorted(set(blockers))


def _has_enough_evidence(packet: CapabilityRequestInput) -> bool:
    return bool(
        _clean(packet.project)
        and _clean(packet.blocker_or_need)
        and _clean(packet.desired_capability)
        and (_clean_items(packet.manual_steps_repeated) or _clean_items(packet.evidence))
    )


def _existing_capability(packet: CapabilityRequestInput) -> bool:
    desired = _slug(packet.desired_capability)
    existing = {_slug(item) for item in packet.existing_capabilities}
    return bool(desired and desired in existing)


def _issue_title(capability_name: str) -> str:
    return f"[agent-task-yellow] Add Skeleton {capability_name} command"


def _allowed_scope(capability_name: str) -> list[str]:
    return [
        f"Add local/offline {capability_name} packet builder.",
        "Read public-safe JSON input only.",
        "Emit reviewable Skeleton issue title/body and status packet.",
        "Add tests and fixtures.",
    ]


def _forbidden_scope() -> list[str]:
    return [
        "No GitHub issue creation from CLI in v1.",
        "No live GitHub API calls from CLI in v1.",
        "No runner execution.",
        "No shell execution.",
        "No merge/deploy authority.",
        "No server SSH or production DB access.",
        "No .env reads or writes.",
        "No secrets or private data in outputs.",
        "No runtime code changes.",
    ]


def _acceptance_criteria(capability_name: str) -> list[str]:
    return [
        f"{capability_name} emits deterministic ready/blocked/unknown statuses.",
        "Unsafe live/merge/deploy/server/secrets requests are blocked.",
        "Unknown or under-evidenced requests require review.",
        "Output always has merge_allowed=false and deploy_allowed=false.",
        "CLI is local/offline/read-only.",
        "Tests and CI pass.",
    ]


def _issue_body(packet: CapabilityRequestInput, capability_name: str) -> str:
    manual_steps = _clean_items(packet.manual_steps_repeated)
    evidence = _clean_items(packet.evidence)
    constraints = _clean_items(packet.safety_constraints)
    lines = [
        f"# YELLOW — Add Skeleton {capability_name} command",
        "",
        "## Source project need",
        "",
        f"Project: {packet.project or 'unknown'}",
        f"Repository: {packet.repository or 'unknown'}",
        f"Source issue: {packet.source_issue if packet.source_issue is not None else 'unknown'}",
        "",
        "## Need summary",
        "",
        _clean(packet.blocker_or_need) or "Unknown need.",
        "",
        "## Repeated manual steps",
        "",
    ]
    lines.extend([f"- {item}" for item in manual_steps] or ["- unknown"])
    lines.extend(["", "## Evidence", ""])
    lines.extend([f"- {item}" for item in evidence] or ["- needs review"])
    lines.extend(["", "## Safety constraints", ""])
    lines.extend([f"- {item}" for item in constraints] or ["- local/offline/public-safe v1"])
    lines.extend(
        [
            "",
            "## Required safety",
            "",
            "```text",
            "Local/offline/public-safe JSON only.",
            "No GitHub writes from CLI in v1.",
            "No live API calls.",
            "No runner execution.",
            "No .env reads.",
            "No secrets.",
            "No merge/deploy authority.",
            "No runtime changes.",
            "```",
        ]
    )
    return "\n".join(lines)


def _next_safe_step(status: CapabilityRequestStatus) -> str:
    if status == "capability_request_ready":
        return "Review and post this as a Skeleton issue if still needed."
    if status == "capability_already_exists":
        return "Update the project workflow to use the existing Skeleton capability."
    if status == "blocked_unsafe_capability":
        return "Stop and redesign the request into a safe local/offline capability, if possible."
    return "Add evidence or narrow the capability request before creating a Skeleton issue."


def build_capability_request(packet: CapabilityRequestInput) -> CapabilityRequestPacket:
    """Build a deterministic capability request packet from a project need."""
    capability_name = _slug(packet.desired_capability)
    blockers = _unsafe_blockers(packet)
    if blockers:
        status: CapabilityRequestStatus = "blocked_unsafe_capability"
        risk_level: RiskLevel = "RED"
    elif _existing_capability(packet):
        status = "capability_already_exists"
        risk_level = "YELLOW"
    elif not _has_enough_evidence(packet):
        status = "unknown_needs_review"
        risk_level = "UNKNOWN"
    else:
        status = "capability_request_ready"
        risk_level = "YELLOW"

    title = _issue_title(capability_name) if capability_name else ""
    issue_body = (
        "" if status == "blocked_unsafe_capability" else _issue_body(packet, capability_name)
    )
    return CapabilityRequestPacket(
        status=status,
        capability_name=capability_name,
        source_project=_clean(packet.project),
        source_repository=_clean(packet.repository),
        source_issue=packet.source_issue,
        need_summary=_clean(packet.blocker_or_need),
        risk_level=risk_level,
        recommended_skeleton_issue_title=title,
        recommended_skeleton_issue_body=issue_body,
        allowed_scope=(
            [] if status == "blocked_unsafe_capability" else _allowed_scope(capability_name)
        ),
        forbidden_scope=_forbidden_scope(),
        acceptance_criteria=(
            [] if status == "blocked_unsafe_capability" else _acceptance_criteria(capability_name)
        ),
        links_or_references=_clean_items(packet.evidence),
        blockers=blockers,
        merge_allowed=False,
        deploy_allowed=False,
        next_safe_step=_next_safe_step(status),
    )


def build_capability_request_from_json(raw_json: str) -> CapabilityRequestPacket:
    """Validate local JSON text and build a capability request packet."""
    return build_capability_request(CapabilityRequestInput.model_validate_json(raw_json))
