"""Safe runner environment preflight for Skeleton tasks."""

from __future__ import annotations

import importlib.util
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field

RunnerEnvCheckStatus = Literal[
    "ready_for_read_only_validation",
    "blocked_no_git",
    "blocked_no_python",
    "blocked_no_workdir",
    "blocked_dns_or_network",
    "blocked_clone_failed",
    "blocked_pytest_unavailable",
    "unsafe_or_policy_violation",
    "unknown_needs_review",
]
CheckState = Literal[
    "ok",
    "failed",
    "missing",
    "not_checked",
    "not_run",
    "not_run_or_failed",
]

REDACTED_REPO_URL = "<redacted-repo-url>"
DEFAULT_NEXT_SAFE_STEP = (
    "Run the task in another ready runner, or fix this runner before assigning work."
)
STATUS_NEXT_STEPS = {
    "ready_for_read_only_validation": "Continue to runner-command-pack for read-only validation work.",
    "blocked_no_git": "Install git or select another runner with git available.",
    "blocked_no_python": "Install Python or select another runner with Python available.",
    "blocked_no_workdir": "Use a writable disposable workdir before assigning work.",
    "blocked_dns_or_network": (
        "Run the task in another runner with GitHub network access, or fix DNS/network in this runner."
    ),
    "blocked_clone_failed": "Fix clone access or select another runner before assigning work.",
    "blocked_pytest_unavailable": "Install pytest or select another runner with project validation dependencies.",
    "unsafe_or_policy_violation": "Stop and review runner preflight safety blockers before continuing.",
    "unknown_needs_review": "Manual review required before assigning work to this runner.",
}


class RunnerEnvCheckInput(BaseModel):
    """Public-safe offline runner environment export."""

    model_config = ConfigDict(extra="ignore")

    repository: str = ""
    repo_url_checked: str = ""
    checks: dict[str, CheckState] = Field(default_factory=dict)
    commands_run: list[str] = Field(default_factory=list)
    blocked_reason: str = ""
    policy_violation: bool = False


class RunnerEnvCheckPacket(BaseModel):
    """Structured runner environment readiness packet."""

    model_config = ConfigDict(extra="forbid")

    status: RunnerEnvCheckStatus
    repository: str = ""
    repo_url_checked: str = ""
    checks: dict[str, CheckState] = Field(default_factory=dict)
    commands_run: list[str] = Field(default_factory=list)
    blocked_reason: str = ""
    safe_for_runner: bool = False
    merge_allowed: bool = False
    deploy_allowed: bool = False
    next_safe_step: str


def _redact_repo_url(repo_url: str) -> str:
    parsed = urlparse(repo_url)
    if parsed.scheme in {"http", "https"} and parsed.netloc and "@" in parsed.netloc:
        return REDACTED_REPO_URL
    if "token" in repo_url.casefold() or "password" in repo_url.casefold():
        return REDACTED_REPO_URL
    return repo_url


def _repo_url_has_credentials(repo_url: str) -> bool:
    parsed = urlparse(repo_url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc and "@" in parsed.netloc)


def _redacted_clone_command(workdir: str) -> str:
    return f"git clone --depth 1 {REDACTED_REPO_URL} {workdir}/repo"


def _infer_repository(repo_url: str) -> str:
    if not repo_url:
        return ""
    cleaned = repo_url.removesuffix(".git")
    if cleaned.startswith("git@github.com:"):
        return cleaned.split(":", 1)[1]
    parsed = urlparse(cleaned)
    if parsed.netloc.endswith("github.com"):
        return parsed.path.strip("/")
    return ""


def _status_from_checks(packet: RunnerEnvCheckInput) -> RunnerEnvCheckStatus:
    checks = packet.checks
    if packet.policy_violation or _repo_url_has_credentials(packet.repo_url_checked):
        return "unsafe_or_policy_violation"
    if checks.get("python") in {"missing", "failed"}:
        return "blocked_no_python"
    if checks.get("git") in {"missing", "failed"}:
        return "blocked_no_git"
    if checks.get("workdir") in {"missing", "failed"}:
        return "blocked_no_workdir"
    if checks.get("dns_github") == "failed":
        return "blocked_dns_or_network"
    if checks.get("clone") in {"failed", "not_run_or_failed"}:
        return "blocked_clone_failed"
    if checks.get("pytest") in {"missing", "failed"}:
        return "blocked_pytest_unavailable"
    required = [checks.get("python"), checks.get("git"), checks.get("workdir")]
    if all(value == "ok" for value in required):
        return "ready_for_read_only_validation"
    return "unknown_needs_review"


