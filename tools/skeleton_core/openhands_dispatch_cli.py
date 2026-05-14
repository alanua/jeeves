"""CLI wrapper for OpenHands issue dispatch v0.

This module reads a public-safe issue payload JSON file and emits a public-safe
dispatch report JSON. It does not call GitHub, mutate labels, merge, deploy, or
restart services.

The default mode is dry-run so the CLI can validate payloads without launching
OpenHands. Real route execution requires --run.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from tools.skeleton_core.openhands_adapter import OpenHandsAdapterConfig
from tools.skeleton_core.openhands_issue_dispatch import (
    OpenHandsIssueDispatchReport,
    build_packet_from_issue,
    dispatch_openhands_issue,
    validate_issue_payload,
)
from tools.skeleton_core.openhands_runner_route import (
    OpenHandsRunnerRouteConfig,
    run_openhands_route,
)

OPENHANDS_DISPATCH_CLI_VERSION = "openhands_dispatch_cli.v0"


def _load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_dry_run_report(payload: dict) -> OpenHandsIssueDispatchReport:
    """Validate payload and build packet without running the route."""

    blocked = validate_issue_payload(payload)
    if blocked:
        return OpenHandsIssueDispatchReport(
            status="blocked",
            blocked_reasons=blocked,
            next_safe_step="Stop and fix issue labels/scope before dispatch.",
        )

    packet = build_packet_from_issue(payload)
    return OpenHandsIssueDispatchReport(
        status="dispatched",
        packet=packet,
        route_report=None,
        next_safe_step="Dry-run only. Review packet before running OpenHands route.",
    )


def build_run_report(
    payload: dict,
    *,
    headless_json: bool = False,
    timeout_seconds: int = 300,
    exit_without_confirmation: bool = False,
) -> OpenHandsIssueDispatchReport:
    """Run the real OpenHands route.

    This expects runner-local secret configuration to already exist. It still
    does not call GitHub or mutate labels.
    """

    def route(packet):
        return run_openhands_route(
            packet,
            config=OpenHandsRunnerRouteConfig(
                timeout_seconds=timeout_seconds,
                adapter_config=OpenHandsAdapterConfig(
                    model=packet.fuel_policy.model,
                    headless_json=headless_json,
                    exit_without_confirmation=exit_without_confirmation,
                ),
            ),
        )

    return dispatch_openhands_issue(payload, route=route)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run OpenHands issue dispatch v0")
    parser.add_argument("--input", required=True, help="Path to issue payload JSON")
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run OpenHands route instead of dry-run validation",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    parser.add_argument(
        "--headless-json",
        action="store_true",
        help="Use OpenHands --headless --json for real --run mode",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout seconds for real --run mode",
    )
    parser.add_argument(
        "--exit-without-confirmation",
        action="store_true",
        help="Pass OpenHands --exit-without-confirmation in real --run mode",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        payload = _load_payload(Path(args.input))
        if args.headless_json and not args.run:
            raise ValueError("--headless-json requires --run")
        if args.exit_without_confirmation and not args.run:
            raise ValueError("--exit-without-confirmation requires --run")
        if args.timeout <= 0:
            raise ValueError("--timeout must be positive")

        report = (
            build_run_report(
                payload,
                headless_json=args.headless_json,
                timeout_seconds=args.timeout,
                exit_without_confirmation=args.exit_without_confirmation,
            )
            if args.run
            else build_dry_run_report(payload)
        )
    except Exception as exc:
        error = {
            "cli_version": OPENHANDS_DISPATCH_CLI_VERSION,
            "status": "error",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        print(json.dumps(error, indent=2 if args.pretty else None, sort_keys=True))
        return 2

    output = report.model_dump(mode="json")
    output["cli_version"] = OPENHANDS_DISPATCH_CLI_VERSION
    print(json.dumps(output, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if report.status != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
