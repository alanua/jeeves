import json

from tools.skeleton_core.cli import main


def test_cli_task_lifecycle_green_fixture(capsys) -> None:
    exit_code = main(["task-lifecycle", "--input", "tests/fixtures/issue_runner_green.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["status"] == "accepted"
    assert payload["risk_level"] == "GREEN"
    assert payload["runner_route"] == "RUNNER_GREEN"
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
    assert payload["initial_checkpoint"]["result"] == "queued"


def test_cli_task_lifecycle_blocks_merge_fixture(capsys) -> None:
    exit_code = main(["task-lifecycle", "--input", "tests/fixtures/issue_runner_red_merge.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["status"] == "blocked"
    assert payload["runner_route"] == "BLOCKED"
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
    assert payload["initial_checkpoint"]["result"] == "blocked"