def _blocked_reason(status: RunnerEnvCheckStatus, packet: RunnerEnvCheckInput) -> str:
    if packet.blocked_reason:
        return packet.blocked_reason
    if status == "blocked_no_python":
        return "Python is not available in the runner."
    if status == "blocked_no_git":
        return "Git is not available in the runner."
    if status == "blocked_no_workdir":
        return "Workdir is not writable or not available."
    if status == "blocked_dns_or_network":
        return "GitHub DNS/network check failed."
    if status == "blocked_clone_failed":
        return "Repository shallow clone failed."
    if status == "blocked_pytest_unavailable":
        return "Pytest is not available in the runner."
    if status == "unsafe_or_policy_violation":
        return "Unsafe runner preflight input or credential-like repository URL."
    if status == "unknown_needs_review":
        return "Runner readiness could not be determined from the provided checks."
    return ""


def build_runner_env_check(packet: RunnerEnvCheckInput) -> RunnerEnvCheckPacket:
    """Build a runner preflight packet from public-safe offline input."""
    status = _status_from_checks(packet)
    safe = status == "ready_for_read_only_validation"
    repo_url = _redact_repo_url(packet.repo_url_checked)
    repository = packet.repository or _infer_repository(packet.repo_url_checked)

    return RunnerEnvCheckPacket(
        status=status,
        repository=repository,
        repo_url_checked=repo_url,
        checks=packet.checks,
        commands_run=packet.commands_run,
        blocked_reason=_blocked_reason(status, packet),
        safe_for_runner=safe,
        merge_allowed=False,
        deploy_allowed=False,
        next_safe_step=STATUS_NEXT_STEPS.get(status, DEFAULT_NEXT_SAFE_STEP),
    )


def build_runner_env_check_from_json(raw_json: str) -> RunnerEnvCheckPacket:
    """Validate local JSON text and build a runner environment packet."""
    return build_runner_env_check(RunnerEnvCheckInput.model_validate_json(raw_json))


def _check_workdir(workdir: Path) -> CheckState:
    try:
        workdir.mkdir(parents=True, exist_ok=True)
        probe = workdir / ".skeleton_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError:
        return "failed"
    return "ok"


def _run_version_command(command: list[str]) -> CheckState:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "failed"
    return "ok" if result.returncode == 0 else "failed"


def _check_dns_github() -> CheckState:
    try:
        socket.gethostbyname("github.com")
    except OSError:
        return "failed"
    return "ok"


def _check_clone(repo_url: str, workdir: Path) -> CheckState:
    target = workdir / "repo"
    if target.exists():
        shutil.rmtree(target)
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(target)],
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )
    except (OSError, subprocess.SubprocessError):
        return "failed"
    return "ok" if result.returncode == 0 else "failed"


def live_runner_env_check(
    *,
    repo_url: str,
    workdir: Path,
    allow_network_check: bool = False,
    skip_clone_check: bool = False,
) -> RunnerEnvCheckPacket:
    """Run a bounded local preflight. Network/clone only run with explicit opt-in."""
    checks: dict[str, CheckState] = {}
    commands_run: list[str] = []

    if _repo_url_has_credentials(repo_url):
        return build_runner_env_check(
            RunnerEnvCheckInput(
                repo_url_checked=repo_url,
                policy_violation=True,
                blocked_reason="Repository URL contains credentials and was redacted.",
            )
        )

    if shutil.which(sys.executable):
        checks["python"] = _run_version_command([sys.executable, "--version"])
    else:
        checks["python"] = "missing"
    commands_run.append("python --version")

    if shutil.which("git"):
        checks["git"] = _run_version_command(["git", "--version"])
    else:
        checks["git"] = "missing"
    commands_run.append("git --version")

    checks["workdir"] = _check_workdir(workdir)
    checks["pytest"] = "ok" if importlib.util.find_spec("pytest") else "missing"

    if allow_network_check:
        checks["dns_github"] = _check_dns_github()
        if not skip_clone_check and checks["dns_github"] == "ok" and checks["git"] == "ok":
            checks["clone"] = _check_clone(repo_url, workdir)
            commands_run.append(_redacted_clone_command(str(workdir)))
        else:
            checks["clone"] = "not_run"
    else:
        checks["dns_github"] = "not_checked"
        checks["clone"] = "not_checked"

    return build_runner_env_check(
        RunnerEnvCheckInput(
            repository=_infer_repository(repo_url),
            repo_url_checked=repo_url,
            checks=checks,
            commands_run=commands_run,
        )
    )
