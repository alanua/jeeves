from __future__ import annotations

from pathlib import Path

from tools.skeleton_core.active_executor import (
    build_active_execution_packet,
    command_is_allowed,
    execute_packet,
    validate_active_packet,
)
from tools.skeleton_core.dry_run_execution_route import (
    GitHubIssueComment,
    GitHubIssueExport,
    GitHubIssueLabel,
)


def _issue() -> GitHubIssueExport:
    return GitHubIssueExport(
        number=126,
        title="[agent-task-yellow] Active executor test",
        body="Public-safe audited issue.",
        url="https://github.com/alanua/jeeves/issues/126",
        state="OPEN",
        labels=[
            GitHubIssueLabel(name="agent:task"),
            GitHubIssueLabel(name="risk:yellow"),
            GitHubIssueLabel(name="runner:hetzner"),
            GitHubIssueLabel(name="agent:audited"),
        ],
        comments=[
            GitHubIssueComment(
                body="Autonomous YELLOW Gemini audit route report\nAdapter status: `live_accept`",
                url="https://github.com/alanua/jeeves/issues/126#comment",
            )
        ],
    )


def test_command_whitelist_accepts_safe_commands() -> None:
    assert command_is_allowed("python -m pytest -q")[0] is True
    assert (
        command_is_allowed("python -m ruff check tools/skeleton_core tests/skeleton_core")[0]
        is True
    )
    assert command_is_allowed("git status --short")[0] is True


def test_command_whitelist_blocks_destructive_commands() -> None:
    assert command_is_allowed("rm -rf /")[0] is False
    assert command_is_allowed("git push --force")[0] is False
    assert command_is_allowed("sudo systemctl restart x")[0] is False


def test_build_plan_packet_is_not_real() -> None:
    packet = build_active_execution_packet(_issue(), real_run=False)

    assert packet.real_run is False
    assert packet.executor_allowed is False
    assert packet.file_writes_allowed is False
    assert packet.pr_creation_allowed is False
    assert packet.merge_allowed is False
    assert packet.deploy_allowed is False
    assert packet.canon_write_allowed is False
    assert validate_active_packet(packet) == []


def test_real_packet_uses_whitelisted_validation_commands() -> None:
    packet = build_active_execution_packet(_issue(), real_run=True)

    assert packet.real_run is True
    assert packet.executor_allowed is True
    assert packet.planned_actions
    assert validate_active_packet(packet) == []


def test_execute_plan_packet_runs_no_commands(tmp_path: Path) -> None:
    packet = build_active_execution_packet(_issue(), real_run=False)

    decision, results, blocked = execute_packet(packet, repo_root=tmp_path)

    assert decision == "would_execute"
    assert results == []
    assert blocked == []


def test_execute_blocks_unapproved_command(tmp_path: Path) -> None:
    packet = build_active_execution_packet(_issue(), real_run=True)
    packet.planned_actions[0].command = "rm -rf /"

    decision, results, blocked = execute_packet(packet, repo_root=tmp_path)

    assert decision == "blocked"
    assert results == []
    assert any("forbidden_substring" in reason for reason in blocked)
