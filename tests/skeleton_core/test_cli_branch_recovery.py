import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["branch-recovery", "--input", path])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_branch_recovery_failed_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/branch_recovery_open_failed.json", capsys)

    assert payload["branch_name"] == "skeleton/example-failed"
    assert payload["issue_number"] == 68
    assert payload["pr_number"] == 69
    assert payload["status"] == "needs_fix"
    assert payload["ci_status"] == "failed"
    assert payload["blockers"] == ["black"]
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_branch_recovery_merged_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/branch_recovery_merged.json", capsys)

    assert payload["status"] == "completed"
    assert payload["merged_sha"] == "abc123def456"
    assert payload["next_safe_action"] == "checkpoint state and continue next task"
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_branch_recovery_missing_ci_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/branch_recovery_missing_ci.json", capsys)

    assert payload["status"] == "wait_for_ci_or_fetch_status"
    assert payload["ci_status"] == "missing"
    assert payload["next_safe_action"] == "wait for CI or fetch public-safe PR status export"
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
