from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.skeleton_core.adapter_contract import AdapterTaskPacket, FuelPolicy
from tools.skeleton_core.openhands_result_collector import OpenHandsResultCollectorConfig
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
        task_instructions="Run bounded OpenHands runner route v0.",
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


def test_route_uses_collector_when_no_explicit_changed_files(tmp_path: Path) -> None:
    secret_file = tmp_path / "openrouter.env"
    task_file = tmp_path / "task.md"
    artifact_file = tmp_path / "result.diff"
    secret_file.write_text("OPENROUTER_API_KEY='sk-or-test-value'\n", encoding="utf-8")

    def fake_runner(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="done", stderr="")

    def fake_git_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        if "status" in command and "--short" in command:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=" M tools/skeleton_core/openhands_runner_route.py\n",
                stderr="",
            )
        if "diff" in command:
            return subprocess.CompletedProcess(command, 0, stdout="+route change\n", stderr="")
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="unexpected command")

    packet = valid_packet().model_copy(
        update={"allowed_files": ["tools/skeleton_core/openhands_runner_route.py"]}
    )

    report = run_openhands_route(
        packet,
        config=OpenHandsRunnerRouteConfig(task_file=task_file, secret_file=secret_file),
        runner=fake_runner,
        collector_config=OpenHandsResultCollectorConfig(diff_artifact_file=artifact_file),
        git_runner=fake_git_runner,
    )

    assert report.collector_report is not None
    assert report.collector_report.changed_files == [
        "tools/skeleton_core/openhands_runner_route.py"
    ]
    assert report.collector_report.diff_artifact_written is True
    assert artifact_file.exists()
    assert report.result.result_validation.status == "valid_adapter_result"
