import pytest
from pydantic import ValidationError

from tools.skeleton_core.trace import TracePacket


def test_trace_packet_defaults_are_public_safe() -> None:
    packet = TracePacket(
        task_id="manual-001",
        risk_level="YELLOW",
        route_target="RUNNER_YELLOW",
        result="completed",
        next_safe_step="review",
    )

    assert packet.project == "skeleton"
    assert packet.sources_read == []
    assert packet.files_changed == []
    assert packet.commands_run == []
    assert packet.blocked_reason is None
    assert packet.private_data_seen is False
    assert packet.runtime_code_touched is False
    assert packet.external_services_called is False


def test_trace_packet_accepts_public_safe_lists() -> None:
    packet = TracePacket(
        task_id="manual-002",
        project="skeleton",
        risk_level="ORANGE",
        route_target="RUNNER_ORANGE",
        result="completed",
        next_safe_step="merge",
        sources_read=["issue #33"],
        files_changed=["tools/skeleton_core/trace.py"],
        commands_run=["python -m pytest -q"],
    )

    assert packet.sources_read == ["issue #33"]
    assert packet.files_changed == ["tools/skeleton_core/trace.py"]
    assert packet.commands_run == ["python -m pytest -q"]


def test_trace_packet_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TracePacket(
            task_id="manual-003",
            risk_level="YELLOW",
            route_target="RUNNER_YELLOW",
            result="completed",
            next_safe_step="review",
            unexpected="value",
        )


def test_trace_packet_rejects_empty_required_fields() -> None:
    required_kwargs = {
        "task_id": "manual-004",
        "risk_level": "YELLOW",
        "route_target": "RUNNER_YELLOW",
        "result": "completed",
        "next_safe_step": "review",
    }

    for field_name in required_kwargs:
        kwargs = required_kwargs.copy()
        kwargs[field_name] = ""
        with pytest.raises(ValidationError):
            TracePacket(**kwargs)
