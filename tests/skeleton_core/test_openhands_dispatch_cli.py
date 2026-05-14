from __future__ import annotations

import json
import subprocess
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


def test_cli_headless_json_requires_run(tmp_path: Path, capsys) -> None:
    path = write_payload(tmp_path, valid_payload())

    code = main(["--input", str(path), "--headless-json"])

    assert code == 2
    captured = json.loads(capsys.readouterr().out)
    assert captured["status"] == "error"
    assert "--headless-json requires --run" in captured["error"]


def test_cli_run_headless_json_passes_config_to_route(tmp_path: Path, capsys, monkeypatch) -> None:
    from tools.skeleton_core import openhands_dispatch_cli as cli
    from tools.skeleton_core.openhands_adapter import (
        build_openhands_result,
        prepare_openhands_task,
    )
    from tools.skeleton_core.openhands_runner_route import OpenHandsRunnerRouteReport

    captured_config = {}

    def fake_run_openhands_route(packet, *, config):
        captured_config["timeout_seconds"] = config.timeout_seconds
        captured_config["headless_json"] = config.adapter_config.headless_json
        captured_config["exit_without_confirmation"] = (
            config.adapter_config.exit_without_confirmation
        )
        captured_config["model"] = config.adapter_config.model

        return OpenHandsRunnerRouteReport(
            prepared=prepare_openhands_task(packet, "/tmp/task.md", config.adapter_config),
            result=build_openhands_result(
                packet,
                executor_status="blocked",
                changed_files=[],
                artifact_paths=[],
                validation_status="blocked",
                risk_flags=[],
                stop_reason="fake_run",
            ),
            returncode=0,
            stdout_tail="",
            stderr_tail="",
            collector_report=None,
        )

    monkeypatch.setattr(cli, "run_openhands_route", fake_run_openhands_route)

    path = write_payload(tmp_path, valid_payload())

    code = main(
        [
            "--input",
            str(path),
            "--run",
            "--headless-json",
            "--exit-without-confirmation",
            "--timeout",
            "7",
        ]
    )

    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "dispatched"
    assert output["route_report"] is not None
    assert captured_config == {
        "timeout_seconds": 7,
        "headless_json": True,
        "exit_without_confirmation": True,
        "model": "deepseek/deepseek-v4-flash:free",
    }
    assert "--headless" in output["route_report"]["prepared"]["command"]
    assert "--json" in output["route_report"]["prepared"]["command"]
    assert "--exit-without-confirmation" in output["route_report"]["prepared"]["command"]


def test_cli_exit_without_confirmation_requires_run(tmp_path: Path, capsys) -> None:
    path = write_payload(tmp_path, valid_payload())

    code = main(["--input", str(path), "--exit-without-confirmation"])

    assert code == 2
    captured = json.loads(capsys.readouterr().out)
    assert captured["status"] == "error"
    assert "--exit-without-confirmation requires --run" in captured["error"]
