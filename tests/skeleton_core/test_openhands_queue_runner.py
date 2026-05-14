from __future__ import annotations

import json
from pathlib import Path

from tools.skeleton_core.openhands_queue_runner import main, run_queue_loop, run_queue_once


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


def failing_dispatch(
    payload_dict: dict,
    *,
    headless_json: bool,
    timeout_seconds: int,
    exit_without_confirmation: bool,
) -> dict:
    raise RuntimeError("dispatch failed")


def write_payload(queue_dir: Path, name: str = "001-payload.json") -> Path:
    queue_dir.mkdir(parents=True, exist_ok=True)
    path = queue_dir / name
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


def test_run_queue_once_moves_payload_to_done_and_writes_report(tmp_path: Path) -> None:
    queue_dir = tmp_path / "queue"
    running_dir = tmp_path / "running"
    done_dir = tmp_path / "done"
    failed_dir = tmp_path / "failed"
    report_dir = tmp_path / "reports"
    payload_file = write_payload(queue_dir)

    report = run_queue_once(
        queue_dir=queue_dir,
        report_dir=report_dir,
        running_dir=running_dir,
        done_dir=done_dir,
        failed_dir=failed_dir,
        headless_json=True,
        timeout_seconds=17,
        exit_without_confirmation=True,
        dispatch=fake_dispatch,
    )

    assert report.status == "done"
    assert report.payload_file == str(payload_file)
    assert report.running_file == str(running_dir / payload_file.name)
    assert report.final_payload_file == str(done_dir / payload_file.name)
    assert report.dispatch_status == "dispatched"
    assert report.result_status == "success"
    assert report.stop_reason == "allowed_file_changes_collected"
    assert report.changed_files == ["QUEUE_TEST.md"]
    assert report.outside_allowed_changes == []
    assert not payload_file.exists()
    assert not (running_dir / payload_file.name).exists()
    assert (done_dir / payload_file.name).exists()
    assert Path(report.report_file).exists()


def test_run_queue_once_invalid_json_moves_payload_to_failed(tmp_path: Path) -> None:
    queue_dir = tmp_path / "queue"
    failed_dir = tmp_path / "failed"
    report_dir = tmp_path / "reports"
    queue_dir.mkdir(parents=True)
    bad_payload = queue_dir / "bad.json"
    bad_payload.write_text("{bad", encoding="utf-8")

    report = run_queue_once(
        queue_dir=queue_dir,
        report_dir=report_dir,
        failed_dir=failed_dir,
        dispatch=fake_dispatch,
    )

    assert report.status == "failed"
    assert report.error_type == "JSONDecodeError"
    assert not bad_payload.exists()
    assert (failed_dir / "bad.json").exists()
    assert Path(report.report_file).exists()


def test_run_queue_once_dispatch_error_moves_payload_to_failed(tmp_path: Path) -> None:
    queue_dir = tmp_path / "queue"
    failed_dir = tmp_path / "failed"
    report_dir = tmp_path / "reports"
    payload_file = write_payload(queue_dir)

    report = run_queue_once(
        queue_dir=queue_dir,
        report_dir=report_dir,
        failed_dir=failed_dir,
        dispatch=failing_dispatch,
    )

    assert report.status == "failed"
    assert report.error_type == "RuntimeError"
    assert "dispatch failed" in report.error
    assert not payload_file.exists()
    assert (failed_dir / payload_file.name).exists()
    assert Path(report.report_file).exists()


def test_queue_runner_main_outputs_json(tmp_path: Path, capsys) -> None:
    queue_dir = tmp_path / "queue"
    report_dir = tmp_path / "reports"
    done_dir = tmp_path / "done"
    write_payload(queue_dir)

    code = main(
        [
            "--queue-dir",
            str(queue_dir),
            "--report-dir",
            str(report_dir),
            "--done-dir",
            str(done_dir),
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
    assert output["status"] == "done"
    assert output["changed_files"] == ["QUEUE_TEST.md"]
    assert Path(output["final_payload_file"]).parent == done_dir


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
    assert output["status"] == "failed"
    assert "--timeout must be positive" in output["error"]


def test_run_queue_loop_processes_multiple_payloads(tmp_path: Path) -> None:
    queue_dir = tmp_path / "queue"
    report_dir = tmp_path / "reports"
    done_dir = tmp_path / "done"
    write_payload(queue_dir, "001-payload.json")
    write_payload(queue_dir, "002-payload.json")

    loop_report = run_queue_loop(
        queue_dir=queue_dir,
        report_dir=report_dir,
        done_dir=done_dir,
        headless_json=True,
        timeout_seconds=17,
        exit_without_confirmation=True,
        max_items=5,
        dispatch=fake_dispatch,
    )

    assert loop_report.status == "completed"
    assert loop_report.processed_count == 2
    assert loop_report.done_count == 2
    assert loop_report.failed_count == 0
    assert loop_report.empty_count == 1
    assert len(loop_report.reports) == 3
    assert not list(queue_dir.glob("*.json"))
    assert (done_dir / "001-payload.json").exists()
    assert (done_dir / "002-payload.json").exists()


def test_queue_runner_main_loop_outputs_loop_report(tmp_path: Path, capsys) -> None:
    queue_dir = tmp_path / "queue"
    report_dir = tmp_path / "reports"
    done_dir = tmp_path / "done"
    write_payload(queue_dir, "001-payload.json")
    write_payload(queue_dir, "002-payload.json")

    code = main(
        [
            "--queue-dir",
            str(queue_dir),
            "--report-dir",
            str(report_dir),
            "--done-dir",
            str(done_dir),
            "--headless-json",
            "--exit-without-confirmation",
            "--timeout",
            "17",
            "--loop",
            "--max-items",
            "2",
            "--pretty",
        ],
        dispatch=fake_dispatch,
    )

    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "completed"
    assert output["processed_count"] == 2
    assert output["done_count"] == 2
    assert output["failed_count"] == 0
    assert len(output["reports"]) == 2


def test_queue_runner_main_rejects_invalid_max_items(tmp_path: Path, capsys) -> None:
    code = main(
        [
            "--queue-dir",
            str(tmp_path / "queue"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--loop",
            "--max-items",
            "0",
        ],
        dispatch=fake_dispatch,
    )

    assert code == 2
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "failed"
    assert "--max-items must be positive" in output["error"]
