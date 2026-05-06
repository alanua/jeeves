import json

from tools.skeleton_core.cli import main


def _run_fixture(args: list[str], capsys) -> dict:
    exit_code = main(args)
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_issue_dispatch_green_fixture(capsys) -> None:
    payload = _run_fixture(
        ["issue-dispatch", "--input", "tests/fixtures/bauclock_issue_22_export.json"],
        capsys,
    )

    assert payload["status"] == "accepted"
    assert payload["risk_level"] == "GREEN"
    assert payload["runner_route"] == "RUNNER_GREEN"
    assert payload["review_required"] is False
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
    assert payload["expected_commands"] == ["python -m pytest"]


def test_cli_issue_dispatch_yellow_run_bridge_fixture(capsys) -> None:
    payload = _run_fixture(
        [
            "issue-dispatch",
            "--input",
            "tests/fixtures/bauclock_issue_23_export.json",
            "--run-bridge",
            "--parent-queue",
            "21",
        ],
        capsys,
    )

    assert payload["status"] == "accepted"
    assert payload["risk_level"] == "YELLOW"
    assert payload["runner_route"] == "RUNNER_YELLOW"
    assert payload["review_required"] is True
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
    assert payload["allowed_files"] == [
        "tests/test_calendar_service.py",
        "tests/test_legal_hardening.py",
    ]
    assert payload["depends_on"] == [22]
    assert "Parent queue #21" in payload["next_action"]


def test_cli_issue_dispatch_red_forbidden_fixture(capsys) -> None:
    payload = _run_fixture(
        [
            "issue-dispatch",
            "--input",
            "tests/fixtures/bauclock_issue_red_forbidden.json",
            "--run-bridge",
        ],
        capsys,
    )

    assert payload["status"] == "blocked"
    assert payload["risk_level"] == "RED"
    assert payload["runner_route"] == "BLOCKED"
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
    assert payload["blockers"]


def test_cli_issue_dispatch_depends_on_flag(capsys) -> None:
    payload = _run_fixture(
        [
            "issue-dispatch",
            "--input",
            "tests/fixtures/bauclock_issue_22_export.json",
            "--depends-on",
            "20,21",
        ],
        capsys,
    )

    assert payload["depends_on"] == [20, 21]
