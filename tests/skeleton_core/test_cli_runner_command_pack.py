import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["runner-command-pack", "--input", path])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_runner_command_pack_green_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_command_bauclock_22_green.json", capsys)

    assert payload["status"] == "ready"
    assert payload["issue_number"] == 22
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
    assert "GREEN read-only validation" in payload["command_text"]
    assert "Do not merge or deploy" in payload["command_text"]


def test_cli_runner_command_pack_yellow_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_command_bauclock_23_yellow.json", capsys)

    assert payload["status"] == "ready"
    assert payload["issue_number"] == 23
    assert "YELLOW test-only task" in payload["command_text"]
    assert "tests/test_calendar_service.py" in payload["command_text"]
    assert "Do not merge or deploy" in payload["command_text"]


def test_cli_runner_command_pack_blocked_red_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_command_blocked_red.json", capsys)

    assert payload["status"] == "blocked"
    assert payload["issue_number"] == 999
    assert payload["command_text"].startswith("BLOCKED")
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_runner_command_pack_missing_fields_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_command_missing_fields.json", capsys)

    assert payload["status"] == "blocked"
    assert "Missing required field: issue_number" in payload["blockers"]
    assert "Missing required field: title" in payload["blockers"]


def test_cli_runner_command_pack_unsafe_text_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_command_unsafe_text.json", capsys)

    assert payload["status"] == "blocked"
    assert any("secret" in blocker for blocker in payload["blockers"])
    assert any("network" in blocker for blocker in payload["blockers"])
