"""Command line entrypoint for the minimal Skeleton core decision gate."""

from __future__ import annotations

import argparse
import json
from typing import Any

from pydantic import ValidationError

from tools.skeleton_core.models import EvidencePolicy, TaskPacket
from tools.skeleton_core.router import route_task
from tools.skeleton_core.templates import render_runner_issue


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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Skeleton task decision packet.")
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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
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


if __name__ == "__main__":
    raise SystemExit(main())
