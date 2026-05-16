"""Bounded OpenHands live-run guard v0.

This module wraps a live OpenHands command with timeout, log capture, and scoped
cleanup. It does not call GitHub, push, merge, deploy, restart services, mutate
labels, or read secrets.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

OPENHANDS_LIVE_RUN_GUARD_VERSION = "openhands_live_run_guard.v0"

LiveRunStatus = Literal[
    "completed",
    "timeout",
    "failed",
    "no_changes",
    "needs_manual_review",
    "cleanup_failed",
]

SAFE_TMUX_SESSION_PREFIXES = (
    "openhands-",
    "openhands-pool-",
    "skeleton-openhands-",
)


class OpenHandsLiveRunGuardConfig(BaseModel):
    """Configuration for a bounded OpenHands live run."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    timeout_seconds: int = 120
    stdout_log_file: Path = Path("/tmp/skeleton-openhands-live-run.stdout.log")
    stderr_log_file: Path = Path("/tmp/skeleton-openhands-live-run.stderr.log")
    openhands_tmux_session_name: str | None = None
    secret_redaction_values: list[str] = Field(default_factory=list, exclude=True)


class OpenHandsLiveRunGuardReport(BaseModel):
    """Public-safe live-run guard report."""

    model_config = ConfigDict(extra="forbid")

    guard_version: str = OPENHANDS_LIVE_RUN_GUARD_VERSION
    status: LiveRunStatus
    returncode: int | None = None
    timed_out: bool = False
    timeout_seconds: int
    stdout_log_path: str
    stderr_log_path: str
    stdout_tail: str = ""
    stderr_tail: str = ""
    cleanup_attempted: bool = False
    cleanup_succeeded: bool | None = None
    cleanup_command: list[str] = Field(default_factory=list)
    cleanup_error: str = ""


CommandRunner = Callable[[list[str], int], subprocess.CompletedProcess[str]]
CleanupRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def default_command_runner(
    command: list[str],
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    """Run a bounded command."""

    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )


def default_cleanup_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a bounded cleanup command."""

    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )


def _to_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _redact(text: str, secrets: list[str]) -> str:
    redacted = text

    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "***redacted***")

    redacted = re.sub(
        r"(OPENROUTER_API_KEY|LLM_API_KEY)=\S+",
        r"\1=***redacted***",
        redacted,
    )
    redacted = re.sub(r"sk-[A-Za-z0-9._-]+", "sk-***redacted***", redacted)
    return redacted


def _write_log(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _tail(text: str, limit: int = 4000) -> str:
    return text[-limit:]


def _is_safe_tmux_session_name(session_name: str) -> bool:
    if not session_name:
        return False
    if not session_name.startswith(SAFE_TMUX_SESSION_PREFIXES):
        return False
    return re.fullmatch(r"[A-Za-z0-9_.:-]+", session_name) is not None


def build_tmux_cleanup_command(session_name: str) -> list[str]:
    """Build a scoped tmux cleanup command for an owned OpenHands session."""

    if not _is_safe_tmux_session_name(session_name):
        raise ValueError("unsafe_openhands_tmux_session_name")

    return ["tmux", "-Lopenhands", "kill-session", "-t", session_name]


def _attempt_cleanup(
    *,
    session_name: str | None,
    cleanup_runner: CleanupRunner,
) -> tuple[bool, bool | None, list[str], str]:
    if not session_name:
        return False, None, [], ""

    try:
        command = build_tmux_cleanup_command(session_name)
    except ValueError as exc:
        return False, False, [], str(exc)

    completed = cleanup_runner(command)
    if completed.returncode == 0:
        return True, True, command, ""

    error = _to_text(completed.stderr).strip() or f"cleanup_returncode={completed.returncode}"
    return True, False, command, error


def run_openhands_live_guard(
    command: list[str],
    *,
    config: OpenHandsLiveRunGuardConfig | None = None,
    command_runner: CommandRunner = default_command_runner,
    cleanup_runner: CleanupRunner = default_cleanup_runner,
) -> OpenHandsLiveRunGuardReport:
    """Run OpenHands through a bounded guard and return a public-safe report."""

    resolved = config or OpenHandsLiveRunGuardConfig()

    try:
        completed = command_runner(command, resolved.timeout_seconds)
        stdout = _redact(_to_text(completed.stdout), resolved.secret_redaction_values)
        stderr = _redact(_to_text(completed.stderr), resolved.secret_redaction_values)

        _write_log(resolved.stdout_log_file, stdout)
        _write_log(resolved.stderr_log_file, stderr)

        status: LiveRunStatus = "completed" if completed.returncode == 0 else "failed"

        return OpenHandsLiveRunGuardReport(
            status=status,
            returncode=completed.returncode,
            timed_out=False,
            timeout_seconds=resolved.timeout_seconds,
            stdout_log_path=str(resolved.stdout_log_file),
            stderr_log_path=str(resolved.stderr_log_file),
            stdout_tail=_tail(stdout),
            stderr_tail=_tail(stderr),
        )

    except subprocess.TimeoutExpired as exc:
        stdout = _redact(_to_text(exc.output), resolved.secret_redaction_values)
        stderr = _redact(_to_text(exc.stderr), resolved.secret_redaction_values)

        _write_log(resolved.stdout_log_file, stdout)
        _write_log(resolved.stderr_log_file, stderr)

        (
            cleanup_attempted,
            cleanup_succeeded,
            cleanup_command,
            cleanup_error,
        ) = _attempt_cleanup(
            session_name=resolved.openhands_tmux_session_name,
            cleanup_runner=cleanup_runner,
        )

        status: LiveRunStatus = "timeout"
        if cleanup_attempted and cleanup_succeeded is False:
            status = "cleanup_failed"

        return OpenHandsLiveRunGuardReport(
            status=status,
            returncode=None,
            timed_out=True,
            timeout_seconds=resolved.timeout_seconds,
            stdout_log_path=str(resolved.stdout_log_file),
            stderr_log_path=str(resolved.stderr_log_file),
            stdout_tail=_tail(stdout),
            stderr_tail=_tail(stderr),
            cleanup_attempted=cleanup_attempted,
            cleanup_succeeded=cleanup_succeeded,
            cleanup_command=cleanup_command,
            cleanup_error=cleanup_error,
        )
