"""Read-only runner/task status diagnostics for Skeleton queues.

This module is intentionally separate from ``yellow_runnerd.py``.
It inspects public-safe status evidence and returns a recommendation packet.
It must not mutate GitHub labels, restart services, kill processes, merge, or deploy.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RunnerStatus = Literal[
    "running",
    "stale",
    "failed",
    "completed_unknown",
    "needs_manual_review",
]
RecommendedQueueAction = Literal[
    "wait_for_runner",
    "review_blocker_report",
    "run_manual_health_check",
    "review_final_report",
    "safe_to_consider_next_queue_item",
    "needs_manual_review",
]

DEFAULT_STALE_AFTER_SECONDS = 60 * 60
SECRET_LIKE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"api[_-]?key\s*[:=]",
        r"token\s*[:=]",
        r"bearer\s+[a-z0-9._\-]+",
        r"private[_-]?key",
        r"password\s*[:=]",
        r"secret\s*[:=]",
        r"ghp_[a-z0-9_]+",
        r"github_pat_[a-z0-9_]+",
        r"AIza[0-9A-Za-z_\-]{20,}",
    ]
]
FAILURE_WORDS = (
    "traceback",
    "exception",
    "failed",
    "failure",
    "error",
    "crash",
    "blocked",
)
COMPLETION_STATUSES = {"complete", "completed", "done", "success", "succeeded", "audit_complete"}
FAILED_STATUSES = {"failed", "failure", "error", "crashed", "blocked"}
RUNNING_LABELS = {"agent:running", "agent:executing", "agent:auditing", "agent:queued"}
FINAL_LABELS = {"agent:executed", "agent:audit-complete", "agent:blocked", "agent:needs-revision"}


class RunnerStatusCheckInput(BaseModel):
    """Public-safe runner status evidence.

    Live collectors should reduce local state into this shape before calling
    ``build_runner_status_check``. Raw logs/secrets/private paths must not be
    passed here; any summaries that contain secret-like text are fail-closed.
    """

    model_config = ConfigDict(extra="ignore")

    repository: str = ""
    issue_number: int | None = None
    runner_name: str = ""
    issue_labels: list[str] = Field(default_factory=list)
    running_since: str | None = None
    last_comment_at: str | None = None
    current_time: str | None = None
    stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS
    lock_file_seen: bool = False
    lock_pid: int | None = None
    lock_pid_alive: bool | None = None
    latest_run_id: str | None = None
    latest_event_status: str | None = None
    latest_event_at: str | None = None
    latest_event_summary: str = ""
    logs_summary: str = ""
    related_subprocesses_seen: list[str] = Field(default_factory=list)
    final_report_seen: bool = False
    completion_evidence_seen: bool = False
    blocker_summary: str = ""


class RunnerStatusCheckPacket(BaseModel):
    """Public-safe runner status packet."""

    model_config = ConfigDict(extra="forbid")

    status: RunnerStatus
    repository: str = ""
    issue_number: int | None = None
    runner_name: str = ""
    issue_labels: list[str] = Field(default_factory=list)
    running_since: str | None = None
    last_comment_at: str | None = None
    lock_file_seen: bool = False
    lock_pid: int | None = None
    lock_pid_alive: bool | None = None
    latest_run_id: str | None = None
    latest_event_status: str | None = None
    related_subprocesses_seen: list[str] = Field(default_factory=list)
    staleness_reason: str = ""
    blocker_summary: str = ""
    recommended_queue_action: RecommendedQueueAction
    merge_allowed: bool = False
    deploy_allowed: bool = False


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _contains_secret_like_text(*values: str) -> bool:
    haystack = "\n".join(value for value in values if value)
    return any(pattern.search(haystack) for pattern in SECRET_LIKE_PATTERNS)


def _redact_secret_like_text(value: str) -> str:
    redacted = value
    for pattern in SECRET_LIKE_PATTERNS:
        redacted = pattern.sub("<redacted-secret-like>", redacted)
    return redacted


def _age_seconds(start_value: str | None, now_value: str | None) -> int | None:
    start = _parse_datetime(start_value)
    if start is None:
        return None
    now = _parse_datetime(now_value) or datetime.now(timezone.utc)
    return max(0, int((now - start).total_seconds()))


def _has_running_label(labels: list[str]) -> bool:
    normalized = {label.casefold() for label in labels}
    return bool(normalized & RUNNING_LABELS)


def _has_final_label(labels: list[str]) -> bool:
    normalized = {label.casefold() for label in labels}
    return bool(normalized & FINAL_LABELS)


def _has_failure_text(packet: RunnerStatusCheckInput) -> bool:
    event_status = (packet.latest_event_status or "").casefold()
    if event_status in FAILED_STATUSES:
        return True
    text = f"{packet.latest_event_summary}\n{packet.logs_summary}\n{packet.blocker_summary}".casefold()
    return any(word in text for word in FAILURE_WORDS)


def _has_completion_evidence(packet: RunnerStatusCheckInput) -> bool:
    event_status = (packet.latest_event_status or "").casefold()
    return (
        packet.completion_evidence_seen
        or event_status in COMPLETION_STATUSES
        or _has_final_label(packet.issue_labels)
    )


def _staleness_reason(packet: RunnerStatusCheckInput) -> str:
    if packet.lock_file_seen and packet.lock_pid is not None and packet.lock_pid_alive is False:
        return "lock PID is not alive"
    if packet.lock_file_seen and packet.lock_pid is None:
        return "lock file exists but contains no PID"
    running_age = _age_seconds(packet.running_since, packet.current_time)
    if running_age is not None and running_age > packet.stale_after_seconds:
        return f"running evidence is older than {packet.stale_after_seconds} seconds"
    event_age = _age_seconds(packet.latest_event_at, packet.current_time)
    if event_age is not None and _has_running_label(packet.issue_labels):
        if event_age > packet.stale_after_seconds and packet.lock_pid_alive is not True:
            return f"latest event is older than {packet.stale_after_seconds} seconds without live PID evidence"
    return ""


def _blocker_summary(packet: RunnerStatusCheckInput, *, secret_like: bool) -> str:
    if secret_like:
        return "secret-like text detected in runner status evidence"
    if packet.blocker_summary:
        return _redact_secret_like_text(packet.blocker_summary)
    return ""


def _infer_status(packet: RunnerStatusCheckInput) -> tuple[RunnerStatus, str, RecommendedQueueAction]:
    secret_like = _contains_secret_like_text(
        packet.logs_summary,
        packet.latest_event_summary,
        packet.blocker_summary,
    )
    if secret_like:
        return "needs_manual_review", "", "needs_manual_review"

    if _has_failure_text(packet):
        return "failed", "", "review_blocker_report"

    stale_reason = _staleness_reason(packet)
    if stale_reason:
        return "stale", stale_reason, "run_manual_health_check"

    completion_evidence = _has_completion_evidence(packet)
    if completion_evidence and not packet.final_report_seen:
        return "completed_unknown", "", "review_final_report"

    if completion_evidence and packet.final_report_seen:
        return "completed_unknown", "", "safe_to_consider_next_queue_item"

    live_runner_evidence = (
        packet.lock_pid_alive is True
        or bool(packet.related_subprocesses_seen)
        or bool(packet.latest_run_id and _has_running_label(packet.issue_labels))
    )
    if _has_running_label(packet.issue_labels) and live_runner_evidence:
        return "running", "", "wait_for_runner"

    return "needs_manual_review", "", "needs_manual_review"


def build_runner_status_check(packet: RunnerStatusCheckInput) -> RunnerStatusCheckPacket:
    """Build a public-safe runner status packet.

    The function is deterministic and side-effect free.
    """
    status, staleness_reason, action = _infer_status(packet)
    secret_like = _contains_secret_like_text(
        packet.logs_summary,
        packet.latest_event_summary,
        packet.blocker_summary,
    )

    return RunnerStatusCheckPacket(
        status=status,
        repository=packet.repository,
        issue_number=packet.issue_number,
        runner_name=packet.runner_name,
        issue_labels=packet.issue_labels,
        running_since=packet.running_since,
        last_comment_at=packet.last_comment_at,
        lock_file_seen=packet.lock_file_seen,
        lock_pid=packet.lock_pid,
        lock_pid_alive=packet.lock_pid_alive,
        latest_run_id=packet.latest_run_id,
        latest_event_status=packet.latest_event_status,
        related_subprocesses_seen=packet.related_subprocesses_seen,
        staleness_reason=staleness_reason,
        blocker_summary=_blocker_summary(packet, secret_like=secret_like),
        recommended_queue_action=action,
        merge_allowed=False,
        deploy_allowed=False,
    )


def build_runner_status_check_from_json(raw_json: str) -> RunnerStatusCheckPacket:
    """Validate public-safe JSON and build a runner status packet."""
    return build_runner_status_check(RunnerStatusCheckInput.model_validate_json(raw_json))


def build_unavailable_live_check(*, repository: str, issue_number: int | None) -> RunnerStatusCheckPacket:
    """Return a fail-closed packet when live collection is not configured."""
    return build_runner_status_check(
        RunnerStatusCheckInput(
            repository=repository,
            issue_number=issue_number,
            blocker_summary="live runner-status-check collection is not configured; provide --input fixture or a bounded collector",
        )
    )
