"""Per-item queue classification for offline public-safe GitHub queue exports."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from tools.skeleton_core.github_queue import normalize_issue, normalize_pr, summarize_queue

QUEUE_CLASSIFICATIONS = (
    "ACTIVE_SKELETON",
    "JEEVES_RUNTIME_NOISE_FOR_NOW",
    "EVIDENCE_ONLY",
    "BLOCKED_WAITING_FOR_OLEKSII",
    "UNKNOWN_NEEDS_REVIEW",
)


class ClassifiedQueueItem(BaseModel):
    """A normalized queue item with an actionable classification."""

    model_config = ConfigDict(extra="forbid")

    kind: str
    number: int | None
    title: str
    classification: str
    reason: str


class QueueClassificationResult(BaseModel):
    """Per-item queue classification result with summary counts."""

    model_config = ConfigDict(extra="forbid")

    items: list[ClassifiedQueueItem]
    summary: dict[str, int]


def _raw_labels(raw: dict[str, Any]) -> list[str]:
    labels = raw.get("labels", [])
    result: list[str] = []
    for label in labels:
        if isinstance(label, str):
            result.append(label)
        elif isinstance(label, dict) and isinstance(label.get("name"), str):
            result.append(label["name"])
    return result


def _normalized_item(raw: dict[str, Any]) -> Any:
    kind = str(raw.get("kind", "issue")).casefold()
    if kind == "pr":
        return normalize_pr(raw)
    return normalize_issue(raw)


def _classification_reason(classification: str, title: str, labels: list[str]) -> str:
    label_text = ", ".join(labels) if labels else "no labels"
    if classification == "ACTIVE_SKELETON":
        return f"Skeleton-active title or labels detected: {label_text}"
    if classification == "JEEVES_RUNTIME_NOISE_FOR_NOW":
        return f"Jeeves/runtime or historical runner noise detected: {label_text}"
    if classification == "EVIDENCE_ONLY":
        return f"Evidence lane item detected: {label_text}"
    if classification == "BLOCKED_WAITING_FOR_OLEKSII":
        return f"Blocked/RED item requires Oleksii decision: {label_text}"
    return f"No known Skeleton queue pattern matched: {title}"


def classify_queue_items(raw_items: list[dict[str, Any]]) -> QueueClassificationResult:
    """Classify raw offline queue items and return item list plus summary counts."""
    normalized_items = [_normalized_item(raw) for raw in raw_items]
    summary = summarize_queue(normalized_items)
    classified_items: list[ClassifiedQueueItem] = []

    for raw, normalized in zip(raw_items, normalized_items, strict=True):
        labels = _raw_labels(raw)
        classification = normalized.classification.value
        classified_items.append(
            ClassifiedQueueItem(
                kind=str(raw.get("kind", "issue")).casefold(),
                number=raw.get("number"),
                title=normalized.title,
                classification=classification,
                reason=_classification_reason(classification, normalized.title, labels),
            )
        )

    for classification in QUEUE_CLASSIFICATIONS:
        summary.setdefault(classification, 0)

    return QueueClassificationResult(items=classified_items, summary=summary)
