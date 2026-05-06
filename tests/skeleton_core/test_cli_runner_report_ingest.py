import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["runner-report-ingest", "--input", path])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_runner_report_ingest_green_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_report_green_22.txt", capsys)

    assert payload["status"] == "green_report"
    assert payload["issue_number"] == 22
    assert payload["test_result"] == "passed"
    assert payload["repo_status"] == "clean"
    assert payload["needs_review"] is False
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
    assert payload["next_queue_signal"] == "dependency_satisfied"


def test_cli_runner_report_ingest_blocked_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_report_blocked_23.txt", capsys)

    assert payload["status"] == "blocked_report"
    assert payload["issue_number"] == 23
    assert payload["blocked_reason"] == "waiting for #22 green baseline validation"
    assert payload["needs_review"] is True
    assert payload["next_queue_signal"] == "blocked"


def test_cli_runner_report_ingest_failed_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_report_failed_tests.txt", capsys)

    assert payload["status"] == "failed_validation"
    assert payload["issue_number"] == 24
    assert payload["test_result"] == "failed"
    assert payload["next_queue_signal"] == "validation_failed"


def test_cli_runner_report_ingest_needs_review_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_report_needs_review_pr.txt", capsys)

    assert payload["status"] == "needs_review"
    assert payload["issue_number"] == 25
    assert payload["open_prs"] == ["PR #88"]
    assert payload["needs_review"] is True
    assert payload["next_queue_signal"] == "review_required"


def test_cli_runner_report_ingest_unsafe_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_report_unsafe_secret_flag.txt", capsys)

    assert payload["status"] == "unsafe_or_policy_violation"
    assert payload["issue_number"] == 26
    assert payload["private_data_seen"] is True
    assert "private_data" in payload["unsafe_flags"]
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
