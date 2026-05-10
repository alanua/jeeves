from __future__ import annotations

import pytest
from pydantic import ValidationError

from tools.skeleton_core.dual_brain_task_packet import (
    DualBrainNode,
    DualBrainReviewPacket,
    DualBrainTaskPacket,
    DualBrainTracePacket,
    PrivacyLevel,
)


def test_minimal_dual_brain_task_packet() -> None:
    packet = DualBrainTaskPacket(
        task_id="task-1",
        project="СК",
        title="Audit bridge",
        goal="Audit one bridge packet.",
    )

    assert packet.schema_version == "dual_brain_task_packet.v1"
    assert packet.privacy_level == PrivacyLevel.PUBLIC_SAFE
    assert packet.executor_allowed is False


def test_dual_brain_task_packet_blocks_extra_fields() -> None:
    with pytest.raises(ValidationError):
        DualBrainTaskPacket(
            task_id="task-1",
            project="СК",
            title="Audit bridge",
            goal="Audit one bridge packet.",
            unexpected=True,
        )


def test_dual_brain_task_packet_bounds_model_rounds() -> None:
    with pytest.raises(ValidationError):
        DualBrainTaskPacket(
            task_id="task-1",
            project="СК",
            title="Audit bridge",
            goal="Audit one bridge packet.",
            max_model_rounds=10,
        )


def test_review_packet_defaults_do_not_execute_or_persist() -> None:
    review = DualBrainReviewPacket(
        task_id="task-1",
        reviewer_node=DualBrainNode.GEMINI_AUDITOR,
        decision="accept",
        summary="Looks safe.",
        next_safe_step="Return to ChatGPT.",
    )

    assert review.execution_allowed is False
    assert review.persistence_allowed is False
    assert review.canon_claim is False
    assert review.commands == []


def test_trace_packet_requires_hashes() -> None:
    with pytest.raises(ValidationError):
        DualBrainTracePacket(
            task_id="task-1",
            node_id=DualBrainNode.GEMINI_AUDITOR,
            decision_code="accept",
            privacy_level=PrivacyLevel.PUBLIC_SAFE,
            timestamp_utc="2026-05-10T00:00:00Z",
        )
