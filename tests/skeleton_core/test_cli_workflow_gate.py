import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["workflow-gate", "--input", path])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_workflow_gate_python_update_ready(capsys) -> None:
    payload = _run_fixture("tests/fixtures/workflow_gate_python_update_ready.json", capsys)

    assert payload["status"] == "action_ready"
    assert payload["allowed_to_continue"] is True
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_workflow_gate_python_update_missing_format(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/workflow_gate_python_update_missing_format.json",
        capsys,
    )

    assert payload["status"] == "blocked_missing_required_skill"
    assert payload["allowed_to_continue"] is False
    assert "local_black_applied" in payload["missing_or_failed_skills"]
    assert "format_preflight" in payload["missing_or_failed_skills"]


def test_cli_workflow_gate_pr_ready_missing_review_gate(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/workflow_gate_pr_ready_missing_review_gate.json",
        capsys,
    )

    assert payload["status"] == "blocked_missing_required_skill"
    assert payload["missing_or_failed_skills"] == ["pr_review_gate"]


def test_cli_workflow_gate_runner_missing_env_check(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/workflow_gate_runner_missing_env_check.json",
        capsys,
    )

    assert payload["status"] == "blocked_missing_required_skill"
    assert "runner_env_check" in payload["missing_or_failed_skills"]


def test_cli_workflow_gate_queue_advance_missing_report(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/workflow_gate_queue_advance_missing_report.json",
        capsys,
    )

    assert payload["status"] == "blocked_missing_required_skill"
    assert "runner_report_ingest" in payload["missing_or_failed_skills"]


def test_cli_workflow_gate_actions_report_unsafe(capsys) -> None:
    payload = _run_fixture(
        "tests/fixtures/workflow_gate_actions_report_unsafe.json",
        capsys,
    )

    assert payload["status"] == "blocked_failed_required_skill"
    assert payload["missing_or_failed_skills"] == [
        "github_actions_runner_control=unsafe_or_policy_violation"
    ]
