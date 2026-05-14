from __future__ import annotations

import subprocess
from pathlib import Path

from tools.skeleton_core.adapter_contract import AdapterTaskPacket, FuelPolicy
from tools.skeleton_core.openhands_result_collector import (
    OPENHANDS_RESULT_COLLECTOR_VERSION,
    OpenHandsResultCollectorConfig,
    collect_openhands_result,
)


def valid_packet() -> AdapterTaskPacket:
    return AdapterTaskPacket(
        task_id="openhands-result-collector-v0",
        repo="alanua/jeeves",
        allowed_files=["tools/skeleton_core/openhands_result_collector.py"],
        forbidden_paths=[".env", ".git", ".ssh", "secrets", "tokens"],
        authority_level="level_2_local_diff",
        risk_level="yellow",
        expected_artifact="diff",
        task_instructions="Collect bounded OpenHands result.",
        fuel_policy=FuelPolicy(
            provider="openrouter",
            model="deepseek/deepseek-v4-flash:free",
            max_usd=1.0,
        ),
    )


def fake_git_runner_with_change(command: list[str]) -> subprocess.CompletedProcess[str]:
    if "status" in command and "--short" in command:
        return subprocess.CompletedProcess(
            command, 0, stdout=" M tools/skeleton_core/openhands_result_collector.py\n", stderr=""
        )
    if "diff" in command:
        return subprocess.CompletedProcess(
            command, 0, stdout="diff --git a/file b/file\n+change\n", stderr=""
        )
    return subprocess.CompletedProcess(command, 1, stdout="", stderr="unexpected command")


def fake_git_runner_no_change(command: list[str]) -> subprocess.CompletedProcess[str]:
    if "status" in command and "--short" in command:
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
    return subprocess.CompletedProcess(command, 1, stdout="", stderr="unexpected command")


def test_collects_allowed_change_and_writes_artifact(tmp_path: Path) -> None:
    artifact_file = tmp_path / "openhands-result.diff"

    report = collect_openhands_result(
        valid_packet(),
        config=OpenHandsResultCollectorConfig(diff_artifact_file=artifact_file),
        git_runner=fake_git_runner_with_change,
    )

    assert report.collector_version == OPENHANDS_RESULT_COLLECTOR_VERSION
    assert report.changed_files == ["tools/skeleton_core/openhands_result_collector.py"]
    assert report.artifact_paths == ["artifacts/openhands-result.diff"]
    assert report.diff_artifact_written is True
    assert artifact_file.exists()
    assert "+change" in artifact_file.read_text(encoding="utf-8")
    assert report.result.result.status == "success"
    assert report.result.result_validation.status == "valid_adapter_result"


def test_blocks_when_no_allowed_file_changes(tmp_path: Path) -> None:
    report = collect_openhands_result(
        valid_packet(),
        config=OpenHandsResultCollectorConfig(diff_artifact_file=tmp_path / "result.diff"),
        git_runner=fake_git_runner_no_change,
    )

    assert report.changed_files == []
    assert report.artifact_paths == []
    assert report.diff_artifact_written is False
    assert report.outside_allowed_changes == []
    assert report.result.result.status == "blocked"
    assert report.result.result.stop_reason == "no_allowed_file_changes"
    assert report.result.result_validation.status == "valid_adapter_result"


def test_invalid_packet_blocks_without_git_calls(tmp_path: Path) -> None:
    packet = valid_packet().model_copy(update={"allowed_files": []})
    called = False

    def git_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        nonlocal called
        called = True
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="must not run")

    report = collect_openhands_result(
        packet,
        config=OpenHandsResultCollectorConfig(diff_artifact_file=tmp_path / "result.diff"),
        git_runner=git_runner,
    )

    assert called is False
    assert report.result.result.status == "blocked"
    assert "missing_allowed_files" in report.result.result_validation.blocked_reasons


def test_status_outside_allowed_is_blocked(tmp_path: Path) -> None:
    def git_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        if "status" in command and "--short" in command:
            return subprocess.CompletedProcess(
                command, 0, stdout=" M tools/skeleton_core/other.py\n", stderr=""
            )
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="unexpected command")

    report = collect_openhands_result(
        valid_packet(),
        config=OpenHandsResultCollectorConfig(diff_artifact_file=tmp_path / "result.diff"),
        git_runner=git_runner,
    )

    assert report.changed_files == []
    assert report.result.result.status == "blocked"
    assert report.result.result.stop_reason == "outside_allowed_changes"
    assert report.outside_allowed_changes == ["tools/skeleton_core/other.py"]


def test_blocks_outside_allowed_changes_even_when_allowed_file_changed(tmp_path: Path) -> None:
    artifact_file = tmp_path / "openhands-result.diff"

    def git_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        if "status" in command and "--short" in command and "--" not in command:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=(
                    " M tools/skeleton_core/openhands_result_collector.py\n"
                    " M tools/skeleton_core/other.py\n"
                ),
                stderr="",
            )
        if "status" in command and "--short" in command:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=" M tools/skeleton_core/openhands_result_collector.py\n",
                stderr="",
            )
        if "diff" in command:
            return subprocess.CompletedProcess(command, 0, stdout="+change\n", stderr="")
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="unexpected command")

    report = collect_openhands_result(
        valid_packet(),
        config=OpenHandsResultCollectorConfig(diff_artifact_file=artifact_file),
        git_runner=git_runner,
    )

    assert report.changed_files == ["tools/skeleton_core/openhands_result_collector.py"]
    assert report.outside_allowed_changes == ["tools/skeleton_core/other.py"]
    assert report.result.result.status == "blocked"
    assert report.result.result.stop_reason == "outside_allowed_changes"
