"""Offline GitHub Actions run report normalizer for Skeleton."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ActionsRunnerStatus = Literal[
    "workflow_success_report",
    "workflow_failed_report",
    "workflow_cancelled_report",
    "workflow_unknown_needs_review",
    "unsafe_or_policy_violation",
]
StepConclusion = Literal[
    "success",
    "failure",
    "cancelled",
    "skipped",
    "neutral",
    "timed_out",
    "unknown",
]

SECRET_MARKERS = (
    "api_key",
    "apikey",
    "authorization:",
    "bearer ",
    "client_secret",
    "ghp_",
    "password=",
    "private_key",
    "secret=",
    "token=",
)


class ActionsStep(BaseModel):
    """Public-safe GitHub Actions step export."""

    model_config = ConfigDict(extra="ignore")

    name: str = ""
    status: str = ""
    conclusion: StepConclusion = "unknown"
    summary: str = ""


class ActionsJob(BaseModel):
    """Public-safe GitHub Actions job export."""

    model_config = ConfigDict(extra="ignore")

    name: str = ""
    status: str = ""
    conclusion: str = ""
    steps: list[ActionsStep] = Field(default_factory=list)


class GithubActionsRunnerInput(BaseModel):
    """Public-safe GitHub Actions run/job export."""

    model_config = ConfigDict(extra="ignore")

    repository: str = ""
    workflow: str = ""
    workflow_file: str = ""
    ref: str = ""
    head_sha: str = ""
    run_id: int | None = None
    run_status: str = ""
    run_conclusion: str = ""
    jobs: list[ActionsJob] = Field(default_factory=list)
    commands_inferred: list[str] = Field(default_factory=list)
    logs_summary: list[str] = Field(default_factory=list)


class GithubActionsRunnerPacket(BaseModel):
    """Structured report packet for Actions-based validation."""

    model_config = ConfigDict(extra="forbid")

    status: ActionsRunnerStatus
    repository: str = ""
    workflow: str = ""
    workflow_file: str = ""
    ref: str = ""
    head_sha: str = ""
    run_id: int | None = None
    run_status: str = ""
    run_conclusion: str = ""
    job_names: list[str] = Field(default_factory=list)
    failed_steps: list[str] = Field(default_factory=list)
    commands_inferred: list[str] = Field(default_factory=list)
    test_result: str = "unknown"
    failure_summary: str | None = None
    issue_report_text: str
    merge_allowed: bool = False
    deploy_allowed: bool = False


def _clean_items(items: list[str]) -> list[str]:
    return [item.strip() for item in items if item.strip()]


def _has_secret_like_text(values: list[str]) -> bool:
    joined = "\n".join(values).casefold()
    return any(marker in joined for marker in SECRET_MARKERS)


def _redacted(value: str) -> str:
    lowered = value.casefold()
    if any(marker in lowered for marker in SECRET_MARKERS):
        return "<redacted-secret-like-log-line>"
    return value


def _failed_steps(jobs: list[ActionsJob]) -> list[str]:
    failed = []
    for job in jobs:
        for step in job.steps:
            if step.conclusion in {"failure", "timed_out"}:
                name = step.name or "unnamed step"
                failed.append(f"{job.name}: {name}" if job.name else name)
    return _clean_items(failed)


def _status(packet: GithubActionsRunnerInput) -> ActionsRunnerStatus:
    if _has_secret_like_text(packet.logs_summary):
        return "unsafe_or_policy_violation"
    if packet.run_conclusion == "success":
        return "workflow_success_report"
    if packet.run_conclusion in {"failure", "timed_out"}:
        return "workflow_failed_report"
    if packet.run_conclusion == "cancelled":
        return "workflow_cancelled_report"
    return "workflow_unknown_needs_review"


def _test_result(status: ActionsRunnerStatus) -> str:
    if status == "workflow_success_report":
        return "passed"
    if status == "workflow_failed_report":
        return "failed"
    if status == "workflow_cancelled_report":
        return "cancelled"
    if status == "unsafe_or_policy_violation":
        return "blocked"
    return "unknown"


def _failure_summary(
    status: ActionsRunnerStatus,
    failed_steps: list[str],
    logs_summary: list[str],
) -> str | None:
    if status == "workflow_success_report":
        return None
    if status == "unsafe_or_policy_violation":
        return (
            "Secret-like content was detected in the Actions export/log summary. "
            "Output was redacted."
        )
    if failed_steps:
        return "Failed steps: " + "; ".join(failed_steps)
    redacted_logs = [_redacted(item) for item in logs_summary]
    if redacted_logs:
        return "Logs summary: " + "; ".join(redacted_logs[:3])
    if status == "workflow_cancelled_report":
        return "Workflow run was cancelled."
    return "Workflow result needs manual review."


def _report_text(
    *,
    packet: GithubActionsRunnerInput,
    status: ActionsRunnerStatus,
    test_result: str,
    failure_summary: str | None,
    failed_steps: list[str],
) -> str:
    lines = [
        "Agent report for BauClock #22",
        "",
        f"Repository: {packet.repository or 'unknown'}",
        f"Workflow: {packet.workflow or 'unknown'}",
        f"Ref: {packet.ref or 'unknown'}",
        f"Head SHA: {packet.head_sha or 'unknown'}",
        f"Run ID: {packet.run_id if packet.run_id is not None else 'unknown'}",
        f"Result: {test_result}",
    ]
    if failure_summary:
        lines.extend(["", f"Failure summary: {failure_summary}"])
    if failed_steps:
        lines.extend(["", "Failed steps:", *[f"- {step}" for step in failed_steps]])
    if status == "workflow_success_report":
        lines.extend(["", "Next safe step: queue-state may unlock the next BauClock task."])
    else:
        next_step = (
            "Next safe step: review or fix the workflow result "
            "before unlocking the queue."
        )
        lines.extend(["", next_step])
    return "\n".join(lines)


def build_github_actions_runner_control(
    packet: GithubActionsRunnerInput,
) -> GithubActionsRunnerPacket:
    """Build a deterministic Actions validation report packet."""
    status = _status(packet)
    failed_steps = _failed_steps(packet.jobs)
    test_result = _test_result(status)
    failure_summary = _failure_summary(status, failed_steps, packet.logs_summary)
    return GithubActionsRunnerPacket(
        status=status,
        repository=packet.repository,
        workflow=packet.workflow,
        workflow_file=packet.workflow_file,
        ref=packet.ref,
        head_sha=packet.head_sha,
        run_id=packet.run_id,
        run_status=packet.run_status,
        run_conclusion=packet.run_conclusion,
        job_names=_clean_items([job.name for job in packet.jobs]),
        failed_steps=failed_steps,
        commands_inferred=_clean_items(packet.commands_inferred),
        test_result=test_result,
        failure_summary=failure_summary,
        issue_report_text=_report_text(
            packet=packet,
            status=status,
            test_result=test_result,
            failure_summary=failure_summary,
            failed_steps=failed_steps,
        ),
        merge_allowed=False,
        deploy_allowed=False,
    )


def build_github_actions_runner_control_from_json(
    raw_json: str,
) -> GithubActionsRunnerPacket:
    """Validate local JSON text and build an Actions report packet."""
    packet = GithubActionsRunnerInput.model_validate_json(raw_json)
    return build_github_actions_runner_control(packet)
