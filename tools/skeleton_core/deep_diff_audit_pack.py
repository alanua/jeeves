"""Public-safe evidence packet builder for deep-diff audits.

This module does not fetch GitHub, read private files, inspect host runtime,
read environment variables, or call external services. It only structures
already-supplied public-safe evidence into a bounded packet suitable for a
future Gemini deep-diff audit.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

SourceType = Literal[
    "issue_body",
    "issue_comments",
    "pr_metadata",
    "pr_changed_files",
    "repo_file_excerpt",
    "manual_excerpt",
]

DeepDiffStatus = Literal[
    "duplicate",
    "overlap",
    "gap",
    "conflict",
    "new",
    "unknown",
]

DEFAULT_MAX_EXCERPT_CHARS = 4_000
DEFAULT_SCHEMA_VERSION = "deep-diff-evidence-packet/v1"

_SECRET_LIKE_PATTERNS = (
    re.compile(r"(?i)\bapi[_-]?key\s*[:=]\s*\S+"),
    re.compile(r"(?i)\btoken\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bbearer\s+[a-z0-9._\-]+"),
    re.compile(r"(?i)\bpassword\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bsecret\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bprivate[_-]?key\s*[:=]?\s*\S*"),
)


class DeepDiffSubject(BaseModel):
    """The proposed work being audited."""

    repo: str = Field(..., min_length=1)
    issue_number: int | None = None
    title: str = ""
    summary: str = ""


class DeepDiffSourceInput(BaseModel):
    """Already-collected public-safe source material."""

    source_type: SourceType
    source_ref: str = Field(..., min_length=1)
    content: str = ""
    retrieved_at: str | None = None
    limits_applied: list[str] = Field(default_factory=list)
    max_excerpt_chars: int = Field(default=DEFAULT_MAX_EXCERPT_CHARS, ge=100, le=20_000)


class DeepDiffSource(BaseModel):
    """Bounded source excerpt included in the packet."""

    source_type: SourceType
    source_ref: str
    retrieved_at: str
    excerpt: str
    limits_applied: list[str] = Field(default_factory=list)
    chars_original: int
    chars_included: int
    truncated: bool
    secret_like_redaction_applied: bool = False


class ExpectedMatrixSchema(BaseModel):
    """Required Gemini answer shape for a real deep-diff audit."""

    required_fields: list[str] = Field(
        default_factory=lambda: [
            "proposed_item",
            "existing_source",
            "status",
            "recommendation",
            "confidence",
        ]
    )
    allowed_statuses: list[DeepDiffStatus] = Field(
        default_factory=lambda: [
            "duplicate",
            "overlap",
            "gap",
            "conflict",
            "new",
            "unknown",
        ]
    )


class DeepDiffEvidencePacket(BaseModel):
    """Public-safe bounded evidence packet."""

    schema_version: str = DEFAULT_SCHEMA_VERSION
    subject: DeepDiffSubject
    sources: list[DeepDiffSource]
    questions: list[str]
    expected_matrix_schema: ExpectedMatrixSchema = Field(default_factory=ExpectedMatrixSchema)
    safety_notes: list[str]
    created_at: str


class DeepDiffEvidenceInput(BaseModel):
    """Input model for building a deep-diff evidence packet."""

    subject: DeepDiffSubject
    sources: list[DeepDiffSourceInput]
    questions: list[str] | None = None


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def contains_secret_like_text(text: str) -> bool:
    """Return True when text resembles a secret/key/token/password."""

    return any(pattern.search(text) for pattern in _SECRET_LIKE_PATTERNS)


def _redact_or_truncate(content: str, *, max_chars: int) -> tuple[str, bool, bool]:
    secret_like = contains_secret_like_text(content)
    if secret_like:
        return "<redacted-secret-like-content>", False, True

    truncated = len(content) > max_chars
    if not truncated:
        return content, False, False

    return content[:max_chars].rstrip() + "\n<truncated>", True, False


def build_deep_diff_source(
    source: DeepDiffSourceInput,
    *,
    default_time: str | None = None,
) -> DeepDiffSource:
    """Build one bounded source excerpt."""

    retrieved_at = source.retrieved_at or default_time or _utc_now()
    excerpt, truncated, secret_like = _redact_or_truncate(
        source.content,
        max_chars=source.max_excerpt_chars,
    )

    limits = list(source.limits_applied)
    if truncated:
        limits.append(f"excerpt_truncated_to_{source.max_excerpt_chars}_chars")
    if secret_like:
        limits.append("secret_like_content_redacted")

    return DeepDiffSource(
        source_type=source.source_type,
        source_ref=source.source_ref,
        retrieved_at=retrieved_at,
        excerpt=excerpt,
        limits_applied=limits,
        chars_original=len(source.content),
        chars_included=len(excerpt),
        truncated=truncated,
        secret_like_redaction_applied=secret_like,
    )


def default_deep_diff_questions() -> list[str]:
    """Questions every deep-diff audit should answer."""

    return [
        "Which proposed items duplicate existing sources?",
        "Which proposed items overlap existing sources but still need a smaller patch?",
        "Which proposed items are genuine gaps?",
        "Which proposed items conflict with existing canon or current state?",
        "Which target file or existing issue/PR should be used next?",
        "What is the smallest safe next action?",
    ]


def default_safety_notes() -> list[str]:
    """Safety notes carried with every packet."""

    return [
        "This packet is public-safe evidence only.",
        "The builder does not fetch GitHub or browse sources by itself.",
        "The builder does not read private Drive, .env files, secrets, or host-local runtime paths.",
        "Gemini should analyze only the supplied evidence packet.",
        "A deep audit is incomplete if the required matrix fields are missing.",
    ]


def build_deep_diff_audit_pack(
    input_packet: DeepDiffEvidenceInput,
) -> DeepDiffEvidencePacket:
    """Build a public-safe deep-diff evidence packet."""

    created_at = _utc_now()
    return DeepDiffEvidencePacket(
        subject=input_packet.subject,
        sources=[
            build_deep_diff_source(source, default_time=created_at)
            for source in input_packet.sources
        ],
        questions=input_packet.questions or default_deep_diff_questions(),
        safety_notes=default_safety_notes(),
        created_at=created_at,
    )


def build_deep_diff_audit_pack_from_json(raw_json: str) -> DeepDiffEvidencePacket:
    """Validate JSON and build a deep-diff evidence packet."""

    return build_deep_diff_audit_pack(DeepDiffEvidenceInput.model_validate_json(raw_json))


def packet_to_json_dict(packet: DeepDiffEvidencePacket) -> dict[str, Any]:
    """Return a JSON-ready packet dict."""

    return packet.model_dump(mode="json")
