import json

from tools.skeleton_core.checkpoint import render_checkpoint
from tools.skeleton_core.trace import TracePacket


def _trace_json_from_checkpoint(checkpoint: str) -> dict:
    _, rest = checkpoint.split("trace_packet_json\n", 1)
    trace_json, _ = rest.split("\nrunner_report\n", 1)
    return json.loads(trace_json)


def test_render_checkpoint_contains_trace_json_and_report() -> None:
    packet = TracePacket(
        task_id="manual-001",
        project="skeleton",
        risk_level="YELLOW",
        route_target="RUNNER_YELLOW",
        result="completed",
        next_safe_step="review",
        files_changed=["tools/skeleton_core/cli.py"],
        commands_run=["python -m pytest -q"],
    )

    checkpoint = render_checkpoint(packet)
    trace_payload = _trace_json_from_checkpoint(checkpoint)

    assert checkpoint.startswith("trace_packet_json\n{")
    assert "\nrunner_report\nchanged_files" in checkpoint
    assert trace_payload["task_id"] == "manual-001"
    assert trace_payload["files_changed"] == ["tools/skeleton_core/cli.py"]
    assert "test_result\nreported in commands_run" in checkpoint
    assert checkpoint.endswith("next_safe_step\nreview")


def test_render_checkpoint_for_blocked_trace() -> None:
    packet = TracePacket(
        task_id="blocked-001",
        risk_level="RED",
        route_target="BLOCKED_RED",
        result="blocked",
        next_safe_step="wait for Oleksii",
        blocked_reason="blocked by policy",
        private_data_seen=True,
    )

    checkpoint = render_checkpoint(packet)
    trace_payload = _trace_json_from_checkpoint(checkpoint)

    assert trace_payload["route_target"] == "BLOCKED_RED"
    assert trace_payload["blocked_reason"] == "blocked by policy"
    assert "errors_or_blockers\nblocked by policy" in checkpoint
    assert "private_data_seen: yes" in checkpoint
    assert checkpoint.endswith("next_safe_step\nwait for Oleksii")
