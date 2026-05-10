"""Typed contracts for bounded execution handoff.

Sprint 5 phase 1 is dry-run only:
- no shell command execution
- no file writes
- no PR creation
- no merge
- no deploy
- no canon writes
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExecutionMode(StrEnum):
    DRY_RUN = "dry_run"


class ExecutionDecision(StrEnum):
    WOULD_EXECUTE = "would_execute"
    BLOCKED = "blocked"
    FAILED = "failed"


class ExecutionActionType(StrEnum):
    NOOP = "noop"
    COMMENT_ONLY = "comment_only"
    LABEL_TRANSITION_ONLY = "label_transition_only"


class ExecutionSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: Literal["github_issue", "github_comment", "audit_report"]
    reference: str
    verified: bool = False
    notes: str = ""


class ExecutionAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str
    action_type: ExecutionActionType
    description: str
    dry_run_only: bool = True
    command: str = ""
    writes_files: bool = False
    network_access: bool = False


class ExecutionPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["bounded_execution_packet.v1"] = "bounded_execution_packet.v1"

    issue_number: int
    issue_url: str
    title: str

    mode: ExecutionMode = ExecutionMode.DRY_RUN
    trigger_labels: list[str] = Field(default_factory=list)

    audit_verified: bool
    audit_status: str
    audit_comment_url: str = ""
    audit_summary: str = ""

    objective: str = ""
    planned_actions: list[ExecutionAction] = Field(default_factory=list)
    sources: list[ExecutionSource] = Field(default_factory=list)

    forbidden_actions: list[str] = Field(
        default_factory=lambda: [
            "execute_shell_commands",
            "write_files",
            "create_pr",
            "merge",
            "deploy",
            "write_canon",
            "print_secrets",
        ]
    )

    executor_allowed: bool = False
    file_writes_allowed: bool = False
    pr_creation_allowed: bool = False
    merge_allowed: bool = False
    deploy_allowed: bool = False
    canon_write_allowed: bool = False

    next_safe_step: str = "Post dry-run execution report and transition labels."


class ExecutionReportPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["bounded_execution_report.v1"] = "bounded_execution_report.v1"

    issue_number: int
    issue_url: str = ""
    decision: ExecutionDecision
    execution_status: Literal["dry_run_complete", "blocked", "failed"]

    packet: ExecutionPacket | None = None
    blocked_reasons: list[str] = Field(default_factory=list)
    labels_added: list[str] = Field(default_factory=list)
    labels_removed: list[str] = Field(default_factory=list)
    posted_comment_url: str = ""

    commands_executed: list[str] = Field(default_factory=list)
    files_changed: list[str] = Field(default_factory=list)

    next_safe_step: str
