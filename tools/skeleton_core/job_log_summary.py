"""Deterministic summarizer for public-safe GitHub Actions job log excerpts."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

JobLogStatus = Literal["needs_fix", "no_failure_detected", "unknown_needs_review"]
FailureType = Literal[
    "black_formatting",
    "ruff_lint",
    "tests_failed",
    "validate_state_failed",
    "dependency_install_failed",
    "unknown",
]

MAX_EVIDENCE_LINES = 8


class JobLogSummary(BaseModel):
    """Deterministic diagnosis packet for a public-safe CI job log excerpt."""

    model_config = ConfigDict(extra="forbid")

    status: JobLogStatus
    detected_failure_type: FailureType
    failed_step: str | None = None
    summary: str
    evidence_lines: list[str] = Field(default_factory=list)
    affected_files: list[str] = Field(default_factory=list)
    next_action: str


def _clean_line(line: str) -> str:
    """Remove common GitHub Actions timestamp/noise prefixes from one log line."""
    line = line.lstrip("\ufeff").strip()
    line = re.sub(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s+", "", line)
    line = re.sub(r"\x1b\[[0-9;]*m", "", line)
    return line.strip()


def _clean_lines(log_text: str) -> list[str]:
    return [line for raw_line in log_text.splitlines() if (line := _clean_line(raw_line))]


def _short_evidence(lines: list[str]) -> list[str]:
    return lines[:MAX_EVIDENCE_LINES]


def _extract_failed_step(lines: list[str]) -> str | None:
    for line in lines:
        if "Run Black check" in line:
            return "Run Black check"
        if "Run Ruff" in line:
            return "Run Ruff"
        if "Run tests" in line or "python -m pytest" in line:
            return "Run tests"
        if "Validate Skeleton state" in line or "validate-state" in line:
            return "Validate Skeleton state"
        if "Install dependencies" in line or "make install" in line or "pip install" in line:
            return "Install dependencies"
    return None


def _black_summary(lines: list[str]) -> JobLogSummary | None:
    affected_files = []
    evidence = []
    for line in lines:
        if "would reformat" in line.casefold():
            evidence.append(line)
            affected_files.append(line.split("would reformat", 1)[1].strip())
        elif "files would be reformatted" in line.casefold() or "file would be reformatted" in line.casefold():
            evidence.append(line)

    if not evidence:
        return None

    count = len(affected_files) or 1
    return JobLogSummary(
        status="needs_fix",
        detected_failure_type="black_formatting",
        failed_step="Run Black check",
        summary=f"Black formatting failed for {count} file(s).",
        evidence_lines=_short_evidence(evidence),
        affected_files=affected_files,
        next_action="Run Black on the affected files, commit the formatting change, and wait for CI.",
    )


def _ruff_summary(lines: list[str]) -> JobLogSummary | None:
    evidence = [
        line
        for line in lines
        if re.match(r"^[A-Z][0-9]{3}\b", line)
        or "ruff failed" in line.casefold()
        or "Found " in line and "error" in line.casefold()
    ]
    if not evidence:
        return None

    affected_files = []
    for line in evidence:
        match = re.search(r"([\w./-]+\.py)(?::\d+)?", line)
        if match:
            affected_files.append(match.group(1))

    return JobLogSummary(
        status="needs_fix",
        detected_failure_type="ruff_lint",
        failed_step="Run Ruff",
        summary="Ruff linting failed.",
        evidence_lines=_short_evidence(evidence),
        affected_files=affected_files,
        next_action="Fix the Ruff lint errors, commit the change, and wait for CI.",
    )


def _pytest_summary(lines: list[str]) -> JobLogSummary | None:
    evidence = [
        line
        for line in lines
        if line.startswith("FAILED ")
        or "short test summary info" in line.casefold()
        or "assert " in line
        or "= FAILURES =" in line
    ]
    if not evidence:
        return None

    affected_files = []
    for line in evidence:
        match = re.search(r"([\w./-]*test[\w./-]*\.py)", line)
        if match:
            affected_files.append(match.group(1))

    return JobLogSummary(
        status="needs_fix",
        detected_failure_type="tests_failed",
        failed_step="Run tests",
        summary="Pytest reported failing tests.",
        evidence_lines=_short_evidence(evidence),
        affected_files=affected_files,
        next_action="Fix the failing tests or implementation, commit the change, and wait for CI.",
    )


def _validate_state_summary(lines: list[str]) -> JobLogSummary | None:
    has_validate_context = any("validate-state" in line or "Validate Skeleton state" in line for line in lines)
    evidence = [
        line
        for line in lines
        if "ok: false" in line.casefold()
        or "missing_files" in line
        or "missing_anchors" in line
        or "state validation" in line.casefold()
    ]
    if not has_validate_context or not evidence:
        return None

    return JobLogSummary(
        status="needs_fix",
        detected_failure_type="validate_state_failed",
        failed_step="Validate Skeleton state",
        summary="Skeleton state validation failed.",
        evidence_lines=_short_evidence(evidence),
        affected_files=[],
        next_action="Fix the missing Skeleton state files or anchors, then rerun validate-state.",
    )


def _dependency_summary(lines: list[str]) -> JobLogSummary | None:
    evidence = [
        line
        for line in lines
        if "ERROR: Could not" in line
        or "No matching distribution found" in line
        or "subprocess-exited-with-error" in line
        or "make: ***" in line
    ]
    if not evidence:
        return None

    return JobLogSummary(
        status="needs_fix",
        detected_failure_type="dependency_install_failed",
        failed_step="Install dependencies",
        summary="Dependency installation failed.",
        evidence_lines=_short_evidence(evidence),
        affected_files=[],
        next_action="Fix dependency metadata or installation commands, then rerun CI.",
    )


def summarize_job_log(log_text: str) -> JobLogSummary:
    """Summarize a public-safe GitHub Actions log excerpt into a diagnosis packet."""
    lines = _clean_lines(log_text)
    for detector in (
        _black_summary,
        _ruff_summary,
        _pytest_summary,
        _validate_state_summary,
        _dependency_summary,
    ):
        if summary := detector(lines):
            return summary

    failure_lines = [
        line
        for line in lines
        if "##[error]" in line or "Process completed with exit code" in line or "error" in line.casefold()
    ]
    if failure_lines:
        return JobLogSummary(
            status="unknown_needs_review",
            detected_failure_type="unknown",
            failed_step=_extract_failed_step(lines),
            summary="The log contains a failure, but no known deterministic pattern matched.",
            evidence_lines=_short_evidence(failure_lines),
            affected_files=[],
            next_action="Review the public-safe log excerpt manually and add a detector if repeated.",
        )

    return JobLogSummary(
        status="no_failure_detected",
        detected_failure_type="unknown",
        failed_step=None,
        summary="No actionable failure was detected in the provided log excerpt.",
        evidence_lines=[],
        affected_files=[],
        next_action="No fix needed from this log excerpt.",
    )
