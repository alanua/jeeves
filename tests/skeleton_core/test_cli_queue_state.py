import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["queue-state", "--input", path, "--project", "bauclock"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_queue_state_initial_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/bauclock_queue_21_state.json", capsys)

    assert payload["repository"] == "alanua/bauclock"
    assert payload["controller_issue"] == 21
    assert payload["next_runnable_issue"] == 22
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
    assert payload["summary"]["runnable"] == 1
    assert payload["summary"]["blocked_by_dependency"] == 2


def test_cli_queue_state_after_green_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/bauclock_queue_21_after_22_green.json", capsys)

    assert payload["next_runnable_issue"] == 23
    assert payload["summary"]["completed_or_reported"] == 1
    assert payload["summary"]["runnable"] == 1
    assert "bauclock" in payload["next_runnable_reason"]


def test_cli_queue_state_fallback_fixture(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/bauclock_queue_21_blocked_impl_green_audit_fallback.json",
        capsys,
    )

    assert payload["next_runnable_issue"] == 25
    assert payload["summary"]["runnable"] == 1
    assert payload["summary"]["blocked_by_dependency"] == 2
    assert payload["items"][1]["blocked_by"] == [99]
