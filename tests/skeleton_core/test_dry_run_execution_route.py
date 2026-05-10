from __future__ import annotations

from tools.skeleton_core.dry_run_execution_route import (
    GitHubIssueComment,
    GitHubIssueExport,
    GitHubIssueLabel,
    build_execution_packet,
    find_verified_audit_comment,
    has_execution_trigger_labels,
    validate_execution_packet,
)


def _issue(comment_body: str) -> GitHubIssueExport:
    return GitHubIssueExport(
        number=126,
        title="[agent-task-yellow] Test",
        body="Public-safe task body.",
        url="https://github.com/alanua/jeeves/issues/126",
        state="OPEN",
        labels=[
            GitHubIssueLabel(name="agent:task"),
            GitHubIssueLabel(name="risk:yellow"),
            GitHubIssueLabel(name="runner:hetzner"),
            GitHubIssueLabel(name="agent:audited"),
        ],
        comments=[
            GitHubIssueComment(
                body=comment_body,
                url="https://github.com/alanua/jeeves/issues/126#comment",
            )
        ],
    )


def test_has_execution_trigger_labels() -> None:
    issue = _issue("Autonomous YELLOW Gemini audit route report\nAdapter status: `live_accept`")
    assert has_execution_trigger_labels(issue) is True


def test_queued_issue_is_not_execution_candidate() -> None:
    issue = _issue("Autonomous YELLOW Gemini audit route report\nAdapter status: `live_accept`")
    issue.labels.append(GitHubIssueLabel(name="agent:queued"))

    assert has_execution_trigger_labels(issue) is False


def test_find_verified_audit_comment() -> None:
    issue = _issue("Autonomous YELLOW Gemini audit route report\nAdapter status: `live_accept`")

    verified, status, url, body = find_verified_audit_comment(issue)

    assert verified is True
    assert status == "live_accept"
    assert url.endswith("#comment")
    assert "Autonomous YELLOW" in body


def test_build_execution_packet_from_verified_audit() -> None:
    issue = _issue("Autonomous YELLOW Gemini audit route report\nAdapter status: `mock_accept`")

    packet = build_execution_packet(issue)

    assert packet.audit_verified is True
    assert packet.audit_status == "mock_accept"
    assert packet.executor_allowed is False
    assert packet.planned_actions
    assert all(action.dry_run_only for action in packet.planned_actions)


def test_validate_execution_packet_blocks_missing_audit() -> None:
    issue = _issue("No accepted audit here.")

    packet = build_execution_packet(issue)
    reasons = validate_execution_packet(packet)

    assert "missing_verified_accept_audit_comment" in reasons
    assert "audit_status_not_accepted" in reasons


def test_validate_execution_packet_accepts_safe_dry_run_packet() -> None:
    issue = _issue("Autonomous YELLOW Gemini audit route report\nAdapter status: `live_accept`")

    packet = build_execution_packet(issue)

    assert validate_execution_packet(packet) == []
