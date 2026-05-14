from __future__ import annotations

import json
from pathlib import Path

from tools.skeleton_core.openhands_dispatch_cli import (
    OPENHANDS_DISPATCH_CLI_VERSION,
    main,
)


def valid_payload() -> dict:
    return {
        "issue_number": 197,
        "repo": "alanua/jeeves",
        "title": "Add OpenHands dispatch CLI v0",
        "body": "bounded test payload",
        "labels": [
            "agent:task",
            "agent:audited",
            "agent:plan-ready",
            "runner:openhands",
            "risk:yellow",
        ],
        "allowed_files": ["tools/skeleton_core/openhands_dispatch_cli.py"],
        "expected_artifact": "diff",
        "authority_level": "level_2_local_diff",
        "risk_level": "yellow",
        "fuel_provider": "openrouter",
        "fuel_model": "deepseek/deepseek-v4-flash:free",
        "fuel_max_usd": 1.0,
    }


def write_payload(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_cli_dry_run_valid_payload_outputs_dispatched_report(
    tmp_path: Path,
    capsys,
) -> None:
    path = write_payload(tmp_path, valid_payload())

    code = main(["--input", str(path)])

    assert code == 0
    captured = json.loads(capsys.readouterr().out)
    assert captured["cli_version"] == OPENHANDS_DISPATCH_CLI_VERSION
    assert captured["status"] == "dispatched"
    assert captured["packet"]["task_id"] == "issue-197-openhands"
    assert captured["route_report"] is None


def test_cli_dry_run_blocked_payload_returns_one(tmp_path: Path, capsys) -> None:
    payload = valid_payload()
    payload["labels"].remove("agent:audited")
    path = write_payload(tmp_path, payload)

    code = main(["--input", str(path)])

    assert code == 1
    captured = json.loads(capsys.readouterr().out)
    assert captured["status"] == "blocked"
    assert "missing_label:agent:audited" in captured["blocked_reasons"]


def test_cli_invalid_json_returns_error(tmp_path: Path, capsys) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{bad", encoding="utf-8")

    code = main(["--input", str(path)])

    assert code == 2
    captured = json.loads(capsys.readouterr().out)
    assert captured["status"] == "error"
    assert captured["error_type"] == "JSONDecodeError"


def test_cli_pretty_outputs_json(tmp_path: Path, capsys) -> None:
    path = write_payload(tmp_path, valid_payload())

    code = main(["--input", str(path), "--pretty"])

    assert code == 0
    output = capsys.readouterr().out
    assert "\n  " in output
    assert json.loads(output)["status"] == "dispatched"
