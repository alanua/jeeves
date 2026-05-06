from tools.skeleton_core.issue_dispatch import (
    IssueDispatchInput,
    build_issue_dispatch_packet,
)


def test_issue_dispatch_accepts_green() -> None:
    result = build_issue_dispatch_packet(
        IssueDispatchInput(
            repository="alanua/bauclock",
            issue_number=22,
            title="[agent-task-green] BauClock overnight baseline validation",
            body="""## Validation required

```bash
python -m pytest
```""",
        )
    )

    assert result.status == "accepted"
    assert result.risk_level == "GREEN"
    assert result.runner_route == "RUNNER_GREEN"
    assert result.review_required is False
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.expected_commands == ["python -m pytest"]


def test_issue_dispatch_accepts_yellow_with_allowed_files_and_dependency() -> None:
    result = build_issue_dispatch_packet(
        IssueDispatchInput(
            repository="alanua/bauclock",
            issue_number=23,
            title="[agent-task-yellow] BauClock test-only hardening",
            body="""## Allowed files

```text
tests/test_calendar_service.py
tests/test_legal_hardening.py
```

## Validation required

```bash
python -m pytest tests/test_calendar_service.py tests/test_legal_hardening.py -q
python -m pytest
```""",
            comments=["depends_on #22"],
        ),
        depends_on=[21],
    )

    assert result.status == "accepted"
    assert result.risk_level == "YELLOW"
    assert result.runner_route == "RUNNER_YELLOW"
    assert result.review_required is True
    assert result.allowed_files == [
        "tests/test_calendar_service.py",
        "tests/test_legal_hardening.py",
    ]
    assert result.expected_commands == [
        "python -m pytest tests/test_calendar_service.py tests/test_legal_hardening.py -q",
        "python -m pytest",
    ]
    assert result.depends_on == [21, 22]


def test_issue_dispatch_run_bridge_reuses_bridge_blocking() -> None:
    result = build_issue_dispatch_packet(
        IssueDispatchInput(
            repository="alanua/bauclock",
            issue_number=999,
            title="[agent-task-red] Deploy production with token",
            body="Deploy to production and use API key from .env.",
        ),
        run_bridge=True,
    )

    assert result.status == "blocked"
    assert result.risk_level == "RED"
    assert result.runner_route == "BLOCKED"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.blockers
    assert any("deploy" in blocker for blocker in result.blockers)


def test_issue_dispatch_unknown_without_marker() -> None:
    result = build_issue_dispatch_packet(
        IssueDispatchInput(
            repository="alanua/bauclock",
            issue_number=24,
            title="Plain task",
            body="Do something public-safe.",
        )
    )

    assert result.status == "unknown_needs_review"
    assert result.risk_level == "UNKNOWN"
    assert result.runner_route == "BLOCKED"
    assert result.blockers == ["Unsupported risk level: UNKNOWN"]
