"""Deterministic offline bridge from public-safe GitHub issue exports to runner packets."""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

BridgeStatus = Literal["accepted", "blocked", "unknown_needs_review"]
BridgeRisk = Literal["GREEN", "YELLOW", "ORANGE", "RED", "UNKNOWN"]
RunnerRoute = Literal["RUNNER_GREEN", "RUNNER_YELLOW", "BLOCKED"]

ALLOWED_RISKS = {"GREEN", "YELLOW"}
BLOCKED_PATTERNS = {
    "merge": r"\bmerge\b|\bмердж\b|\bзмердж",
    "deploy": r"\bdeploy\b|\bdeployment\b|\bdeployed\b|\bдеплой",
    "release": r"\brelease\b|\bproduction release\b",
    "production": r"\bproduction\b|\bprod\b|\bпрод\b",
    "secret": r"\bsecret\b|\bsecrets\b|\btoken\b|\btokens\b|\bcredential\b|\bcredentials\b|api key|apikey|ключ",
    "network": r"\bnetwork\b|\bexternal service\b|\bexternal api\b|\blive mode\b|\bhttp[s]?://",
}


class IssueLabel(BaseModel):
    """Minimal public-safe label representation."""

    model_config = ConfigDict(extra="ignore")

    name: str


class IssueRunnerInput(BaseModel):
    """Public-safe issue export accepted by the local bridge."""

    model_config = ConfigDict(extra="ignore")

    issue_number: int | None = None
    number: int | None = None
    title: str
    body: str = ""
    labels: list[str | IssueLabel] = Field(default_factory=list)
    risk_level: str | None = None
    requested_by: str = "oleksii"
    project: str = "skeleton"


class IssueRunnerPacket(BaseModel):
    """Deterministic runner bridge result."""

    model_config = ConfigDict(extra="forbid")

    issue_number: int
    status: BridgeStatus
    risk_level: BridgeRisk
    runner_route: RunnerRoute
    review_required: bool
    merge_allowed: bool = False
    deploy_allowed: bool = False
    summary: str
    blockers: list[str] = Field(default_factory=list)
    next_action: str


def _label_name(label: str | IssueLabel) -> str:
    if isinstance(label, str):
        return label
    return label.name


def _risk_from_labels(labels: list[str | IssueLabel]) -> BridgeRisk:
    names = {_label_name(label).casefold() for label in labels}
    if "risk:green" in names or "green" in names:
        return "GREEN"
    if "risk:yellow" in names or "yellow" in names:
        return "YELLOW"
    if "risk:orange" in names or "orange" in names:
        return "ORANGE"
    if "risk:red" in names or "red" in names:
        return "RED"
    return "UNKNOWN"


def _normalize_risk(raw_risk: str | None, labels: list[str | IssueLabel]) -> BridgeRisk:
    if raw_risk:
        normalized = raw_risk.strip().upper()
        if normalized in {"GREEN", "YELLOW", "ORANGE", "RED"}:
            return normalized  # type: ignore[return-value]
    return _risk_from_labels(labels)


def _issue_number(packet: IssueRunnerInput) -> int:
    return packet.issue_number or packet.number or 0


def _content(packet: IssueRunnerInput) -> str:
    return f"{packet.title}\n{packet.body}"


def _safety_blockers(text: str) -> list[str]:
    blockers = []
    for name, pattern in BLOCKED_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            blockers.append(f"Blocked unsafe request: {name}")
    return blockers


def build_issue_runner_packet(packet: IssueRunnerInput) -> IssueRunnerPacket:
    """Build a deterministic bridge packet for GREEN/YELLOW issue exports only."""
    issue_number = _issue_number(packet)
    risk = _normalize_risk(packet.risk_level, packet.labels)
    safety_blockers = _safety_blockers(_content(packet))

    if safety_blockers:
        return IssueRunnerPacket(
            issue_number=issue_number,
            status="blocked",
            risk_level=risk,
            runner_route="BLOCKED",
            review_required=True,
            merge_allowed=False,
            deploy_allowed=False,
            summary=f"Issue #{issue_number} is blocked by the strict no-merge/no-deploy safety gate.",
            blockers=safety_blockers,
            next_action="Rewrite the issue to remove merge/deploy/secret/live-access scope, or request explicit human handling outside the runner bridge.",
        )

    if risk not in ALLOWED_RISKS:
        return IssueRunnerPacket(
            issue_number=issue_number,
            status="blocked" if risk in {"ORANGE", "RED"} else "unknown_needs_review",
            risk_level=risk,
            runner_route="BLOCKED",
            review_required=True,
            merge_allowed=False,
            deploy_allowed=False,
            summary=f"Issue #{issue_number} is not eligible for the GREEN/YELLOW runner bridge.",
            blockers=[f"Unsupported risk level: {risk}"],
            next_action="Route this issue through manual ChatGPT review or a higher-risk runner path; do not merge or deploy.",
        )

    review_required = risk == "YELLOW"
    runner_route: RunnerRoute = "RUNNER_YELLOW" if review_required else "RUNNER_GREEN"
    return IssueRunnerPacket(
        issue_number=issue_number,
        status="accepted",
        risk_level=risk,
        runner_route=runner_route,
        review_required=review_required,
        merge_allowed=False,
        deploy_allowed=False,
        summary=f"Issue #{issue_number} accepted for {runner_route} as an offline public-safe runner packet.",
        blockers=[],
        next_action="Create a branch and PR for the bounded task. Do not merge or deploy without explicit Oleksii approval.",
    )


def build_issue_runner_packet_from_raw(raw: dict[str, Any]) -> IssueRunnerPacket:
    """Validate raw JSON-compatible issue export and build a bridge packet."""
    return build_issue_runner_packet(IssueRunnerInput.model_validate(raw))
