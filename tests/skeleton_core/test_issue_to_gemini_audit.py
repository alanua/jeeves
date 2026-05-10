from __future__ import annotations

import json

from tools.skeleton_core.issue_to_gemini_audit import build_packets_from_issue_json


def _issue_json(body: str = "Public-safe test body.") -> str:
    return json.dumps(
        {
            "number": 101,
            "title": "[agent-task-yellow] Operator-authorized Gemini auditor bridge ping",
            "body": body,
            "url": "https://github.com/alanua/jeeves/issues/101",
            "state": "OPEN",
            "labels": [
                {"name": "agent:task"},
                {"name": "agent:queued"},
                {"name": "risk:yellow"},
                {"name": "runner:hetzner"},
            ],
        }
    )


def test_build_packets_from_issue_json() -> None:
    task, gemini_input = build_packets_from_issue_json(_issue_json(), mode="mock")

    assert task.task_id == "github-issue-101"
    assert task.risk == "YELLOW"
    assert task.executor_allowed is False
    assert gemini_input.packet_id == "github-issue-101"
    assert gemini_input.mode == "mock"
    assert gemini_input.privacy_level == "PUBLIC_SAFE"


def test_issue_body_is_truncated() -> None:
    _, gemini_input = build_packets_from_issue_json(
        _issue_json("x" * 200),
        mode="mock",
        max_body_chars=20,
    )

    assert "[TRUNCATED_BY_issue_to_gemini_audit]" in gemini_input.evidence


def test_issue_to_gemini_input_contains_forbidden_actions() -> None:
    _, gemini_input = build_packets_from_issue_json(_issue_json(), mode="mock")

    assert "merge" in gemini_input.forbidden_actions
    assert "deploy" in gemini_input.forbidden_actions
    assert "print_secrets" in gemini_input.forbidden_actions
