import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["project-skeleton-profile", "--input", path])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_bauclock_project_profile_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/project_profile_bauclock.json", capsys)

    assert payload["project"] == "BauClock"
    assert payload["profile_status"] == "ready"
    assert payload["development_flow"] == [
        "issue-dispatch",
        "runner-command-pack",
        "runner-report-ingest",
        "pr-review-gate",
        "branch-recovery",
    ]
    assert payload["recommended_next_gate"] == "pr-review-gate"
    assert "runner-env-check" in payload["missing_capability_signals"]
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_skeleton_project_profile_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/project_profile_skeleton.json", capsys)

    assert payload["project"] == "Skeleton Core"
    assert payload["profile_status"] == "ready"
    assert "validate-state" in payload["development_flow"]
    assert "handoff-pack" in payload["development_flow"]
    assert payload["missing_capability_signals"] == []
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_unsafe_project_profile_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/project_profile_unsafe_capability.json", capsys)

    assert payload["profile_status"] == "blocked_unsafe_default"
    assert payload["development_flow"] == []
    assert payload["blockers"]
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
