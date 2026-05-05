import json
from pathlib import Path

from tools.skeleton_core.github_queue import (
    QueueClassification,
    QueueItemKind,
    QueueItemState,
    classify_queue_item,
    normalize_issue,
    normalize_pr,
    summarize_queue,
)

FIXTURE_PATH = Path("tests/fixtures/github_queue_sample.json")


def test_normalize_issue_preserves_public_safe_metadata() -> None:
    raw = {
        "number": 27,
        "title": "Implement Skeleton github_queue offline adapter",
        "body": "Preserve EvidencePolicy and blocked_reason.",
        "labels": [{"name": "skeleton"}],
        "state": "open",
        "risk_level": "ORANGE",
        "route_target": "RUNNER_ORANGE",
        "evidence_policy": "NONE",
        "source_repo": "alanua/jeeves",
        "url": "https://example.invalid/issue/27",
    }

    item = normalize_issue(raw)

    assert item.number_or_id == "27"
    assert item.title == "Implement Skeleton github_queue offline adapter"
    assert item.labels == ["skeleton"]
    assert item.state == QueueItemState.OPEN
    assert item.kind == QueueItemKind.ISSUE
    assert item.evidence_policy == "NONE"


def test_normalize_pr_detects_draft_state() -> None:
    item = normalize_pr(
        {
            "number": 28,
            "title": "Draft Skeleton PR",
            "body": "Draft PR body",
            "draft": True,
            "state": "open",
        }
    )

    assert item.kind == QueueItemKind.PR
    assert item.state == QueueItemState.DRAFT


def test_active_skeleton_item_classifies_active() -> None:
    item = normalize_issue(
        {
            "title": "Implement Skeleton runner contour",
            "body": "Add TaskPacket and RouteDecision support.",
            "labels": ["skeleton"],
            "state": "open",
        }
    )

    assert classify_queue_item(item) == QueueClassification.ACTIVE_SKELETON


def test_runtime_item_classifies_noise() -> None:
    item = normalize_issue(
        {
            "title": "Refactor FastAPI /ask orchestrator",
            "body": "Change app/api and app/orchestration runtime behavior.",
            "labels": ["runtime"],
            "state": "open",
        }
    )

    assert classify_queue_item(item) == QueueClassification.JEEVES_RUNTIME_NOISE_FOR_NOW


def test_evidence_item_classifies_evidence_only() -> None:
    item = normalize_issue(
        {
            "title": "Gemini audit notes",
            "body": "Manual external auditor evidence only from Antigravity sandbox workbench.",
            "labels": ["evidence"],
            "state": "open",
        }
    )

    assert classify_queue_item(item) == QueueClassification.EVIDENCE_ONLY


def test_blocked_item_classifies_waiting_for_oleksii() -> None:
    item = normalize_issue(
        {
            "title": "Production token task",
            "body": "Blocked waiting for Oleksii approval.",
            "labels": ["risk:red"],
            "state": "open",
            "risk_level": "RED",
            "route_target": "BLOCKED_RED",
            "blocked_reason": "RED tripwire",
        }
    )

    assert classify_queue_item(item) == QueueClassification.BLOCKED_WAITING_FOR_OLEKSII


def test_superseded_item_classifies_duplicate_or_superseded() -> None:
    item = normalize_issue(
        {
            "title": "Draft PR superseded",
            "body": "Superseded by non-draft PR.",
            "labels": ["skeleton"],
            "state": "closed",
        }
    )

    assert classify_queue_item(item) == QueueClassification.DUPLICATE_OR_SUPERSEDED


def test_fixture_summary_counts() -> None:
    raw_items = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    items = [normalize_issue(raw) for raw in raw_items]

    summary = summarize_queue(items)

    assert summary[QueueClassification.ACTIVE_SKELETON] == 1
    assert summary[QueueClassification.JEEVES_RUNTIME_NOISE_FOR_NOW] == 1
    assert summary[QueueClassification.EVIDENCE_ONLY] == 1
    assert summary[QueueClassification.BLOCKED_WAITING_FOR_OLEKSII] == 1
    assert summary[QueueClassification.DUPLICATE_OR_SUPERSEDED] == 0
    assert summary[QueueClassification.UNKNOWN_NEEDS_REVIEW] == 0
