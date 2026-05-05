"""Public-safe trace packet model for Skeleton actions."""

from pydantic import BaseModel, ConfigDict, Field


class TracePacket(BaseModel):
    """Small machine-readable trace/checkpoint packet for Skeleton work."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(..., min_length=1)
    risk_level: str = Field(..., min_length=1)
    route_target: str = Field(..., min_length=1)
    result: str = Field(..., min_length=1)
    next_safe_step: str = Field(..., min_length=1)
    project: str = Field(default="skeleton", min_length=1)
    sources_read: list[str] = Field(default_factory=list)
    files_changed: list[str] = Field(default_factory=list)
    commands_run: list[str] = Field(default_factory=list)
    blocked_reason: str | None = None
    private_data_seen: bool = False
    runtime_code_touched: bool = False
    external_services_called: bool = False
