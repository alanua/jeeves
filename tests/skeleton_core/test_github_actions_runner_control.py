from tools.skeleton_core.github_actions_runner_control import (
    ActionsJob,
    ActionsStep,
    GithubActionsRunnerInput,
    build_github_actions_runner_control,
)


def _base_packet(**overrides) -> GithubActionsRunnerInput:
    data = {
        "repository": "alanua/bauclock",
        "workflow": "Tests",
        "workflow_file": "tests.yml",
        "ref": "main",
        "head_sha": "abc123",
        "run_id": 1001,
        "run_status": "completed",
        "run_conclusion": "success",
        "commands_inferred": ["pytest"],
        "logs_summary": ["All tests passed."],
        "jobs": [
            ActionsJob(
                name="tests",
                status="completed",
                conclusion="success",
                steps=[
                    ActionsStep(
                        name="Run tests",
                        status="completed",
                        conclusion="success",
                        summary="228 passed",
                    )
                ],
            )
        ],
    }
    data.update(overrides)
    return GithubActionsRunnerInput(**data)


def test_actions_success_report() -> None:
    result = build_github_actions_runner_control(_base_packet())

    assert result.status == "workflow_success_report"
    assert result.test_result == "passed"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert "BauClock #22" in result.issue_report_text
    assert "queue-state may unlock" in result.issue_report_text


def test_actions_failed_report_includes_failed_step() -> None:
    result = build_github_actions_runner_control(
        _base_packet(
            run_conclusion="failure",
            logs_summary=["pytest failed"],
            jobs=[
                ActionsJob(
                    name="tests",
                    status="completed",
                    conclusion="failure",
                    steps=[
                        ActionsStep(
                            name="Run tests",
                            status="completed",
                            conclusion="failure",
                            summary="1 failed",
                        )
                    ],
                )
            ],
        )
    )

    assert result.status == "workflow_failed_report"
    assert result.test_result == "failed"
    assert result.failed_steps == ["tests: Run tests"]
    assert result.failure_summary == "Failed steps: tests: Run tests"


def test_actions_cancelled_report() -> None:
    result = build_github_actions_runner_control(
        _base_packet(run_conclusion="cancelled", jobs=[], logs_summary=[])
    )

    assert result.status == "workflow_cancelled_report"
    assert result.test_result == "cancelled"
    assert result.failure_summary == "Workflow run was cancelled."


def test_actions_secret_like_log_is_blocked_and_redacted() -> None:
    result = build_github_actions_runner_control(
        _base_packet(
            run_conclusion="failure",
            logs_summary=["token=<redacted-fixture-value> appeared"],
        )
    )

    assert result.status == "unsafe_or_policy_violation"
    assert result.test_result == "blocked"
    assert result.failure_summary is not None
    assert "Secret-like content" in result.failure_summary
    assert "token=" not in result.failure_summary


def test_actions_unknown_needs_review() -> None:
    result = build_github_actions_runner_control(_base_packet(run_conclusion="", jobs=[]))

    assert result.status == "workflow_unknown_needs_review"
    assert result.test_result == "unknown"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
