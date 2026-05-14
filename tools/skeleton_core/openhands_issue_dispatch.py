"""OpenHands issue dispatch v0 for Skeleton.

This module converts an issue-like payload into a bounded AdapterTaskPacket and
calls an injected OpenHands runner route.

It does not call GitHub, mutate labels, merge, deploy, restart services, or
launch OpenHands directly in tests.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.adapter_contract import AdapterTaskPacket, FuelPolicy
from tools.skeleton_core.openhands_runner_route import OpenHandsRunnerRouteReport

OPENHANDS_ISSUE_DISPATCH_VERSION = "openhands_issue_dispatch.v0"

REQUIRED_LABELS = {
    "agent:task",
    "agent:audited",
    "agent:plan-ready",
    "runner:openhands",
    "risk:yellow",
}

FORBIDDEN_LABELS = {
    "agent:running",
    "agent:blocked",
    "agent:executed",
    "risk:red",
}

DEFAULT_FORBIDDEN_PATHS = [
    ".env",
    ".git",
    ".ssh",
    "secrets",
    "tokens",
    "server",
    "production",
    "db",
]


class OpenHandsIssuePayload(BaseModel):
    """Public-safe issue-like dispatch payload."""

    model_config = ConfigDict(extra="forbid")

    issue_number: int
    repo: str
    title: str
    body: str = ""
    labels: list[str]
    allowed_files: list[str]
    expected_artifact: str = "diff"
    authority_level: str = "level_2_local_diff"
    risk_level: str = "yellow"
    fuel_provider: str = "openrouter"
    fuel_model: str = "deepseek/deepseek-v4-flash:free"
    fuel_max_usd: float = 1.0


class OpenHandsIssueDispatchReport(BaseModel):
    """Public-safe issue dispatch report."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    dispatch_version: str = OPENHANDS_ISSUE_DISPATCH_VERSION
    status: str
    blocked_reasons: list[str] = Field(default_factory=list)
    packet: AdapterTaskPacket | None = None
    route_report: OpenHandsRunnerRouteReport | None = None
    next_safe_step: str = ""


RouteFn = Callable[[AdapterTaskPacket], OpenHandsRunnerRouteReport]


def validate_issue_payload(payload: OpenHandsIssuePayload | dict[str, Any]) -> list[str]:
    """Validate labels and minimal dispatch scope."""

    issue = (
        payload
        if isinstance(payload, OpenHandsIssuePayload)
        else OpenHandsIssuePayload.model_validate(payload)
    )

    blocked: list[str] = []
    labels = set(issue.labels)

    missing = sorted(REQUIRED_LABELS - labels)
    blocked.extend(f"missing_label:{label}" for label in missing)

    forbidden = sorted(FORBIDDEN_LABELS & labels)
    blocked.extend(f"forbidden_label:{label}" for label in forbidden)

    if issue.issue_number <= 0:
        blocked.append("invalid_issue_number")
    if not issue.repo.strip():
        blocked.append("missing_repo")
    if not issue.title.strip():
        blocked.append("missing_title")
    if not issue.allowed_files:
        blocked.append("missing_allowed_files")
    if issue.risk_level != "yellow":
        blocked.append("risk_level_must_be_yellow_for_v0")
    if issue.authority_level == "level_5_forbidden":
        blocked.append("authority_level_forbidden")
    if issue.fuel_provider != "openrouter":
        blocked.append("fuel_provider_must_be_openrouter_for_v0")
    if not issue.fuel_model.strip():
        blocked.append("missing_fuel_model")
    if issue.fuel_max_usd < 0:
        blocked.append("negative_fuel_max_usd")

    return sorted(set(blocked))


def build_packet_from_issue(
    payload: OpenHandsIssuePayload | dict[str, Any],
) -> AdapterTaskPacket:
    """Build a bounded AdapterTaskPacket from an issue-like payload."""

    issue = (
        payload
        if isinstance(payload, OpenHandsIssuePayload)
        else OpenHandsIssuePayload.model_validate(payload)
    )

    return AdapterTaskPacket(
        task_id=f"issue-{issue.issue_number}-openhands",
        repo=issue.repo,
        allowed_files=issue.allowed_files,
        forbidden_paths=DEFAULT_FORBIDDEN_PATHS,
        authority_level=issue.authority_level,
        risk_level=issue.risk_level,
        expected_artifact=issue.expected_artifact,
        fuel_policy=FuelPolicy(
            provider=issue.fuel_provider,
            model=issue.fuel_model,
            max_usd=issue.fuel_max_usd,
        ),
    )


def dispatch_openhands_issue(
    payload: OpenHandsIssuePayload | dict[str, Any],
    *,
    route: RouteFn,
) -> OpenHandsIssueDispatchReport:
    """Validate an issue-like payload and call an injected route if safe."""

    issue = (
        payload
        if isinstance(payload, OpenHandsIssuePayload)
        else OpenHandsIssuePayload.model_validate(payload)
    )

    blocked = validate_issue_payload(issue)
    if blocked:
        return OpenHandsIssueDispatchReport(
            status="blocked",
            blocked_reasons=blocked,
            next_safe_step="Stop and fix issue labels/scope before dispatch.",
        )

    packet = build_packet_from_issue(issue)
    route_report = route(packet)

    return OpenHandsIssueDispatchReport(
        status="dispatched",
        packet=packet,
        route_report=route_report,
        next_safe_step="Review route report before any PR, merge, deploy, or label mutation.",
    )
