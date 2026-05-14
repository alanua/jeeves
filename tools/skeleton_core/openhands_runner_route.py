"""OpenHands runner route v0 for Skeleton.

This module bridges the OpenHands adapter to an injectable process runner.
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

OPENHANDS_RUNNER_ROUTE_VERSION = "openhands_runner_route.v0"

DEFAULT_SECRET_FILE = Path("/home/agent/agent-dev/runner-secrets/openrouter.env")


class OpenHandsRunnerRouteConfig(BaseModel):
    """Configuration for the OpenHands runner route."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    task_file: Path = Path("/tmp/skeleton-openhands-task.md")
    secret_file: Path = DEFAULT_SECRET_FILE
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


RunnerFn = Callable[[list[str], dict[str, str]], subprocess.CompletedProcess[str]]


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


def default_runner(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Run OpenHands command with a merged environment."""

    merged_env = os.environ.copy()
    merged_env.update(env)
    return subprocess.run(
        command,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def run_openhands_route(
    packet: AdapterTaskPacket,
    *,
    config: OpenHandsRunnerRouteConfig | None = None,
    runner: RunnerFn = default_runner,
    changed_files: list[str] | None = None,
    artifact_paths: list[str] | None = None,
) -> OpenHandsRunnerRouteReport:
    """Prepare, run, and validate a bounded OpenHands task.

    `changed_files` and `artifact_paths` are supplied by the caller or a later
    collector layer. This v0 route intentionally avoids scanning arbitrary files.
    """

    resolved = config or OpenHandsRunnerRouteConfig()
    prepared = prepare_openhands_task(packet, str(resolved.task_file), resolved.adapter_config)

    resolved.task_file.write_text(prepared.task_text, encoding="utf-8")

    api_key = load_openrouter_key(resolved.secret_file)
    env = build_openhands_env(api_key, resolved.adapter_config)
    completed = runner(prepared.command, env)

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

    return OpenHandsRunnerRouteReport(
        prepared=prepared,
        result=validated,
        returncode=completed.returncode,
        stdout_tail=_tail(completed.stdout or ""),
        stderr_tail=_tail(completed.stderr or ""),
    )
