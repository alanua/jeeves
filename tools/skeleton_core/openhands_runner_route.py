"""OpenHands runner route v0 for Skeleton.

This module bridges the OpenHands adapter to an injectable process runner.
It is designed so tests can validate behavior without launching real OpenHands.

It does not merge, deploy, restart services, mutate GitHub labels, or read .env.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.adapter_contract import AdapterTaskPacket
from tools.skeleton_core.openhands_adapter import (
    OpenHandsAdapterConfig,
    OpenHandsPreparedTask,
    OpenHandsValidatedResult,
    build_openhands_env,
    build_openhands_result,
    prepare_openhands_task,
)
from tools.skeleton_core.openhands_result_collector import (
    GitRunner,
    OpenHandsResultCollectorConfig,
    OpenHandsResultCollectorReport,
    collect_openhands_result,
)

OPENHANDS_RUNNER_ROUTE_VERSION = "openhands_runner_route.v0"

DEFAULT_SECRET_FILE = Path("/home/agent/agent-dev/runner-secrets/openrouter.env")


class OpenHandsRunnerRouteConfig(BaseModel):
    """Configuration for the OpenHands runner route."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    task_file: Path = Path("/tmp/skeleton-openhands-task.md")
    secret_file: Path = DEFAULT_SECRET_FILE
    timeout_seconds: int = 300
    adapter_config: OpenHandsAdapterConfig = Field(default_factory=OpenHandsAdapterConfig)


class OpenHandsRunnerRouteReport(BaseModel):
    """Public-safe route report."""

    model_config = ConfigDict(extra="forbid")

    route_version: str = OPENHANDS_RUNNER_ROUTE_VERSION
    prepared: OpenHandsPreparedTask
    result: OpenHandsValidatedResult
    returncode: int
    stdout_tail: str = ""
    stderr_tail: str = ""
    collector_report: OpenHandsResultCollectorReport | None = None


RunnerFn = Callable[..., subprocess.CompletedProcess[str]]

INTERACTIVE_CONFIRMATION_MARKERS = (
    "Yes, proceed",
    "No, dismiss",
    "Confirm",
    "Confirm 1 action",
    "Confirm 2 action",
    "OpenHands CLI terminal UI may not work correctly",
    "interactive UI may not render correctly",
    "TTY_INTERACTIVE",
)


def _looks_like_interactive_confirmation(stdout: str, stderr: str) -> bool:
    combined = f"{stdout}\n{stderr}"
    return any(marker in combined for marker in INTERACTIVE_CONFIRMATION_MARKERS)


def _tail(value: str, limit: int = 4000) -> str:
    return value[-limit:]


def load_openrouter_key(secret_file: Path = DEFAULT_SECRET_FILE) -> str:
    """Load OPENROUTER_API_KEY from a runner-local secret file.

    The returned value is a secret and must not be printed or placed in public
    reports.
    """

    if not secret_file.exists():
        raise FileNotFoundError(f"OpenRouter secret file not found: {secret_file}")

    values: dict[str, str] = {}
    for raw_line in secret_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')

    api_key = values.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY missing from secret file")
    if any(token in api_key for token in ("cat >", "export ", "\n", "\r", "\t")):
        raise ValueError("OPENROUTER_API_KEY secret file looks corrupted")

    return api_key


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
    stderr = f"{stderr}\nopenhands_timeout_seconds={timeout_seconds}".strip()
    return subprocess.CompletedProcess(command, 124, stdout=stdout, stderr=stderr)


def default_runner(
    command: list[str],
    env: dict[str, str],
    timeout_seconds: int = 300,
) -> subprocess.CompletedProcess[str]:
    """Run OpenHands command with a merged environment and timeout."""

    merged_env = os.environ.copy()
    merged_env.update(env)
    try:
        return subprocess.run(
            command,
            env=merged_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return _timeout_completed_process(command, timeout_seconds, exc)


def run_openhands_route(
    packet: AdapterTaskPacket,
    *,
    config: OpenHandsRunnerRouteConfig | None = None,
    runner: RunnerFn = default_runner,
    changed_files: list[str] | None = None,
    artifact_paths: list[str] | None = None,
    collector_config: OpenHandsResultCollectorConfig | None = None,
    git_runner: GitRunner | None = None,
) -> OpenHandsRunnerRouteReport:
    """Prepare, run, collect, and validate a bounded OpenHands task.

    If `changed_files` or `artifact_paths` are supplied, they are used directly.
    Otherwise, a bounded result collector inspects only packet.allowed_files.
    """

    resolved = config or OpenHandsRunnerRouteConfig()
    prepared = prepare_openhands_task(packet, str(resolved.task_file), resolved.adapter_config)

    resolved.task_file.write_text(prepared.task_text, encoding="utf-8")

    api_key = load_openrouter_key(resolved.secret_file)
    env = build_openhands_env(api_key, resolved.adapter_config)
    completed = runner(prepared.command, env, resolved.timeout_seconds)

    timeout_occurred = completed.returncode == 124

    collector_report = None
    if changed_files is None and artifact_paths is None:
        collector_kwargs = {}
        if collector_config is not None:
            collector_kwargs["config"] = collector_config
        if git_runner is not None:
            collector_kwargs["git_runner"] = git_runner

        collector_report = collect_openhands_result(packet, **collector_kwargs)
        validated = collector_report.result
    else:
        executor_status = "success" if completed.returncode == 0 else "failed"
        validation_status = "passed" if completed.returncode == 0 else "failed"

        validated = build_openhands_result(
            packet,
            executor_status=executor_status,
            changed_files=changed_files or [],
            artifact_paths=artifact_paths or [],
            validation_status=validation_status,
            risk_flags=[],
            stop_reason=f"openhands_returncode={completed.returncode}",
        )

    if timeout_occurred:
        timeout_changed_files = []
        timeout_artifact_paths = []
        timeout_risk_flags = ["timeout"]

        if collector_report is not None:
            timeout_changed_files = collector_report.changed_files
            timeout_artifact_paths = collector_report.artifact_paths
            if collector_report.outside_allowed_changes:
                timeout_risk_flags.append("outside_allowed_changes")
        else:
            timeout_changed_files = changed_files or []
            timeout_artifact_paths = artifact_paths or []

        validated = build_openhands_result(
            packet,
            executor_status="blocked",
            changed_files=timeout_changed_files,
            artifact_paths=timeout_artifact_paths,
            validation_status="blocked",
            risk_flags=timeout_risk_flags,
            stop_reason="openhands_timeout",
        )

    if (
        collector_report is not None
        and completed.returncode == 0
        and validated.result.status == "blocked"
        and validated.result.stop_reason == "no_allowed_file_changes"
        and _looks_like_interactive_confirmation(completed.stdout or "", completed.stderr or "")
    ):
        validated = build_openhands_result(
            packet,
            executor_status="blocked",
            changed_files=[],
            artifact_paths=[],
            validation_status="blocked",
            risk_flags=["interactive_confirmation_required"],
            stop_reason="interactive_confirmation_required",
        )

    return OpenHandsRunnerRouteReport(
        prepared=prepared,
        result=validated,
        returncode=completed.returncode,
        stdout_tail=_tail(completed.stdout or ""),
        stderr_tail=_tail(completed.stderr or ""),
        collector_report=collector_report,
    )
