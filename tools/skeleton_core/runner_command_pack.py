"""Local offline runner command generator for public-safe task packets."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RunnerCommandStatus = Literal["ready", "blocked", "unknown_needs_review"]

UNSAFE_PATTERNS = {
    "secret": r"\bsecret\b|\bsecrets\b|\btoken\b|\btokens\b|\bcredential\b|\bcredentials\b|api key|apikey|password|\.env",
    "server": r"\bserver ssh\b|\bssh\b|production db|production database|\bprod db\b",
    "network": r"\bnetwork\b|\bexternal service\b|\bexternal api\b|\blive mode\b|http[s]?://",
    "merge": r"\bmerge this\b|\bmerge pr\b|\bmerge pull request\b|\bauto-merge\b",
    "deploy": r"\bdeploy to\b|\bdeployment\b|\bdeploy production\b|\brelease to\b",
}


class RunnerCommandInput(BaseModel):
    """Public-safe task/lifecycle packet accepted by runner-command-pack."""

    model_config = ConfigDict(extra="ignore")

    repository: str | None = None
    issue_number: int | None = None
    title: str | None = None
    risk_level: str | None = None
    runner_route: str | None = None
    review_required: bool | None = None
    allowed_files: list[str] = Field(default_factory=list)
    expected_commands: list[str] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    merge_allowed: bool = False
    deploy_allowed: bool = False
    body: str = ""


class RunnerCommandPack(BaseModel):
    """Deterministic local/offline runner command output."""

    model_config = ConfigDict(extra="forbid")

    status: RunnerCommandStatus
    issue_number: int | None
    command_text: str
    merge_allowed: bool = False
    deploy_allowed: bool = False
    blockers: list[str] = Field(default_factory=list)


def _project_from_repository(repository: str | None) -> str:
    if not repository:
        return "Skeleton"
    name = repository.rsplit("/", 1)[-1]
    if name.casefold() == "bauclock":
        return "BauClock"
    if name.casefold() == "jeeves":
        return "Skeleton"
    return name


def _normalized_risk(packet: RunnerCommandInput) -> str:
    return (packet.risk_level or "UNKNOWN").strip().upper()


def _unsafe_blockers(packet: RunnerCommandInput) -> list[str]:
    text_parts = [
        packet.repository or "",
        packet.title or "",
        packet.body,
        "\n".join(packet.allowed_files),
        "\n".join(packet.expected_commands),
    ]
    text = "\n".join(text_parts)
    blockers: list[str] = []
    for name, pattern in UNSAFE_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            blockers.append(f"Unsafe text detected: {name}")
    return sorted(set(blockers))


def _missing_field_blockers(packet: RunnerCommandInput) -> list[str]:
    missing = []
    if not packet.repository:
        missing.append("Missing required field: repository")
    if packet.issue_number is None:
        missing.append("Missing required field: issue_number")
    if not packet.title:
        missing.append("Missing required field: title")
    if not packet.risk_level:
        missing.append("Missing required field: risk_level")
    return missing


def _blocked_result(packet: RunnerCommandInput, blockers: list[str]) -> RunnerCommandPack:
    issue_label = f"issue #{packet.issue_number}" if packet.issue_number is not None else "packet"
    reason = "; ".join(blockers) if blockers else "not safe for runner command"
    return RunnerCommandPack(
        status="blocked",
        issue_number=packet.issue_number,
        command_text=f"BLOCKED: {issue_label} is not safe for runner command. Reason: {reason}.",
        merge_allowed=False,
        deploy_allowed=False,
        blockers=blockers,
    )


def _format_expected_commands(commands: list[str]) -> str:
    if not commands:
        return "Run the validation commands from the issue."
    return " Expected commands: " + " ; ".join(commands) + "."


def _format_allowed_files(files: list[str]) -> str:
    if not files:
        return ""
    return " Change only allowed files: " + ", ".join(files) + "."


def _green_command(packet: RunnerCommandInput) -> str:
    project = _project_from_repository(packet.repository)
    issue_number = packet.issue_number or 0
    return (
        f"КОД {project}: execute issue #{issue_number} as GREEN read-only validation. "
        "Use latest main. Do not change files."
        f"{_format_expected_commands(packet.expected_commands)} "
        "Post report with branch, head SHA, commands, result, failures, open PRs, and clean/dirty state. "
        "Do not merge or deploy."
    )


def _yellow_command(packet: RunnerCommandInput) -> str:
    project = _project_from_repository(packet.repository)
    issue_number = packet.issue_number or 0
    return (
        f"КОД {project}: execute issue #{issue_number} as YELLOW test-only task. "
        "Create a fresh branch from latest main."
        f"{_format_allowed_files(packet.allowed_files)}"
        f"{_format_expected_commands(packet.expected_commands)} "
        "Open a draft PR or blocked report. "
        "Do not change production code unless stopped and reported first. "
        "Do not merge or deploy."
    )


def build_runner_command_pack(packet: RunnerCommandInput) -> RunnerCommandPack:
    """Build one compact safe runner command from a local public-safe packet."""
    blockers = []
    blockers.extend(_missing_field_blockers(packet))
    blockers.extend(_unsafe_blockers(packet))
    blockers.extend(packet.blocked_by)
    blockers.extend(packet.blockers)

    if packet.merge_allowed:
        blockers.append("merge_allowed must be false")
    if packet.deploy_allowed:
        blockers.append("deploy_allowed must be false")

    risk = _normalized_risk(packet)
    if risk not in {"GREEN", "YELLOW"}:
        blockers.append(f"Unsupported risk level: {risk}")
    if risk == "YELLOW" and not packet.allowed_files:
        blockers.append("YELLOW task must include allowed_files")

    if blockers:
        return _blocked_result(packet, sorted(set(blockers)))

    command = _green_command(packet) if risk == "GREEN" else _yellow_command(packet)
    return RunnerCommandPack(
        status="ready",
        issue_number=packet.issue_number,
        command_text=command,
        merge_allowed=False,
        deploy_allowed=False,
        blockers=[],
    )


def build_runner_command_pack_from_json(raw_json: str) -> RunnerCommandPack:
    """Validate local JSON text and build a runner command pack."""
    return build_runner_command_pack(RunnerCommandInput.model_validate_json(raw_json))
