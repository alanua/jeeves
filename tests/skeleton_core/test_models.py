import pytest
from pydantic import ValidationError

from tools.skeleton_core.models import (
    EvidencePolicy,
    RouteDecision,
    RouteTarget,
    RiskLevel,
    TaskPacket,
)


def test_task_packet_defaults() -> None:
    packet = TaskPacket(title="Write docs", body="Write a markdown note")

    assert packet.project == "skeleton"
    assert packet.requested_by == "oleksii"
    assert packet.evidence_policy == EvidencePolicy.NONE


def test_task_packet_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TaskPacket(title="Test", body="Body", unexpected="value")


def test_task_packet_requires_non_empty_strings() -> None:
    with pytest.raises(ValidationError):
        TaskPacket(title="", body="Body")

    with pytest.raises(ValidationError):
        TaskPacket(title="Title", body="")


def test_route_decision_includes_evidence_policy_and_blocked_reason() -> None:
    decision = RouteDecision(
        risk_level=RiskLevel.RED,
        route_target=RouteTarget.BLOCKED_RED,
        evidence_policy=EvidencePolicy.PRIVATE_EVIDENCE_REQUIRES_REVIEW,
        blocked_reason="blocked",
    )

    assert decision.evidence_policy == EvidencePolicy.PRIVATE_EVIDENCE_REQUIRES_REVIEW
    assert decision.blocked_reason == "blocked"
