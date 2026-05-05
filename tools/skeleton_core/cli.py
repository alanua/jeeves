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
from tools.skeleton_core.router import route_task
from tools.skeleton_core.templates import render_runner_issue

SUBCOMMANDS = {"decide", "queue-summary"}


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


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "queue-summary":
        return _run_queue_summary(args)
    return _run_decide(args)


if __name__ == "__main__":
    raise SystemExit(main())
