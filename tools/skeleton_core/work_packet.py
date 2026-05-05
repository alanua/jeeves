"""Public-safe work packet rendering for Skeleton tasks."""

from tools.skeleton_core.models import RouteDecision, RouteTarget, TaskPacket
from tools.skeleton_core.templates import render_runner_issue

WORK_PACKET_FIELD_ORDER = (
    "title",
    "project",
    "risk_level",
    "route_target",
    "evidence_policy",
    "blocked_reason",
    "goal",
    "runner_issue_body",
    "next_safe_step",
)


def next_safe_step_for_decision(decision: RouteDecision) -> str:
    """Return the next safe human-facing step for a routed task."""
    if decision.route_target == RouteTarget.BLOCKED_RED:
        return "wait for Oleksii"
    return "create GitHub issue"


def render_work_packet(packet: TaskPacket, decision: RouteDecision) -> str:
    """Render a standard public-safe work packet for a routed task."""
    return "\n".join(
        [
            "title",
            packet.title,
            "project",
            packet.project,
            "risk_level",
            decision.risk_level.value,
            "route_target",
            decision.route_target.value,
            "evidence_policy",
            decision.evidence_policy.value,
            "blocked_reason",
            decision.blocked_reason or "none",
            "goal",
            packet.body,
            "runner_issue_body",
            render_runner_issue(packet, decision),
            "next_safe_step",
            next_safe_step_for_decision(decision),
        ]
    )
