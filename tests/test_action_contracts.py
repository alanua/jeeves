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


@pytest.mark.parametrize(
    ("model_cls", "payload"),
    [
        (
            ActionProposal,
            {
                "proposal_id": "proposal-1",
                "action_type": "calendar.create_event",
                "title": "Create planning hold",
                "description": "Create a tentative calendar hold for planning.",
                "unexpected": "nope",
            },
        ),
        (
            ActionApproval,
            {
                "proposal_id": "proposal-1",
                "approved": True,
                "unexpected": "nope",
            },
        ),
        (
            ActionResult,
            {
                "proposal_id": "proposal-1",
                "unexpected": "nope",
            },
        ),
    ],
)
def test_action_contracts_reject_extra_fields(model_cls, payload):
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        model_cls(**payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("proposal_id", ""),
        ("action_type", ""),
        ("title", ""),
        ("description", ""),
    ],
)
def test_action_proposal_rejects_empty_required_strings(field, value):
    payload = {
        "proposal_id": "proposal-1",
        "action_type": "calendar.create_event",
        "title": "Create planning hold",
        "description": "Create a tentative calendar hold for planning.",
        field: value,
    }

    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        ActionProposal(**payload)


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


@pytest.mark.parametrize(
    ("approved", "status"),
    [
        (True, ActionStatus.approved),
        (False, ActionStatus.rejected),
    ],
)
def test_action_approval_accepts_explicit_matching_status(approved, status):
    approval = ActionApproval(
        proposal_id="proposal-1",
        approved=approved,
        status=status,
    )

    assert approval.approved is approved
    assert approval.status is status


def test_action_approval_status_can_be_omitted_by_callers():
    schema = ActionApproval.model_json_schema()

    assert "status" not in schema["required"]
    assert (
        ActionApproval(proposal_id="proposal-1", approved=True).model_dump(mode="json")["status"]
        == "approved"
    )
    assert (
        ActionApproval(proposal_id="proposal-1", approved=False).model_dump(mode="json")["status"]
        == "rejected"
    )


def test_action_approval_rejects_mismatched_status():
    with pytest.raises(ValidationError, match="approval status must match approved flag"):
        ActionApproval(
            proposal_id="proposal-1",
            approved=False,
            status=ActionStatus.approved,
        )


def test_action_approval_rejects_empty_proposal_id():
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        ActionApproval(proposal_id="", approved=True)


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


def test_action_result_status_can_be_omitted_by_callers():
    schema = ActionResult.model_json_schema()

    assert "status" not in schema["required"]
    assert ActionResult(proposal_id="proposal-1").model_dump(mode="json")["status"] == "completed"
    assert (
        ActionResult(proposal_id="proposal-1", success=False).model_dump(mode="json")["status"]
        == "failed"
    )


@pytest.mark.parametrize(
    ("success", "status"),
    [
        (True, ActionStatus.failed),
        (False, ActionStatus.completed),
    ],
)
def test_action_result_rejects_mismatched_status(success, status):
    with pytest.raises(ValidationError, match="result status must match success flag"):
        ActionResult(
            proposal_id="proposal-1",
            success=success,
            status=status,
        )


def test_action_result_rejects_empty_proposal_id():
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        ActionResult(proposal_id="")


def test_action_proposal_allows_only_proposed_status():
    with pytest.raises(ValidationError, match="action proposals must use proposed status"):
        ActionProposal(
            proposal_id="proposal-1",
            action_type="email.send",
            title="Send message",
            description="Send a message.",
            status=ActionStatus.approved,
        )


def test_ask_response_schema_does_not_expose_action_fields():
    from app.schemas.ask import AskResponse

    schema = AskResponse.model_json_schema()

    assert "proposed_actions" not in schema["properties"]
    assert "action_approvals" not in schema["properties"]
    assert "action_executions" not in schema["properties"]
