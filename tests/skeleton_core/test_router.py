from tools.skeleton_core.models import EvidencePolicy, RiskLevel, RouteTarget, TaskPacket
from tools.skeleton_core.router import route_task


def test_green_routes_to_runner_green() -> None:
    decision = route_task(TaskPacket(title="Sort queue", body="Classify items"))

    assert decision.risk_level == RiskLevel.GREEN
    assert decision.route_target == RouteTarget.RUNNER_GREEN
    assert decision.blocked_reason is None


def test_yellow_routes_to_runner_yellow() -> None:
    decision = route_task(TaskPacket(title="Write docs", body="Add README note"))

    assert decision.risk_level == RiskLevel.YELLOW
    assert decision.route_target == RouteTarget.RUNNER_YELLOW


def test_orange_routes_to_runner_orange() -> None:
    decision = route_task(TaskPacket(title="Implement CLI", body="Add package tests"))

    assert decision.risk_level == RiskLevel.ORANGE
    assert decision.route_target == RouteTarget.RUNNER_ORANGE


def test_red_routes_to_blocked_red_with_reason() -> None:
    decision = route_task(TaskPacket(title="Deploy with token", body="Use production .env"))

    assert decision.risk_level == RiskLevel.RED
    assert decision.route_target == RouteTarget.BLOCKED_RED
    assert decision.blocked_reason is not None
    assert "non-executable" in decision.blocked_reason


def test_evidence_policy_is_preserved() -> None:
    packet = TaskPacket(
        title="Review note",
        body="Write docs",
        evidence_policy=EvidencePolicy.GEMINI_EVIDENCE_ALLOWED,
    )

    decision = route_task(packet)

    assert decision.evidence_policy == EvidencePolicy.GEMINI_EVIDENCE_ALLOWED
