from __future__ import annotations

from enum import Enum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ActionRisk(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ActionStatus(str, Enum):
    proposed = "proposed"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"
    failed = "failed"


class ActionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str = Field(..., min_length=1)
    action_type: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    risk: ActionRisk = ActionRisk.medium
    status: ActionStatus = ActionStatus.proposed
    parameters: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = True

    @model_validator(mode="after")
    def proposal_must_remain_proposed(self) -> Self:
        if self.status is not ActionStatus.proposed:
            raise ValueError("action proposals must use proposed status")
        return self


class ActionApproval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str = Field(..., min_length=1)
    approved: bool
    status: ActionStatus
    approved_by: str | None = None
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def approve(
        cls,
        proposal_id: str,
        *,
        approved_by: str | None = None,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Self:
        return cls(
            proposal_id=proposal_id,
            approved=True,
            approved_by=approved_by,
            reason=reason,
            metadata=metadata or {},
        )

    @classmethod
    def reject(
        cls,
        proposal_id: str,
        *,
        approved_by: str | None = None,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Self:
        return cls(
            proposal_id=proposal_id,
            approved=False,
            approved_by=approved_by,
            reason=reason,
            metadata=metadata or {},
        )

    @model_validator(mode="before")
    @classmethod
    def add_default_status(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "approved" not in data or data.get("status") is not None:
            return data

        status = ActionStatus.approved if data["approved"] else ActionStatus.rejected
        return {**data, "status": status}

    @model_validator(mode="after")
    def status_must_match_approval(self) -> Self:
        expected_status = ActionStatus.approved if self.approved else ActionStatus.rejected
        if self.status is not expected_status:
            raise ValueError("approval status must match approved flag")
        return self


class ActionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str = Field(..., min_length=1)
    success: bool = True
    status: ActionStatus
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def add_default_status(cls, data: Any) -> Any:
        if not isinstance(data, dict) or data.get("status") is not None:
            return data

        status = ActionStatus.completed if data.get("success", True) else ActionStatus.failed
        return {**data, "status": status}

    @model_validator(mode="after")
    def status_must_match_success(self) -> Self:
        expected_status = ActionStatus.completed if self.success else ActionStatus.failed
        if self.status is not expected_status:
            raise ValueError("result status must match success flag")
        return self
