"""Read-only runner/task status diagnostics for Skeleton queues.

This module is intentionally separate from ``yellow_runnerd.py``.
It inspects public-safe status evidence and returns a recommendation packet.
It must not mutate GitHub labels, restart services, kill processes, merge, or deploy.
"""

from __future__ import annotations

import os
import re
from datetime import UTC, datetime
from pathlib import Path
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
DEFAULT_LOCK_FILE_PATH = "/home/agent/agent-dev/runner-state/yellow_runnerd.lock"
DEFAULT_AGENT_RUNS_DIR = "/home/agent/agent-dev/agent-runs"
DEFAULT_LOGS_DIR = "/home/agent/agent-dev/logs"
DEFAULT_LOG_TAIL_LINES = 80
DEFAULT_LOG_TAIL_BYTES = 20_000
MAX_LIVE_LOG_FILES = 5
SAFE_PROCESS_WORDS = ("yellow_runnerd", "agent-run", "python", "codex", "gemini", "pytest", "git")
SECRET_LIKE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"api[_-]?key\s*[:=]\s*[^\s]+",
        r"token\s*[:=]\s*[^\s]+",
        r"bearer\s+[a-z0-9._\-]+",
        r"private[_-]?key\s*[:=]?\s*[^\s]*",
        r"password\s*[:=]\s*[^\s]+",
        r"secret\s*[:=]\s*[^\s]+",
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
FINAL_LABELS = {
    "agent:executed",
    "agent:audit-complete",
    "agent:blocked",
    "agent:needs-revision",
}


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
    process_command_summary: str = ""
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
    process_command_summary: str = ""
    latest_event_summary: str = ""
    logs_summary: str = ""
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
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


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
    now = _parse_datetime(now_value) or datetime.now(UTC)
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
    text = (
        f"{packet.latest_event_summary}\n{packet.logs_summary}\n{packet.blocker_summary}".casefold()
    )
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
    if (
        event_age is not None
        and _has_running_label(packet.issue_labels)
        and event_age > packet.stale_after_seconds
        and packet.lock_pid_alive is not True
    ):
        return (
            f"latest event is older than {packet.stale_after_seconds} seconds "
            "without live PID evidence"
        )
    return ""


def _blocker_summary(packet: RunnerStatusCheckInput, *, secret_like: bool) -> str:
    if secret_like:
        return "secret-like text detected in runner status evidence"
    if packet.blocker_summary:
        return _redact_secret_like_text(packet.blocker_summary)
    return ""


def _infer_status(
    packet: RunnerStatusCheckInput,
) -> tuple[RunnerStatus, str, RecommendedQueueAction]:
    secret_like = _contains_secret_like_text(
        packet.logs_summary,
        packet.latest_event_summary,
        packet.blocker_summary,
    )
    if secret_like or packet.blocker_summary == "secret-like text detected in runner log tail":
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
        process_command_summary=_redact_secret_like_text(packet.process_command_summary),
        latest_event_summary=_redact_secret_like_text(packet.latest_event_summary),
        logs_summary=_redact_secret_like_text(packet.logs_summary),
        staleness_reason=staleness_reason,
        blocker_summary=_blocker_summary(packet, secret_like=secret_like),
        recommended_queue_action=action,
        merge_allowed=False,
        deploy_allowed=False,
    )


def build_runner_status_check_from_json(raw_json: str) -> RunnerStatusCheckPacket:
    """Validate public-safe JSON and build a runner status packet."""
    return build_runner_status_check(RunnerStatusCheckInput.model_validate_json(raw_json))


def _parse_lock_pid(lock_file: Path) -> int | None:
    try:
        raw_value = lock_file.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    try:
        pid = int(raw_value)
    except ValueError:
        return None
    return pid if pid > 0 else None


def _pid_alive(pid: int | None) -> bool | None:
    if pid is None:
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _safe_process_command_summary(pid: int | None) -> str:
    if pid is None:
        return ""
    cmdline = Path("/proc") / str(pid) / "cmdline"
    try:
        raw = cmdline.read_bytes()
    except OSError:
        return ""
    parts = [part.decode("utf-8", errors="replace") for part in raw.split(b"\0") if part]
    if not parts:
        return ""
    summary = " ".join(parts[:8])
    return _redact_secret_like_text(summary[:500])


def _safe_process_names() -> list[str]:
    names: set[str] = set()
    proc_root = Path("/proc")
    try:
        entries = list(proc_root.iterdir())
    except OSError:
        return []
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            comm = (entry / "comm").read_text(encoding="utf-8", errors="replace").strip()
            cmdline = (
                (entry / "cmdline")
                .read_bytes()
                .decode("utf-8", errors="replace")
                .replace("\0", " ")
            )
        except OSError:
            continue
        haystack = f"{comm} {cmdline}".casefold()
        for word in SAFE_PROCESS_WORDS:
            if word in haystack:
                names.add(word)
    return sorted(names)


