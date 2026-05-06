"""Local offline PR review gate for Skeleton controller flow."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PRReviewGateStatus = Literal[
    "ready_for_chatgpt_review",
    "blocked_disallowed_files",
    "blocked_failed_ci",
    "blocked_scope_mismatch",
    "blocked_runtime_change",
    "blocked_unsafe_text",
    "unknown_needs_review",
]
RiskLevel = Literal["GREEN", "YELLOW", "ORANGE", "RED", "UNKNOWN"]

UNSAFE_TEXT_PATTERNS = {
    "merge": r"\bmerge\b|auto-merge",
    "deploy": r"\bdeploy\b|deployment|release",
    "server": r"server ssh|\bssh\b|production server",
    "production_db": r"production db|production database|prod db",
    "env": r"\.env|environment secret|env file",
    "secret": r"\bsecret\b|\bsecrets\b|\btoken\b|api key|credential|password",
    "network": r"live network|external service|external api|http[s]?://",
}
RUNTIME_PREFIXES = (
    "app/",
    "alembic/",
    "db/",
    "migrations/",
    "scripts/",
)
RUNTIME_FILENAMES = (
    "docker-compose.yml",
    "Dockerfile",
    ".env",
)


class SourceIssuePacket(BaseModel):
    """Public-safe source issue constraints."""

    model_config = ConfigDict(extra="ignore")

    issue_number: int
    risk_level: RiskLevel = "UNKNOWN"
    allowed_files: list[str] = Field(default_factory=list)
    test_only: bool = True


class CIStatus(BaseModel):
    """Public-safe CI status."""

    model_config = ConfigDict(extra="ignore")

    status: str | None = None
    conclusion: str | None = None


class PRReviewGateInput(BaseModel):
    """Public-safe PR review export."""

    model_config = ConfigDict(extra="ignore")

    repository: str
    pr_number: int
    title: str
    draft: bool = True
    source_issue: SourceIssuePacket | None = None
    changed_files: list[str] = Field(default_factory=list)
    ci: CIStatus | None = None
    body: str = ""


class PRReviewGatePacket(BaseModel):
    """Deterministic PR review gate decision."""

    model_config = ConfigDict(extra="forbid")

    status: PRReviewGateStatus
    repository: str
    pr_number: int
    source_issue: int | None = None
    changed_files_ok: bool
    ci_ok: bool
    scope_ok: bool
    blockers: list[str] = Field(default_factory=list)
    merge_allowed: bool = False
    deploy_allowed: bool = False
    next_safe_step: str


def _unsafe_text_blockers(packet: PRReviewGateInput) -> list[str]:
    text = "\n".join([packet.title, packet.body])
    blockers = []
    for name, pattern in UNSAFE_TEXT_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            blockers.append(f"Unsafe PR text detected: {name}")
    return sorted(set(blockers))


def _runtime_files(files: list[str]) -> list[str]:
    runtime_files = []
    for path in files:
        normalized = path.strip()
        if normalized in RUNTIME_FILENAMES or normalized.startswith(RUNTIME_PREFIXES):
            runtime_files.append(normalized)
    return sorted(set(runtime_files))


def _disallowed_files(packet: PRReviewGateInput) -> list[str]:
    if packet.source_issue is None or not packet.source_issue.allowed_files:
        return []
    allowed = set(packet.source_issue.allowed_files)
    return sorted(path for path in packet.changed_files if path not in allowed)


def _ci_ok(packet: PRReviewGateInput) -> bool:
    if packet.ci is None:
        return False
    return packet.ci.status == "completed" and packet.ci.conclusion == "success"


def _source_issue_ambiguous(packet: PRReviewGateInput) -> bool:
    if packet.source_issue is None:
        return True
    return packet.source_issue.risk_level not in {"GREEN", "YELLOW"}


def _next_step(status: PRReviewGateStatus) -> str:
    if status == "ready_for_chatgpt_review":
        return "ChatGPT review PR diff before any merge decision."
    if status == "blocked_failed_ci":
        return "Fix or rerun CI before ChatGPT review."
    if status == "blocked_disallowed_files":
        return "Restrict PR to source issue allowed files before review."
    if status == "blocked_runtime_change":
        return "Remove runtime/app changes or create a separately approved higher-risk task."
    if status == "blocked_unsafe_text":
        return "Stop and review safety blockers before continuing."
    if status == "blocked_scope_mismatch":
        return "Align PR scope with source issue before review."
    return "Manual review required before any merge decision."


def build_pr_review_gate(packet: PRReviewGateInput) -> PRReviewGatePacket:
    """Build a local/offline PR review gate decision."""
    blockers: list[str] = []
    unsafe_blockers = _unsafe_text_blockers(packet)
    runtime_files = _runtime_files(packet.changed_files)
    disallowed_files = _disallowed_files(packet)
    ci_ok = _ci_ok(packet)

    if _source_issue_ambiguous(packet):
        blockers.append("Missing or unsupported source issue risk level")
    if disallowed_files:
        blockers.extend(f"File outside allowed scope: {path}" for path in disallowed_files)
    if not ci_ok:
        blockers.append("Required CI is not completed successfully")
    if packet.source_issue and packet.source_issue.test_only and runtime_files:
        blockers.extend(
            f"Runtime/app file changed in test-only task: {path}" for path in runtime_files
        )
    blockers.extend(unsafe_blockers)

    if unsafe_blockers:
        status: PRReviewGateStatus = "blocked_unsafe_text"
    elif packet.source_issue and packet.source_issue.test_only and runtime_files:
        status = "blocked_runtime_change"
    elif disallowed_files:
        status = "blocked_disallowed_files"
    elif not ci_ok:
        status = "blocked_failed_ci" if packet.ci is not None else "unknown_needs_review"
    elif _source_issue_ambiguous(packet):
        status = "unknown_needs_review"
    elif not packet.changed_files:
        status = "unknown_needs_review"
        blockers.append("No changed files provided")
    else:
        status = "ready_for_chatgpt_review"

    return PRReviewGatePacket(
        status=status,
        repository=packet.repository,
        pr_number=packet.pr_number,
        source_issue=packet.source_issue.issue_number if packet.source_issue else None,
        changed_files_ok=not disallowed_files and bool(packet.changed_files),
        ci_ok=ci_ok,
        scope_ok=not runtime_files and not disallowed_files and not _source_issue_ambiguous(packet),
        blockers=sorted(set(blockers)),
        merge_allowed=False,
        deploy_allowed=False,
        next_safe_step=_next_step(status),
    )


def build_pr_review_gate_from_json(raw_json: str) -> PRReviewGatePacket:
    """Validate local JSON text and build a PR review gate packet."""
    return build_pr_review_gate(PRReviewGateInput.model_validate_json(raw_json))
