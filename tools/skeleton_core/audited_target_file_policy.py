"""Validator for audited explicit target-file task packets.

This module is intentionally narrow. It only validates whether a post-audit
task packet is safe to treat as a plan packet. It does not create branches,
commits, pull requests, merges, deployments, or runtime changes.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

POLICY_NAME = "audited_explicit_target_files.v1"
VALID_PLAN_PACKET = "valid_plan_packet"
BLOCKED = "blocked"

REQUIRED_LABELS = {
    "agent:task",
    "agent:audited",
    "agent:plan-ready",
    "risk:yellow",
}

RUNNER_LABELS = {
    "runner:any",
    "runner:hetzner",
}

EXPECTED_PACKET_TYPE = "pr_creation"
EXPECTED_PACKET_COMMAND = "python -m tools.skeleton_core.cli create-pr"

UNSAFE_COMMAND_SUBSTRINGS = (
    ";",
    "&&",
    "||",
    "|",
    ">",
    ">>",
    "$(",
    "`",
)

ALLOWLISTED_VALIDATION_COMMANDS = {
    "python -m pytest tests/skeleton_core/test_project_audit_route.py",
    "python -m pytest tests/skeleton_core/test_cli_create_pr.py",
    "python -m pytest tests/skeleton_core/test_audited_target_file_policy.py",
    "python -m tools.skeleton_core.cli validate-state",
}

ROOT_OR_SHORTCUT_TARGETS = {
    "",
    ".",
    "./",
    "-A",
}

DIRECTORY_SHORTCUT_TARGETS = {
    "tools",
    "tools/",
    "tests",
    "tests/",
    "src",
    "src/",
    "canon",
    "canon/",
    "knowledge_base",
    "knowledge_base/",
}


class AuditedTaskPacket(BaseModel):
    """Legacy-compatible local task packet shape."""

    model_config = ConfigDict(extra="allow")

    id: int
    type: str
    command: str
    safety_level: str = ""
    pr_creation_allowed: bool = False
    target_files: list[str] = Field(default_factory=list)
    pr_title: str = ""
    pr_body: str = ""


class AuditedTargetFilePolicyInput(BaseModel):
    """Input for audited explicit target-file validation."""

    model_config = ConfigDict(extra="forbid")

    source_issue: int
    source_repo: str = ""
    labels: list[str]
    audit_status: str = "accepted"
    audit_blocked_reasons: list[str] = Field(default_factory=list)
    security_flags: list[str] = Field(default_factory=list)
    merge_allowed: bool = False
    deploy_allowed: bool = False
    human_review_required: bool = True
    packet: AuditedTaskPacket
    requested_files: list[str] = Field(default_factory=list)
    validation_commands: list[str] = Field(default_factory=list)


class AuditedTargetFilePolicyResult(BaseModel):
    """Result of audited explicit target-file validation."""

    model_config = ConfigDict(extra="forbid")

    policy: str = POLICY_NAME
    status: Literal["valid_plan_packet", "blocked"]
    blocked_reasons: list[str] = Field(default_factory=list)
    target_files: list[str] = Field(default_factory=list)
    requested_files: list[str] = Field(default_factory=list)
    next_safe_step: str = ""


def _has_wildcard(value: str) -> bool:
    return any(token in value for token in ("*", "?", "["))


def _is_path_traversal(value: str) -> bool:
    path = PurePosixPath(value)
    return ".." in path.parts


def _target_file_block_reasons(value: str) -> list[str]:
    reasons: list[str] = []
    normalized = value.strip().replace("\\", "/")

    if normalized != value:
        reasons.append("target_file_contains_backslash")

    if normalized in ROOT_OR_SHORTCUT_TARGETS:
        reasons.append("dot_or_root_target_file")

    if normalized in DIRECTORY_SHORTCUT_TARGETS or normalized.endswith("/"):
        reasons.append("directory_shortcut_target_file")

    if normalized.startswith("/"):
        reasons.append("absolute_target_file")

    if _is_path_traversal(normalized):
        reasons.append("path_traversal_target_file")

    if _has_wildcard(normalized):
        reasons.append("wildcard_target_file")

    return reasons


def _validation_command_block_reasons(command: str) -> list[str]:
    stripped = command.strip()
    reasons: list[str] = []

    if not stripped:
        reasons.append("empty_validation_command")
        return reasons

    for unsafe in UNSAFE_COMMAND_SUBSTRINGS:
        if unsafe in stripped:
            reasons.append("unsafe_validation_command")
            break

    if stripped not in ALLOWLISTED_VALIDATION_COMMANDS:
        reasons.append("validation_command_not_allowlisted")

    return reasons


def validate_audited_target_file_policy(
    data: AuditedTargetFilePolicyInput | dict[str, Any],
) -> AuditedTargetFilePolicyResult:
    """Validate an audited explicit target-file packet.

    The function is deterministic and side-effect free.
    """

    input_data = (
        data
        if isinstance(data, AuditedTargetFilePolicyInput)
        else AuditedTargetFilePolicyInput.model_validate(data)
    )

    blocked: list[str] = []
    labels = set(input_data.labels)

    for label in sorted(REQUIRED_LABELS):
        if label not in labels:
            blocked.append(f"missing_{label.replace(':', '_').replace('-', '_')}")

    if not (labels & RUNNER_LABELS):
        blocked.append("missing_runner_label")

    if input_data.audit_status != "accepted":
        blocked.append("missing_accepted_audit")

    if input_data.audit_blocked_reasons:
        blocked.append("audit_blocked_reasons_not_empty")

    if input_data.security_flags:
        blocked.append("security_flags_not_empty")

    if input_data.merge_allowed:
        blocked.append("merge_allowed_true")

    if input_data.deploy_allowed:
        blocked.append("deploy_allowed_true")

    if not input_data.human_review_required:
        blocked.append("human_review_required_false")

    packet = input_data.packet

    if packet.id != input_data.source_issue:
        blocked.append("packet_issue_mismatch")

    if packet.type != EXPECTED_PACKET_TYPE:
        blocked.append("invalid_packet_type")

    if packet.command != EXPECTED_PACKET_COMMAND:
        blocked.append("invalid_packet_command")

    if not packet.pr_creation_allowed:
        blocked.append("pr_creation_not_allowed")

    target_files = [item.strip() for item in packet.target_files if item.strip()]

    if not target_files:
        blocked.append("missing_target_files")

    if len(target_files) != len(set(target_files)):
        blocked.append("duplicate_target_files")

    for target in target_files:
        blocked.extend(_target_file_block_reasons(target))

    requested_files = input_data.requested_files or target_files
    target_set = set(target_files)

    for requested in requested_files:
        if requested not in target_set:
            blocked.append("requested_file_not_in_target_files")
        blocked.extend(_target_file_block_reasons(requested))

    for command in input_data.validation_commands:
        blocked.extend(_validation_command_block_reasons(command))

    unique_blocked = sorted(set(blocked))
    status: Literal["valid_plan_packet", "blocked"] = (
        BLOCKED if unique_blocked else VALID_PLAN_PACKET
    )

    return AuditedTargetFilePolicyResult(
        status=status,
        blocked_reasons=unique_blocked,
        target_files=target_files,
        requested_files=requested_files,
        next_safe_step=(
            "Stop and fix the audited target-file packet."
            if unique_blocked
            else "Packet is valid for the next reviewed lifecycle stage."
        ),
    )
