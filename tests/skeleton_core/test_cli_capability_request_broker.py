import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["capability-request-broker", "--input", path])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_capability_request_runner_env_ready(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/capability_request_bauclock_runner_env_check.json",
        capsys,
    )

    assert payload["status"] == "capability_request_ready"
    assert payload["capability_name"] == "runner-env-check"
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_capability_request_actions_ready(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/capability_request_bauclock_actions_runner_control.json",
        capsys,
    )

    assert payload["status"] == "capability_request_ready"
    assert payload["capability_name"] == "github-actions-runner-control"
    assert "github-actions-runner-control" in payload["recommended_skeleton_issue_title"]


def test_cli_capability_request_existing(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/capability_request_existing_capability.json",
        capsys,
    )

    assert payload["status"] == "capability_already_exists"
    assert (
        payload["next_safe_step"]
        == "Update the project workflow to use the existing Skeleton capability."
    )


def test_cli_capability_request_unsafe(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/capability_request_unsafe_live_executor.json",
        capsys,
    )

    assert payload["status"] == "blocked_unsafe_capability"
    assert payload["risk_level"] == "RED"
    assert payload["recommended_skeleton_issue_body"] == ""
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_capability_request_unknown(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/capability_request_unknown_needs_review.json",
        capsys,
    )

    assert payload["status"] == "unknown_needs_review"
    assert payload["risk_level"] == "UNKNOWN"
