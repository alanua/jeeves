"""OpenHands adapter v0 for Skeleton.

This module prepares bounded OpenHands tasks and validates returned artifacts
through the Skeleton adapter contract. It does not run OpenHands by itself,
read secrets, create branches, push, merge, deploy, or access production.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from tools.skeleton_core.adapter_contract import (
    AdapterExecutionResult,
    AdapterTaskPacket,
    ContractValidationResult,
    validate_adapter_result,
    validate_task_packet,
)

OPENHANDS_ADAPTER_VERSION = "openhands_adapter.v0"


class OpenHandsAdapterConfig(BaseModel):
    """Runtime configuration for an OpenHands invocation wrapper."""

    model_config = ConfigDict(extra="forbid")

    executable: str = "/home/agent/.local/bin/openhands"
    model: str = "deepseek/deepseek-v4-flash:free"
    base_url: str = "https://openrouter.ai/api/v1"
    suppress_banner: bool = True


class OpenHandsPreparedTask(BaseModel):
    """Public-safe prepared task metadata."""

    model_config = ConfigDict(extra="forbid")

    adapter_version: str = OPENHANDS_ADAPTER_VERSION
    task_text: str
    command: list[str]
    env_keys: list[str]
    task_validation: ContractValidationResult


class OpenHandsValidatedResult(BaseModel):
    """Executor result plus Skeleton contract validation."""

    model_config = ConfigDict(extra="forbid")

    adapter_version: str = OPENHANDS_ADAPTER_VERSION
    result: AdapterExecutionResult
    result_validation: ContractValidationResult


def _format_list(values: list[str]) -> str:
    if not values:
        return "- none"
    return "\n".join(f"- {value}" for value in values)


def build_openhands_task_text(packet: AdapterTaskPacket | dict[str, Any]) -> str:
    """Render a bounded OpenHands task file from an adapter task packet."""

    task = (
        packet
        if isinstance(packet, AdapterTaskPacket)
        else AdapterTaskPacket.model_validate(packet)
    )
    fuel = task.fuel_policy

    return f"""You are a bounded coding executor inside the Skeleton project.

Task id:
{task.task_id}

Repository:
{task.repo}

Authority level:
{task.authority_level}

Risk level:
{task.risk_level}

Expected artifact:
{task.expected_artifact}

Allowed files:
{_format_list(task.allowed_files)}

Forbidden paths:
{_format_list(task.forbidden_paths)}

Fuel policy:
- provider: {fuel.provider}
- model: {fuel.model}
- max_usd: {fuel.max_usd}
- allow_free_models: {fuel.allow_free_models}

Hard boundaries:
- Do not read .env, .git, .ssh, secrets, tokens, SSH keys, server config, DB, or production.
- Do not install packages.
- Do not push, merge, deploy, restart services, or change labels.
- Do not read or edit files outside the allowed files list.
- Return changed files, validation result, git diff summary, and stop.
"""


def build_openhands_command(
    task_file: str,
    config: OpenHandsAdapterConfig | None = None,
) -> list[str]:
    """Build the OpenHands CLI command."""

    resolved = config or OpenHandsAdapterConfig()
    return [
        resolved.executable,
        "--override-with-envs",
        "-f",
        task_file,
    ]


def build_openhands_env(
    api_key: str,
    config: OpenHandsAdapterConfig | None = None,
) -> dict[str, str]:
    """Build the OpenHands LLM environment.

    The returned environment contains the secret value because the process needs
    it. Public metadata must expose only key names, never values.
    """

    resolved = config or OpenHandsAdapterConfig()
    env = {
        "LLM_API_KEY": api_key,
        "LLM_MODEL": resolved.model,
        "LLM_BASE_URL": resolved.base_url,
    }
    if resolved.suppress_banner:
        env["OPENHANDS_SUPPRESS_BANNER"] = "1"
    return env


def prepare_openhands_task(
    packet: AdapterTaskPacket | dict[str, Any],
    task_file: str,
    config: OpenHandsAdapterConfig | None = None,
) -> OpenHandsPreparedTask:
    """Prepare public-safe OpenHands task metadata."""

    resolved = config or OpenHandsAdapterConfig()
    task_validation = validate_task_packet(packet)
    env_keys = sorted(build_openhands_env("__redacted__", resolved).keys())

    return OpenHandsPreparedTask(
        task_text=build_openhands_task_text(packet),
        command=build_openhands_command(task_file, resolved),
        env_keys=env_keys,
        task_validation=task_validation,
    )


def build_openhands_result(
    packet: AdapterTaskPacket | dict[str, Any],
    *,
    executor_status: str,
    changed_files: list[str],
    artifact_paths: list[str],
    validation_status: str,
    risk_flags: list[str],
    stop_reason: str,
) -> OpenHandsValidatedResult:
    """Build and validate an OpenHands adapter result."""

    result = AdapterExecutionResult(
        status=executor_status,
        executor=OPENHANDS_ADAPTER_VERSION,
        changed_files=changed_files,
        artifact_paths=artifact_paths,
        validation_status=validation_status,
        risk_flags=risk_flags,
        stop_reason=stop_reason,
    )

    return OpenHandsValidatedResult(
        result=result,
        result_validation=validate_adapter_result(packet, result),
    )
