from __future__ import annotations

import subprocess
from pathlib import Path

from tools.skeleton_core.openhands_live_run_guard import (
    OpenHandsLiveRunGuardConfig,
    build_tmux_cleanup_command,
    run_openhands_live_guard,
)


def test_live_run_guard_completed_subprocess(tmp_path: Path) -> None:
    stdout_log = tmp_path / "stdout.log"
    stderr_log = tmp_path / "stderr.log"

    def runner(command: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="done", stderr="")

    report = run_openhands_live_guard(
        ["openhands", "-f", "task.md"],
        config=OpenHandsLiveRunGuardConfig(
            timeout_seconds=5,
            stdout_log_file=stdout_log,
            stderr_log_file=stderr_log,
        ),
        command_runner=runner,
    )

    assert report.status == "completed"
    assert report.returncode == 0
    assert report.timed_out is False
    assert stdout_log.read_text(encoding="utf-8") == "done"
    assert stderr_log.read_text(encoding="utf-8") == ""


def test_live_run_guard_failed_return_code(tmp_path: Path) -> None:
    def runner(command: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="failed")

    report = run_openhands_live_guard(
        ["openhands", "-f", "task.md"],
        config=OpenHandsLiveRunGuardConfig(
            timeout_seconds=5,
            stdout_log_file=tmp_path / "stdout.log",
            stderr_log_file=tmp_path / "stderr.log",
        ),
        command_runner=runner,
    )

    assert report.status == "failed"
    assert report.returncode == 2
    assert report.stderr_tail == "failed"


def test_live_run_guard_timeout_runs_scoped_cleanup(tmp_path: Path) -> None:
    cleanup_calls: list[list[str]] = []

    def runner(command: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(command, timeout_seconds, output="partial", stderr="slow")

    def cleanup_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        cleanup_calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    report = run_openhands_live_guard(
        ["openhands", "-f", "task.md"],
        config=OpenHandsLiveRunGuardConfig(
            timeout_seconds=5,
            stdout_log_file=tmp_path / "stdout.log",
            stderr_log_file=tmp_path / "stderr.log",
            openhands_tmux_session_name="openhands-pool-test",
        ),
        command_runner=runner,
        cleanup_runner=cleanup_runner,
    )

    assert report.status == "timeout"
    assert report.timed_out is True
    assert report.cleanup_attempted is True
    assert report.cleanup_succeeded is True
    assert cleanup_calls == [["tmux", "-Lopenhands", "kill-session", "-t", "openhands-pool-test"]]


def test_live_run_guard_refuses_unscoped_cleanup(tmp_path: Path) -> None:
    cleanup_calls: list[list[str]] = []

    def runner(command: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(command, timeout_seconds)

    def cleanup_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        cleanup_calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    report = run_openhands_live_guard(
        ["openhands", "-f", "task.md"],
        config=OpenHandsLiveRunGuardConfig(
            timeout_seconds=5,
            stdout_log_file=tmp_path / "stdout.log",
            stderr_log_file=tmp_path / "stderr.log",
            openhands_tmux_session_name="unrelated-session",
        ),
        command_runner=runner,
        cleanup_runner=cleanup_runner,
    )

    assert report.status == "timeout"
    assert report.cleanup_attempted is False
    assert report.cleanup_succeeded is False
    assert report.cleanup_command == []
    assert report.cleanup_error == "unsafe_openhands_tmux_session_name"
    assert cleanup_calls == []


def test_live_run_guard_redacts_secret_values(tmp_path: Path) -> None:
    secret = "sk-test-secret-value"

    def runner(command: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=f"OPENROUTER_API_KEY={secret}\nLLM_API_KEY=sk-other-secret",
            stderr=secret,
        )

    report = run_openhands_live_guard(
        ["openhands", "-f", "task.md"],
        config=OpenHandsLiveRunGuardConfig(
            timeout_seconds=5,
            stdout_log_file=tmp_path / "stdout.log",
            stderr_log_file=tmp_path / "stderr.log",
            secret_redaction_values=[secret],
        ),
        command_runner=runner,
    )

    dumped = report.model_dump_json()
    assert secret not in dumped
    assert "sk-other-secret" not in dumped
    assert secret not in (tmp_path / "stdout.log").read_text(encoding="utf-8")
    assert secret not in (tmp_path / "stderr.log").read_text(encoding="utf-8")
    assert "***redacted***" in report.stdout_tail


def test_tmux_cleanup_command_rejects_unrelated_session() -> None:
    try:
        build_tmux_cleanup_command("bash")
    except ValueError as exc:
        assert str(exc) == "unsafe_openhands_tmux_session_name"
    else:
        raise AssertionError("unsafe session name was accepted")
