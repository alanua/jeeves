"""Explicit queue commit executor v0.

Reads a queue report containing commit_preparation and, only with --execute,
creates a local git commit for the prepared files.

Default mode is dry-run. This module does not push, merge, deploy, open PRs,
call GitHub APIs, mutate labels, read secrets, or touch production systems.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

QUEUE_COMMIT_EXECUTOR_VERSION = "queue_commit_executor.v0"

FORBIDDEN_PATH_NAMES = {".git", ".ssh", ".env"}
FORBIDDEN_PATH_PREFIXES = ("secrets/", "tokens/", "server/", "production/", "db/")


class QueueCommitExecutorReport(BaseModel):
    """Public-safe explicit commit executor report."""

    model_config = ConfigDict(extra="forbid")

    executor_version: str = QUEUE_COMMIT_EXECUTOR_VERSION
    status: str
    mode: str = "dry_run"
    report_file: str = ""
    commit_files: list[str] = Field(default_factory=list)
    suggested_commit_message: str = ""
    blocked_reasons: list[str] = Field(default_factory=list)
    git_status_short: dict[str, str] = Field(default_factory=dict)
    commit_sha: str = ""
    stdout_tail: str = ""
    stderr_tail: str = ""


def _tail(value: str, limit: int = 4000) -> str:
    return value[-limit:]


def _normalize_path(path: str) -> str:
    return path.strip().replace("\\", "/")


def _path_block_reasons(path: str) -> list[str]:
    normalized = _normalize_path(path)
    reasons: list[str] = []

    if not normalized:
        reasons.append("empty_path")
    if normalized.startswith("/"):
        reasons.append("absolute_path")
    if ".." in Path(normalized).parts:
        reasons.append("path_traversal")
    if normalized in {".", "./"}:
        reasons.append("root_path")
    if normalized in FORBIDDEN_PATH_NAMES:
        reasons.append("forbidden_path")
    if any(normalized.startswith(f"{name}/") for name in FORBIDDEN_PATH_NAMES):
        reasons.append("forbidden_path")
    if any(normalized.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
        reasons.append("forbidden_path")
    if any(token in normalized for token in ("*", "?", "[")):
        reasons.append("wildcard_path")

    return reasons


def _git_status_path_from_line(line: str) -> str:
    value = line[2:].strip() if len(line) >= 2 else ""
    if " -> " in value:
        value = value.split(" -> ", 1)[1].strip()
    return value


def _git_status_short(*, repo_root: Path, git_runner) -> dict[str, str]:
    completed = git_runner(
        ["git", "-C", str(repo_root), "status", "--short"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git status failed: {completed.stderr}")

    result: dict[str, str] = {}
    for line in (completed.stdout or "").splitlines():
        path = _git_status_path_from_line(line)
        if path:
            result[path] = line
    return result


def _git_commit_sha(*, repo_root: Path, git_runner) -> str:
    completed = git_runner(
        ["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return (completed.stdout or "").strip()


def _load_commit_preparation(report_file: Path) -> dict[str, Any]:
    data = json.loads(report_file.read_text(encoding="utf-8"))

    if "commit_preparation" in data:
        return data["commit_preparation"] or {}

    # Fallback for possible future wrapped reports.
    queue_report = data.get("queue_report") or {}
    if "commit_preparation" in queue_report:
        return queue_report["commit_preparation"] or {}

    return {}


def validate_commit_preparation(
    *,
    commit_preparation: dict[str, Any],
    git_status_short: dict[str, str],
) -> tuple[list[str], list[str], str]:
    blocked_reasons: list[str] = []

    status = str(commit_preparation.get("status") or "")
    commit_files = [
        _normalize_path(item) for item in list(commit_preparation.get("commit_files") or [])
    ]
    suggested_commit_message = str(commit_preparation.get("suggested_commit_message") or "").strip()

    if status != "ready":
        blocked_reasons.append("commit_preparation_not_ready")
    if not commit_files:
        blocked_reasons.append("missing_commit_files")
    if not suggested_commit_message:
        blocked_reasons.append("missing_commit_message")

    for path in commit_files:
        blocked_reasons.extend(_path_block_reasons(path))

    dirty_paths = sorted(git_status_short)
    outside_dirty = sorted(set(dirty_paths) - set(commit_files))
    missing_dirty = sorted(set(commit_files) - set(dirty_paths))

    if outside_dirty:
        blocked_reasons.append("dirty_paths_outside_commit_files")
    if missing_dirty:
        blocked_reasons.append("commit_files_not_dirty")

    return sorted(set(blocked_reasons)), commit_files, suggested_commit_message


def prepare_or_execute_commit(
    *,
    report_file: Path,
    repo_root: Path = Path("."),
    execute: bool = False,
    git_runner=subprocess.run,
) -> QueueCommitExecutorReport:
    """Prepare or explicitly execute one local commit from commit_preparation."""

    commit_preparation = _load_commit_preparation(report_file)
    status_short = _git_status_short(repo_root=repo_root, git_runner=git_runner)
    blocked_reasons, commit_files, suggested_commit_message = validate_commit_preparation(
        commit_preparation=commit_preparation,
        git_status_short=status_short,
    )

    if blocked_reasons:
        return QueueCommitExecutorReport(
            status="blocked",
            mode="execute" if execute else "dry_run",
            report_file=str(report_file),
            commit_files=commit_files,
            suggested_commit_message=suggested_commit_message,
            blocked_reasons=blocked_reasons,
            git_status_short=status_short,
        )

    if not execute:
        return QueueCommitExecutorReport(
            status="ready",
            mode="dry_run",
            report_file=str(report_file),
            commit_files=commit_files,
            suggested_commit_message=suggested_commit_message,
            blocked_reasons=[],
            git_status_short=status_short,
        )

    add_completed = git_runner(
        ["git", "-C", str(repo_root), "add", *commit_files],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if add_completed.returncode != 0:
        return QueueCommitExecutorReport(
            status="failed",
            mode="execute",
            report_file=str(report_file),
            commit_files=commit_files,
            suggested_commit_message=suggested_commit_message,
            blocked_reasons=["git_add_failed"],
            git_status_short=status_short,
            stdout_tail=_tail(add_completed.stdout or ""),
            stderr_tail=_tail(add_completed.stderr or ""),
        )

    commit_completed = git_runner(
        ["git", "-C", str(repo_root), "commit", "-m", suggested_commit_message],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if commit_completed.returncode != 0:
        return QueueCommitExecutorReport(
            status="failed",
            mode="execute",
            report_file=str(report_file),
            commit_files=commit_files,
            suggested_commit_message=suggested_commit_message,
            blocked_reasons=["git_commit_failed"],
            git_status_short=_git_status_short(repo_root=repo_root, git_runner=git_runner),
            stdout_tail=_tail(commit_completed.stdout or ""),
            stderr_tail=_tail(commit_completed.stderr or ""),
        )

    return QueueCommitExecutorReport(
        status="committed",
        mode="execute",
        report_file=str(report_file),
        commit_files=commit_files,
        suggested_commit_message=suggested_commit_message,
        blocked_reasons=[],
        git_status_short=_git_status_short(repo_root=repo_root, git_runner=git_runner),
        commit_sha=_git_commit_sha(repo_root=repo_root, git_runner=git_runner),
        stdout_tail=_tail(commit_completed.stdout or ""),
        stderr_tail=_tail(commit_completed.stderr or ""),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare or execute a queued local commit")
    parser.add_argument("--report-file", required=True, help="Queue report JSON file")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually run git add and git commit. Default is dry-run.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        report = prepare_or_execute_commit(
            report_file=Path(args.report_file),
            repo_root=Path(args.repo_root),
            execute=args.execute,
        )
    except Exception as exc:
        report = QueueCommitExecutorReport(
            status="failed",
            mode="execute" if args.execute else "dry_run",
            report_file=str(args.report_file),
            blocked_reasons=[type(exc).__name__],
            stderr_tail=str(exc),
        )

    print(
        json.dumps(
            report.model_dump(mode="json"),
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0 if report.status in {"ready", "committed"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