def _safe_tail(
    path: Path,
    *,
    max_lines: int = DEFAULT_LOG_TAIL_LINES,
    max_bytes: int = DEFAULT_LOG_TAIL_BYTES,
) -> tuple[str, bool]:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - max_bytes))
            raw = handle.read(max_bytes)
    except OSError:
        return "", False

    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()[-max_lines:]
    tail = "\n".join(lines)
    secret_like = _contains_secret_like_text(tail)
    return _redact_secret_like_text(tail), secret_like


def _candidate_run_dirs(
    *,
    agent_runs_dir: Path,
    repository: str,
    issue_number: int | None,
    run_id: str | None,
) -> list[Path]:
    if run_id:
        candidate = agent_runs_dir / run_id
        return [candidate] if candidate.exists() and candidate.is_dir() else []

    if not agent_runs_dir.exists() or not agent_runs_dir.is_dir():
        return []

    repo_slug = repository.replace("/", "-")
    issue_suffix = f"-{issue_number}" if issue_number is not None else ""
    candidates: list[Path] = []
    try:
        for entry in agent_runs_dir.iterdir():
            if not entry.is_dir():
                continue
            name = entry.name
            if repo_slug and repo_slug not in name:
                continue
            if issue_suffix and not name.endswith(issue_suffix):
                continue
            candidates.append(entry)
    except OSError:
        return []

    return sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)[
        :MAX_LIVE_LOG_FILES
    ]


def _candidate_log_files(
    *,
    run_dirs: list[Path],
    logs_dir: Path,
    run_id: str | None,
) -> list[Path]:
    files: list[Path] = []
    for run_dir in run_dirs:
        log_file = run_dir / "log.txt"
        if log_file.exists() and log_file.is_file():
            files.append(log_file)

    if logs_dir.exists() and logs_dir.is_dir() and run_id:
        try:
            for entry in logs_dir.iterdir():
                if entry.is_file() and run_id in entry.name:
                    files.append(entry)
        except OSError:
            pass

    unique: list[Path] = []
    seen: set[Path] = set()
    for file_path in files:
        resolved = file_path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(file_path)
    return unique[:MAX_LIVE_LOG_FILES]


def live_runner_status_check(
    *,
    repository: str,
    issue_number: int | None,
    run_id: str | None = None,
    lock_file_path: Path | str = DEFAULT_LOCK_FILE_PATH,
    agent_runs_dir: Path | str = DEFAULT_AGENT_RUNS_DIR,
    logs_dir: Path | str = DEFAULT_LOGS_DIR,
    stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS,
    current_time: str | None = None,
) -> RunnerStatusCheckPacket:
    """Collect bounded public-safe local runner status evidence.

    This function is read-only. It does not read environment variables, does not
    inspect .env files, does not kill/restart processes, and does not mutate
    GitHub state.
    """
    lock_file = Path(lock_file_path)
    runs_dir = Path(agent_runs_dir)
    safe_logs_dir = Path(logs_dir)

    lock_file_seen = lock_file.exists()
    lock_pid = _parse_lock_pid(lock_file) if lock_file_seen else None
    lock_pid_alive = _pid_alive(lock_pid)

    run_dirs = _candidate_run_dirs(
        agent_runs_dir=runs_dir,
        repository=repository,
        issue_number=issue_number,
        run_id=run_id,
    )
    latest_run_id = run_id or (run_dirs[0].name if run_dirs else None)
    log_files = _candidate_log_files(
        run_dirs=run_dirs, logs_dir=safe_logs_dir, run_id=latest_run_id
    )

    log_tails = []
    secret_like_log_seen = False
    for log_file in log_files:
        tail, tail_secret_like = _safe_tail(log_file)
        secret_like_log_seen = secret_like_log_seen or tail_secret_like
        if tail:
            log_tails.append(f"== {log_file.name} ==\n{tail}")

    logs_summary = "\n\n".join(log_tails)
    latest_event_summary = ""
    if logs_summary:
        latest_event_summary = logs_summary.splitlines()[-1][:500]

    packet = RunnerStatusCheckInput(
        repository=repository,
        issue_number=issue_number,
        issue_labels=["agent:running"] if latest_run_id or lock_pid_alive else [],
        stale_after_seconds=stale_after_seconds,
        current_time=current_time,
        lock_file_seen=lock_file_seen,
        lock_pid=lock_pid,
        lock_pid_alive=lock_pid_alive,
        latest_run_id=latest_run_id,
        latest_event_summary=latest_event_summary,
        logs_summary=logs_summary,
        related_subprocesses_seen=_safe_process_names(),
        process_command_summary=_safe_process_command_summary(lock_pid),
        blocker_summary=(
            "secret-like text detected in runner log tail"
            if secret_like_log_seen
            else "" if latest_run_id or lock_file_seen else "no live runner evidence found"
        ),
    )
    return build_runner_status_check(packet)


def build_unavailable_live_check(
    *, repository: str, issue_number: int | None
) -> RunnerStatusCheckPacket:
    """Return a fail-closed packet when live collection is not configured."""
    return build_runner_status_check(
        RunnerStatusCheckInput(
            repository=repository,
            issue_number=issue_number,
            blocker_summary=(
                "live runner-status-check collection is not configured; provide --input "
                "fixture or a bounded collector"
            ),
        )
    )
