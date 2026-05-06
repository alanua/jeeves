from tools.skeleton_core.runner_command_pack import (
    RunnerCommandInput,
    build_runner_command_pack,
)


def test_runner_command_pack_green_read_only() -> None:
    result = build_runner_command_pack(
        RunnerCommandInput(
            repository="alanua/bauclock",
            issue_number=22,
            title="[agent-task-green] BauClock overnight baseline validation",
            risk_level="GREEN",
            runner_route="RUNNER_GREEN",
            review_required=False,
            expected_commands=["python -m pytest"],
        )
    )

    assert result.status == "ready"
    assert result.issue_number == 22
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert "КОД BauClock" in result.command_text
    assert "GREEN read-only validation" in result.command_text
    assert "Do not change files" in result.command_text
    assert "python -m pytest" in result.command_text
    assert "Do not merge or deploy" in result.command_text


def test_runner_command_pack_yellow_allowed_files() -> None:
    result = build_runner_command_pack(
        RunnerCommandInput(
            repository="alanua/bauclock",
            issue_number=23,
            title="[agent-task-yellow] BauClock access-control hardening",
            risk_level="YELLOW",
            runner_route="RUNNER_YELLOW",
            review_required=True,
            allowed_files=["tests/test_calendar_service.py"],
            expected_commands=["python -m pytest tests/test_calendar_service.py -q"],
        )
    )

    assert result.status == "ready"
    assert result.issue_number == 23
    assert "YELLOW test-only task" in result.command_text
    assert "tests/test_calendar_service.py" in result.command_text
    assert "Open a draft PR or blocked report" in result.command_text
    assert "Do not merge or deploy" in result.command_text


def test_runner_command_pack_blocks_red() -> None:
    result = build_runner_command_pack(
        RunnerCommandInput(
            repository="alanua/bauclock",
            issue_number=999,
            title="[agent-task-red] risky task",
            risk_level="RED",
            runner_route="BLOCKED",
            review_required=True,
        )
    )

    assert result.status == "blocked"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.command_text.startswith("BLOCKED")
    assert any("Unsupported risk level: RED" == blocker for blocker in result.blockers)


def test_runner_command_pack_blocks_missing_fields() -> None:
    result = build_runner_command_pack(
        RunnerCommandInput(repository="alanua/bauclock", risk_level="YELLOW")
    )

    assert result.status == "blocked"
    assert "Missing required field: issue_number" in result.blockers
    assert "Missing required field: title" in result.blockers
    assert "YELLOW task must include allowed_files" in result.blockers


def test_runner_command_pack_blocks_unsafe_text() -> None:
    result = build_runner_command_pack(
        RunnerCommandInput(
            repository="alanua/bauclock",
            issue_number=1000,
            title="Use token and live mode",
            risk_level="YELLOW",
            runner_route="RUNNER_YELLOW",
            review_required=True,
            allowed_files=["tests/test_example.py"],
        )
    )

    assert result.status == "blocked"
    assert any("secret" in blocker for blocker in result.blockers)
    assert any("network" in blocker for blocker in result.blockers)


def test_runner_command_pack_blocks_merge_or_deploy_allowed_true() -> None:
    result = build_runner_command_pack(
        RunnerCommandInput(
            repository="alanua/bauclock",
            issue_number=24,
            title="[agent-task-green] baseline",
            risk_level="GREEN",
            runner_route="RUNNER_GREEN",
            review_required=False,
            merge_allowed=True,
            deploy_allowed=True,
        )
    )

    assert result.status == "blocked"
    assert "merge_allowed must be false" in result.blockers
    assert "deploy_allowed must be false" in result.blockers
