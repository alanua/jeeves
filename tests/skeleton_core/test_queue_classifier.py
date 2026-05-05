from tools.skeleton_core.queue_classifier import classify_queue_items


def test_classify_queue_items_returns_items_and_summary() -> None:
    result = classify_queue_items(
        [
            {
                "kind": "issue",
                "number": 40,
                "title": "[skeleton] Stage 2 practical exoskeleton growth",
                "labels": ["skeleton"],
            },
            {
                "kind": "pr",
                "number": 15,
                "title": "test(jeeves): harden runtime action contracts",
                "labels": [],
            },
            {
                "kind": "issue",
                "number": 280,
                "title": "Gemini external-secret readiness note",
                "labels": ["evidence"],
            },
            {
                "kind": "issue",
                "number": 99,
                "title": "Blocked RED task",
                "labels": ["risk:red"],
            },
        ]
    )

    assert [item.classification for item in result.items] == [
        "ACTIVE_SKELETON",
        "JEEVES_RUNTIME_NOISE_FOR_NOW",
        "EVIDENCE_ONLY",
        "BLOCKED_WAITING_FOR_OLEKSII",
    ]
    assert result.items[0].kind == "issue"
    assert result.items[0].number == 40
    assert result.items[0].title == "[skeleton] Stage 2 practical exoskeleton growth"
    assert "Skeleton-active" in result.items[0].reason
    assert result.summary["ACTIVE_SKELETON"] == 1
    assert result.summary["JEEVES_RUNTIME_NOISE_FOR_NOW"] == 1
    assert result.summary["EVIDENCE_ONLY"] == 1
    assert result.summary["BLOCKED_WAITING_FOR_OLEKSII"] == 1
    assert result.summary["UNKNOWN_NEEDS_REVIEW"] == 0


def test_classify_queue_items_handles_unknown() -> None:
    result = classify_queue_items(
        [
            {
                "kind": "issue",
                "number": 1,
                "title": "Unclear follow-up",
                "labels": [],
            }
        ]
    )

    assert result.items[0].classification == "UNKNOWN_NEEDS_REVIEW"
    assert "No known Skeleton queue pattern" in result.items[0].reason
    assert result.summary["UNKNOWN_NEEDS_REVIEW"] == 1
