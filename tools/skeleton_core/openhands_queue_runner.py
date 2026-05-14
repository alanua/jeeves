"""Local OpenHands queue runner v0.

Reads one JSON payload from a local queue directory, runs the existing
OpenHands dispatch path, and writes a public-safe JSON report.

This does not poll GitHub, mutate labels, merge, deploy, restart services,
or read repo secrets.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable, Sequence

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.openhands_dispatch_cli import build_run_report

OPENHANDS_QUEUE_RUNNER_VERSION = "openhands_queue_runner.v0"


class OpenHandsQueueRunReport(BaseModel):
    """Public-safe report for one local queue item."""

    model_config = ConfigDict(extra="forbid")

    queue_version: str = OPENHANDS_QUEUE_RUNNER_VERSION
    status: str
    payload_file: str = ""
    report_file: str = ""
    dispatch_status: str = ""
    result_status: str = ""
    stop_reason: str = ""
    changed_files: list[str] = Field(default_factory=list)
    outside_allowed_changes: list[str] = Field(default_factory=list)
    error_type: str = ""
    error: str = ""


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


def run_queue_once(
    *,
    queue_dir: Path,
    report_dir: Path,
    headless_json: bool = False,
    timeout_seconds: int = 300,
    exit_without_confirmation: bool = False,
    dispatch: DispatchFn = _default_dispatch,
) -> OpenHandsQueueRunReport:
    """Run one local queue payload and write one JSON report."""

    queue_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    payload_file = _first_payload(queue_dir)
    if payload_file is None:
        return OpenHandsQueueRunReport(status="empty")

    report_file = report_dir / f"{payload_file.stem}.report.json"

    try:
        payload = json.loads(payload_file.read_text(encoding="utf-8"))
        dispatch_report = dispatch(
            payload,
            headless_json=headless_json,
            timeout_seconds=timeout_seconds,
            exit_without_confirmation=exit_without_confirmation,
        )
        dispatch_json = _as_jsonable(dispatch_report)
        report_file.write_text(
            json.dumps(dispatch_json, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        summary = _extract_summary(dispatch_json)
        return OpenHandsQueueRunReport(
            status="reported",
            payload_file=str(payload_file),
            report_file=str(report_file),
            **summary,
        )
    except Exception as exc:
        error_json = {
            "queue_version": OPENHANDS_QUEUE_RUNNER_VERSION,
            "status": "error",
            "payload_file": str(payload_file),
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        report_file.write_text(
            json.dumps(error_json, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return OpenHandsQueueRunReport(
            status="error",
            payload_file=str(payload_file),
            report_file=str(report_file),
            error_type=type(exc).__name__,
            error=str(exc),
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one local OpenHands queue item")
    parser.add_argument("--queue-dir", required=True, help="Directory with JSON payloads")
    parser.add_argument("--report-dir", required=True, help="Directory for JSON reports")
    parser.add_argument(
        "--headless-json", action="store_true", help="Use guarded headless JSON run"
    )
    parser.add_argument(
        "--exit-without-confirmation",
        action="store_true",
        help="Pass OpenHands --exit-without-confirmation",
    )
    parser.add_argument("--timeout", type=int, default=300, help="OpenHands timeout seconds")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print queue report")
    return parser


def main(argv: Sequence[str] | None = None, *, dispatch: DispatchFn = _default_dispatch) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.timeout <= 0:
        report = OpenHandsQueueRunReport(
            status="error",
            error_type="ValueError",
            error="--timeout must be positive",
        )
        print(json.dumps(report.model_dump(mode="json"), sort_keys=True))
        return 2

    report = run_queue_once(
        queue_dir=Path(args.queue_dir),
        report_dir=Path(args.report_dir),
        headless_json=args.headless_json,
        timeout_seconds=args.timeout,
        exit_without_confirmation=args.exit_without_confirmation,
        dispatch=dispatch,
    )

    print(
        json.dumps(
            report.model_dump(mode="json"),
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 2 if report.status == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
