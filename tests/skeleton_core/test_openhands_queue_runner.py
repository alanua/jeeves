from __future__ import annotations

import json
from pathlib import Path

from tools.skeleton_core.openhands_queue_runner import main, run_queue_once


def payload() -> dict:
    return {
        "issue_number": 211,
        "repo": "alanua/jeeves",
        "title": "Queue runner test payload",
        "body": "Create one allowed file.",
        "labels": [
            "agent:task",
            "agent:audited",
            "agent:plan-ready",
            "runner:openhands",
            "risk:yellow",
        ],
        "allowed_files": ["QUEUE_TEST.md"],
        "expected_artifact": "diff",
        "authority_level": "level_2_local_diff",
        "risk_level": "yellow",
        "fuel_provider": "openrouter",
        "fuel_model": "deepseek/deepseek-v4-flash:free",
        "fuel_max_usd": 1.0,
    }


def fake_dispatch(
    payload_dict: dict,
    *,
    headless_json: bool,
    timeout_seconds: int,
    exit_without_confirmation: bool,
) -> dict:
    assert payload_dict["issue_number"] == 211
    assert headless_json is True
    assert timeout_seconds == 17
    assert exit_without_confirmation is True

    return {
        "status": "dispatched",
        "route_report": {
            "result": {
                "result": {
                    "status": "success",
                    "stop_reason": "allowed_file_changes_collected",
                    "changed_files": ["QUEUE_TEST.md"],
                }
            },
            "collector_report": {
                "outside_allowed_changes": [],
            },
        },
    }


def write_payload(queue_dir: Path) -> Path:
    queue_dir.mkdir(parents=True, exist_ok=True)
    path = queue_dir / "001-payload.json"
    path.write_text(json.dumps(payload()), encoding="utf-8")
    return path


def test_run_queue_once_empty_queue(tmp_path: Path) -> None:
    report = run_queue_once(
        queue_dir=tmp_path / "queue",
        report_dir=tmp_path / "reports",
        dispatch=fake_dispatch,
    )

    assert report.status == "empty"
    assert report.payload_file == ""


def test_run_queue_once_writes_report_and_summary(tmp_path: Path) -> None:
    queue_dir = tmp_path / "queue"
    report_dir = tmp_path / "reports"
    payload_file = write_payload(queue_dir)

    report = run_queue_once(
        queue_dir=queue_dir,
        report_dir=report_dir,
        headless_json=True,
        timeout_seconds=17,
        exit_without_confirmation=True,
        dispatch=fake_dispatch,
    )

    assert report.status == "reported"
    assert report.payload_file == str(payload_file)
    assert report.dispatch_status == "dispatched"
    assert report.result_status == "success"
    assert report.stop_reason == "allowed_file_changes_collected"
    assert report.changed_files == ["QUEUE_TEST.md"]
    assert report.outside_allowed_changes == []
    assert Path(report.report_file).exists()


def test_run_queue_once_invalid_json_writes_error_report(tmp_path: Path) -> None:
    queue_dir = tmp_path / "queue"
    report_dir = tmp_path / "reports"
    queue_dir.mkdir(parents=True)
    bad_payload = queue_dir / "bad.json"
    bad_payload.write_text("{bad", encoding="utf-8")

    report = run_queue_once(
        queue_dir=queue_dir,
        report_dir=report_dir,
        dispatch=fake_dispatch,
    )

    assert report.status == "error"
    assert report.error_type == "JSONDecodeError"
    assert Path(report.report_file).exists()


def test_queue_runner_main_outputs_json(tmp_path: Path, capsys) -> None:
    queue_dir = tmp_path / "queue"
    report_dir = tmp_path / "reports"
    write_payload(queue_dir)

    code = main(
        [
            "--queue-dir",
            str(queue_dir),
            "--report-dir",
            str(report_dir),
            "--headless-json",
            "--exit-without-confirmation",
            "--timeout",
            "17",
            "--pretty",
        ],
        dispatch=fake_dispatch,
    )

    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "reported"
    assert output["changed_files"] == ["QUEUE_TEST.md"]


def test_queue_runner_main_rejects_invalid_timeout(tmp_path: Path, capsys) -> None:
    code = main(
        [
            "--queue-dir",
            str(tmp_path / "queue"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--timeout",
            "0",
        ],
        dispatch=fake_dispatch,
    )

    assert code == 2
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "error"
    assert "--timeout must be positive" in output["error"]
