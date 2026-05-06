"""Offline task lifecycle packet builder for public-safe issue exports."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.issue_runner_bridge import (
    BridgeRisk,
    BridgeStatus,
    IssueRunnerInput,
    RunnerRoute,
    build_issue_runner_packet,
)

LifecycleStatus = Literal["accepted", "blocked", "unknown_needs_review"]


class InitialCheckpoint(BaseModel):
    """Small public-safe checkpoint skeleton for a queued runner task."""

    model_config = ConfigDict(extra="forbid")

    task_id: str
    project: str
    result: str
    next_safe_step: str


class TaskLifecyclePacket(BaseModel):
    """Compact lifecycle packet for one public-safe issue export."""

    model_config = ConfigDict(extra="forbid")

    issue_number: int
    status: LifecycleStatus
    risk_level: BridgeRisk
    runner_route: RunnerRoute
    review_required: bool
    merge_allowed: bool = False
    deploy_allowed: bool = False
    work_summary: str
    initial_checkpoint: InitialCheckpoint
    blockers: list[str] = Field(default_factory=list)
    next_safe_runner_instruction: str


def _issue_number(packet: IssueRunnerInput) -> int:
    return packet.issue_number or packet.number or 0


def _work_summary(packet: IssueRunnerInput) -> str:
    issue_number = _issue_number(packet)
    title = " ".join(packet.title.split())
    return f"Issue #{issue_number}: {title}"


def _checkpoint_result(status: BridgeStatus) -> str:
    if status == "accepted":
        return "queued"
    if status == "unknown_needs_review":
        return "unknown_needs_review"
    return "blocked"


def build_task_lifecycle_packet(packet: IssueRunnerInput) -> TaskLifecyclePacket:
    """Build one local/offline task lifecycle packet from a public-safe issue export."""
    bridge = build_issue_runner_packet(packet)
    issue_number = _issue_number(packet)
    next_safe_step = bridge.next_action

    return TaskLifecyclePacket(
        issue_number=issue_number,
        status=bridge.status,
        risk_level=bridge.risk_level,
        runner_route=bridge.runner_route,
        review_required=bridge.review_required,
        merge_allowed=False,
        deploy_allowed=False,
        work_summary=_work_summary(packet),
        initial_checkpoint=InitialCheckpoint(
            task_id=f"issue-{issue_number}",
            project=packet.project,
            result=_checkpoint_result(bridge.status),
            next_safe_step=next_safe_step,
        ),
        blockers=bridge.blockers,
        next_safe_runner_instruction=next_safe_step,
    )
