"""Public-safe runner report rendering for Skeleton trace packets."""

from tools.skeleton_core.trace import TracePacket

REPORT_FIELD_ORDER = (
    "changed_files",
    "commands_run",
    "test_result",
    "lint_result",
    "format_result",
    "diff_summary",
    "errors_or_blockers",
    "private_data_seen",
    "runtime_code_touched",
    "external_services_called",
    "next_safe_step",
)


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _list_block(values: list[str]) -> str:
    if not values:
        return "none"
    return "\n".join(f"- {value}" for value in values)


def _has_command(commands: list[str], needle: str) -> bool:
    return any(needle in command for command in commands)


def _reported_if_command(commands: list[str], needle: str) -> str:
    if _has_command(commands, needle):
        return "reported in commands_run"
    return "not reported"


def render_runner_report_from_trace(packet: TracePacket) -> str:
    """Render the standard short public-safe runner report shape."""
    return "\n".join(
        [
            "changed_files",
            _list_block(packet.files_changed),
            "commands_run",
            _list_block(packet.commands_run),
            "test_result",
            _reported_if_command(packet.commands_run, "pytest"),
            "lint_result",
            _reported_if_command(packet.commands_run, "ruff"),
            "format_result",
            _reported_if_command(packet.commands_run, "black"),
            "diff_summary",
            "not reported",
            "errors_or_blockers",
            packet.blocked_reason or "none",
            f"private_data_seen: {_yes_no(packet.private_data_seen)}",
            f"runtime_code_touched: {_yes_no(packet.runtime_code_touched)}",
            f"external_services_called: {_yes_no(packet.external_services_called)}",
            "next_safe_step",
            packet.next_safe_step,
        ]
    )
