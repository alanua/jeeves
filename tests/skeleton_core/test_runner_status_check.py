from __future__ import annotations

from pathlib import Path

from tools.skeleton_core.runner_status_check import (
    RunnerStatusCheckInput,
    build_runner_status_check,
    build_runner_status_check_from_json,
    build_unavailable_live_check,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _load_fixture(name: str):
    return build_runner_status_check_from_json((FIXTURES / name).read_text(encoding="utf-8"))


def test_running_issue_with_live_pid_returns_running() -> None:
    result = _load_fixture("runner_status_check_running.json")

    assert result.status == "running"
    assert result.lock_file_seen is True
    assert result.lock_pid_alive is True
    assert result.recommended_queue_action == "wait_for_runner"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_old_running_issue_with_dead_pid_returns_stale() -> None:
    result = _load_fixture("runner_status_check_stale.json")

    assert result.status == "stale"
    assert "PID" in result.staleness_reason
    assert result.recommended_queue_action == "run_manual_health_check"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_failed_event_returns_failed() -> None:
    result = _load_fixture("runner_status_check_failed.json")

    assert result.status == "failed"
    assert result.blocker_summary == "validation failed"
    assert result.recommended_queue_action == "review_blocker_report"


def test_completion_evidence_without_report_returns_completed_unknown() -> None:
    result = _load_fixture("runner_status_check_completed_unknown.json")

    assert result.status == "completed_unknown"
    assert result.recommended_queue_action == "review_final_report"


def test_missing_or_ambiguous_evidence_returns_needs_manual_review() -> None:
    result = build_runner_status_check(
        RunnerStatusCheckInput(repository="alanua/bauclock", issue_number=48)
    )

    assert result.status == "needs_manual_review"
    assert result.recommended_queue_action == "needs_manual_review"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_secret_like_text_is_blocked_and_redacted() -> None:
    result = build_runner_status_check(
        RunnerStatusCheckInput(
            repository="alanua/bauclock",
            issue_number=48,
            logs_summary="token=abc123 appeared in log summary",
        )
    )

    assert result.status == "needs_manual_review"
    assert result.blocker_summary == "secret-like text detected in runner status evidence"
    assert "abc123" not in result.blocker_summary
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_unavailable_live_check_fails_closed() -> None:
    result = build_unavailable_live_check(repository="alanua/bauclock", issue_number=48)

    assert result.status == "needs_manual_review"
    assert result.repository == "alanua/bauclock"
    assert result.issue_number == 48
    assert result.recommended_queue_action == "needs_manual_review"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
