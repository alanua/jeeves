"""Local/offline workflow gate that enforces ready Skeleton skills."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

WorkflowGateStatus = Literal[
    "action_ready",
    "blocked_missing_required_skill",
    "blocked_failed_required_skill",
    "blocked_unsafe_or_policy_violation",
    "unknown_needs_review",
]

UNSAFE_PATTERNS = {
    "merge": r"\bmerge\b|auto-merge",
    "deploy": r"\bdeploy\b|deployment|release",
    "server": r"server ssh|\bssh\b|production server",
    "production_db": r"production db|production database|prod db",
    "secret": r"\.env|\bsecret\b|\bsecrets\b|\btoken\b|api key|apikey|credential|password",
}

PYTHON_UPDATE_REQUIREMENTS = {
    "local_black_applied": {"ok"},
    "format_preflight": {"format_ready"},
    "head_sha_verified": {"ok"},
}
PR_REVIEW_REQUIREMENTS = {
    "pr_review_gate": {"ready_for_chatgpt_review"},
    "ci_status": {"success"},
}
RUNNER_REQUIREMENTS = {
    "runner_env_check": {"ready_for_read_only_validation"},
    "runner_command_pack": {"ready"},
}
QUEUE_REQUIREMENTS = {
    "queue_state": {"has_next_runnable_issue", "next_runnable_issue"},
    "runner_report_ingest": {"green_report", "approved_equivalent"},
}
ACTIONS_REQUIREMENTS = {
    "github_actions_runner_control": {
        "workflow_success_report",
        "workflow_failed_report",
        "workflow_cancelled_report",
    },
}


class WorkflowGateInput(BaseModel):
    """Public-safe workflow action packet."""

    model_config = ConfigDict(extra="ignore")

    action: str = ""
    repository: str = ""
    branch: str = ""
    changed_files: list[str] = Field(default_factory=list)
    python_files_changed: bool = False
    preflights: dict[str, str] = Field(default_factory=dict)
    requested_next_action: str = ""
    queue_next_runnable_issue: int | None = None
    human_override: bool = False


class WorkflowGatePacket(BaseModel):
    """Deterministic workflow gate decision."""

    model_config = ConfigDict(extra="forbid")

    status: WorkflowGateStatus
    requested_next_action: str
    required_skills: list[str] = Field(default_factory=list)
    missing_or_failed_skills: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    allowed_to_continue: bool = False
    merge_allowed: bool = False
    deploy_allowed: bool = False
    next_safe_step: str


def _normalized(value: str | None) -> str:
    return (value or "").strip().casefold().replace("-", "_")


def _combined_text(packet: WorkflowGateInput) -> str:
    parts = [
        packet.action,
        packet.requested_next_action,
        packet.repository,
        packet.branch,
        "\n".join(packet.changed_files),
        "\n".join(f"{key}={value}" for key, value in packet.preflights.items()),
    ]
    return "\n".join(parts)


def _unsafe_blockers(packet: WorkflowGateInput) -> list[str]:
    text = _combined_text(packet)
    blockers = []
    for name, pattern in UNSAFE_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            blockers.append(f"Unsafe workflow action detected: {name}")
    if _normalized(packet.requested_next_action) in {"merge", "deploy", "release"}:
        blockers.append("Requested next action is not allowed for Skeleton workflow-gate")
    return sorted(set(blockers))


def _is_python_update(packet: WorkflowGateInput) -> bool:
    action = _normalized(packet.action)
    requested = _normalized(packet.requested_next_action)
    return (
        packet.python_files_changed
        or action in {"github_update_file", "update_file"}
        or requested == "update_file"
    )


def _is_pr_review(packet: WorkflowGateInput) -> bool:
    action = _normalized(packet.action)
    requested = _normalized(packet.requested_next_action)
    return action in {"pr_ready", "ready_for_review", "pr_review"} or requested in {
        "ready_for_review",
        "mark_ready_for_review",
    }


def _is_runner_dispatch(packet: WorkflowGateInput) -> bool:
    action = _normalized(packet.action)
    requested = _normalized(packet.requested_next_action)
    return action in {"runner_dispatch", "runner_task"} or requested == "runner_dispatch"


def _is_queue_advance(packet: WorkflowGateInput) -> bool:
    action = _normalized(packet.action)
    requested = _normalized(packet.requested_next_action)
    return action in {
        "queue_advance",
        "start_next_issue",
        "open_next_issue",
    } or requested in {
        "queue_advance",
        "start_next_issue",
        "open_next_issue",
    }


def _is_actions_report(packet: WorkflowGateInput) -> bool:
    action = _normalized(packet.action)
    requested = _normalized(packet.requested_next_action)
    return action in {"actions_report", "use_actions_report"} or requested in {
        "actions_report",
        "use_actions_report",
    }


def _requirements(packet: WorkflowGateInput) -> dict[str, set[str]]:
    requirements: dict[str, set[str]] = {}
    if _is_python_update(packet):
        requirements.update(PYTHON_UPDATE_REQUIREMENTS)
    if _is_pr_review(packet):
        requirements.update(PR_REVIEW_REQUIREMENTS)
    if _is_runner_dispatch(packet):
        requirements.update(RUNNER_REQUIREMENTS)
    if _is_queue_advance(packet):
        requirements.update(QUEUE_REQUIREMENTS)
    if _is_actions_report(packet):
        requirements.update(ACTIONS_REQUIREMENTS)
    return requirements


def _missing_or_failed(
    packet: WorkflowGateInput,
    requirements: dict[str, set[str]],
) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    failed: list[str] = []
    preflights = {_normalized(key): _normalized(value) for key, value in packet.preflights.items()}
    for skill, allowed_values in requirements.items():
        value = preflights.get(_normalized(skill))
        normalized_allowed = {_normalized(item) for item in allowed_values}
        if value in {None, "", "missing", "not_checked", "unknown"}:
            missing.append(skill)
        elif value not in normalized_allowed:
            failed.append(f"{skill}={value}")
    if "queue_state" in requirements and packet.queue_next_runnable_issue is not None:
        missing = [item for item in missing if item != "queue_state"]
        failed = [item for item in failed if not item.startswith("queue_state=")]
    return sorted(missing), sorted(failed)


def _next_step(status: WorkflowGateStatus, missing_or_failed: list[str]) -> str:
    if status == "action_ready":
        return "Continue with the requested action, then verify the resulting state."
    if status == "blocked_unsafe_or_policy_violation":
        return "Stop and review unsafe workflow scope before continuing."
    if (
        any(item.startswith("local_black_applied") for item in missing_or_failed)
        or "local_black_applied" in missing_or_failed
    ):
        return "Run real local Black on outgoing Python content before update_file."
    if (
        any(item.startswith("format_preflight") for item in missing_or_failed)
        or "format_preflight" in missing_or_failed
    ):
        return "Run format-preflight and require format_ready before continuing."
    if (
        any(item.startswith("pr_review_gate") for item in missing_or_failed)
        or "pr_review_gate" in missing_or_failed
    ):
        return "Run pr-review-gate and require ready_for_chatgpt_review."
    if (
        any(item.startswith("runner_env_check") for item in missing_or_failed)
        or "runner_env_check" in missing_or_failed
    ):
        return "Run runner-env-check before dispatching runner work."
    if (
        any(item.startswith("runner_report_ingest") for item in missing_or_failed)
        or "runner_report_ingest" in missing_or_failed
    ):
        return "Ingest the previous runner report before advancing the queue."
    if (
        any(item.startswith("github_actions_runner_control") for item in missing_or_failed)
        or "github_actions_runner_control" in missing_or_failed
    ):
        return "Build a safe GitHub Actions runner-control report before using Actions as evidence."
    if status == "unknown_needs_review":
        return "Manual review required; no matching workflow gate was selected."
    return "Satisfy the missing or failed required Skeleton skill before continuing."


def build_workflow_gate(packet: WorkflowGateInput) -> WorkflowGatePacket:
    """Enforce ready Skeleton skills before the requested workflow action."""
    unsafe_blockers = _unsafe_blockers(packet)
    requirements = _requirements(packet)
    required_skills = sorted(requirements)
    missing, failed = _missing_or_failed(packet, requirements)
    missing_or_failed = [*missing, *failed]

    if unsafe_blockers:
        status: WorkflowGateStatus = "blocked_unsafe_or_policy_violation"
    elif failed:
        status = "blocked_failed_required_skill"
    elif missing:
        status = "blocked_missing_required_skill"
    elif requirements or packet.human_override:
        status = "action_ready"
    else:
        status = "unknown_needs_review"

    allowed = status == "action_ready"
    return WorkflowGatePacket(
        status=status,
        requested_next_action=packet.requested_next_action or packet.action or "unknown",
        required_skills=required_skills,
        missing_or_failed_skills=missing_or_failed,
        blockers=unsafe_blockers,
        allowed_to_continue=allowed,
        merge_allowed=False,
        deploy_allowed=False,
        next_safe_step=_next_step(status, missing_or_failed),
    )


def build_workflow_gate_from_json(raw_json: str) -> WorkflowGatePacket:
    """Validate local JSON text and build a workflow gate packet."""
    return build_workflow_gate(WorkflowGateInput.model_validate_json(raw_json))
