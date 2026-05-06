import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["runner-env-check", "--input", path])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_runner_env_check_ready_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_env_check_ready.json", capsys)

    assert payload["status"] == "ready_for_read_only_validation"
    assert payload["safe_for_runner"] is True
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_runner_env_check_dns_failure_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_env_check_dns_failure.json", capsys)

    assert payload["status"] == "blocked_dns_or_network"
    assert payload["safe_for_runner"] is False
    assert payload["blocked_reason"] == "Could not resolve host: github.com"
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_runner_env_check_no_git_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_env_check_no_git.json", capsys)

    assert payload["status"] == "blocked_no_git"
    assert payload["safe_for_runner"] is False


def test_cli_runner_env_check_clone_failed_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_env_check_clone_failed.json", capsys)

    assert payload["status"] == "blocked_clone_failed"
    assert payload["safe_for_runner"] is False


def test_cli_runner_env_check_policy_violation_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/runner_env_check_policy_violation.json", capsys)

    assert payload["status"] == "unsafe_or_policy_violation"
    assert payload["repo_url_checked"] == "<redacted-repo-url>"
    assert "token" not in json.dumps(payload)
    assert payload["safe_for_runner"] is False


def test_cli_runner_env_check_missing_args(capsys) -> None:
    exit_code = main(["runner-env-check"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["status"] == "unknown_needs_review"
    assert payload["safe_for_runner"] is False
    assert "Provide --input" in payload["blocked_reason"]
