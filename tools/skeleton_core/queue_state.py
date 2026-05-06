"""Local offline queue-state selector for Skeleton controller queues."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

QueueItemState = Literal[
    "runnable",
    "blocked_by_dependency",
    "completed_or_reported",
    "needs_review",
    "unsafe_or_unknown",
]
QueueRiskLevel = Literal["GREEN", "YELLOW", "ORANGE", "RED", "UNKNOWN"]

UNSAFE_PATTERNS = {
    "merge": r"\bmerge\b|\bauto-merge\b",
    "deploy": r"\bdeploy\b|\bdeployment\b|\brelease\b",
    "production": r"production db|production database|\bprod db\b",
    "server": r"server ssh|\bssh\b",
    "secret": r"\.env|\bsecret\b|\bsecrets\b|\btoken\b|\btokens\b|api key|apikey|credential|password",
    "network": r"live network|live executor|external service|external api|http[s]?://",
}


class QueueControllerIssue(BaseModel):
    """Public-safe controller issue metadata."""

    model_config = ConfigDict(extra="ignore")

    repository: str
    issue_number: int
    title: str
    body: str = ""


class QueueStateInputItem(BaseModel):
    """Public-safe task item in a controller queue export."""

    model_config = ConfigDict(extra="ignore")

    issue_number: int
    title: str
    risk_level: QueueRiskLevel = "UNKNOWN"
    state: str = "open"
    body: str = ""
    comments: list[str] = Field(default_factory=list)
    prs: list[dict[str, object]] = Field(default_factory=list)
    depends_on: list[int] = Field(default_factory=list)


class QueueStateInput(BaseModel):
    """Public-safe controller queue export."""

    model_config = ConfigDict(extra="ignore")

    controller_issue: QueueControllerIssue
    items: list[QueueStateInputItem]


class QueueStateItem(BaseModel):
    """Deterministic state for one queue item."""

    model_config = ConfigDict(extra="forbid")

    issue_number: int
    risk_level: QueueRiskLevel
    state: QueueItemState
    blocked_by: list[int] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    recommended_command: str


class QueueStateResult(BaseModel):
    """Queue-state output."""

    model_config = ConfigDict(extra="forbid")

    repository: str
    controller_issue: int
    next_runnable_issue: int | None
    next_runnable_reason: str
    summary: dict[QueueItemState, int]
    items: list[QueueStateItem]
    merge_allowed: bool = False
    deploy_allowed: bool = False


def _combined_text(item: QueueStateInputItem) -> str:
    return "\n".join([item.title, item.body, *item.comments])


def _completed_or_reported(item: QueueStateInputItem) -> bool:
    if item.state.casefold() in {"closed", "done", "completed"}:
        return True
    text = _combined_text(item).casefold()
    if any(marker in text for marker in ("agent report", "completed", "validation passed", "ci success")):
        return True
    for pr in item.prs:
        merged = pr.get("merged")
        state = str(pr.get("state", "")).casefold()
        if merged is True or state in {"merged", "closed"}:
            return True
    return False


def _needs_review(item: QueueStateInputItem) -> bool:
    text = _combined_text(item).casefold()
    if "needs review" in text or "ready for review" in text:
        return True
    for pr in item.prs:
        if str(pr.get("state", "")).casefold() == "open":
            return True
    return False


def _unsafe_blockers(item: QueueStateInputItem) -> list[str]:
    text = _combined_text(item)
    blockers = []
    for name, pattern in UNSAFE_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            blockers.append(f"Unsafe text detected: {name}")
    if item.risk_level not in {"GREEN", "YELLOW"}:
        blockers.append(f"Unsupported risk level: {item.risk_level}")
    return sorted(set(blockers))


def _inferred_dependencies(item: QueueStateInputItem) -> list[int]:
    dependencies = set(item.depends_on)
    text = _combined_text(item)
    for pattern in (
        r"do not execute\s*#?\d+\s*until\s*#?(\d+)",
        r"blocked until\s*#?(\d+)",
        r"after\s*#(\d+)",
        r"depends[_ -]?on\s*#?(\d+)",
    ):
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            dependencies.add(int(match.group(1)))
    return sorted(dependencies)


def _recommended_command(item: QueueStateInputItem, state: QueueItemState) -> str:
    if state == "runnable" and item.risk_level == "GREEN":
        return "issue-dispatch then task-lifecycle then GREEN read-only validation"
    if state == "runnable" and item.risk_level == "YELLOW":
        return "issue-dispatch --run-bridge then runner-command-pack for YELLOW draft PR"
    if state == "blocked_by_dependency":
        return "wait for dependency completion/report"
    if state == "completed_or_reported":
        return "no action"
    if state == "needs_review":
        return "review report or PR before continuing"
    return "manual review required"


def _controller_order(queue: QueueStateInput) -> list[int]:
    body = queue.controller_issue.body
    ordered = []
    for match in re.finditer(r"#(\d+)", body):
        value = int(match.group(1))
        if value != queue.controller_issue.issue_number and value not in ordered:
            ordered.append(value)
    item_numbers = [item.issue_number for item in queue.items]
    return [number for number in ordered if number in item_numbers] + [
        number for number in item_numbers if number not in ordered
    ]


def build_queue_state(queue: QueueStateInput, *, project: str | None = None) -> QueueStateResult:
    """Build a deterministic local/offline queue-state result."""
    completed = {item.issue_number for item in queue.items if _completed_or_reported(item)}
    order = _controller_order(queue)
    item_by_number = {item.issue_number: item for item in queue.items}
    states: list[QueueStateItem] = []

    for issue_number in order:
        item = item_by_number[issue_number]
        blockers = _unsafe_blockers(item)
        dependencies = _inferred_dependencies(item)
        open_dependencies = [dependency for dependency in dependencies if dependency not in completed]

        if _completed_or_reported(item):
            state: QueueItemState = "completed_or_reported"
            blocked_by: list[int] = []
        elif _needs_review(item):
            state = "needs_review"
            blocked_by = []
        elif blockers:
            state = "unsafe_or_unknown"
            blocked_by = []
        elif open_dependencies:
            state = "blocked_by_dependency"
            blocked_by = open_dependencies
        else:
            state = "runnable"
            blocked_by = []

        states.append(
            QueueStateItem(
                issue_number=item.issue_number,
                risk_level=item.risk_level,
                state=state,
                blocked_by=blocked_by,
                blockers=blockers,
                recommended_command=_recommended_command(item, state),
            )
        )

    next_item = next((item for item in states if item.state == "runnable"), None)
    summary: dict[QueueItemState, int] = {
        "runnable": 0,
        "blocked_by_dependency": 0,
        "completed_or_reported": 0,
        "needs_review": 0,
        "unsafe_or_unknown": 0,
    }
    for item in states:
        summary[item.state] += 1

    project_note = f" for {project}" if project else ""
    if next_item is None:
        reason = f"no runnable queue item{project_note}; review blocked/unknown items"
    else:
        reason = f"first safe runnable item{project_note} in controller order"

    return QueueStateResult(
        repository=queue.controller_issue.repository,
        controller_issue=queue.controller_issue.issue_number,
        next_runnable_issue=next_item.issue_number if next_item else None,
        next_runnable_reason=reason,
        summary=summary,
        items=states,
        merge_allowed=False,
        deploy_allowed=False,
    )


def build_queue_state_from_json(raw_json: str, *, project: str | None = None) -> QueueStateResult:
    """Validate local JSON text and build a queue-state result."""
    return build_queue_state(QueueStateInput.model_validate_json(raw_json), project=project)
