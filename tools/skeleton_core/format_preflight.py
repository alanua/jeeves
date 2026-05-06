"""Local/offline formatter preflight for Skeleton changes."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FormatPreflightStatus = Literal[
    "format_ready",
    "needs_black_format",
    "blocked_missing_black",
    "unknown_needs_review",
]
BlackAvailability = Literal["ok", "missing", "not_checked"]


class FormatPreflightInput(BaseModel):
    """Public-safe formatter preflight export."""

    model_config = ConfigDict(extra="ignore")

    formatter: str = "black"
    checked_paths: list[str] = Field(default_factory=list)
    files_needing_format: list[str] = Field(default_factory=list)
    black_available: BlackAvailability = "not_checked"
    blocked_reason: str = ""


class FormatPreflightPacket(BaseModel):
    """Structured formatter readiness packet."""

    model_config = ConfigDict(extra="forbid")

    status: FormatPreflightStatus
    formatter: str = "black"
    checked_paths: list[str] = Field(default_factory=list)
    files_needing_format: list[str] = Field(default_factory=list)
    commands_recommended: list[str] = Field(default_factory=list)
    safe_to_continue_ci: bool = False
    blocked_reason: str = ""
    merge_allowed: bool = False
    deploy_allowed: bool = False
    next_safe_step: str


def _clean_items(items: list[str]) -> list[str]:
    return sorted({item.strip() for item in items if item.strip()})


def _commands(status: FormatPreflightStatus, checked_paths: list[str]) -> list[str]:
    paths = " ".join(checked_paths) if checked_paths else "tools/skeleton_core tests/skeleton_core"
    if status == "needs_black_format":
        return [f"python -m black {paths}", f"python -m black --check {paths}"]
    if status == "blocked_missing_black":
        return ["pip install -e .[dev]", f"python -m black --check {paths}"]
    if status == "format_ready":
        return [f"python -m black --check {paths}"]
    return []


def _next_step(status: FormatPreflightStatus) -> str:
    if status == "format_ready":
        return "Continue to CI or PR review."
    if status == "needs_black_format":
        return "Run Black on listed files before pushing or re-running CI."
    if status == "blocked_missing_black":
        return "Install dev dependencies with Black before formatting checks."
    return "Manual review required before continuing."


def _blocked_reason(status: FormatPreflightStatus, packet: FormatPreflightInput) -> str:
    if packet.blocked_reason:
        return packet.blocked_reason
    if status == "needs_black_format":
        return "Black would reformat one or more checked files."
    if status == "blocked_missing_black":
        return "Black is not available in this environment."
    if status == "unknown_needs_review":
        return "Formatter readiness could not be determined."
    return ""


def build_format_preflight(packet: FormatPreflightInput) -> FormatPreflightPacket:
    """Build a formatter preflight packet from public-safe input."""
    checked_paths = _clean_items(packet.checked_paths)
    files_needing_format = _clean_items(packet.files_needing_format)

    if packet.black_available == "missing":
        status: FormatPreflightStatus = "blocked_missing_black"
    elif files_needing_format:
        status = "needs_black_format"
    elif checked_paths and packet.black_available in {"ok", "not_checked"}:
        status = "format_ready"
    else:
        status = "unknown_needs_review"

    return FormatPreflightPacket(
        status=status,
        formatter=packet.formatter or "black",
        checked_paths=checked_paths,
        files_needing_format=files_needing_format,
        commands_recommended=_commands(status, checked_paths),
        safe_to_continue_ci=status == "format_ready",
        blocked_reason=_blocked_reason(status, packet),
        merge_allowed=False,
        deploy_allowed=False,
        next_safe_step=_next_step(status),
    )


def build_format_preflight_from_json(raw_json: str) -> FormatPreflightPacket:
    """Validate local JSON text and build a formatter preflight packet."""
    return build_format_preflight(FormatPreflightInput.model_validate_json(raw_json))


def _parse_black_files(output: str) -> list[str]:
    files = []
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("would reformat "):
            files.append(stripped.removeprefix("would reformat ").strip())
    return _clean_items(files)


def live_format_preflight(paths: list[Path]) -> FormatPreflightPacket:
    """Run Black in check-only mode. This does not modify files."""
    checked_paths = [str(path) for path in paths]
    if importlib.util.find_spec("black") is None:
        return build_format_preflight(
            FormatPreflightInput(
                checked_paths=checked_paths,
                black_available="missing",
            )
        )

    result = subprocess.run(
        [sys.executable, "-m", "black", "--check", *checked_paths],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    files = _parse_black_files(result.stdout + "\n" + result.stderr)
    return build_format_preflight(
        FormatPreflightInput(
            checked_paths=checked_paths,
            files_needing_format=files,
            black_available="ok",
        )
    )
