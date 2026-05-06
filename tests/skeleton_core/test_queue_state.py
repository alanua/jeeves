from tools.skeleton_core.queue_state import (
    QueueControllerIssue,
    QueueStateInput,
    QueueStateInputItem,
    build_queue_state,
)


def _controller(body: str = "Queue order: #22 then #23 then #24.") -> QueueControllerIssue:
    return QueueControllerIssue(
        repository="alanua/bauclock",
        issue_number=21,
        title="[night-queue] BauClock expanded safe overnight queue",
        body=body,
    )


def test_queue_state_initial_returns_green_baseline() -> None:
    result = build_queue_state(
        QueueStateInput(
            controller_issue=_controller(),
            items=[
                QueueStateInputItem(
                    issue_number=22,
                    title="[agent-task-green] BauClock overnight baseline validation",
                    risk_level="GREEN",
                ),
                QueueStateInputItem(
                    issue_number=23,
                    title="[agent-task-yellow] BauClock hardening",
                    risk_level="YELLOW",
                    depends_on=[22],
                ),
            ],
        )
    )

    assert result.next_runnable_issue == 22
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.summary["runnable"] == 1
    assert result.summary["blocked_by_dependency"] == 1
    assert result.items[0].state == "runnable"
    assert result.items[1].state == "blocked_by_dependency"
    assert result.items[1].blocked_by == [22]


def test_queue_state_after_green_returns_yellow() -> None:
    result = build_queue_state(
        QueueStateInput(
            controller_issue=_controller(),
            items=[
                QueueStateInputItem(
                    issue_number=22,
                    title="[agent-task-green] BauClock overnight baseline validation",
                    risk_level="GREEN",
                    comments=["Agent report: validation passed."],
                ),
                QueueStateInputItem(
                    issue_number=23,
                    title="[agent-task-yellow] BauClock hardening",
                    risk_level="YELLOW",
                    depends_on=[22],
                ),
            ],
        )
    )

    assert result.next_runnable_issue == 23
    assert result.summary["completed_or_reported"] == 1
    assert result.summary["runnable"] == 1
    assert result.items[0].state == "completed_or_reported"
    assert result.items[1].state == "runnable"


def test_queue_state_green_fallback_when_impl_blocked() -> None:
    result = build_queue_state(
        QueueStateInput(
            controller_issue=_controller("Queue order: #22 then #23 then #24 then #25."),
            items=[
                QueueStateInputItem(
                    issue_number=22,
                    title="[agent-task-green] BauClock baseline",
                    risk_level="GREEN",
                    comments=["Agent report: validation passed."],
                ),
                QueueStateInputItem(
                    issue_number=23,
                    title="[agent-task-yellow] BauClock hardening",
                    risk_level="YELLOW",
                    comments=["blocked until #99 external prerequisite"],
                ),
                QueueStateInputItem(
                    issue_number=24,
                    title="[agent-task-yellow] BauClock implementation guard",
                    risk_level="YELLOW",
                    depends_on=[23],
                ),
                QueueStateInputItem(
                    issue_number=25,
                    title="[agent-task-green] BauClock fallback audit",
                    risk_level="GREEN",
                ),
            ],
        )
    )

    assert result.next_runnable_issue == 25
    assert result.summary["runnable"] == 1
    assert result.summary["blocked_by_dependency"] == 2
    assert result.items[1].blocked_by == [99]
    assert result.items[3].state == "runnable"


def test_queue_state_blocks_unsafe_or_unknown() -> None:
    result = build_queue_state(
        QueueStateInput(
            controller_issue=_controller("Queue order: #30."),
            items=[
                QueueStateInputItem(
                    issue_number=30,
                    title="[agent-task-red] Deploy production with token",
                    risk_level="RED",
                    body="Deploy to production with API key from .env.",
                )
            ],
        )
    )

    assert result.next_runnable_issue is None
    assert result.summary["unsafe_or_unknown"] == 1
    assert result.items[0].state == "unsafe_or_unknown"
    assert result.items[0].blockers
