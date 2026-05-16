from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.skeleton_core.adapter_contract import AdapterTaskPacket, FuelPolicy
from tools.skeleton_core.openhands_live_run_guard import OpenHandsLiveRunGuardReport
from tools.skeleton_core.openhands_runner_route import (
    OpenHandsRunnerRouteConfig,
    load_openrouter_key,
    run_openhands_route,
)


def valid_packet() -> AdapterTaskPacket:
    return AdapterTaskPacket(
        task_id="openhands-runner-route-v0",
        repo="alanua/jeeves",
        allowed_files=["tools/skeleton_core/openhands_runner_route.py"],
        forbidden_paths=[".env", ".git", ".ssh", "secrets", "tokens"],
        authority_level="level_2_local_diff",
        risk_level="yellow",
        expected_artifact="diff",
        task_instructions="Update the OpenHands runner route in a bounded way.",
        fuel_policy=FuelPolicy(
            provider="openrouter",
            model="deepseek/deepseek-v4-flash:free",
            max_usd=1.0,
        ),
    )


def test_load_openrouter_key_reads_runner_secret_file(tmp_path: Path) -> None:
    secret_file = tmp_path / "openrouter.env"
    secret_file.write_text("OPENROUTER_API_KEY='sk-or-test-value'\n", encoding="utf-8")

    assert load_openrouter_key(secret_file) == "sk-or-test-value"


def test_load_openrouter_key_blocks_corrupted_secret_file(tmp_path: Path) -> None:
    secret_file = tmp_path / "openrouter.env"
    secret_file.write_text("OPENROUTER_API_KEY='cat > /tmp/bad.sh'\n", encoding="utf-8")

    with pytest.raises(ValueError, match="corrupted"):
        load_openrouter_key(secret_file)


