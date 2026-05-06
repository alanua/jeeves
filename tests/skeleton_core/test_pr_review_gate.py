from tools.skeleton_core.pr_review_gate import (
    CIStatus,
    PRReviewGateInput,
    SourceIssuePacket,
    build_pr_review_gate,
)


def _base_packet(**overrides) -> PRReviewGateInput:
    data = {
        "repository": "alanua/bauclock",
        "pr_number": 101,
        "title": "test: add calendar access-control regressions",
        "draft": True,
        "source_issue": SourceIssuePacket(
            issue_number=23,
            risk_level="YELLOW",
            allowed_files=[
                "tests/test_calendar_service.py",
                "tests/test_legal_hardening.py",
            ],
            test_only=True,
        ),
        "changed_files": ["tests/test_calendar_service.py"],
        "ci": CIStatus(status="completed", conclusion="success"),
        "body": "Public-safe test-only PR body.",
    }
    data.update(overrides)
    return PRReviewGateInput(**data)


def test_pr_review_gate_ready_for_chatgpt_review() -> None:
    result = build_pr_review_gate(_base_packet())

    assert result.status == "ready_for_chatgpt_review"
    assert result.repository == "alanua/bauclock"
    assert result.pr_number == 101
    assert result.source_issue == 23
    assert result.changed_files_ok is True
    assert result.ci_ok is True
    assert result.scope_ok is True
    assert result.blockers == []
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_pr_review_gate_blocks_disallowed_files() -> None:
    result = build_pr_review_gate(
        _base_packet(
            changed_files=[
                "tests/test_calendar_service.py",
                "app/services/calendar_service.py",
            ]
        )
    )

    assert result.status == "blocked_runtime_change"
    assert result.changed_files_ok is False
    assert result.scope_ok is False
    assert any("File outside allowed scope" in blocker for blocker in result.blockers)


def test_pr_review_gate_blocks_failed_ci() -> None:
    result = build_pr_review_gate(
        _base_packet(ci=CIStatus(status="completed", conclusion="failure"))
    )

    assert result.status == "blocked_failed_ci"
    assert result.ci_ok is False
    assert any("Required CI" in blocker for blocker in result.blockers)


def test_pr_review_gate_blocks_runtime_change_in_test_only_task() -> None:
    result = build_pr_review_gate(
        _base_packet(
            source_issue=SourceIssuePacket(
                issue_number=23,
                risk_level="YELLOW",
                allowed_files=["app/services/calendar_service.py"],
                test_only=True,
            ),
            changed_files=["app/services/calendar_service.py"],
        )
    )

    assert result.status == "blocked_runtime_change"
    assert result.changed_files_ok is True
    assert result.scope_ok is False
    assert any("Runtime/app file" in blocker for blocker in result.blockers)


def test_pr_review_gate_blocks_unsafe_text() -> None:
    result = build_pr_review_gate(
        _base_packet(title="test: deploy calendar regressions", body="Mentions production DB.")
    )

    assert result.status == "blocked_unsafe_text"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert any("Unsafe PR text" in blocker for blocker in result.blockers)


def test_pr_review_gate_unknown_when_source_issue_missing() -> None:
    result = build_pr_review_gate(_base_packet(source_issue=None))

    assert result.status == "unknown_needs_review"
    assert result.source_issue is None
    assert result.scope_ok is False
    assert any("source issue" in blocker for blocker in result.blockers)
