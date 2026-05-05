"""Deterministic PR status reader for public-safe exported GitHub/CI data."""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PRStatusValue = Literal[
    "ready_to_merge",
    "blocked",
    "needs_fix",
    "waiting_for_ci",
    "unknown_needs_review",
]
CIStateValue = Literal["success", "failure", "pending", "unknown"]

PENDING_STATUSES = {"queued", "in_progress", "requested", "pending", "waiting"}
FAILURE_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}
SUCCESS_CONCLUSIONS = {"success", "skipped", "neutral"}


class WorkflowRunStatus(BaseModel):
    """Public-safe workflow run status export."""

    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    conclusion: str | None = None


class JobStatus(BaseModel):
    """Public-safe workflow job status export."""

    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    conclusion: str | None = None
    failed_step: str | None = None


class PRStatusInput(BaseModel):
    """Public-safe PR/CI status export."""

    model_config = ConfigDict(extra="forbid")

    pr_number: int
    title: str
    state: str
    mergeable: bool | None = None
    draft: bool = False
    head_sha: str | None = None
    workflow_runs: list[WorkflowRunStatus] = Field(default_factory=list)
    jobs: list[JobStatus] = Field(default_factory=list)
    log_excerpt: str | None = None


class PRStatusResult(BaseModel):
    """Deterministic PR status decision packet."""

    model_config = ConfigDict(extra="forbid")

    pr_number: int
    status: PRStatusValue
    summary: str
    blockers: list[str]
    next_action: str
    ci_state: CIStateValue


def _casefold(value: str | None) -> str:
    return (value or "").casefold()


def _has_pending_status(packet: PRStatusInput) -> bool:
    statuses = [_casefold(run.status) for run in packet.workflow_runs]
    statuses.extend(_casefold(job.status) for job in packet.jobs)
    return any(status in PENDING_STATUSES for status in statuses)


def _failed_workflow_blockers(packet: PRStatusInput) -> list[str]:
    blockers: list[str] = []
    for run in packet.workflow_runs:
        if _casefold(run.conclusion) in FAILURE_CONCLUSIONS:
            blockers.append(f"Workflow failed: {run.name}")
    for job in packet.jobs:
        if _casefold(job.conclusion) in FAILURE_CONCLUSIONS:
            if job.failed_step:
                blockers.append(f"Job failed: {job.name} / {job.failed_step}")
            else:
                blockers.append(f"Job failed: {job.name}")
    return blockers


def _black_format_blockers(log_excerpt: str | None) -> list[str]:
    if not log_excerpt:
        return []
    if "would reformat" not in log_excerpt.casefold():
        return []

    paths = re.findall(r"would reformat\s+([^\n\r]+)", log_excerpt)
    if not paths:
        return ["Black formatting check failed: files would be reformatted"]

    clean_paths = [path.strip() for path in paths]
    return ["Black formatting check failed: " + ", ".join(clean_paths)]


def _all_ci_success(packet: PRStatusInput) -> bool:
    if not packet.workflow_runs and not packet.jobs:
        return False
    conclusions = [_casefold(run.conclusion) for run in packet.workflow_runs]
    conclusions.extend(_casefold(job.conclusion) for job in packet.jobs)
    return all(conclusion in SUCCESS_CONCLUSIONS for conclusion in conclusions if conclusion)


def build_pr_status(packet: PRStatusInput) -> PRStatusResult:
    """Build a deterministic status packet from public-safe PR/CI export data."""
    if packet.draft:
        return PRStatusResult(
            pr_number=packet.pr_number,
            status="blocked",
            summary=f"PR #{packet.pr_number} is draft.",
            blockers=["PR is draft"],
            next_action="Mark the PR ready for review before merge consideration.",
            ci_state="unknown",
        )

    if _casefold(packet.state) != "open":
        return PRStatusResult(
            pr_number=packet.pr_number,
            status="blocked",
            summary=f"PR #{packet.pr_number} is not open.",
            blockers=[f"PR state is {packet.state}"],
            next_action="Review PR state before taking further action.",
            ci_state="unknown",
        )

    if packet.mergeable is False:
        return PRStatusResult(
            pr_number=packet.pr_number,
            status="blocked",
            summary=f"PR #{packet.pr_number} is not mergeable.",
            blockers=["PR is not mergeable"],
            next_action="Resolve merge conflicts or branch protection blockers.",
            ci_state="unknown",
        )

    if _has_pending_status(packet):
        return PRStatusResult(
            pr_number=packet.pr_number,
            status="waiting_for_ci",
            summary=f"PR #{packet.pr_number} is waiting for CI.",
            blockers=[],
            next_action="Wait for GitHub Actions to complete, then re-run pr-status.",
            ci_state="pending",
        )

    blockers = _failed_workflow_blockers(packet)
    blockers.extend(_black_format_blockers(packet.log_excerpt))
    if blockers:
        return PRStatusResult(
            pr_number=packet.pr_number,
            status="needs_fix",
            summary=f"PR #{packet.pr_number} has CI blockers.",
            blockers=blockers,
            next_action="Fix the listed blocker, push a new commit, and wait for CI.",
            ci_state="failure",
        )

    if packet.mergeable is True and _all_ci_success(packet):
        return PRStatusResult(
            pr_number=packet.pr_number,
            status="ready_to_merge",
            summary=f"PR #{packet.pr_number} is open, mergeable, non-draft, and CI is green.",
            blockers=[],
            next_action="Ask Oleksii for explicit merge approval before merging.",
            ci_state="success",
        )

    return PRStatusResult(
        pr_number=packet.pr_number,
        status="unknown_needs_review",
        summary=f"PR #{packet.pr_number} status cannot be decided from the provided export.",
        blockers=["Insufficient or ambiguous PR/CI status data"],
        next_action="Fetch/update public-safe PR and CI status export, then re-run pr-status.",
        ci_state="unknown",
    )


def build_pr_status_from_raw(raw: dict[str, Any]) -> PRStatusResult:
    """Validate raw JSON-compatible data and build a deterministic PR status result."""
    return build_pr_status(PRStatusInput.model_validate(raw))
