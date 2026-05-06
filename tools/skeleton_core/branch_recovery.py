"""Offline branch recovery packet builder for interrupted Skeleton work."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RecoveryStatus = Literal[
    "completed",
    "needs_fix",
    "wait_for_ci_or_fetch_status",
    "create_pr_if_branch_ready",
    "unknown_needs_review",
]

FAILED_CI = {"failed", "failure", "error", "cancelled", "timed_out"}
WAITING_CI = {"", "missing", "pending", "queued", "in_progress", "waiting", "requested"}
SUCCESS_CI = {"success", "passed", "green"}


class BranchRecoveryInput(BaseModel):
    """Public-safe branch/PR status export accepted by branch-recovery."""

    model_config = ConfigDict(extra="ignore")

    branch_name: str
    issue_number: int | None = None
    pr_number: int | None = None
    pr_state: str = ""
    merged: bool = False
    merged_sha: str = ""
    changed_files: list[str] = Field(default_factory=list)
    ci_status: str = ""
    ci_blockers: list[str] = Field(default_factory=list)
    checkpoint_result: str = ""


class BranchRecoveryPacket(BaseModel):
    """Compact recovery packet for one interrupted branch."""

    model_config = ConfigDict(extra="forbid")

    branch_name: str
    issue_number: int | None
    pr_number: int | None
    status: RecoveryStatus
    merged_sha: str
    changed_files: list[str] = Field(default_factory=list)
    ci_status: str
    blockers: list[str] = Field(default_factory=list)
    merge_allowed: bool = False
    deploy_allowed: bool = False
    next_safe_action: str


def _normalize(value: str) -> str:
    return value.strip().casefold()


def _ci_status(raw_status: str) -> str:
    return _normalize(raw_status) or "missing"


def _blockers(packet: BranchRecoveryInput, fallback: str) -> list[str]:
    blockers = [item.strip() for item in packet.ci_blockers if item.strip()]
    return blockers or [fallback]


def _status_and_action(packet: BranchRecoveryInput) -> tuple[RecoveryStatus, list[str], str]:
    ci_status = _ci_status(packet.ci_status)
    pr_state = _normalize(packet.pr_state)

    if packet.merged or packet.merged_sha:
        return "completed", [], "checkpoint state and continue next task"

    if not packet.pr_number:
        return "create_pr_if_branch_ready", [], "create PR if branch is ready and scope is bounded"

    if pr_state == "closed":
        return "unknown_needs_review", ["PR is closed without merged=true"], "review closed PR state manually"

    if ci_status in FAILED_CI:
        return "needs_fix", _blockers(packet, "ci_failed"), "read job log summary, fix blocker, rerun CI"

    if ci_status in WAITING_CI:
        return "wait_for_ci_or_fetch_status", [], "wait for CI or fetch current PR status"

    if ci_status in SUCCESS_CI:
        return "unknown_needs_review", [], "review PR and request explicit merge approval if appropriate"

    return "unknown_needs_review", [f"unknown_ci_status:{ci_status}"], "review branch state manually"


def build_branch_recovery_packet(packet: BranchRecoveryInput) -> BranchRecoveryPacket:
    """Build a deterministic recovery packet without external calls or merge authority."""
    status, blockers, next_safe_action = _status_and_action(packet)
    return BranchRecoveryPacket(
        branch_name=packet.branch_name,
        issue_number=packet.issue_number,
        pr_number=packet.pr_number,
        status=status,
        merged_sha=packet.merged_sha,
        changed_files=packet.changed_files,
        ci_status=_ci_status(packet.ci_status),
        blockers=blockers,
        merge_allowed=False,
        deploy_allowed=False,
        next_safe_action=next_safe_action,
    )
