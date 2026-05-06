import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["github-actions-runner-control", "--input", path])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_actions_success_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/actions_run_bauclock_tests_success.json", capsys)

    assert payload["status"] == "workflow_success_report"
    assert payload["test_result"] == "passed"
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
    assert "BauClock #22" in payload["issue_report_text"]


def test_cli_actions_failed_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/actions_run_bauclock_tests_failed.json", capsys)

    assert payload["status"] == "workflow_failed_report"
    assert payload["test_result"] == "failed"
    assert payload["failed_steps"] == ["tests: Run tests"]


def test_cli_actions_cancelled_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/actions_run_bauclock_tests_cancelled.json", capsys)

    assert payload["status"] == "workflow_cancelled_report"
    assert payload["test_result"] == "cancelled"


def test_cli_actions_secret_like_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/actions_run_secret_like_log_blocked.json", capsys)

    assert payload["status"] == "unsafe_or_policy_violation"
    assert payload["test_result"] == "blocked"
    assert "token=" not in json.dumps(payload)
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
