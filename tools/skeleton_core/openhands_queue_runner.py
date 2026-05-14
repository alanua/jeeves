"""Local OpenHands queue runner v0.

Reads one JSON payload from a local queue directory, moves it through a local
lifecycle, runs the existing OpenHands dispatch path, and writes a public-safe
JSON report.

Lifecycle:

queue/*.json -> running/*.json -> done/*.json
queue/*.json -> running/*.json -> failed/*.json

This does not poll GitHub, mutate labels, merge, deploy, restart services,
or read repo secrets.
"""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path
from typing import Any, Callable, Sequence

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.local_tool_runner import (
    LocalToolReport,
    LocalToolRequest,
    run_local_tool,
)
from tools.skeleton_core.openhands_dispatch_cli import build_run_report

OPENHANDS_QUEUE_RUNNER_VERSION = "openhands_queue_runner.v0"


class OpenHandsQueueRunReport(BaseModel):
    """Public-safe report for one local queue item."""

    model_config = ConfigDict(extra="forbid")

    queue_version: str = OPENHANDS_QUEUE_RUNNER_VERSION
    status: str
    payload_file: str = ""
    running_file: str = ""
    final_payload_file: str = ""
    report_file: str = ""
    dispatch_status: str = ""
    result_status: str = ""
    stop_reason: str = ""
    changed_files: list[str] = Field(default_factory=list)
    outside_allowed_changes: list[str] = Field(default_factory=list)
    validation_status: str = "not_run"
    validation_reports: list[LocalToolReport] = Field(default_factory=list)
    error_type: str = ""
    error: str = ""


class OpenHandsQueueLoopReport(BaseModel):
    """Public-safe report for a bounded local queue loop."""

    model_config = ConfigDict(extra="forbid")

    queue_version: str = OPENHANDS_QUEUE_RUNNER_VERSION
    status: str
    processed_count: int = 0
    done_count: int = 0
    failed_count: int = 0
    empty_count: int = 0
    max_items: int = 0
    reports: list[OpenHandsQueueRunReport] = Field(default_factory=list)


DispatchFn = Callable[..., Any]


def _default_dispatch(
    payload: dict[str, Any],
    *,
    headless_json: bool,
    timeout_seconds: int,
    exit_without_confirmation: bool,
) -> Any:
    return build_run_report(
        payload,
        headless_json=headless_json,
        timeout_seconds=timeout_seconds,
        exit_without_confirmation=exit_without_confirmation,
    )


