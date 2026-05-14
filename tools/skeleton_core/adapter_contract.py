"""Skeleton adapter contract core v0.

This module defines a small deterministic contract between the Skeleton control
layer and external executors. It is side-effect free: it does not run tools,
create branches, open pull requests, merge, deploy, read secrets, or access
production systems.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ADAPTER_CONTRACT_VERSION = "skeleton_adapter_contract.v0"

AuthorityLevel = Literal[
    "level_0_report",
    "level_1_draft_artifact",
    "level_2_local_diff",
    "level_3_draft_pr",
    "level_4_human_approved_action",
    "level_5_forbidden",
]
RiskLevel = Literal["green", "yellow", "red"]
ExecutorStatus = Literal["success", "blocked", "failed", "partial"]
ValidationStatus = Literal["not_run", "passed", "failed", "blocked"]
ContractStatus = Literal["valid_task_packet", "valid_adapter_result", "blocked"]

UNSAFE_PATH_PARTS = {".env", ".git", ".ssh", "id_rsa", "id_ed25519"}
UNSAFE_PATH_SUFFIXES = (".pem", ".key", ".p12", ".pfx")
ROOT_OR_SHORTCUT_TARGETS = {"", ".", "./", "-A"}
DIRECTORY_SHORTCUT_TARGETS = {
    "app",
    "app/",
    "api",
    "api/",
    "bot",
    "bot/",
    "db",
    "db/",
    "tools",
    "tools/",
    "tests",
    "tests/",
    "knowledge_base",
    "knowledge_base/",
}
BLOCKING_RISK_FLAGS = {
    "secret",
    "secrets",
    "secret_access",
    "forbidden_scope",
    "package_install",
    "server_access",
    "ssh_access",
    "database_access",
    "production_access",
    "merge_attempt",
    "deploy_attempt",
}


class FuelPolicy(BaseModel):
    """Budget and provider envelope for an executor."""

    model_config = ConfigDict(extra="forbid")

    provider: str = "none"
    model: str = ""
    max_usd: float | None = None
    allow_free_models: bool = True


class AdapterTaskPacket(BaseModel):
    """Bounded input packet sent from Skeleton to an external adapter."""

    model_config = ConfigDict(extra="forbid")

    task_id: str
    repo: str
    allowed_files: list[str]
    forbidden_paths: list[str] = Field(default_factory=list)
    authority_level: AuthorityLevel
    risk_level: RiskLevel
    expected_artifact: str
    fuel_policy: FuelPolicy = Field(default_factory=FuelPolicy)


class AdapterExecutionResult(BaseModel):
    """Public-safe result packet returned by an executor adapter."""

    model_config = ConfigDict(extra="forbid")

    status: ExecutorStatus
    executor: str
    changed_files: list[str] = Field(default_factory=list)
    artifact_paths: list[str] = Field(default_factory=list)
    validation_status: ValidationStatus = "not_run"
    risk_flags: list[str] = Field(default_factory=list)
    stop_reason: str = ""


class ContractValidationResult(BaseModel):
    """Side-effect-free validation result for task packets or adapter results."""

    model_config = ConfigDict(extra="forbid")

    contract_version: str = ADAPTER_CONTRACT_VERSION
    status: ContractStatus
    blocked_reasons: list[str] = Field(default_factory=list)
    normalized_allowed_files: list[str] = Field(default_factory=list)
    normalized_forbidden_paths: list[str] = Field(default_factory=list)
    next_safe_step: str = ""


def _normalize_path(value: str) -> str:
    return value.strip().replace("\\", "/")


def _has_wildcard(value: str) -> bool:
    return any(token in value for token in ("*", "?", "["))


def _is_path_traversal(value: str) -> bool:
    return ".." in PurePosixPath(value).parts


def _path_block_reasons(value: str, *, field_name: str) -> list[str]:
    normalized = _normalize_path(value)
    reasons: list[str] = []

    if normalized != value:
        reasons.append(f"{field_name}_contains_backslash")
    if normalized in ROOT_OR_SHORTCUT_TARGETS:
        reasons.append(f"{field_name}_is_root_or_shortcut")
    if normalized in DIRECTORY_SHORTCUT_TARGETS or normalized.endswith("/"):
        reasons.append(f"{field_name}_is_directory_shortcut")
    if normalized.startswith("/"):
        reasons.append(f"{field_name}_is_absolute_path")
    if _is_path_traversal(normalized):
        reasons.append(f"{field_name}_contains_path_traversal")
    if _has_wildcard(normalized):
        reasons.append(f"{field_name}_contains_wildcard")

    parts = set(PurePosixPath(normalized).parts)
    if parts.intersection(UNSAFE_PATH_PARTS):
        reasons.append(f"{field_name}_contains_secret_or_control_path")
    if normalized.endswith(UNSAFE_PATH_SUFFIXES):
        reasons.append(f"{field_name}_contains_secret_file_suffix")

    return reasons


def _path_matches_scope(path: str, scope: str) -> bool:
    normalized_path = _normalize_path(path)
    normalized_scope = _normalize_path(scope).rstrip("/")
    return normalized_path == normalized_scope or normalized_path.startswith(
        f"{normalized_scope}/"
    )


def _unique_normalized(values: list[str]) -> tuple[list[str], list[str]]:
    normalized = [_normalize_path(value) for value in values if value.strip()]
    reasons: list[str] = []
    if len(normalized) != len(set(normalized)):
        reasons.append("duplicate_paths")
    return normalized, reasons


def validate_task_packet(
    packet: AdapterTaskPacket | dict[str, Any],
) -> ContractValidationResult:
    """Validate a bounded adapter task packet."""

    task = packet if isinstance(packet, AdapterTaskPacket) else AdapterTaskPacket.model_validate(packet)
    blocked: list[str] = []

    allowed_files, allowed_reasons = _unique_normalized(task.allowed_files)
    forbidden_paths, forbidden_reasons = _unique_normalized(task.forbidden_paths)
    blocked.extend(f"allowed_files_{reason}" for reason in allowed_reasons)
    blocked.extend(f"forbidden_paths_{reason}" for reason in forbidden_reasons)

    if not task.task_id.strip():
        blocked.append("missing_task_id")
    if not task.repo.strip():
        blocked.append("missing_repo")
    if not allowed_files:
        blocked.append("missing_allowed_files")
    if not task.expected_artifact.strip():
        blocked.append("missing_expected_artifact")
    if task.authority_level == "level_5_forbidden":
        blocked.append("authority_level_forbidden")

    for allowed_file in allowed_files:
        blocked.extend(_path_block_reasons(allowed_file, field_name="allowed_file"))

    for forbidden_path in forbidden_paths:
        blocked.extend(_path_block_reasons(forbidden_path, field_name="forbidden_path"))

    for allowed_file in allowed_files:
        for forbidden_path in forbidden_paths:
            if _path_matches_scope(allowed_file, forbidden_path):
                blocked.append("allowed_file_overlaps_forbidden_path")

    fuel = task.fuel_policy
    if fuel.provider != "none":
        if not fuel.model.strip():
            blocked.append("fuel_model_missing")
        if fuel.max_usd is None:
            blocked.append("fuel_max_usd_missing")
        elif fuel.max_usd < 0:
            blocked.append("fuel_max_usd_negative")

    unique_blocked = sorted(set(blocked))
    return ContractValidationResult(
        status="blocked" if unique_blocked else "valid_task_packet",
        blocked_reasons=unique_blocked,
        normalized_allowed_files=allowed_files,
        normalized_forbidden_paths=forbidden_paths,
        next_safe_step=(
            "Stop and fix the adapter task packet."
            if unique_blocked
            else "Adapter task packet is valid for a bounded executor."
        ),
    )


def validate_adapter_result(
    packet: AdapterTaskPacket | dict[str, Any],
    result: AdapterExecutionResult | dict[str, Any],
) -> ContractValidationResult:
    """Validate an executor result against its original task packet."""

    task = packet if isinstance(packet, AdapterTaskPacket) else AdapterTaskPacket.model_validate(packet)
    adapter_result = (
        result
        if isinstance(result, AdapterExecutionResult)
        else AdapterExecutionResult.model_validate(result)
    )

    task_validation = validate_task_packet(task)
    blocked = list(task_validation.blocked_reasons)
    allowed_files = task_validation.normalized_allowed_files
    allowed_set = set(allowed_files)

    changed_files, changed_reasons = _unique_normalized(adapter_result.changed_files)
    artifact_paths, artifact_reasons = _unique_normalized(adapter_result.artifact_paths)
    blocked.extend(f"changed_files_{reason}" for reason in changed_reasons)
    blocked.extend(f"artifact_paths_{reason}" for reason in artifact_reasons)

    for changed_file in changed_files:
        if changed_file not in allowed_set:
            blocked.append("changed_file_outside_allowed_scope")
        blocked.extend(_path_block_reasons(changed_file, field_name="changed_file"))

    for artifact_path in artifact_paths:
        blocked.extend(_path_block_reasons(artifact_path, field_name="artifact_path"))

    if adapter_result.status == "success" and not artifact_paths:
        blocked.append("success_without_artifact")
    if adapter_result.status == "success" and adapter_result.validation_status in {
        "failed",
        "blocked",
    }:
        blocked.append("success_with_failed_validation")

    normalized_flags = {flag.strip().lower() for flag in adapter_result.risk_flags}
    if normalized_flags.intersection(BLOCKING_RISK_FLAGS):
        blocked.append("blocking_risk_flag_present")

    unique_blocked = sorted(set(blocked))
    return ContractValidationResult(
        status="blocked" if unique_blocked else "valid_adapter_result",
        blocked_reasons=unique_blocked,
        normalized_allowed_files=allowed_files,
        normalized_forbidden_paths=task_validation.normalized_forbidden_paths,
        next_safe_step=(
            "Stop and review the adapter result."
            if unique_blocked
            else "Adapter result is valid for artifact review."
        ),
    )
