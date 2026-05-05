from tools.skeleton_core.report import REPORT_FIELD_ORDER, render_runner_report_from_trace
from tools.skeleton_core.trace import TracePacket


def test_report_field_order_is_stable() -> None:
    assert REPORT_FIELD_ORDER == (
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


def test_render_runner_report_from_trace() -> None:
    packet = TracePacket(
        task_id="issue-35",
        project="skeleton",
        risk_level="ORANGE",
        route_target="RUNNER_ORANGE",
        result="merged",
        next_safe_step="use task-from-text for new Skeleton intake",
        files_changed=["tools/skeleton_core/cli.py", "tests/skeleton_core/test_cli.py"],
        commands_run=[
            "python -m pytest -q",
            "python -m ruff check tools/skeleton_core tests/skeleton_core",
            "python -m black --check tools/skeleton_core tests/skeleton_core",
        ],
    )

    report = render_runner_report_from_trace(packet)

    assert "changed_files\n- tools/skeleton_core/cli.py" in report
    assert "commands_run\n- python -m pytest -q" in report
    assert "test_result\nreported in commands_run" in report
    assert "lint_result\nreported in commands_run" in report
    assert "format_result\nreported in commands_run" in report
    assert "diff_summary\nnot reported" in report
    assert "errors_or_blockers\nnone" in report
    assert "private_data_seen: no" in report
    assert "runtime_code_touched: no" in report
    assert "external_services_called: no" in report
    assert "next_safe_step\nuse task-from-text for new Skeleton intake" in report


def test_render_runner_report_from_blocked_trace() -> None:
    packet = TracePacket(
        task_id="manual-blocked",
        risk_level="RED",
        route_target="BLOCKED_RED",
        result="blocked",
        next_safe_step="wait for Oleksii",
        blocked_reason="RED task detected",
        private_data_seen=True,
        runtime_code_touched=True,
        external_services_called=True,
    )

    report = render_runner_report_from_trace(packet)

    assert "changed_files\nnone" in report
    assert "commands_run\nnone" in report
    assert "test_result\nnot reported" in report
    assert "lint_result\nnot reported" in report
    assert "format_result\nnot reported" in report
    assert "errors_or_blockers\nRED task detected" in report
    assert "private_data_seen: yes" in report
    assert "runtime_code_touched: yes" in report
    assert "external_services_called: yes" in report
