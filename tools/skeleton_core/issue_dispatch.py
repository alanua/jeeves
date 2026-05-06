"""Local offline issue export dispatcher for Skeleton runner bridge."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.issue_runner_bridge import (
    BridgeRisk,
    BridgeStatus,
    IssueRunnerInput,
    RunnerRoute,
    build_issue_runner_packet,
)

IssueDispatchStatus = Literal["accepted", "blocked", "unknown_needs_review"]

RISK_TITLE_PATTERNS: tuple[tuple[str, BridgeRisk], ...] = (
    (r"\[agent-task-green\]", "GREEN"),
    (r"\[agent-task-yellow\]", "YELLOW"),
    (r"\[agent-task-orange\]", "ORANGE"),
    (r"\[agent-task-red\]", "RED"),
)


class IssueDispatchInput(BaseModel):
    """Public-safe GitHub issue export accepted by issue-dispatch."""

    model_config = ConfigDict(extra="ignore")

    repository: str
    issue_number: int | None = None
    number: int | None = None
    title: str
    body: str = ""
    comments: list[str] = Field(default_factory=list)
    state: str = "open"
    labels: list[str] = Field(default_factory=list)


class IssueDispatchPacket(BaseModel):
    """Normalized public-safe dispatch output for issue-runner-bridge."""

    model_config = ConfigDict(extra="forbid")

    issue_number: int
    repository: str
    status: IssueDispatchStatus
    risk_level: BridgeRisk
    runner_route: RunnerRoute
    review_required: bool
    merge_allowed: bool = False
    deploy_allowed: bool = False
    allowed_files: list[str] = Field(default_factory=list)
    expected_commands: list[str] = Field(default_factory=list)
    depends_on: list[int] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    next_action: str


def _issue_number(packet: IssueDispatchInput) -> int:
    return packet.issue_number or packet.number or 0


def _combined_text(packet: IssueDispatchInput) -> str:
    return "\n".join([packet.title, packet.body, *packet.comments])


def _infer_risk(packet: IssueDispatchInput) -> BridgeRisk:
    text = _combined_text(packet)
    for pattern, risk in RISK_TITLE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return risk
    return "UNKNOWN"


def _section_lines(body: str, headings: tuple[str, ...]) -> list[str]:
    lines = body.splitlines()
    captured: list[str] = []
    collecting = False
    for line in lines:
        stripped = line.strip()
        heading = stripped.strip("#:").casefold()
        if any(heading.startswith(candidate) for candidate in headings):
            collecting = True
            continue
        if collecting and stripped.startswith("##"):
            break
        if collecting and stripped:
            captured.append(stripped)
    return captured


def _clean_list_item(line: str) -> str:
    return line.strip().lstrip("-*").strip().strip("`")


def _extract_allowed_files(body: str) -> list[str]:
    lines = _section_lines(body, ("allowed files", "allowed files only"))
    files = []
    for line in lines:
        cleaned = _clean_list_item(line)
        if cleaned and not cleaned.startswith("```"):
            files.append(cleaned)
    return files


def _extract_expected_commands(body: str) -> list[str]:
    commands: list[str] = []
    in_fence = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```bash") or stripped.startswith("```shell"):
            in_fence = True
            continue
        if stripped.startswith("```"):
            in_fence = False
            continue
        if in_fence and stripped:
            commands.append(stripped)
    if commands:
        return commands

    lines = _section_lines(body, ("validation", "validation required", "expected commands"))
    return [_clean_list_item(line) for line in lines if _clean_list_item(line)]


def _extract_dependencies(packet: IssueDispatchInput) -> list[int]:
    text = _combined_text(packet)
    dependencies = set()
    for pattern in (
        r"depends[_ -]?on\s*#?(\d+)",
        r"blocked until\s*#?(\d+)",
        r"after\s*#(\d+)",
    ):
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            dependencies.add(int(match.group(1)))
    return sorted(dependencies)


def _bridge_input(packet: IssueDispatchInput, risk: BridgeRisk) -> IssueRunnerInput:
    return IssueRunnerInput(
        issue_number=_issue_number(packet),
        title=packet.title,
        body=packet.body,
        labels=packet.labels,
        risk_level=risk,
        project="skeleton",
        requested_by="oleksii",
    )


def build_issue_dispatch_packet(
    packet: IssueDispatchInput,
    *,
    run_bridge: bool = False,
    parent_queue: int | None = None,
    depends_on: list[int] | None = None,
) -> IssueDispatchPacket:
    """Normalize a public-safe issue export and optionally run issue-runner-bridge."""
    risk = _infer_risk(packet)
    issue_number = _issue_number(packet)
    dependencies = sorted(set(_extract_dependencies(packet) + (depends_on or [])))
    allowed_files = _extract_allowed_files(packet.body)
    expected_commands = _extract_expected_commands(packet.body)

    if run_bridge:
        bridge_result = build_issue_runner_packet(_bridge_input(packet, risk))
        status: BridgeStatus = bridge_result.status
        runner_route = bridge_result.runner_route
        review_required = bridge_result.review_required
        blockers = list(bridge_result.blockers)
        next_action = bridge_result.next_action
    else:
        status = "accepted" if risk in {"GREEN", "YELLOW"} else "unknown_needs_review"
        runner_route = (
            "RUNNER_YELLOW"
            if risk == "YELLOW"
            else "RUNNER_GREEN"
            if risk == "GREEN"
            else "BLOCKED"
        )
        review_required = risk == "YELLOW"
        blockers = [] if risk in {"GREEN", "YELLOW"} else [f"Unsupported risk level: {risk}"]
        next_action = "Run issue-runner-bridge for the normalized packet; do not merge or deploy."

    if parent_queue is not None:
        next_action = f"Parent queue #{parent_queue}. {next_action}"

    return IssueDispatchPacket(
        issue_number=issue_number,
        repository=packet.repository,
        status=status,
        risk_level=risk,
        runner_route=runner_route,
        review_required=review_required,
        merge_allowed=False,
        deploy_allowed=False,
        allowed_files=allowed_files,
        expected_commands=expected_commands,
        depends_on=dependencies,
        blockers=blockers,
        next_action=next_action,
    )


def build_issue_dispatch_packet_from_json(
    raw_json: str,
    *,
    run_bridge: bool = False,
    parent_queue: int | None = None,
    depends_on: list[int] | None = None,
) -> IssueDispatchPacket:
    """Validate local JSON text and build an issue dispatch packet."""
    return build_issue_dispatch_packet(
        IssueDispatchInput.model_validate_json(raw_json),
        run_bridge=run_bridge,
        parent_queue=parent_queue,
        depends_on=depends_on,
    )
