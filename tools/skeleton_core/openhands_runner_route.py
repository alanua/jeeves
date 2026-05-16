"""OpenHands runner route v0 for Skeleton.

This module bridges the OpenHands adapter to a bounded live-run guard.
It is designed so tests can validate behavior without launching real OpenHands.

It does not merge, deploy, restart services, mutate GitHub labels, or read .env.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable
from pathlib import Path

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
from tools.skeleton_core.openhands_live_run_guard import (
    OpenHandsLiveRunGuardConfig,
    OpenHandsLiveRunGuardReport,
    run_openhands_live_guard,
)

OPENHANDS_RUNNER_ROUTE_VERSION = "openhands_runner_route.v0"

DEFAULT_SECRET_FILE = Path("/home/agent/agent-dev/runner-secrets/openrouter.env")


class OpenHandsRunnerRouteConfig(BaseModel):
    """Configuration for the OpenHands runner route."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    task_file: Path = Path("/tmp/skeleton-openhands-task.md")
    secret_file: Path = DEFAULT_SECRET_FILE
    adapter_config: OpenHandsAdapterConfig = Field(default_factory=OpenHandsAdapterConfig)
    timeout_seconds: int = 120
    stdout_log_file: Path = Path("/tmp/skeleton-openhands-live-run.stdout.log")
    stderr_log_file: Path = Path("/tmp/skeleton-openhands-live-run.stderr.log")
    openhands_tmux_session_name: str | None = None


class OpenHandsRunnerRouteReport(BaseModel):
    """Public-safe route report."""

    model_config = ConfigDict(extra="forbid")

    route_version: str = OPENHANDS_RUNNER_ROUTE_VERSION
    prepared: OpenHandsPreparedTask
    result: OpenHandsValidatedResult
    returncode: int | None
    stdout_tail: str = ""
    stderr_tail: str = ""
    timed_out: bool = False
    stdout_log_path: str = ""
    stderr_log_path: str = ""
    live_run: OpenHandsLiveRunGuardReport | None = None


RunnerFn = Callable[[list[str], dict[str, str]], subprocess.CompletedProcess[str]]
LiveRunFn = Callable[
    [list[str], dict[str, str], OpenHandsRunnerRouteConfig],
    OpenHandsLiveRunGuardReport,
]


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


def default_live_run(
    command: list[str],
    env: dict[str, str],
    config: OpenHandsRunnerRouteConfig,
) -> OpenHandsLiveRunGuardReport:
    """Run OpenHands through the bounded live-run guard."""

    def guarded_runner(
        guarded_command: list[str],
        timeout_seconds: int,
    ) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        merged_env.update(env)
        return subprocess.run(
            guarded_command,
            env=merged_env,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )

    api_key = env.get("LLM_API_KEY", "")
    return run_openhands_live_guard(
        command,
        config=OpenHandsLiveRunGuardConfig(
            timeout_seconds=config.timeout_seconds,
            stdout_log_file=config.stdout_log_file,
            stderr_log_file=config.stderr_log_file,
            openhands_tmux_session_name=config.openhands_tmux_session_name,
            secret_redaction_values=[api_key] if api_key else [],
        ),
        command_runner=guarded_runner,
    )


def default_runner(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Compatibility runner for injected unit tests.

    Real route execution should use default_live_run.
    """

    merged_env = os.environ.copy()
    merged_env.update(env)
    return subprocess.run(
        command,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def _status_from_live_report(
    live_report: OpenHandsLiveRunGuardReport,
) -> tuple[str, str, str]:
    if live_report.status == "completed" and live_report.returncode == 0:
        return "success", "passed", "openhands_returncode=0"
    if live_report.status == "no_changes":
        return "blocked", "blocked", "openhands_no_changes"
    if live_report.status == "timeout":
        return "failed", "failed", "openhands_timeout"
    if live_report.status == "cleanup_failed":
        return "failed", "failed", "openhands_cleanup_failed"
    if live_report.returncode is not None:
        return "failed", "failed", f"openhands_returncode={live_report.returncode}"
    return "failed", "failed", f"openhands_status={live_report.status}"


def run_openhands_route(
    packet: AdapterTaskPacket,
    *,
    config: OpenHandsRunnerRouteConfig | None = None,
    runner: RunnerFn | None = None,
    live_run: LiveRunFn = default_live_run,
    changed_files: list[str] | None = None,
    artifact_paths: list[str] | None = None,
) -> OpenHandsRunnerRouteReport:
    """Prepare, run, and validate a bounded OpenHands task.

    `changed_files` and `artifact_paths` are supplied by the caller or a later
    collector layer. This route intentionally avoids scanning arbitrary files.
    """

    resolved = config or OpenHandsRunnerRouteConfig()
    prepared = prepare_openhands_task(packet, str(resolved.task_file), resolved.adapter_config)

    resolved.task_file.write_text(prepared.task_text, encoding="utf-8")

    api_key = load_openrouter_key(resolved.secret_file)
    env = build_openhands_env(api_key, resolved.adapter_config)

    live_report: OpenHandsLiveRunGuardReport | None = None

    if runner is not None:
        completed = runner(prepared.command, env)
        returncode: int | None = completed.returncode
        stdout_tail = _tail(completed.stdout or "")
        stderr_tail = _tail(completed.stderr or "")
        timed_out = False
        stdout_log_path = ""
        stderr_log_path = ""
        executor_status = "success" if completed.returncode == 0 else "failed"
        validation_status = "passed" if completed.returncode == 0 else "failed"
        stop_reason = f"openhands_returncode={completed.returncode}"
    else:
        live_report = live_run(prepared.command, env, resolved)
        returncode = live_report.returncode
        stdout_tail = live_report.stdout_tail
        stderr_tail = live_report.stderr_tail
        timed_out = live_report.timed_out
        stdout_log_path = live_report.stdout_log_path
        stderr_log_path = live_report.stderr_log_path
        executor_status, validation_status, stop_reason = _status_from_live_report(live_report)

    validated = build_openhands_result(
        packet,
        executor_status=executor_status,
        changed_files=changed_files or [],
        artifact_paths=artifact_paths or [],
        validation_status=validation_status,
        risk_flags=[],
        stop_reason=stop_reason,
    )

    return OpenHandsRunnerRouteReport(
        prepared=prepared,
        result=validated,
        returncode=returncode,
        stdout_tail=stdout_tail,
        stderr_tail=stderr_tail,
        timed_out=timed_out,
        stdout_log_path=stdout_log_path,
        stderr_log_path=stderr_log_path,
        live_run=live_report,
    )
