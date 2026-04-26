from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.actions import ActionApproval, ActionProposal, ActionResult, ActionRisk, ActionStatus


def test_action_proposal_construction_defaults():
    proposal = ActionProposal(
        proposal_id="proposal-1",
        action_type="calendar.create_event",
        title="Create planning hold",
        description="Create a tentative calendar hold for planning.",
    )

    assert proposal.risk is ActionRisk.medium
    assert proposal.status is ActionStatus.proposed
    assert proposal.parameters == {}
    assert proposal.metadata == {}
    assert proposal.requires_approval is True


def test_action_proposal_serializes_enums_and_payload():
    proposal = ActionProposal(
        proposal_id="proposal-2",
        action_type="email.draft",
        title="Draft reply",
        description="Draft a reply without sending it.",
        risk=ActionRisk.high,
        parameters={"thread_id": "thread-123"},
        metadata={"source": "unit-test"},
    )

    assert proposal.model_dump(mode="json") == {
        "proposal_id": "proposal-2",
        "action_type": "email.draft",
        "title": "Draft reply",
        "description": "Draft a reply without sending it.",
        "risk": "high",
        "status": "proposed",
        "parameters": {"thread_id": "thread-123"},
        "metadata": {"source": "unit-test"},
        "requires_approval": True,
    }


def test_action_approval_and_rejection_shapes():
    approval = ActionApproval.approve(
        "proposal-1",
        approved_by="user-1",
        reason="Looks correct",
    )
    rejection = ActionApproval.reject(
        "proposal-2",
        approved_by="user-1",
        reason="Too risky",
        metadata={"ticket": "INC-42"},
    )

    assert approval.model_dump(mode="json") == {
        "proposal_id": "proposal-1",
        "approved": True,
        "status": "approved",
        "approved_by": "user-1",
        "reason": "Looks correct",
        "metadata": {},
    }
    assert rejection.model_dump(mode="json") == {
        "proposal_id": "proposal-2",
        "approved": False,
        "status": "rejected",
        "approved_by": "user-1",
        "reason": "Too risky",
        "metadata": {"ticket": "INC-42"},
    }


def test_action_approval_normalizes_default_status():
    approval = ActionApproval(proposal_id="proposal-1", approved=True)
    rejection = ActionApproval(proposal_id="proposal-1", approved=False)

    assert approval.status is ActionStatus.approved
    assert rejection.status is ActionStatus.rejected


def test_action_approval_rejects_mismatched_status():
    with pytest.raises(ValidationError, match="approval status must match approved flag"):
        ActionApproval(
            proposal_id="proposal-1",
            approved=False,
            status=ActionStatus.approved,
        )


def test_action_result_defaults_and_serialization():
    result = ActionResult(
        proposal_id="proposal-1",
        output={"draft_id": "draft-123"},
        metadata={"provider": "mock"},
    )

    assert result.status is ActionStatus.completed
    assert result.model_dump(mode="json") == {
        "proposal_id": "proposal-1",
        "success": True,
        "status": "completed",
        "output": {"draft_id": "draft-123"},
        "error": None,
        "metadata": {"provider": "mock"},
    }


def test_action_result_failure_shape():
    result = ActionResult(
        proposal_id="proposal-1",
        success=False,
        error="Action was not executed.",
    )

    assert result.status is ActionStatus.failed
    assert result.model_dump(mode="json")["error"] == "Action was not executed."


def test_action_proposal_allows_only_proposed_status():
    with pytest.raises(ValidationError, match="action proposals must use proposed status"):
        ActionProposal(
            proposal_id="proposal-1",
            action_type="email.send",
            title="Send message",
            description="Send a message.",
            status=ActionStatus.approved,
        )
