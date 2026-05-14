"""Local tool runner v0.

Runs a small allowlist of local no-API validation tools and returns a
public-safe structured report.

This module does not call LLM APIs, GitHub APIs, read secrets, push, merge,
deploy, restart services, or touch production systems.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

LOCAL_TOOL_RUNNER_VERSION = "local_tool_runner.v0"

LocalToolName = Literal["py_compile", "pytest", "ruff_check", "black_check"]
LocalToolStatus = Literal["success", "failed", "blocked"]


class LocalToolRequest(BaseModel):
    """Bounded local tool request."""

    model_config = ConfigDict(extra="forbid")

    tool: LocalToolName
    targets: list[str] = Field(default_factory=list)
    timeout_seconds: int = 120
    cwd: str = "."


class LocalToolReport(BaseModel):
    """Public-safe local tool report."""

    model_config = ConfigDict(extra="forbid")

    runner_version: str = LOCAL_TOOL_RUNNER_VERSION
    status: LocalToolStatus
    tool: LocalToolName
    command: list[str] = Field(default_factory=list)
    returncode: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""
    blocked_reasons: list[str] = Field(default_factory=list)


def _tail(value: str, limit: int = 4000) -> str:
    return value[-limit:]


def _normalize_target(target: str) -> str:
    return target.strip().replace("\\", "/")


def _target_block_reasons(target: str) -> list[str]:
    normalized = _normalize_target(target)
    reasons: list[str] = []

    if not normalized:
        reasons.append("empty_target")
    if normalized.startswith("/"):
        reasons.append("absolute_target")
    if ".." in Path(normalized).parts:
        reasons.append("path_traversal")
    if normalized in {".", "./", ""}:
        reasons.append("root_target")
    if normalized.startswith((".git/", ".ssh/", ".env")) or normalized in {
        ".git",
        ".ssh",
        ".env",
    }:
        reasons.append("secret_or_control_path")
    if any(token in normalized for token in ("*", "?", "[")):
        reasons.append("wildcard_target")

    return reasons


def validate_local_tool_request(request: LocalToolRequest) -> list[str]:
    reasons: list[str] = []

    if request.timeout_seconds <= 0:
        reasons.append("timeout_must_be_positive")
    if not request.targets:
        reasons.append("missing_targets")

    for target in request.targets:
        reasons.extend(_target_block_reasons(target))

    return sorted(set(reasons))


def build_local_tool_command(request: LocalToolRequest) -> list[str]:
    targets = [_normalize_target(target) for target in request.targets]

    python = sys.executable

    if request.tool == "py_compile":
        return [python, "-m", "py_compile", *targets]
    if request.tool == "pytest":
        return [python, "-m", "pytest", "-q", *targets]
    if request.tool == "ruff_check":
        return [python, "-m", "ruff", "check", *targets]
    if request.tool == "black_check":
        return [python, "-m", "black", "--check", *targets]

    raise ValueError(f"Unsupported local tool: {request.tool}")


def _timeout_completed_process(
    command: list[str],
    timeout_seconds: int,
    exc: subprocess.TimeoutExpired,
) -> subprocess.CompletedProcess[str]:
    stdout = exc.stdout or ""
    stderr = exc.stderr or ""
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", errors="replace")

    stderr = f"{stderr}\nlocal_tool_timeout_seconds={timeout_seconds}".strip()
    return subprocess.CompletedProcess(command, 124, stdout=stdout, stderr=stderr)


def run_local_tool(
    request: LocalToolRequest,
    *,
    runner=subprocess.run,
) -> LocalToolReport:
    """Run one allowlisted local tool request."""

    blocked_reasons = validate_local_tool_request(request)
    command = build_local_tool_command(request) if not blocked_reasons else []

    if blocked_reasons:
        return LocalToolReport(
            status="blocked",
            tool=request.tool,
            command=command,
            blocked_reasons=blocked_reasons,
        )

    env = os.environ.copy()
    try:
        completed = runner(
            command,
            cwd=request.cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=request.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        completed = _timeout_completed_process(command, request.timeout_seconds, exc)

    return LocalToolReport(
        status="success" if completed.returncode == 0 else "failed",
        tool=request.tool,
        command=command,
        returncode=completed.returncode,
        stdout_tail=_tail(completed.stdout or ""),
        stderr_tail=_tail(completed.stderr or ""),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one allowlisted local tool")
    parser.add_argument(
        "tool",
        choices=["py_compile", "pytest", "ruff_check", "black_check"],
        help="Local tool to run",
    )
    parser.add_argument("targets", nargs="+", help="Target files/directories")
    parser.add_argument("--cwd", default=".", help="Working directory")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout seconds")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report = run_local_tool(
        LocalToolRequest(
            tool=args.tool,
            targets=args.targets,
            timeout_seconds=args.timeout,
            cwd=args.cwd,
        )
    )

    print(
        json.dumps(
            report.model_dump(mode="json"),
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0 if report.status == "success" else 2


if __name__ == "__main__":
    raise SystemExit(main())
