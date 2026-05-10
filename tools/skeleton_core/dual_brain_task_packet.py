"""Typed packet contracts for Skeleton dual-brain workflows."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PrivacyLevel(StrEnum):
    PUBLIC_SAFE = "PUBLIC_SAFE"
    STRICT_REDACTION = "STRICT_REDACTION"
    INTERNAL_BHK = "INTERNAL_BHK"


class TaskRisk(StrEnum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"
    UNKNOWN = "UNKNOWN"


class DualBrainNode(StrEnum):
    CHATGPT_SKELETON = "chatgpt_skeleton"
    GEMINI_AUDITOR = "gemini_auditor"
    RUNNER = "runner"
    EXECUTOR = "executor"
    OLEKSII = "oleksii"


class ApprovalMode(StrEnum):
    NONE = "none"
    BEFORE_EXECUTION = "before_execution"
    BEFORE_PERSISTENCE = "before_persistence"
    ALWAYS = "always"


class PersistenceTarget(StrEnum):
    NONE = "none"
    GITHUB_ISSUE_COMMENT = "github_issue_comment"
    GITHUB_PUBLIC_KB = "github_public_kb"
    DRIVE_PRIVATE_MEMORY = "drive_private_memory"
    RUNNER_TRACE_ONLY = "runner_trace_only"
    LOCAL_ENCRYPTED = "local_encrypted"


class DualBrainSource(BaseModel):
    """A source allowed to influence a dual-brain task."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    source_type: Literal[
        "github_issue",
        "github_pr",
        "github_file",
        "drive_doc",
        "runner_output",
        "user_message",
        "private_handoff",
        "manual_note",
    ]
    reference: str
    privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC_SAFE
    verified: bool = False
    notes: str = ""


class DualBrainForbiddenAction(BaseModel):
    """An explicitly forbidden action for this task."""

    model_config = ConfigDict(extra="forbid")

    action: str
    reason: str = ""


class DualBrainQuestionSet(BaseModel):
    """Questions routed to each reasoning node."""

    model_config = ConfigDict(extra="forbid")

    for_gemini: list[str] = Field(default_factory=list)
    for_chatgpt: list[str] = Field(default_factory=list)
    for_runner: list[str] = Field(default_factory=list)


class DualBrainExpectedOutput(BaseModel):
    """Expected output contract for a bounded task."""

    model_config = ConfigDict(extra="forbid")

    output_type: Literal[
        "audit_packet",
        "review_packet",
        "code_patch",
        "runner_report",
        "decision_packet",
        "trace_packet",
        "handoff_packet",
    ]
    required_fields: list[str] = Field(default_factory=list)
    forbidden_fields: list[str] = Field(default_factory=list)
    public_safe_required: bool = True


class DualBrainTaskPacket(BaseModel):
    """Top-level packet for one bounded dual-brain cycle."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["dual_brain_task_packet.v1"] = "dual_brain_task_packet.v1"

    task_id: str
    parent_task_id: str = ""
    project: str
    title: str
    goal: str

    risk: TaskRisk = TaskRisk.UNKNOWN
    privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC_SAFE
    requested_by: str = "oleksii"

    confirmed_canon: str = ""
    evidence_summary: str = ""
    draft_artifact: str = ""

    sources_allowed: list[DualBrainSource] = Field(default_factory=list)
    sources_forbidden: list[str] = Field(default_factory=list)

    questions: DualBrainQuestionSet = Field(default_factory=DualBrainQuestionSet)
    expected_outputs: list[DualBrainExpectedOutput] = Field(default_factory=list)

    allowed_nodes: list[DualBrainNode] = Field(
        default_factory=lambda: [
            DualBrainNode.CHATGPT_SKELETON,
            DualBrainNode.GEMINI_AUDITOR,
            DualBrainNode.RUNNER,
        ]
    )

    executor_allowed: bool = False
    external_api_allowed: bool = False

    forbidden_actions: list[DualBrainForbiddenAction] = Field(default_factory=list)

    approval_mode: ApprovalMode = ApprovalMode.BEFORE_PERSISTENCE
    persistence_target: PersistenceTarget = PersistenceTarget.RUNNER_TRACE_ONLY

    max_model_rounds: int = Field(default=2, ge=1, le=5)
    max_runner_attempts: int = Field(default=1, ge=0, le=3)

    next_safe_step: str = ""


class DualBrainReviewPacket(BaseModel):
    """Result packet after a dual-brain review."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["dual_brain_review_packet.v1"] = "dual_brain_review_packet.v1"

    task_id: str
    reviewer_node: DualBrainNode
    decision: Literal[
        "accept",
        "revise",
        "block",
        "needs_oleksii_review",
        "unknown_needs_source",
    ]

    summary: str
    rationale: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    security_flags: list[str] = Field(default_factory=list)

    canon_claim: bool = False
    commands: list[str] = Field(default_factory=list)
    persistence_allowed: bool = False
    execution_allowed: bool = False

    next_safe_step: str


class DualBrainTracePacket(BaseModel):
    """Minimal trace metadata for a dual-brain interaction."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["dual_brain_trace_packet.v1"] = "dual_brain_trace_packet.v1"

    task_id: str
    parent_task_id: str = ""
    node_id: DualBrainNode

    input_hash: str
    output_hash: str

    decision_code: str
    privacy_level: PrivacyLevel
    timestamp_utc: str

    sources_read: list[str] = Field(default_factory=list)
    files_changed: list[str] = Field(default_factory=list)
    commands_run: list[str] = Field(default_factory=list)

    blocked_reason: str = ""
    human_approval_status: Literal[
        "not_required",
        "pending",
        "approved",
        "rejected",
        "unknown",
    ] = "unknown"
