"""Bounded OpenHands result collector v0.

This module collects only explicitly allowed file changes and builds a public-safe
adapter result. It does not scan the whole repository, call GitHub, merge, deploy,
restart services, or read secrets.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.adapter_contract import AdapterTaskPacket, validate_task_packet
from tools.skeleton_core.openhands_adapter import (
    OpenHandsValidatedResult,
    build_openhands_result,
)

OPENHANDS_RESULT_COLLECTOR_VERSION = "openhands_result_collector.v0"


class OpenHandsResultCollectorConfig(BaseModel):
    """Configuration for bounded result collection."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    repo_root: Path = Path(".")
    diff_artifact_file: Path = Path("/tmp/skeleton-openhands-artifacts/openhands-result.diff")
    public_artifact_path: str = "artifacts/openhands-result.diff"


class OpenHandsResultCollectorReport(BaseModel):
    """Public-safe collector report."""

    model_config = ConfigDict(extra="forbid")

    collector_version: str = OPENHANDS_RESULT_COLLECTOR_VERSION
    changed_files: list[str] = Field(default_factory=list)
    artifact_paths: list[str] = Field(default_factory=list)
    outside_allowed_changes: list[str] = Field(default_factory=list)
    git_status_short: dict[str, str] = Field(default_factory=dict)
    full_git_status_short: str = ""
    diff_artifact_written: bool = False
    result: OpenHandsValidatedResult


GitRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def default_git_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a bounded git command."""

    return subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _status_path_from_line(line: str) -> str:
    """Extract a path from `git status --short` output.

    Git short status uses two status columns followed by a space and a path.
    Examples:
    - " M path/to/file.py"
    - "?? path/to/file.py"
    - "R  old.py -> new.py"
    """
    value = line[2:].strip() if len(line) >= 2 else ""
    if " -> " in value:
        value = value.split(" -> ", 1)[1].strip()
    return value


def _status_for_allowed_file(
    *,
    repo_root: Path,
    allowed_file: str,
    git_runner: GitRunner,
) -> str:
    command = [
        "git",
        "-C",
        str(repo_root),
        "status",
        "--short",
        "--",
        allowed_file,
    ]
    completed = git_runner(command)
    if completed.returncode != 0:
        raise RuntimeError(f"git status failed for {allowed_file}: {completed.stderr}")
    return completed.stdout.strip()


def _changed_files_from_status(
    *,
    allowed_files: list[str],
    status_by_file: dict[str, str],
) -> list[str]:
    allowed_set = set(allowed_files)
    changed: list[str] = []

    for status_output in status_by_file.values():
        for line in status_output.splitlines():
            path = _status_path_from_line(line)
            if path in allowed_set:
                changed.append(path)

    return sorted(set(changed))


def _full_status(
    *,
    repo_root: Path,
    git_runner: GitRunner,
) -> str:
    command = ["git", "-C", str(repo_root), "status", "--short"]
    completed = git_runner(command)
    if completed.returncode != 0:
        raise RuntimeError(f"git status failed: {completed.stderr}")
    return completed.stdout.strip()


def _all_changed_paths_from_status(status_output: str) -> list[str]:
    paths: list[str] = []
    for line in status_output.splitlines():
        path = _status_path_from_line(line)
        if path:
            paths.append(path)
    return sorted(set(paths))


def _outside_allowed_changes(
    *,
    full_status_output: str,
    allowed_files: list[str],
) -> list[str]:
    allowed_set = set(allowed_files)
    return [
        path
        for path in _all_changed_paths_from_status(full_status_output)
        if path not in allowed_set
    ]


def _diff_for_file(
    *,
    repo_root: Path,
    changed_file: str,
    git_runner: GitRunner,
) -> str:
    command = [
        "git",
        "-C",
        str(repo_root),
        "diff",
        "--",
        changed_file,
    ]
    completed = git_runner(command)
    if completed.returncode != 0:
        raise RuntimeError(f"git diff failed for {changed_file}: {completed.stderr}")
    return completed.stdout


def _write_diff_artifact(
    *,
    repo_root: Path,
    changed_files: list[str],
    artifact_file: Path,
    git_runner: GitRunner,
) -> bool:
    artifact_file.parent.mkdir(parents=True, exist_ok=True)

    chunks: list[str] = []
    for changed_file in changed_files:
        chunks.append(f"# diff for {changed_file}\n")
        chunks.append(
            _diff_for_file(repo_root=repo_root, changed_file=changed_file, git_runner=git_runner)
        )
        chunks.append("\n")

    artifact_file.write_text("".join(chunks), encoding="utf-8")
    return True


def collect_openhands_result(
    packet: AdapterTaskPacket,
    *,
    config: OpenHandsResultCollectorConfig | None = None,
    git_runner: GitRunner = default_git_runner,
) -> OpenHandsResultCollectorReport:
    """Collect changed allowed files and build a validated adapter result."""

    resolved = config or OpenHandsResultCollectorConfig()
    task_validation = validate_task_packet(packet)

    status_by_file: dict[str, str] = {}
    full_status_output = ""
    outside_changes: list[str] = []
    changed_files: list[str] = []
    artifact_paths: list[str] = []
    artifact_written = False

    if task_validation.status == "valid_task_packet":
        full_status_output = _full_status(repo_root=resolved.repo_root, git_runner=git_runner)
        outside_changes = _outside_allowed_changes(
            full_status_output=full_status_output,
            allowed_files=task_validation.normalized_allowed_files,
        )

        for allowed_file in task_validation.normalized_allowed_files:
            status_by_file[allowed_file] = _status_for_allowed_file(
                repo_root=resolved.repo_root,
                allowed_file=allowed_file,
                git_runner=git_runner,
            )

        changed_files = _changed_files_from_status(
            allowed_files=task_validation.normalized_allowed_files,
            status_by_file=status_by_file,
        )

        if changed_files:
            artifact_written = _write_diff_artifact(
                repo_root=resolved.repo_root,
                changed_files=changed_files,
                artifact_file=resolved.diff_artifact_file,
                git_runner=git_runner,
            )
            artifact_paths = [resolved.public_artifact_path]

    if task_validation.status != "valid_task_packet":
        executor_status = "blocked"
        validation_status = "blocked"
        stop_reason = "task_packet_blocked"
    elif outside_changes:
        executor_status = "blocked"
        validation_status = "blocked"
        stop_reason = "outside_allowed_changes"
    elif not changed_files:
        executor_status = "blocked"
        validation_status = "blocked"
        stop_reason = "no_allowed_file_changes"
    else:
        executor_status = "success"
        validation_status = "passed"
        stop_reason = "allowed_file_changes_collected"

    result = build_openhands_result(
        packet,
        executor_status=executor_status,
        changed_files=changed_files,
        artifact_paths=artifact_paths,
        validation_status=validation_status,
        risk_flags=[],
        stop_reason=stop_reason,
    )

    return OpenHandsResultCollectorReport(
        changed_files=changed_files,
        artifact_paths=artifact_paths,
        outside_allowed_changes=outside_changes,
        git_status_short=status_by_file,
        full_git_status_short=full_status_output,
        diff_artifact_written=artifact_written,
        result=result,
    )
