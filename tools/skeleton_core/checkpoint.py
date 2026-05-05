"""Public-safe checkpoint bundle rendering for Skeleton trace packets."""

import json

from tools.skeleton_core.report import render_runner_report_from_trace
from tools.skeleton_core.trace import TracePacket


def render_checkpoint(packet: TracePacket) -> str:
    """Render TracePacket JSON and runner report in one public-safe bundle."""
    trace_json = json.dumps(packet.model_dump(mode="json"), ensure_ascii=False, indent=2)
    return "\n".join(
        [
            "trace_packet_json",
            trace_json,
            "runner_report",
            render_runner_report_from_trace(packet),
        ]
    )
