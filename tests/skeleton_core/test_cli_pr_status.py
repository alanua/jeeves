import json

from tools.skeleton_core.cli import main


def test_cli_pr_status_green_fixture(capsys) -> None:
    exit_code = main(["pr-status", "--input", "tests/fixtures/pr_status_sample_green.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["pr_number"] == 52
    assert payload["status"] == "ready_to_merge"
    assert payload["ci_state"] == "success"
    assert payload["blockers"] == []


def test_cli_pr_status_black_failed_fixture(capsys) -> None:
    exit_code = main(["pr-status", "--input", "tests/fixtures/pr_status_sample_black_failed.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["status"] == "needs_fix"
    assert payload["ci_state"] == "failure"
    assert any("Run Black check" in blocker for blocker in payload["blockers"])
    assert any("Black formatting check failed" in blocker for blocker in payload["blockers"])
