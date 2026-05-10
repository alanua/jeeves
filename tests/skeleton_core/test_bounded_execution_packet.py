from __future__ import annotations

import pytest
from pydantic import ValidationError

from tools.skeleton_core.bounded_execution_packet import (
    ExecutionDecision,
    ExecutionPacket,
    ExecutionReportPacket,
)


def test_execution_packet_defaults_are_safe() -> None:
    packet = ExecutionPacket(
        issue_number=1,
        issue_url="https://github.com/alanua/jeeves/issues/1",
        title="Test",
        audit_verified=True,
        audit_status="live_accept",
    )

    assert packet.mode == "dry_run"
    assert packet.executor_allowed is False
    assert packet.file_writes_allowed is False
    assert packet.pr_creation_allowed is False
    assert packet.merge_allowed is False
    assert packet.deploy_allowed is False
    assert packet.canon_write_allowed is False


def test_execution_packet_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ExecutionPacket(
            issue_number=1,
            issue_url="https://github.com/alanua/jeeves/issues/1",
            title="Test",
            audit_verified=True,
            audit_status="live_accept",
            unexpected=True,
        )


def test_execution_report_contains_no_commands_by_default() -> None:
    packet = ExecutionPacket(
        issue_number=1,
        issue_url="https://github.com/alanua/jeeves/issues/1",
        title="Test",
        audit_verified=True,
        audit_status="live_accept",
    )
    report = ExecutionReportPacket(
        issue_number=1,
        decision=ExecutionDecision.WOULD_EXECUTE,
        execution_status="dry_run_complete",
        packet=packet,
        next_safe_step="Done.",
    )

    assert report.commands_executed == []
    assert report.files_changed == []
