import json

from tools.skeleton_core.cli import main


def test_cli_outputs_decision_json(capsys) -> None:
    exit_code = main(["--title", "Write docs", "--body", "Add markdown note"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["task"]["title"] == "Write docs"
    assert payload["risk_level"] == "YELLOW"
    assert payload["route_target"] == "RUNNER_YELLOW"
    assert payload["evidence_policy"] == "NONE"
    assert payload["blocked_reason"] is None
    assert "required runner report shape" in payload["runner_issue_body"].casefold()


def test_cli_outputs_decision_json_with_subcommand(capsys) -> None:
    exit_code = main(["decide", "--title", "Write docs", "--body", "Add markdown note"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["task"]["title"] == "Write docs"
    assert payload["risk_level"] == "YELLOW"
    assert payload["route_target"] == "RUNNER_YELLOW"


def test_cli_preserves_evidence_policy(capsys) -> None:
    exit_code = main(
        [
            "--title",
            "Review evidence",
            "--body",
            "Write docs note",
            "--evidence-policy",
            "GEMINI_EVIDENCE_ALLOWED",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["evidence_policy"] == "GEMINI_EVIDENCE_ALLOWED"
    assert "GEMINI_EVIDENCE_ALLOWED" in payload["runner_issue_body"]


def test_cli_blocks_red_task(capsys) -> None:
    exit_code = main(["--title", "Use token", "--body", "Read production .env"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["risk_level"] == "RED"
    assert payload["route_target"] == "BLOCKED_RED"
    assert payload["blocked_reason"] is not None
    assert "not executable" in payload["runner_issue_body"]


def test_cli_queue_summary(capsys) -> None:
    exit_code = main(["queue-summary", "--input", "tests/fixtures/github_queue_sample.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["ACTIVE_SKELETON"] == 1
    assert payload["JEEVES_RUNTIME_NOISE_FOR_NOW"] == 1
    assert payload["EVIDENCE_ONLY"] == 1
    assert payload["BLOCKED_WAITING_FOR_OLEKSII"] == 1
    assert payload["UNKNOWN_NEEDS_REVIEW"] == 0


def test_cli_runner_report_from_trace(capsys) -> None:
    exit_code = main(
        [
            "runner-report-from-trace",
            "--input",
            "tests/fixtures/trace_packet_sample.json",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "changed_files\n- tools/skeleton_core/cli.py" in captured.out
    assert "commands_run\n- python -m pytest -q" in captured.out
    assert "test_result\nreported in commands_run" in captured.out
    assert "lint_result\nreported in commands_run" in captured.out
    assert "format_result\nreported in commands_run" in captured.out
    assert "private_data_seen: no" in captured.out
    assert "runtime_code_touched: no" in captured.out
    assert "external_services_called: no" in captured.out
    assert "next_safe_step\nuse task-from-text for new Skeleton intake" in captured.out


def test_cli_task_from_text_docs_routes_yellow(capsys) -> None:
    exit_code = main(
        [
            "task-from-text",
            "--text",
            "Write docs note for Skeleton queue usage",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["task"]["title"] == "Write docs note for Skeleton queue usage"
    assert payload["task"]["body"] == "Write docs note for Skeleton queue usage"
    assert payload["risk_level"] == "YELLOW"
    assert payload["route_target"] == "RUNNER_YELLOW"


def test_cli_task_from_text_code_routes_orange(capsys) -> None:
    exit_code = main(["task-from-text", "--text", "Implement CLI test package"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["risk_level"] == "ORANGE"
    assert payload["route_target"] == "RUNNER_ORANGE"


def test_cli_task_from_text_red_routes_blocked(capsys) -> None:
    exit_code = main(["task-from-text", "--text", "Use production token from .env"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["risk_level"] == "RED"
    assert payload["route_target"] == "BLOCKED_RED"
    assert payload["blocked_reason"] is not None


def test_cli_task_from_text_preserves_title_and_evidence_policy(capsys) -> None:
    exit_code = main(
        [
            "task-from-text",
            "--text",
            "Write docs note",
            "--title",
            "Manual title",
            "--evidence-policy",
            "MANUAL_EVIDENCE_ALLOWED",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["task"]["title"] == "Manual title"
    assert payload["evidence_policy"] == "MANUAL_EVIDENCE_ALLOWED"


def test_cli_trace_packet(capsys) -> None:
    exit_code = main(
        [
            "trace-packet",
            "--task-id",
            "manual-001",
            "--project",
            "skeleton",
            "--risk-level",
            "YELLOW",
            "--route-target",
            "RUNNER_YELLOW",
            "--result",
            "completed",
            "--next-safe-step",
            "review",
            "--sources-read",
            "issue #33,CURRENT_STATE.md",
            "--files-changed",
            "tools/skeleton_core/trace.py",
            "--commands-run",
            "python -m pytest -q",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["task_id"] == "manual-001"
    assert payload["project"] == "skeleton"
    assert payload["risk_level"] == "YELLOW"
    assert payload["route_target"] == "RUNNER_YELLOW"
    assert payload["result"] == "completed"
    assert payload["next_safe_step"] == "review"
    assert payload["sources_read"] == ["issue #33", "CURRENT_STATE.md"]
    assert payload["files_changed"] == ["tools/skeleton_core/trace.py"]
    assert payload["commands_run"] == ["python -m pytest -q"]
    assert payload["private_data_seen"] is False
    assert payload["runtime_code_touched"] is False
    assert payload["external_services_called"] is False


def test_cli_work_packet_docs_routes_yellow(capsys) -> None:
    exit_code = main(
        [
            "work-packet",
            "--text",
            "Write docs note for Skeleton queue usage",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.startswith(
        "title\nWrite docs note for Skeleton queue usage\nproject\nskeleton"
    )
    assert "risk_level\nYELLOW" in captured.out
    assert "route_target\nRUNNER_YELLOW" in captured.out
    assert "goal\nWrite docs note for Skeleton queue usage" in captured.out
    assert "runner_issue_body\n# YELLOW" in captured.out
    assert "next_safe_step\ncreate GitHub issue" in captured.out


def test_cli_work_packet_code_routes_orange(capsys) -> None:
    exit_code = main(["work-packet", "--text", "Implement CLI test package"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "risk_level\nORANGE" in captured.out
    assert "route_target\nRUNNER_ORANGE" in captured.out
    assert "runner_issue_body\n# ORANGE" in captured.out


def test_cli_work_packet_red_routes_blocked(capsys) -> None:
    exit_code = main(["work-packet", "--text", "Use production token from .env"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "risk_level\nRED" in captured.out
    assert "route_target\nBLOCKED_RED" in captured.out
    assert "blocked_reason\n" in captured.out
    assert "not executable" in captured.out
    assert "next_safe_step\nwait for Oleksii" in captured.out


def test_cli_work_packet_preserves_title_and_evidence_policy(capsys) -> None:
    exit_code = main(
        [
            "work-packet",
            "--text",
            "Write docs note",
            "--title",
            "Manual title",
            "--evidence-policy",
            "MANUAL_EVIDENCE_ALLOWED",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.startswith("title\nManual title\nproject\nskeleton")
    assert "evidence_policy\nMANUAL_EVIDENCE_ALLOWED" in captured.out
    assert "MANUAL_EVIDENCE_ALLOWED" in captured.out


def test_cli_returns_2_for_invalid_packet(capsys) -> None:
    exit_code = main(["--title", "", "--body", "Body"])

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "string_too_short" in captured.out
