"""Command line entrypoint for the minimal Skeleton core decision gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from tools.skeleton_core.github_queue import normalize_issue, normalize_pr, summarize_queue
from tools.skeleton_core.models import EvidencePolicy, TaskPacket
from tools.skeleton_core.report import render_runner_report_from_trace
from tools.skeleton_core.router import route_task
from tools.skeleton_core.templates import render_runner_issue
from tools.skeleton_core.trace import TracePacket
from tools.skeleton_core.work_packet import render_work_packet

SUBCOMMANDS = {
    "decide",
    "queue-summary",
    "runner-report-from-trace",
    "task-from-text",
    "trace-packet",
    "work-packet",
}
MAX_AUTO_TITLE_LENGTH = 80


def build_decision_payload(packet: TaskPacket) -> dict[str, Any]:
    """Build the JSON-serializable decision payload for a task packet."""
    decision = route_task(packet)
    return {
        "task": packet.model_dump(mode="json"),
        "risk_level": decision.risk_level.value,
        "route_target": decision.route_target.value,
        "evidence_policy": decision.evidence_policy.value,
        "blocked_reason": decision.blocked_reason,
        "runner_issue_body": render_runner_issue(packet, decision),
    }


def build_queue_summary_payload(input_path: Path) -> dict[str, int]:
    """Build summary counts from an offline public-safe queue fixture."""
    raw_items = json.loads(input_path.read_text(encoding="utf-8"))
    items = []
    for raw in raw_items:
        kind = str(raw.get("kind", "issue")).casefold()
        if kind == "pr":
            items.append(normalize_pr(raw))
        else:
            items.append(normalize_issue(raw))
    return summarize_queue(items)


def build_trace_packet_payload(packet: TracePacket) -> dict[str, Any]:
    """Build the JSON-serializable trace packet payload."""
    return packet.model_dump(mode="json")


def load_trace_packet(input_path: Path) -> TracePacket:
    """Load and validate a TracePacket from a JSON file."""
    return TracePacket.model_validate_json(input_path.read_text(encoding="utf-8"))


def title_from_text(text: str, max_length: int = MAX_AUTO_TITLE_LENGTH) -> str:
    """Create a short deterministic title from free-form task text."""
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 1].rstrip() + "…"


def build_task_from_text_packet(
    *,
    text: str,
    title: str | None,
    project: str,
    requested_by: str,
    evidence_policy: EvidencePolicy,
) -> TaskPacket:
    """Build a TaskPacket from free-form text without model calls."""
    return TaskPacket(
        title=title or title_from_text(text),
        body=text,
        project=project,
        requested_by=requested_by,
        evidence_policy=evidence_policy,
    )


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _add_decide_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--title", required=True, help="Task title")
    parser.add_argument("--body", required=True, help="Task body")
    parser.add_argument("--project", default="skeleton", help="Project name")
    parser.add_argument("--requested-by", default="oleksii", help="Requester name")
    parser.add_argument(
        "--evidence-policy",
        choices=[policy.value for policy in EvidencePolicy],
        default=EvidencePolicy.NONE.value,
        help="Allowed evidence policy to record without calling external services",
    )


def _add_task_from_text_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", required=True, help="Free-form task text")
    parser.add_argument("--title", default=None, help="Optional title override")
    parser.add_argument("--project", default="skeleton", help="Project name")
    parser.add_argument("--requested-by", default="oleksii", help="Requester name")
    parser.add_argument(
        "--evidence-policy",
        choices=[policy.value for policy in EvidencePolicy],
        default=EvidencePolicy.NONE.value,
        help="Allowed evidence policy to record without calling external services",
    )


def _add_trace_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--task-id", required=True, help="Trace task id")
    parser.add_argument("--project", default="skeleton", help="Project name")
    parser.add_argument("--risk-level", required=True, help="Risk level")
    parser.add_argument("--route-target", required=True, help="Route target")
    parser.add_argument("--result", required=True, help="Result status")
    parser.add_argument("--next-safe-step", required=True, help="Next safe step")
    parser.add_argument(
        "--sources-read",
        default="",
        help="Comma-separated public-safe sources read",
    )
    parser.add_argument("--files-changed", default="", help="Comma-separated files changed")
    parser.add_argument("--commands-run", default="", help="Comma-separated commands run")
    parser.add_argument("--blocked-reason", default=None, help="Optional blocked reason")
    parser.add_argument(
        "--private-data-seen",
        action="store_true",
        help="Mark private data as seen",
    )
    parser.add_argument(
        "--runtime-code-touched",
        action="store_true",
        help="Mark runtime code as touched",
    )
    parser.add_argument(
        "--external-services-called",
        action="store_true",
        help="Mark external services as called",
    )


def _subcommand_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Skeleton Externalizer v0 CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    decide_parser = subparsers.add_parser("decide", help="Build a Skeleton task decision packet")
    _add_decide_args(decide_parser)

    queue_parser = subparsers.add_parser(
        "queue-summary",
        help="Summarize an offline queue JSON file",
    )
    queue_parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to public-safe queue JSON",
    )

    report_parser = subparsers.add_parser(
        "runner-report-from-trace",
        help="Render a short runner report from a TracePacket JSON file",
    )
    report_parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to public-safe TracePacket JSON",
    )

    task_from_text_parser = subparsers.add_parser(
        "task-from-text",
        help="Build a Skeleton decision packet from free-form text",
    )
    _add_task_from_text_args(task_from_text_parser)

    trace_parser = subparsers.add_parser("trace-packet", help="Build a Skeleton trace packet")
    _add_trace_args(trace_parser)

    work_packet_parser = subparsers.add_parser(
        "work-packet",
        help="Render a public-safe work packet from free-form task text",
    )
    _add_task_from_text_args(work_packet_parser)
    return parser


def _legacy_decide_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a Skeleton task decision packet.")
    _add_decide_args(parser)
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    effective_argv = sys.argv[1:] if argv is None else argv
    if effective_argv and effective_argv[0] in SUBCOMMANDS:
        return _subcommand_parser().parse_args(effective_argv)

    args = _legacy_decide_parser().parse_args(effective_argv)
    args.command = "decide"
    return args


def _run_decide(args: argparse.Namespace) -> int:
    try:
        packet = TaskPacket(
            title=args.title,
            body=args.body,
            project=args.project,
            requested_by=args.requested_by,
            evidence_policy=EvidencePolicy(args.evidence_policy),
        )
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(json.dumps(build_decision_payload(packet), ensure_ascii=False, indent=2), flush=True)
    return 0


def _run_queue_summary(args: argparse.Namespace) -> int:
    print(
        json.dumps(build_queue_summary_payload(args.input), ensure_ascii=False, indent=2),
        flush=True,
    )
    return 0


def _run_runner_report_from_trace(args: argparse.Namespace) -> int:
    try:
        packet = load_trace_packet(args.input)
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(render_runner_report_from_trace(packet), flush=True)
    return 0


def _run_task_from_text(args: argparse.Namespace) -> int:
    try:
        packet = build_task_from_text_packet(
            text=args.text,
            title=args.title,
            project=args.project,
            requested_by=args.requested_by,
            evidence_policy=EvidencePolicy(args.evidence_policy),
        )
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(json.dumps(build_decision_payload(packet), ensure_ascii=False, indent=2), flush=True)
    return 0


def _run_trace_packet(args: argparse.Namespace) -> int:
    try:
        packet = TracePacket(
            task_id=args.task_id,
            project=args.project,
            risk_level=args.risk_level,
            route_target=args.route_target,
            result=args.result,
            next_safe_step=args.next_safe_step,
            sources_read=_split_csv(args.sources_read),
            files_changed=_split_csv(args.files_changed),
            commands_run=_split_csv(args.commands_run),
            blocked_reason=args.blocked_reason,
            private_data_seen=args.private_data_seen,
            runtime_code_touched=args.runtime_code_touched,
            external_services_called=args.external_services_called,
        )
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(
        json.dumps(build_trace_packet_payload(packet), ensure_ascii=False, indent=2),
        flush=True,
    )
    return 0


def _run_work_packet(args: argparse.Namespace) -> int:
    try:
        packet = build_task_from_text_packet(
            text=args.text,
            title=args.title,
            project=args.project,
            requested_by=args.requested_by,
            evidence_policy=EvidencePolicy(args.evidence_policy),
        )
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(render_work_packet(packet, route_task(packet)), flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "queue-summary":
        return _run_queue_summary(args)
    if args.command == "runner-report-from-trace":
        return _run_runner_report_from_trace(args)
    if args.command == "task-from-text":
        return _run_task_from_text(args)
    if args.command == "trace-packet":
        return _run_trace_packet(args)
    if args.command == "work-packet":
        return _run_work_packet(args)
    return _run_decide(args)


if __name__ == "__main__":
    raise SystemExit(main())
