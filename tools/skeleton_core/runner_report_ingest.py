"""Local offline runner report ingester for Skeleton queue state."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RunnerReportStatus = Literal[
    "green_report",
    "blocked_report",
    "failed_validation",
    "needs_review",
    "unknown_needs_review",
    "unsafe_or_policy_violation",
]

UNSAFE_PATTERNS = {
    "private_data": (
        r"private[_ -]?data[_ -]?seen\s*[:=]\s*true|private data was used|private data seen"
    ),
    "runtime_code": (r"runtime[_ -]?code[_ -]?touched\s*[:=]\s*true|runtime code touched"),
    "external_service": (
        r"external[_ -]?services?[_ -]?called\s*[:=]\s*true|external service called|external api called"
    ),
    "secret": (
        r"secret(s)?\s+(used|touched|read|exposed)|used secret|read secret|api key from|token from"
    ),
    "env": r"read\s+\.env|used\s+\.env|\.env\s+(read|used|touched)",
    "server": r"server ssh used|ssh to server|production server",
    "production_db": r"production db access|production database access|prod db access",
}


class RunnerReportIngestPacket(BaseModel):
    """Normalized public-safe runner report status."""

    model_config = ConfigDict(extra="forbid")

    status: RunnerReportStatus
    issue_number: int | None = None
    branch: str | None = None
    head_sha: str | None = None
    commands_run: list[str] = Field(default_factory=list)
    test_result: str | None = None
    failure_summary: str | None = None
    open_prs: list[str] = Field(default_factory=list)
    repo_status: str | None = None
    changed_files: list[str] = Field(default_factory=list)
    private_data_seen: bool = False
    runtime_code_touched: bool = False
    external_services_called: bool = False
    blocked_reason: str | None = None
    needs_review: bool = False
    unsafe_flags: list[str] = Field(default_factory=list)
    merge_allowed: bool = False
    deploy_allowed: bool = False
    next_queue_signal: str


def _field_value(text: str, *names: str) -> str | None:
    for name in names:
        pattern = rf"^\s*{re.escape(name)}\s*[:=]\s*(.+?)\s*$"
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip().strip("`")
    return None


def _field_bool(text: str, *names: str) -> bool:
    value = _field_value(text, *names)
    if value is None:
        return False
    return value.casefold() in {"true", "yes", "1", "y"}


def _issue_number(text: str) -> int | None:
    value = _field_value(text, "issue_number", "issue")
    if value:
        match = re.search(r"#?(\d+)", value)
        if match:
            return int(match.group(1))
    match = re.search(
        r"(?:issue|task)\s+#(\d+)|#(\d+)\s+report",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return int(next(group for group in match.groups() if group))
    return None


def _section_items(text: str, *headings: str) -> list[str]:
    lines = text.splitlines()
    items: list[str] = []
    collecting = False
    for line in lines:
        stripped = line.strip()
        heading = stripped.strip("#:").strip().casefold()
        if any(heading.startswith(candidate.casefold()) for candidate in headings):
            collecting = True
            continue
        if collecting and (stripped.startswith("##") or re.match(r"^[A-Za-z_ -]+:\s*$", stripped)):
            break
        if collecting and stripped.startswith("```"):
            continue
        if collecting and stripped:
            items.append(stripped.lstrip("-*").strip().strip("`"))
    return items


def _csv_or_section(text: str, field: str, *headings: str) -> list[str]:
    value = _field_value(text, field)
    if value:
        return [item.strip() for item in value.split(",") if item.strip()]
    return _section_items(text, *headings)


def _unsafe_flags(text: str) -> list[str]:
    flags = []
    for name, pattern in UNSAFE_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            flags.append(name)
    return sorted(set(flags))


def _blocked_reason(text: str) -> str | None:
    value = _field_value(text, "blocked_reason", "blocked reason")
    if value:
        return value
    match = re.search(r"blocked(?: report)?\s*[:\-]\s*(.+)", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _failure_summary(text: str) -> str | None:
    value = _field_value(text, "failure_summary", "failure summary")
    if value:
        return value
    match = re.search(r"(?:failed|failure|error)\s*[:\-]\s*(.+)", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _test_result(text: str) -> str | None:
    value = _field_value(text, "test_result", "tests", "validation")
    if value:
        lowered = value.casefold()
        if any(marker in lowered for marker in ("pass", "success", "green")):
            return "passed"
        if any(marker in lowered for marker in ("fail", "error", "red")):
            return "failed"
        return value
    lowered_text = text.casefold()
    if re.search(r"\b\d+\s+passed\b", lowered_text) or "tests passed" in lowered_text:
        return "passed"
    if "tests failed" in lowered_text or "validation failed" in lowered_text:
        return "failed"
    return None


def _repo_status(text: str) -> str | None:
    value = _field_value(text, "repo_status", "repo status", "working tree")
    if value:
        lowered = value.casefold()
        if "clean" in lowered:
            return "clean"
        if "dirty" in lowered or "changed" in lowered:
            return "dirty"
        return value
    if "repo clean" in text.casefold() or "working tree clean" in text.casefold():
        return "clean"
    return None


def _open_prs(text: str) -> list[str]:
    explicit = _csv_or_section(text, "open_prs", "open prs", "open pull requests")
    if explicit:
        return explicit
    return sorted(set(re.findall(r"PR\s*#?\d+|pull request\s*#?\d+", text, flags=re.IGNORECASE)))


def _status(
    *,
    text: str,
    test_result: str | None,
    repo_status: str | None,
    blocked_reason: str | None,
    open_prs: list[str],
    unsafe_flags: list[str],
) -> tuple[RunnerReportStatus, bool, str]:
    lowered = text.casefold()
    if unsafe_flags:
        return "unsafe_or_policy_violation", True, "blocked_policy_violation"
    if blocked_reason or "blocked report" in lowered:
        return "blocked_report", True, "blocked"
    if test_result == "failed" or "validation failed" in lowered:
        return "failed_validation", True, "validation_failed"
    if (
        open_prs
        or "needs review" in lowered
        or "ready for review" in lowered
        or "draft pr" in lowered
    ):
        return "needs_review", True, "review_required"
    if test_result == "passed" and repo_status == "clean":
        return "green_report", False, "dependency_satisfied"
    return "unknown_needs_review", True, "manual_review_required"


def ingest_runner_report(text: str) -> RunnerReportIngestPacket:
    """Parse a public-safe runner report/comment excerpt into structured status."""
    unsafe_flags = _unsafe_flags(text)
    private_data_seen = (
        _field_bool(text, "private_data_seen", "private data seen")
        or "private_data" in unsafe_flags
    )
    runtime_code_touched = (
        _field_bool(text, "runtime_code_touched", "runtime code touched")
        or "runtime_code" in unsafe_flags
    )
    external_services_called = (
        _field_bool(text, "external_services_called", "external services called")
        or "external_service" in unsafe_flags
    )
    test_result = _test_result(text)
    repo_status = _repo_status(text)
    blocked_reason = _blocked_reason(text)
    open_prs = _open_prs(text)
    status, needs_review, next_signal = _status(
        text=text,
        test_result=test_result,
        repo_status=repo_status,
        blocked_reason=blocked_reason,
        open_prs=open_prs,
        unsafe_flags=unsafe_flags,
    )

    return RunnerReportIngestPacket(
        status=status,
        issue_number=_issue_number(text),
        branch=_field_value(text, "branch"),
        head_sha=_field_value(text, "head_sha", "head sha"),
        commands_run=_csv_or_section(text, "commands_run", "commands run", "commands"),
        test_result=test_result,
        failure_summary=_failure_summary(text),
        open_prs=open_prs,
        repo_status=repo_status,
        changed_files=_csv_or_section(text, "changed_files", "changed files"),
        private_data_seen=private_data_seen,
        runtime_code_touched=runtime_code_touched,
        external_services_called=external_services_called,
        blocked_reason=blocked_reason,
        needs_review=needs_review,
        unsafe_flags=unsafe_flags,
        merge_allowed=False,
        deploy_allowed=False,
        next_queue_signal=next_signal,
    )


def ingest_runner_report_file_content(raw_text: str) -> RunnerReportIngestPacket:
    """Alias for CLI readability."""
    return ingest_runner_report(raw_text)
