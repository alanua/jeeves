import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["pr-review-gate", "--input", path])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_pr_review_gate_ready_fixture(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/pr_review_gate_bauclock_test_only_green.json",
        capsys,
    )

    assert payload["status"] == "ready_for_chatgpt_review"
    assert payload["repository"] == "alanua/bauclock"
    assert payload["pr_number"] == 101
    assert payload["changed_files_ok"] is True
    assert payload["ci_ok"] is True
    assert payload["scope_ok"] is True
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_pr_review_gate_disallowed_file_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/pr_review_gate_disallowed_file.json", capsys)

    assert payload["status"] == "blocked_disallowed_files"
    assert payload["changed_files_ok"] is False
    assert payload["scope_ok"] is False
    assert payload["blockers"]


def test_cli_pr_review_gate_failed_ci_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/pr_review_gate_failed_ci.json", capsys)

    assert payload["status"] == "blocked_failed_ci"
    assert payload["ci_ok"] is False
    assert payload["blockers"]


def test_cli_pr_review_gate_runtime_change_fixture(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/pr_review_gate_runtime_change_blocked.json",
        capsys,
    )

    assert payload["status"] == "blocked_runtime_change"
    assert payload["changed_files_ok"] is True
    assert payload["scope_ok"] is False
    assert payload["blockers"]


def test_cli_pr_review_gate_unsafe_text_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/pr_review_gate_unsafe_text_blocked.json", capsys)

    assert payload["status"] == "blocked_unsafe_text"
    assert payload["ci_ok"] is True
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