def test_route_writes_task_and_runs_injected_runner(tmp_path: Path) -> None:
    secret_file = tmp_path / "openrouter.env"
    task_file = tmp_path / "task.md"
    secret_file.write_text("OPENROUTER_API_KEY='sk-or-test-value'\n", encoding="utf-8")

    calls: list[tuple[list[str], dict[str, str]]] = []

    def fake_runner(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        calls.append((command, env))
        return subprocess.CompletedProcess(command, 0, stdout="done", stderr="")

    report = run_openhands_route(
        valid_packet(),
        config=OpenHandsRunnerRouteConfig(task_file=task_file, secret_file=secret_file),
        runner=fake_runner,
        changed_files=["tools/skeleton_core/openhands_runner_route.py"],
        artifact_paths=["artifacts/openhands-runner-route-v0.diff"],
    )

    assert task_file.exists()
    assert "openhands-runner-route-v0" in task_file.read_text(encoding="utf-8")
    assert calls
    assert calls[0][1]["LLM_API_KEY"] == "sk-or-test-value"
    assert "sk-or-test-value" not in report.model_dump_json()
    assert report.returncode == 0
    assert report.live_run is None
    assert report.result.result_validation.status == "valid_adapter_result"


def test_route_blocks_success_without_artifact(tmp_path: Path) -> None:
    secret_file = tmp_path / "openrouter.env"
    task_file = tmp_path / "task.md"
    secret_file.write_text("OPENROUTER_API_KEY='sk-or-test-value'\n", encoding="utf-8")

    def fake_runner(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="done", stderr="")

    report = run_openhands_route(
        valid_packet(),
        config=OpenHandsRunnerRouteConfig(task_file=task_file, secret_file=secret_file),
        runner=fake_runner,
        changed_files=["tools/skeleton_core/openhands_runner_route.py"],
        artifact_paths=[],
    )

    assert report.result.result_validation.status == "blocked"
    assert "success_without_artifact" in report.result.result_validation.blocked_reasons


def test_route_failed_runner_returns_failed_result(tmp_path: Path) -> None:
    secret_file = tmp_path / "openrouter.env"
    task_file = tmp_path / "task.md"
    secret_file.write_text("OPENROUTER_API_KEY='sk-or-test-value'\n", encoding="utf-8")

    def fake_runner(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="failed")

    report = run_openhands_route(
        valid_packet(),
        config=OpenHandsRunnerRouteConfig(task_file=task_file, secret_file=secret_file),
        runner=fake_runner,
        changed_files=[],
        artifact_paths=[],
    )

    assert report.returncode == 2
    assert report.result.result.status == "failed"
    assert report.result.result_validation.status == "valid_adapter_result"
    assert report.stderr_tail == "failed"


def test_route_uses_live_run_guard_report_for_success(tmp_path: Path) -> None:
    secret_file = tmp_path / "openrouter.env"
    task_file = tmp_path / "task.md"
    secret_file.write_text("OPENROUTER_API_KEY='sk-or-test-value'\n", encoding="utf-8")

    calls: list[tuple[list[str], dict[str, str], OpenHandsRunnerRouteConfig]] = []

    def fake_live_run(
        command: list[str],
        env: dict[str, str],
        config: OpenHandsRunnerRouteConfig,
    ) -> OpenHandsLiveRunGuardReport:
        calls.append((command, env, config))
        return OpenHandsLiveRunGuardReport(
            status="completed",
            returncode=0,
            timed_out=False,
            timeout_seconds=config.timeout_seconds,
            stdout_log_path=str(tmp_path / "stdout.log"),
            stderr_log_path=str(tmp_path / "stderr.log"),
            stdout_tail="done",
            stderr_tail="",
        )

    report = run_openhands_route(
        valid_packet(),
        config=OpenHandsRunnerRouteConfig(task_file=task_file, secret_file=secret_file),
        live_run=fake_live_run,
        changed_files=["tools/skeleton_core/openhands_runner_route.py"],
        artifact_paths=["artifacts/openhands-runner-route-v0.diff"],
    )

    assert calls
    assert calls[0][1]["LLM_API_KEY"] == "sk-or-test-value"
    assert report.live_run is not None
    assert report.returncode == 0
    assert report.stdout_tail == "done"
    assert report.result.result.status == "success"
    assert report.result.result_validation.status == "valid_adapter_result"
    assert "sk-or-test-value" not in report.model_dump_json()


def test_route_maps_live_run_timeout_to_failed_report(tmp_path: Path) -> None:
    secret_file = tmp_path / "openrouter.env"
    task_file = tmp_path / "task.md"
    secret_file.write_text("OPENROUTER_API_KEY='sk-or-test-value'\n", encoding="utf-8")

    def fake_live_run(
        command: list[str],
        env: dict[str, str],
        config: OpenHandsRunnerRouteConfig,
    ) -> OpenHandsLiveRunGuardReport:
        return OpenHandsLiveRunGuardReport(
            status="timeout",
            returncode=None,
            timed_out=True,
            timeout_seconds=config.timeout_seconds,
            stdout_log_path=str(tmp_path / "stdout.log"),
            stderr_log_path=str(tmp_path / "stderr.log"),
            stdout_tail="partial",
            stderr_tail="slow",
            cleanup_attempted=True,
            cleanup_succeeded=True,
            cleanup_command=["tmux", "-Lopenhands", "kill-session", "-t", "openhands-pool-test"],
        )

    report = run_openhands_route(
        valid_packet(),
        config=OpenHandsRunnerRouteConfig(
            task_file=task_file,
            secret_file=secret_file,
            timeout_seconds=7,
        ),
        live_run=fake_live_run,
        changed_files=[],
        artifact_paths=[],
    )

    assert report.returncode is None
    assert report.timed_out is True
    assert report.live_run is not None
    assert report.live_run.status == "timeout"
    assert report.result.result.status == "failed"
    assert report.result.result.stop_reason == "openhands_timeout"
    assert report.result.result_validation.status == "valid_adapter_result"


def test_route_maps_cleanup_failed_to_failed_report(tmp_path: Path) -> None:
    secret_file = tmp_path / "openrouter.env"
    task_file = tmp_path / "task.md"
    secret_file.write_text("OPENROUTER_API_KEY='sk-or-test-value'\n", encoding="utf-8")

    def fake_live_run(
        command: list[str],
        env: dict[str, str],
        config: OpenHandsRunnerRouteConfig,
    ) -> OpenHandsLiveRunGuardReport:
        return OpenHandsLiveRunGuardReport(
            status="cleanup_failed",
            returncode=None,
            timed_out=True,
            timeout_seconds=config.timeout_seconds,
            stdout_log_path=str(tmp_path / "stdout.log"),
            stderr_log_path=str(tmp_path / "stderr.log"),
            cleanup_attempted=True,
            cleanup_succeeded=False,
            cleanup_error="cleanup_returncode=1",
        )

    report = run_openhands_route(
        valid_packet(),
        config=OpenHandsRunnerRouteConfig(task_file=task_file, secret_file=secret_file),
        live_run=fake_live_run,
    )

    assert report.result.result.status == "failed"
    assert report.result.result.stop_reason == "openhands_cleanup_failed"
    assert report.result.result_validation.status == "valid_adapter_result"
