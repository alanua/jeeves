"""Local offline recovery packet builder for interrupted Skeleton branches."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BranchRecoveryStatus = Literal[
    "completed",
    "needs_fix",
    "wait_for_ci_or_fetch_status",
    "create_pr_if_branch_ready",
    "unknown_needs_review",
]
CIStatus = Literal["success", "failed", "pending", "missing", "unknown"]


class BranchRecoveryInput(BaseModel):
    """Public-safe interrupted branch export."""

    model_config = ConfigDict(extra="ignore")

    branch_name: str
    issue_number: int | None = None
    pr_number: int | None = None
    pr_state: str | None = None
    merged: bool = False
    merged_sha: str = ""
    changed_files: list[str] = Field(default_factory=list)
    ci_status: CIStatus = "unknown"
    ci_blockers: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    checkpoint_result: str | None = None


class BranchRecoveryPacket(BaseModel):
    """Deterministic branch recovery output."""

    model_config = ConfigDict(extra="forbid")

    branch_name: str
    issue_number: int | None = None
    pr_number: int | None = None
    status: BranchRecoveryStatus
    merged_sha: str = ""
    changed_files: list[str] = Field(default_factory=list)
    ci_status: CIStatus
    blockers: list[str] = Field(default_factory=list)
    merge_allowed: bool = False
    deploy_allowed: bool = False
    next_safe_action: str


def _combined_blockers(packet: BranchRecoveryInput) -> list[str]:
    blockers = [*packet.blockers, *packet.ci_blockers]
    if packet.pr_state and packet.pr_state.casefold() not in {"open", "closed", "merged"}:
        blockers.append(f"Unknown PR state: {packet.pr_state}")
    return sorted(set(item for item in blockers if item))


def _has_open_pr(packet: BranchRecoveryInput) -> bool:
    return packet.pr_number is not None and (packet.pr_state or "open").casefold() == "open"


def _has_any_pr(packet: BranchRecoveryInput) -> bool:
    return packet.pr_number is not None


def _next_action(status: BranchRecoveryStatus) -> str:
    if status == "completed":
        return "checkpoint state and continue next task"
    if status == "needs_fix":
        return "read job log summary, fix blocker, rerun CI"
    if status == "wait_for_ci_or_fetch_status":
        return "wait for CI or fetch public-safe PR status export"
    if status == "create_pr_if_branch_ready":
        return "create draft PR if branch diff is still needed and public-safe"
    return "manual review required before continuing"


def build_branch_recovery(packet: BranchRecoveryInput) -> BranchRecoveryPacket:
    """Build a local/offline recovery packet for an interrupted branch."""
    blockers = _combined_blockers(packet)

    if packet.merged:
        status: BranchRecoveryStatus = "completed"
    elif _has_open_pr(packet) and packet.ci_status == "failed":
        status = "needs_fix"
    elif _has_open_pr(packet) and packet.ci_status in {"missing", "pending", "unknown"}:
        status = "wait_for_ci_or_fetch_status"
    elif not _has_any_pr(packet) and packet.changed_files:
        status = "create_pr_if_branch_ready"
    else:
        status = "unknown_needs_review"

    if packet.merged and not packet.merged_sha:
        blockers.append("Merged PR has no merged_sha in export")
        status = "unknown_needs_review"
    if status == "needs_fix" and not blockers:
        blockers.append("CI failed without blocker details")
    if not packet.branch_name.strip():
        blockers.append("Missing branch_name")
        status = "unknown_needs_review"

    return BranchRecoveryPacket(
        branch_name=packet.branch_name,
        issue_number=packet.issue_number,
        pr_number=packet.pr_number,
        status=status,
        merged_sha=packet.merged_sha,
        changed_files=packet.changed_files,
        ci_status=packet.ci_status,
        blockers=sorted(set(blockers)),
        merge_allowed=False,
        deploy_allowed=False,
        next_safe_action=_next_action(status),
    )


def build_branch_recovery_from_json(raw_json: str) -> BranchRecoveryPacket:
    """Validate local JSON text and build a branch recovery packet."""
    return build_branch_recovery(BranchRecoveryInput.model_validate_json(raw_json))
