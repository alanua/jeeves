from tools.skeleton_core.runner_report_ingest import ingest_runner_report


def test_ingest_green_report() -> None:
    result = ingest_runner_report(
        """Agent report for issue #22

issue_number: 22
branch: bauclock/overnight-baseline
head_sha: abc123def456
commands_run: python -m pytest
test_result: passed
repo_status: clean
private_data_seen: false
runtime_code_touched: false
external_services_called: false
178 passed
working tree clean
"""
    )

    assert result.status == "green_report"
    assert result.issue_number == 22
    assert result.branch == "bauclock/overnight-baseline"
    assert result.head_sha == "abc123def456"
    assert result.commands_run == ["python -m pytest"]
    assert result.test_result == "passed"
    assert result.repo_status == "clean"
    assert result.needs_review is False
    assert result.next_queue_signal == "dependency_satisfied"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_ingest_blocked_report() -> None:
    result = ingest_runner_report(
        """Blocked report: missing dependency #22 report.
issue_number: 23
blocked_reason: waiting for #22 green baseline validation
repo_status: clean
"""
    )

    assert result.status == "blocked_report"
    assert result.issue_number == 23
    assert result.blocked_reason == "waiting for #22 green baseline validation"
    assert result.needs_review is True
    assert result.next_queue_signal == "blocked"


def test_ingest_failed_validation() -> None:
    result = ingest_runner_report(
        """Agent report for issue #24
issue_number: 24
commands_run: python -m pytest
test_result: failed
repo_status: dirty
failure_summary: tests failed in test_calendar_service.py
validation failed: tests failed in test_calendar_service.py
"""
    )

    assert result.status == "failed_validation"
    assert result.issue_number == 24
    assert result.test_result == "failed"
    assert result.failure_summary == "tests failed in test_calendar_service.py"
    assert result.next_queue_signal == "validation_failed"


def test_ingest_needs_review_pr() -> None:
    result = ingest_runner_report(
        """Runner report for issue #25
issue_number: 25
commands_run: python -m pytest
Tests: passed
repo_status: clean
open_prs: PR #88
Draft PR #88 is ready for ChatGPT/Oleksii review.
"""
    )

    assert result.status == "needs_review"
    assert result.issue_number == 25
    assert result.open_prs == ["PR #88"]
    assert result.needs_review is True
    assert result.next_queue_signal == "review_required"


def test_ingest_unsafe_secret_flag() -> None:
    result = ingest_runner_report(
        """Runner report for issue #26
issue_number: 26
test_result: passed
repo_status: clean
private_data_seen: true
failure_summary: used secret from environment by mistake
"""
    )

    assert result.status == "unsafe_or_policy_violation"
    assert result.issue_number == 26
    assert result.private_data_seen is True
    assert "private_data" in result.unsafe_flags
    assert "secret" in result.unsafe_flags
    assert result.needs_review is True
    assert result.next_queue_signal == "blocked_policy_violation"


def test_ingest_unknown_report_requires_review() -> None:
    result = ingest_runner_report("Issue #30 maybe done, not sure.")

    assert result.status == "unknown_needs_review"
    assert result.issue_number == 30
    assert result.needs_review is True
    assert result.next_queue_signal == "manual_review_required"
