"""Command line entrypoint for the minimal Skeleton core decision gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from tools.skeleton_core.checkpoint import render_checkpoint
from tools.skeleton_core.github_queue import normalize_issue, normalize_pr, summarize_queue
from tools.skeleton_core.handoff_pack import render_handoff_pack
from tools.skeleton_core.issue_dispatch import IssueDispatchInput, build_issue_dispatch_packet
from tools.skeleton_core.issue_runner_bridge import IssueRunnerInput, build_issue_runner_packet
from tools.skeleton_core.job_log_summary import summarize_job_log
from tools.skeleton_core.models import EvidencePolicy, TaskPacket
from tools.skeleton_core.pr_status import PRStatusInput, build_pr_status
from tools.skeleton_core.queue_classifier import classify_queue_items
from tools.skeleton_core.report import render_runner_report_from_trace
from tools.skeleton_core.router import route_task
from tools.skeleton_core.runner_command_pack import RunnerCommandInput, build_runner_command_pack
from tools.skeleton_core.state_validator import validate_state
from tools.skeleton_core.task_lifecycle import build_task_lifecycle_packet
from tools.skeleton_core.templates import render_runner_issue
from tools.skeleton_core.trace import TracePacket
from tools.skeleton_core.work_packet import render_work_packet

SUBCOMMANDS = {
    "checkpoint",
    "classify-queue",
    "decide",
    "handoff-pack",
    "issue-dispatch",
    "issue-runner-bridge",
    "job-log-summary",
    "pr-status",
    "queue-summary",
    "runner-command-pack",
    "runner-report-from-trace",
    "task-from-text",
    "task-lifecycle",
    "trace-packet",
    "validate-state",
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


def load_queue_items(input_path: Path) -> list[dict[str, Any]]:
    """Load raw offline public-safe queue items from JSON."""
    raw_items = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(raw_items, list):
        raise ValueError("queue input must be a JSON list")
    return raw_items


def load_pr_status_input(input_path: Path) -> PRStatusInput:
    """Load public-safe PR status input from JSON."""
    return PRStatusInput.model_validate_json(input_path.read_text(encoding="utf-8"))


def load_issue_runner_input(input_path: Path) -> IssueRunnerInput:
    """Load public-safe issue runner input from JSON."""
    return IssueRunnerInput.model_validate_json(input_path.read_text(encoding="utf-8"))


def load_issue_dispatch_input(input_path: Path) -> IssueDispatchInput:
    """Load public-safe issue dispatch input from JSON."""
    return IssueDispatchInput.model_validate_json(input_path.read_text(encoding="utf-8"))


def load_runner_command_input(input_path: Path) -> RunnerCommandInput:
    """Load public-safe runner command input from JSON."""
    return RunnerCommandInput.model_validate_json(input_path.read_text(encoding="utf-8"))


def build_queue_summary_payload(input_path: Path) -> dict[str, int]:
    """Build summary counts from an offline public-safe queue fixture."""
    items = []
    for raw in load_queue_items(input_path):
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


def _add_input_arg(parser: argparse.ArgumentParser, help_text: str) -> None:
    parser.add_argument("--input", required=True, type=Path, help=help_text)


def _add_issue_input_arg(parser: argparse.ArgumentParser) -> None:
    _add_input_arg(parser, "Path to public-safe GitHub issue JSON")


def _subcommand_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Skeleton Externalizer CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    checkpoint_parser = subparsers.add_parser(
        "checkpoint",
        help="Build a Skeleton checkpoint bundle",
    )
    _add_trace_args(checkpoint_parser)

    classify_queue_parser = subparsers.add_parser(
        "classify-queue",
        help="Classify offline queue JSON items",
    )
    _add_input_arg(classify_queue_parser, "Path to public-safe queue JSON")

    decide_parser = subparsers.add_parser("decide", help="Build a Skeleton task decision packet")
    _add_decide_args(decide_parser)

    handoff_pack_parser = subparsers.add_parser(
        "handoff-pack",
        help="Render a compact Skeleton handoff packet",
    )
    handoff_pack_parser.add_argument(
        "--root",
        default=Path("."),
        type=Path,
        help="Repository root to use",
    )

    issue_dispatch_parser = subparsers.add_parser(
        "issue-dispatch",
        help="Normalize a public-safe issue export for runner bridge",
    )
    _add_issue_input_arg(issue_dispatch_parser)
    issue_dispatch_parser.add_argument(
        "--run-bridge",
        action="store_true",
        help="Run normalized packet through issue-runner-bridge locally",
    )
    issue_dispatch_parser.add_argument(
        "--parent-queue",
        type=int,
        default=None,
        help="Optional parent queue issue number",
    )
    issue_dispatch_parser.add_argument(
        "--depends-on",
        default="",
        help="Optional comma-separated dependency issue numbers",
    )

    issue_runner_parser = subparsers.add_parser(
        "issue-runner-bridge",
        help="Build a GREEN/YELLOW runner packet from public-safe issue JSON",
    )
    _add_issue_input_arg(issue_runner_parser)

    job_log_parser = subparsers.add_parser(
        "job-log-summary",
        help="Summarize a public-safe GitHub Actions job log excerpt",
    )
    _add_input_arg(job_log_parser, "Path to public-safe job log text")

    pr_status_parser = subparsers.add_parser(
        "pr-status",
        help="Build a deterministic PR status packet from public-safe JSON",
    )
    _add_input_arg(pr_status_parser, "Path to public-safe PR status JSON")

    queue_parser = subparsers.add_parser(
        "queue-summary",
        help="Summarize an offline queue JSON file",
    )
    _add_input_arg(queue_parser, "Path to public-safe queue JSON")

    runner_command_parser = subparsers.add_parser(
        "runner-command-pack",
        help="Build a compact runner command from public-safe JSON",
    )
    _add_input_arg(runner_command_parser, "Path to public-safe runner command JSON")

    report_parser = subparsers.add_parser(
        "runner-report-from-trace",
        help="Render a short runner report from a TracePacket JSON file",
    )
    _add_input_arg(report_parser, "Path to public-safe TracePacket JSON")

    task_from_text_parser = subparsers.add_parser(
        "task-from-text",
        help="Build a Skeleton decision packet from free-form text",
    )
    _add_task_from_text_args(task_from_text_parser)

    task_lifecycle_parser = subparsers.add_parser(
        "task-lifecycle",
        help="Build a compact lifecycle packet from public-safe issue JSON",
    )
    _add_issue_input_arg(task_lifecycle_parser)

    trace_parser = subparsers.add_parser("trace-packet", help="Build a Skeleton trace packet")
    _add_trace_args(trace_parser)

    validate_state_parser = subparsers.add_parser(
        "validate-state",
        help="Validate Skeleton boot and current-state files",
    )
    validate_state_parser.add_argument(
        "--root",
        default=Path("."),
        type=Path,
        help="Repository root to validate",
    )

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


def _run_checkpoint(args: argparse.Namespace) -> int:
    try:
        packet = _trace_packet_from_args(args)
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(render_checkpoint(packet), flush=True)
    return 0


def _run_classify_queue(args: argparse.Namespace) -> int:
    result = classify_queue_items(load_queue_items(args.input))
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2), flush=True)
    return 0


def _run_handoff_pack(args: argparse.Namespace) -> int:
    print(render_handoff_pack(args.root), flush=True)
    return 0


def _run_issue_dispatch(args: argparse.Namespace) -> int:
    try:
        result = build_issue_dispatch_packet(
            load_issue_dispatch_input(args.input),
            run_bridge=args.run_bridge,
            parent_queue=args.parent_queue,
            depends_on=[int(value) for value in _split_csv(args.depends_on)],
        )
    except (ValidationError, ValueError) as exc:
        print(str(exc), flush=True)
        return 2

    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2), flush=True)
    return 0


def _run_issue_runner_bridge(args: argparse.Namespace) -> int:
    try:
        result = build_issue_runner_packet(load_issue_runner_input(args.input))
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2), flush=True)
    return 0


def _run_job_log_summary(args: argparse.Namespace) -> int:
    result = summarize_job_log(args.input.read_text(encoding="utf-8"))
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2), flush=True)
    return 0


def _run_pr_status(args: argparse.Namespace) -> int:
    try:
        result = build_pr_status(load_pr_status_input(args.input))
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2), flush=True)
    return 0


def _run_queue_summary(args: argparse.Namespace) -> int:
    print(
        json.dumps(build_queue_summary_payload(args.input), ensure_ascii=False, indent=2),
        flush=True,
    )
    return 0


def _run_runner_command_pack(args: argparse.Namespace) -> int:
    try:
        result = build_runner_command_pack(load_runner_command_input(args.input))
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2), flush=True)
    return 0


def _run_runner_report_from_trace(args: argparse.Namespace) -> int:
    try:
        packet = load_trace_packet(args.input)
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(render_runner_report_from_trace(packet), flush=True)
    return 0


def _run_task_lifecycle(args: argparse.Namespace) -> int:
    try:
        result = build_task_lifecycle_packet(load_issue_runner_input(args.input))
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2), flush=True)
    return 0


def _trace_packet_from_args(args: argparse.Namespace) -> TracePacket:
    return TracePacket(
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
        packet = _trace_packet_from_args(args)
    except ValidationError as exc:
        print(exc.json(), flush=True)
        return 2

    print(
        json.dumps(build_trace_packet_payload(packet), ensure_ascii=False, indent=2),
        flush=True,
    )
    return 0


def _run_validate_state(args: argparse.Namespace) -> int:
    result = validate_state(args.root)
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2), flush=True)
    return 0 if result.ok else 1


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
    if args.command == "checkpoint":
        return _run_checkpoint(args)
    if args.command == "classify-queue":
        return _run_classify_queue(args)
    if args.command == "handoff-pack":
        return _run_handoff_pack(args)
    if args.command == "issue-dispatch":
        return _run_issue_dispatch(args)
    if args.command == "issue-runner-bridge":
        return _run_issue_runner_bridge(args)
    if args.command == "job-log-summary":
        return _run_job_log_summary(args)
    if args.command == "pr-status":
        return _run_pr_status(args)
    if args.command == "queue-summary":
        return _run_queue_summary(args)
    if args.command == "runner-command-pack":
        return _run_runner_command_pack(args)
    if args.command == "runner-report-from-trace":
        return _run_runner_report_from_trace(args)
    if args.command == "task-from-text":
        return _run_task_from_text(args)
    if args.command == "task-lifecycle":
        return _run_task_lifecycle(args)
    if args.command == "trace-packet":
        return _run_trace_packet(args)
    if args.command == "validate-state":
        return _run_validate_state(args)
    if args.command == "work-packet":
        return _run_work_packet(args)
    return _run_decide(args)


if __name__ == "__main__":
    raise SystemExit(main())
