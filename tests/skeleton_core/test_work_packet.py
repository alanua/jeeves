from tools.skeleton_core.models import (
    EvidencePolicy,
    RiskLevel,
    RouteDecision,
    RouteTarget,
    TaskPacket,
)
from tools.skeleton_core.work_packet import (
    WORK_PACKET_FIELD_ORDER,
    next_safe_step_for_decision,
    render_work_packet,
)


def test_work_packet_field_order_is_stable() -> None:
    assert WORK_PACKET_FIELD_ORDER == (
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


def test_render_work_packet_for_runnable_task() -> None:
    packet = TaskPacket(
        title="Write docs note",
        body="Write docs note for Skeleton queue usage",
    )
    decision = RouteDecision(
        risk_level=RiskLevel.YELLOW,
        route_target=RouteTarget.RUNNER_YELLOW,
        evidence_policy=EvidencePolicy.NONE,
    )

    work_packet = render_work_packet(packet, decision)

    assert work_packet.startswith("title\nWrite docs note\nproject\nskeleton")
    assert "risk_level\nYELLOW" in work_packet
    assert "route_target\nRUNNER_YELLOW" in work_packet
    assert "evidence_policy\nNONE" in work_packet
    assert "blocked_reason\nnone" in work_packet
    assert "goal\nWrite docs note for Skeleton queue usage" in work_packet
    assert "runner_issue_body\n# YELLOW — Write docs note" in work_packet
    assert "required runner report shape" in work_packet.casefold()
    assert work_packet.endswith("next_safe_step\ncreate GitHub issue")


def test_render_work_packet_for_blocked_task() -> None:
    packet = TaskPacket(
        title="Use production token from .env",
        body="Use production token from .env",
    )
    decision = RouteDecision(
        risk_level=RiskLevel.RED,
        route_target=RouteTarget.BLOCKED_RED,
        evidence_policy=EvidencePolicy.NONE,
        blocked_reason="Contains secret or credential access request.",
    )

    work_packet = render_work_packet(packet, decision)

    assert "risk_level\nRED" in work_packet
    assert "route_target\nBLOCKED_RED" in work_packet
    assert "blocked_reason\nContains secret or credential access request." in work_packet
    assert "not executable" in work_packet
    assert work_packet.endswith("next_safe_step\nwait for Oleksii")


def test_next_safe_step_for_decision() -> None:
    assert (
        next_safe_step_for_decision(
            RouteDecision(
                risk_level=RiskLevel.YELLOW,
                route_target=RouteTarget.RUNNER_YELLOW,
                evidence_policy=EvidencePolicy.NONE,
            )
        )
        == "create GitHub issue"
    )
    assert (
        next_safe_step_for_decision(
            RouteDecision(
                risk_level=RiskLevel.RED,
                route_target=RouteTarget.BLOCKED_RED,
                evidence_policy=EvidencePolicy.NONE,
                blocked_reason="blocked",
            )
        )
        == "wait for Oleksii"
    )
