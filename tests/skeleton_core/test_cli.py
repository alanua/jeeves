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


def test_cli_returns_2_for_invalid_packet(capsys) -> None:
    exit_code = main(["--title", "", "--body", "Body"])

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "string_too_short" in captured.out
