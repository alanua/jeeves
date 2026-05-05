"""Offline GitHub queue normalization and classification for Skeleton work."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QueueItemKind(StrEnum):
    """Supported queue item kinds."""

    ISSUE = "ISSUE"
    PR = "PR"
    REPORT = "REPORT"


class QueueItemState(StrEnum):
    """Normalized queue item state."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    MERGED = "MERGED"
    DRAFT = "DRAFT"
    UNKNOWN = "UNKNOWN"


class QueueClassification(StrEnum):
    """Skeleton queue classification labels."""

    ACTIVE_SKELETON = "ACTIVE_SKELETON"
    JEEVES_RUNTIME_NOISE_FOR_NOW = "JEEVES_RUNTIME_NOISE_FOR_NOW"
    EVIDENCE_ONLY = "EVIDENCE_ONLY"
    DUPLICATE_OR_SUPERSEDED = "DUPLICATE_OR_SUPERSEDED"
    BLOCKED_WAITING_FOR_OLEKSII = "BLOCKED_WAITING_FOR_OLEKSII"
    UNKNOWN_NEEDS_REVIEW = "UNKNOWN_NEEDS_REVIEW"


class QueueItem(BaseModel):
    """Public-safe normalized GitHub queue item."""

    model_config = ConfigDict(extra="forbid")

    number_or_id: str | None = None
    title: str = ""
    body_or_summary: str = ""
    labels: list[str] = Field(default_factory=list)
    state: QueueItemState = QueueItemState.UNKNOWN
    kind: QueueItemKind
    risk_level: str | None = None
    route_target: str | None = None
    evidence_policy: str | None = None
    blocked_reason: str | None = None
    source_repo: str | None = None
    url: str | None = None


SKELETON_TERMS = (
    "skeleton",
    "exoskeleton",
    "ск",
    "chatgpt exoskeleton",
    "runner contour",
    "handoff",
    "memory layer",
    "skeleton_core",
    "evidencepolicy",
    "routedecision",
    "taskpacket",
)

EVIDENCE_TERMS = (
    "gemini",
    "gemini audit",
    "notebooklm",
    "gemini notebooks",
    "antigravity",
    "manual external auditor",
    "evidence only",
    "sandbox workbench",
)

RUNTIME_TERMS = (
    "fastapi",
    "/ask",
    "orchestrator",
    "llm router",
    "database migration",
    "app/api",
    "app/orchestration",
    "runtime",
    "jeeves runtime",
)

BLOCKED_TERMS = (
    "waiting for oleksii approval",
    "blocked waiting for oleksii",
    "blocked_red",
    "blocked red",
)

SUPERSEDED_TERMS = (
    "superseded",
    "duplicate",
    "replaced by",
)


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _labels(raw: dict[str, Any]) -> list[str]:
    labels = raw.get("labels") or []
    normalized: list[str] = []
    for label in labels:
        if isinstance(label, dict):
            name = label.get("name")
        else:
            name = label
        if name:
            normalized.append(str(name))
    return normalized


def _state(raw: dict[str, Any], *, is_pr: bool = False) -> QueueItemState:
    if raw.get("merged") is True or raw.get("merged_at"):
        return QueueItemState.MERGED
    if is_pr and raw.get("draft") is True:
        return QueueItemState.DRAFT

    state = _as_text(raw.get("state")).casefold()
    if state == "open":
        return QueueItemState.OPEN
    if state == "closed":
        return QueueItemState.CLOSED
    return QueueItemState.UNKNOWN


def _joined(item: QueueItem) -> str:
    return "\n".join(
        [
            item.title,
            item.body_or_summary,
            " ".join(item.labels),
            _as_text(item.risk_level),
            _as_text(item.route_target),
            _as_text(item.evidence_policy),
            _as_text(item.blocked_reason),
        ]
    ).casefold()


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def normalize_issue(raw: dict[str, Any]) -> QueueItem:
    """Normalize public-safe issue metadata from a dict or fixture."""
    return QueueItem(
        number_or_id=_as_text(raw.get("number") or raw.get("id")) or None,
        title=_as_text(raw.get("title")),
        body_or_summary=_as_text(raw.get("body") or raw.get("summary")),
        labels=_labels(raw),
        state=_state(raw),
        kind=QueueItemKind.ISSUE,
        risk_level=raw.get("risk_level"),
        route_target=raw.get("route_target"),
        evidence_policy=raw.get("evidence_policy"),
        blocked_reason=raw.get("blocked_reason"),
        source_repo=raw.get("source_repo") or raw.get("repo"),
        url=raw.get("url") or raw.get("html_url"),
    )


def normalize_pr(raw: dict[str, Any]) -> QueueItem:
    """Normalize public-safe pull request metadata from a dict or fixture."""
    return QueueItem(
        number_or_id=_as_text(raw.get("number") or raw.get("id")) or None,
        title=_as_text(raw.get("title")),
        body_or_summary=_as_text(raw.get("body") or raw.get("summary")),
        labels=_labels(raw),
        state=_state(raw, is_pr=True),
        kind=QueueItemKind.PR,
        risk_level=raw.get("risk_level"),
        route_target=raw.get("route_target"),
        evidence_policy=raw.get("evidence_policy"),
        blocked_reason=raw.get("blocked_reason"),
        source_repo=raw.get("source_repo") or raw.get("repo"),
        url=raw.get("url") or raw.get("html_url"),
    )


def classify_queue_item(item: QueueItem) -> QueueClassification:
    """Classify one queue item without network or live GitHub access."""
    text = _joined(item)

    if _contains_any(text, SUPERSEDED_TERMS):
        return QueueClassification.DUPLICATE_OR_SUPERSEDED
    if item.route_target == "BLOCKED_RED" or item.risk_level == "RED" or item.blocked_reason:
        return QueueClassification.BLOCKED_WAITING_FOR_OLEKSII
    if _contains_any(text, BLOCKED_TERMS):
        return QueueClassification.BLOCKED_WAITING_FOR_OLEKSII
    if _contains_any(text, RUNTIME_TERMS):
        return QueueClassification.JEEVES_RUNTIME_NOISE_FOR_NOW
    if _contains_any(text, EVIDENCE_TERMS) and not _contains_any(text, SKELETON_TERMS):
        return QueueClassification.EVIDENCE_ONLY
    if _contains_any(text, SKELETON_TERMS):
        return QueueClassification.ACTIVE_SKELETON
    if _contains_any(text, EVIDENCE_TERMS):
        return QueueClassification.EVIDENCE_ONLY
    return QueueClassification.UNKNOWN_NEEDS_REVIEW


def summarize_queue(items: list[QueueItem]) -> dict[str, int]:
    """Count queue items by Skeleton classification."""
    counts = {classification.value: 0 for classification in QueueClassification}
    for item in items:
        counts[classify_queue_item(item).value] += 1
    return counts
