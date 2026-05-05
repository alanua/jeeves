"""Route Skeleton task packets to the safest available target."""

from tools.skeleton_core.classifier import classify_task
from tools.skeleton_core.models import RouteDecision, RouteTarget, RiskLevel, TaskPacket

BLOCKED_RED_REASON = (
    "RED task detected by Skeleton tripwire. It is non-executable until Oleksii gives "
    "explicit narrow approval in a later task."
)


def route_task(packet: TaskPacket) -> RouteDecision:
    """Create a route decision for a Skeleton task packet."""
    risk_level = classify_task(packet)

    if risk_level == RiskLevel.RED:
        return RouteDecision(
            risk_level=risk_level,
            route_target=RouteTarget.BLOCKED_RED,
            evidence_policy=packet.evidence_policy,
            blocked_reason=BLOCKED_RED_REASON,
        )
    if risk_level == RiskLevel.ORANGE:
        target = RouteTarget.RUNNER_ORANGE
    elif risk_level == RiskLevel.YELLOW:
        target = RouteTarget.RUNNER_YELLOW
    else:
        target = RouteTarget.RUNNER_GREEN

    return RouteDecision(
        risk_level=risk_level,
        route_target=target,
        evidence_policy=packet.evidence_policy,
        blocked_reason=None,
    )
