from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tools.skeleton_core.queue_commit_executor import (
    prepare_or_execute_commit,
    validate_commit_preparation,
)


def write_report(tmp_path: Path, *, status: str = "ready") -> Path:
    path = tmp_path / "queue-report.json"
    path.write_text(
        json.dumps(
            {
                "commit_preparation": {
                    "status": status,
                    "commit_files": ["QUEUE_COMMIT.py"],
                    "suggested_commit_message": "chore(skeleton): queue commit",
                    "blocked_reasons": [],
                }
            }
        ),
        encoding="utf-8",
    )
    return path


def fake_git_runner_success(command: list[str], **kwargs):
    if "status" in command and "--short" in command:
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="?? QUEUE_COMMIT.py\n",
            stderr="",
        )
    if "add" in command:
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
    if "commit" in command:
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="[branch abc123] chore(skeleton): queue commit\n",
            stderr="",
        )
    if "rev-parse" in command:
        return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
    return subprocess.CompletedProcess(command, 1, stdout="", stderr="unexpected")


def test_validate_commit_preparation_ready() -> None:
    blocked, commit_files, message = validate_commit_preparation(
        commit_preparation={
            "status": "ready",
            "commit_files": ["QUEUE_COMMIT.py"],
            "suggested_commit_message": "chore(skeleton): queue commit",
        },
        git_status_short={"QUEUE_COMMIT.py": "?? QUEUE_COMMIT.py"},
    )

    assert blocked == []
    assert commit_files == ["QUEUE_COMMIT.py"]
    assert message == "chore(skeleton): queue commit"


def test_validate_blocks_outside_dirty_file() -> None:
    blocked, _, _ = validate_commit_preparation(
        commit_preparation={
            "status": "ready",
            "commit_files": ["QUEUE_COMMIT.py"],
            "suggested_commit_message": "chore(skeleton): queue commit",
        },
        git_status_short={
            "QUEUE_COMMIT.py": "?? QUEUE_COMMIT.py",
            "OTHER.py": "?? OTHER.py",
        },
    )

    assert "dirty_paths_outside_commit_files" in blocked


def test_validate_blocks_unsafe_path() -> None:
    blocked, _, _ = validate_commit_preparation(
        commit_preparation={
            "status": "ready",
            "commit_files": ["../secret.py"],
            "suggested_commit_message": "chore(skeleton): queue commit",
        },
        git_status_short={"../secret.py": "?? ../secret.py"},
    )

    assert "path_traversal" in blocked


def test_prepare_commit_dry_run_ready(tmp_path: Path) -> None:
    report_file = write_report(tmp_path)

    report = prepare_or_execute_commit(
        report_file=report_file,
        repo_root=tmp_path,
        execute=False,
        git_runner=fake_git_runner_success,
    )

    assert report.status == "ready"
    assert report.mode == "dry_run"
    assert report.commit_files == ["QUEUE_COMMIT.py"]
    assert report.commit_sha == ""


def test_execute_commit_runs_add_and_commit(tmp_path: Path) -> None:
    report_file = write_report(tmp_path)
    seen_commands: list[list[str]] = []

    def git_runner(command: list[str], **kwargs):
        seen_commands.append(command)
        return fake_git_runner_success(command, **kwargs)

    report = prepare_or_execute_commit(
        report_file=report_file,
        repo_root=tmp_path,
        execute=True,
        git_runner=git_runner,
    )

    assert report.status == "committed"
    assert report.mode == "execute"
    assert report.commit_sha == "abc123"
    assert any(command[3] == "add" for command in seen_commands)
    assert any(command[3] == "commit" for command in seen_commands)


def test_prepare_blocks_when_commit_preparation_not_ready(tmp_path: Path) -> None:
    report_file = write_report(tmp_path, status="blocked")

    report = prepare_or_execute_commit(
        report_file=report_file,
        repo_root=tmp_path,
        execute=True,
        git_runner=fake_git_runner_success,
    )

    assert report.status == "blocked"
    assert "commit_preparation_not_ready" in report.blocked_reasons