def _as_jsonable(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return value
    raise TypeError(f"Unsupported dispatch report type: {type(value).__name__}")


QUEUE_ONLY_PAYLOAD_KEYS = {"local_validations"}


def _payload_for_dispatch(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove queue-runner-only fields before OpenHands issue dispatch validation."""

    return {key: value for key, value in payload.items() if key not in QUEUE_ONLY_PAYLOAD_KEYS}


def _validation_requests_from_payload(payload: dict[str, Any]) -> list[LocalToolRequest]:
    raw_items = payload.get("local_validations") or []
    if not isinstance(raw_items, list):
        raise ValueError("local_validations must be a list")

    requests: list[LocalToolRequest] = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            raise ValueError("local_validations items must be objects")
        requests.append(LocalToolRequest.model_validate(raw_item))
    return requests


def _run_local_validations(payload: dict[str, Any]) -> tuple[str, list[LocalToolReport]]:
    requests = _validation_requests_from_payload(payload)
    if not requests:
        return "not_run", []

    reports = [run_local_tool(request) for request in requests]
    if all(report.status == "success" for report in reports):
        return "passed", reports
    return "failed", reports


def _extract_summary(report: dict[str, Any]) -> dict[str, Any]:
    route = report.get("route_report") or {}
    result_packet = route.get("result") or {}
    result = result_packet.get("result") or {}
    collector = route.get("collector_report") or {}

    return {
        "dispatch_status": str(report.get("status") or ""),
        "result_status": str(result.get("status") or ""),
        "stop_reason": str(result.get("stop_reason") or ""),
        "changed_files": list(result.get("changed_files") or []),
        "outside_allowed_changes": list(collector.get("outside_allowed_changes") or []),
    }


def _first_payload(queue_dir: Path) -> Path | None:
    payloads = sorted(path for path in queue_dir.glob("*.json") if path.is_file())
    return payloads[0] if payloads else None


def _move_payload(source: Path, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    if target.exists():
        raise FileExistsError(f"Queue target already exists: {target}")
    shutil.move(str(source), str(target))
    return target


def _default_state_dirs(queue_dir: Path) -> tuple[Path, Path, Path]:
    base_dir = queue_dir.parent
    return base_dir / "running", base_dir / "done", base_dir / "failed"


def run_queue_once(
    *,
    queue_dir: Path,
    report_dir: Path,
    running_dir: Path | None = None,
    done_dir: Path | None = None,
    failed_dir: Path | None = None,
    headless_json: bool = False,
    timeout_seconds: int = 300,
    exit_without_confirmation: bool = False,
    dispatch: DispatchFn = _default_dispatch,
) -> OpenHandsQueueRunReport:
    """Run one local queue payload and write one JSON report."""

    default_running_dir, default_done_dir, default_failed_dir = _default_state_dirs(queue_dir)
    resolved_running_dir = running_dir or default_running_dir
    resolved_done_dir = done_dir or default_done_dir
    resolved_failed_dir = failed_dir or default_failed_dir

    queue_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    resolved_running_dir.mkdir(parents=True, exist_ok=True)
    resolved_done_dir.mkdir(parents=True, exist_ok=True)
    resolved_failed_dir.mkdir(parents=True, exist_ok=True)

    payload_file = _first_payload(queue_dir)
    if payload_file is None:
        return OpenHandsQueueRunReport(status="empty")

    running_file = _move_payload(payload_file, resolved_running_dir)
    report_file = report_dir / f"{running_file.stem}.report.json"

    try:
        payload = json.loads(running_file.read_text(encoding="utf-8"))
        dispatch_report = dispatch(
            _payload_for_dispatch(payload),
            headless_json=headless_json,
            timeout_seconds=timeout_seconds,
            exit_without_confirmation=exit_without_confirmation,
        )
        dispatch_json = _as_jsonable(dispatch_report)
        validation_status, validation_reports = _run_local_validations(payload)

        combined_report = {
            "dispatch_report": dispatch_json,
            "validation_status": validation_status,
            "validation_reports": [report.model_dump(mode="json") for report in validation_reports],
        }
        report_file.write_text(
            json.dumps(combined_report, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        summary = _extract_summary(dispatch_json)
        final_status = "done" if validation_status in {"not_run", "passed"} else "failed"
        final_dir = resolved_done_dir if final_status == "done" else resolved_failed_dir
        final_file = _move_payload(running_file, final_dir)

        return OpenHandsQueueRunReport(
            status=final_status,
            payload_file=str(payload_file),
            running_file=str(running_file),
            final_payload_file=str(final_file),
            report_file=str(report_file),
            validation_status=validation_status,
            validation_reports=validation_reports,
            **summary,
        )
    except Exception as exc:
        error_json = {
            "queue_version": OPENHANDS_QUEUE_RUNNER_VERSION,
            "status": "failed",
            "payload_file": str(payload_file),
            "running_file": str(running_file),
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        report_file.write_text(
            json.dumps(error_json, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        final_payload_file = ""
        if running_file.exists():
            final_payload_file = str(_move_payload(running_file, resolved_failed_dir))

        return OpenHandsQueueRunReport(
            status="failed",
            payload_file=str(payload_file),
            running_file=str(running_file),
            final_payload_file=final_payload_file,
            report_file=str(report_file),
            error_type=type(exc).__name__,
            error=str(exc),
        )


def run_queue_loop(
    *,
    queue_dir: Path,
    report_dir: Path,
    running_dir: Path | None = None,
    done_dir: Path | None = None,
    failed_dir: Path | None = None,
    headless_json: bool = False,
    timeout_seconds: int = 300,
    exit_without_confirmation: bool = False,
    max_items: int = 1,
    sleep_seconds: float = 0.0,
    dispatch: DispatchFn = _default_dispatch,
) -> OpenHandsQueueLoopReport:
    """Run a bounded local queue loop.

    This is intentionally bounded by max_items. Infinite daemon mode remains a
    later wrapper/service concern.
    """

    if max_items <= 0:
        raise ValueError("max_items must be positive")
    if sleep_seconds < 0:
        raise ValueError("sleep_seconds must not be negative")

    reports: list[OpenHandsQueueRunReport] = []

    for index in range(max_items):
        report = run_queue_once(
            queue_dir=queue_dir,
            report_dir=report_dir,
            running_dir=running_dir,
            done_dir=done_dir,
            failed_dir=failed_dir,
            headless_json=headless_json,
            timeout_seconds=timeout_seconds,
            exit_without_confirmation=exit_without_confirmation,
            dispatch=dispatch,
        )
        reports.append(report)

        if report.status == "empty":
            break

        if sleep_seconds and index < max_items - 1:
            time.sleep(sleep_seconds)

    done_count = sum(1 for report in reports if report.status == "done")
    failed_count = sum(1 for report in reports if report.status == "failed")
    empty_count = sum(1 for report in reports if report.status == "empty")
    processed_count = done_count + failed_count

    return OpenHandsQueueLoopReport(
        status="completed",
        processed_count=processed_count,
        done_count=done_count,
        failed_count=failed_count,
        empty_count=empty_count,
        max_items=max_items,
        reports=reports,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one local OpenHands queue item")
    parser.add_argument("--queue-dir", required=True, help="Directory with JSON payloads")
    parser.add_argument("--report-dir", required=True, help="Directory for JSON reports")
    parser.add_argument("--running-dir", help="Directory for payload currently being processed")
    parser.add_argument("--done-dir", help="Directory for successfully processed payloads")
    parser.add_argument("--failed-dir", help="Directory for failed payloads")
    parser.add_argument(
        "--headless-json", action="store_true", help="Use guarded headless JSON run"
    )
    parser.add_argument(
        "--exit-without-confirmation",
        action="store_true",
        help="Pass OpenHands --exit-without-confirmation",
    )
    parser.add_argument("--timeout", type=int, default=300, help="OpenHands timeout seconds")
    parser.add_argument("--loop", action="store_true", help="Run a bounded queue loop")
    parser.add_argument("--max-items", type=int, default=1, help="Maximum queue items for --loop")
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.0,
        help="Sleep between queue items in --loop mode",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print queue report")
    return parser


def main(argv: Sequence[str] | None = None, *, dispatch: DispatchFn = _default_dispatch) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    error = ""
    if args.timeout <= 0:
        error = "--timeout must be positive"
    elif args.max_items <= 0:
        error = "--max-items must be positive"
    elif args.sleep_seconds < 0:
        error = "--sleep-seconds must not be negative"

    if error:
        report = OpenHandsQueueRunReport(
            status="failed",
            error_type="ValueError",
            error=error,
        )
        print(json.dumps(report.model_dump(mode="json"), sort_keys=True))
        return 2

    common_kwargs = {
        "queue_dir": Path(args.queue_dir),
        "report_dir": Path(args.report_dir),
        "running_dir": Path(args.running_dir) if args.running_dir else None,
        "done_dir": Path(args.done_dir) if args.done_dir else None,
        "failed_dir": Path(args.failed_dir) if args.failed_dir else None,
        "headless_json": args.headless_json,
        "timeout_seconds": args.timeout,
        "exit_without_confirmation": args.exit_without_confirmation,
        "dispatch": dispatch,
    }

    if args.loop:
        loop_report = run_queue_loop(
            **common_kwargs,
            max_items=args.max_items,
            sleep_seconds=args.sleep_seconds,
        )
        print(
            json.dumps(
                loop_report.model_dump(mode="json"),
                indent=2 if args.pretty else None,
                sort_keys=True,
            )
        )
        return 2 if loop_report.failed_count else 0

    report = run_queue_once(**common_kwargs)

    print(
        json.dumps(
            report.model_dump(mode="json"),
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 2 if report.status == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
