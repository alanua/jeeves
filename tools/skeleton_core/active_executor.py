"""Active bounded executor.

Sprint 7 phase 1:
- still fail-closed
- only executes commands from a strict allowlist
- only acts on already audited issues
- logs every real action to Skeleton diary
- records failure state in current_state.json via memory_service
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.bounded_execution_packet import (
    ExecutionAction,
    ExecutionActionType,
    ExecutionDecision,
    ExecutionMode,
    ExecutionPacket,
    ExecutionSource,
)
from tools.skeleton_core.dry_run_execution_route import (
    ACCEPT_STATUSES,
    GitHubIssueExport,
    _gh_json,
    _run,
    find_verified_audit_comment,
)
from tools.skeleton_core.memory_service import (
    append_to_skeleton_diary,
    create_system_snapshot,
)

ExecutorMode = Literal["plan", "real"]

SAFE_COMMAND_PREFIXES = (
    ("python", "-m", "pytest"),
    ("python", "-m", "ruff", "check"),
    ("python", "-m", "black", "--check"),
    ("python", "-m", "tools.skeleton_core.cli", "validate-state"),
    ("git", "status", "--short"),
    ("git", "diff", "--stat"),
    ("git", "add"),
    ("git", "commit", "-m"),
    ("git", "push", "-u", "origin"),
    ("gh", "pr", "create"),
    ("gh", "issue", "edit"),
    ("gh", "api"),
)

FORBIDDEN_COMMAND_TOKENS = {
    "rm",
    "rmdir",
    "mv",
    "cp",
    "chmod",
    "chown",
    "sudo",
    "su",
    "ssh",
    "scp",
    "rsync",
    "curl",
    "wget",
    "docker",
    "systemctl",
    "journalctl",
    "kill",
    "pkill",
    "reboot",
    "shutdown",
    "dd",
    "mkfs",
}

FORBIDDEN_SUBSTRINGS = {
    "rm -rf",
    "--force",
    "push -f",
    "push --force",
    "git push -f",
    "git push --force",
    ">",
    ">>",
    "|",
    ";",
    "&&",
    "||",
    "`",
    "$(",
}


class CommandResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: str
    returncode: int
    stdout_tail: str = ""
    stderr_tail: str = ""


class ActiveExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issue_number: int
    issue_url: str = ""
    mode: ExecutorMode
    decision: ExecutionDecision
    status: Literal["planned", "real_complete", "blocked", "failed"]
    packet: ExecutionPacket
    command_results: list[CommandResult] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
    posted_comment_url: str = ""
    labels_added: list[str] = Field(default_factory=list)
    labels_removed: list[str] = Field(default_factory=list)
    next_safe_step: str = ""


def parse_command(command: str) -> list[str]:
    return shlex.split(command)


def command_is_allowed(command: str, allowed_commands: list[str] | None = None) -> tuple[bool, str]:
    stripped = command.strip()
    if not stripped:
        return False, "empty_command"

    for forbidden in FORBIDDEN_SUBSTRINGS:
        if forbidden in stripped:
            return False, f"forbidden_substring:{forbidden}"

    parts = parse_command(stripped)
    if not parts:
        return False, "empty_command_after_parse"

    if parts[0] in FORBIDDEN_COMMAND_TOKENS:
        return False, f"forbidden_command_token:{parts[0]}"

    if parts[:3] == ["git", "push", "--force"] or parts[:3] == ["git", "push", "-f"]:
        return False, "git_force_push_blocked"

    allowed_exact = set(allowed_commands or [])
    if stripped in allowed_exact:
        return True, ""

    for prefix in SAFE_COMMAND_PREFIXES:
        if tuple(parts[: len(prefix)]) == prefix:
            return True, ""

    return False, "command_not_whitelisted"


def fetch_execution_candidates(repo: str, *, limit: int) -> list[GitHubIssueExport]:
    raw_items = _gh_json(
        [
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--label",
            "agent:task",
            "--label",
            "agent:audited",
            "--json",
            "number,title,url,state,labels",
            "--limit",
            str(limit),
        ]
    )

    issues: list[GitHubIssueExport] = []
    for item in raw_items:
        number = int(item["number"])
        full = _gh_json(
            [
                "issue",
                "view",
                str(number),
                "--repo",
                repo,
                "--json",
                "number,title,body,labels,comments,url,state",
            ]
        )
        issue = GitHubIssueExport.model_validate(full)
        labels = {label.name for label in issue.labels}
        if "agent:audited" in labels and "agent:executed" not in labels:
            issues.append(issue)

    return issues


def build_active_execution_packet(issue: GitHubIssueExport, *, real_run: bool) -> ExecutionPacket:
    verified, audit_status, audit_comment_url, audit_body = find_verified_audit_comment(issue)
    labels = sorted(label.name for label in issue.labels)

    return ExecutionPacket(
        issue_number=issue.number,
        issue_url=issue.url,
        title=issue.title,
        mode=ExecutionMode.REAL if real_run else ExecutionMode.DRY_RUN,
        real_run=real_run,
        allowed_commands=[
            "python -m pytest -q",
            "python -m ruff check tools/skeleton_core tests/skeleton_core",
            "python -m tools.skeleton_core.cli validate-state",
            "git status --short",
            "git diff --stat",
        ],
        target_branch=f"skeleton-exec-issue-{issue.number}",
        trigger_labels=labels,
        audit_verified=verified,
        audit_status=audit_status,
        audit_comment_url=audit_comment_url,
        audit_summary=audit_body[:1000],
        objective=issue.body[:2000],
        planned_actions=[
            ExecutionAction(
                action_id="validate-pytest",
                action_type=ExecutionActionType.NOOP,
                description="Run test suite validation only if explicitly authorized by packet.",
                dry_run_only=not real_run,
                command="python -m pytest -q" if real_run else "",
                writes_files=False,
                network_access=False,
            ),
            ExecutionAction(
                action_id="validate-ruff",
                action_type=ExecutionActionType.NOOP,
                description="Run ruff validation only if explicitly authorized by packet.",
                dry_run_only=not real_run,
                command=(
                    "python -m ruff check tools/skeleton_core tests/skeleton_core"
                    if real_run
                    else ""
                ),
                writes_files=False,
                network_access=False,
            ),
            ExecutionAction(
                action_id="validate-state",
                action_type=ExecutionActionType.NOOP,
                description="Run Skeleton state validation only if explicitly authorized by packet.",
                dry_run_only=not real_run,
                command=("python -m tools.skeleton_core.cli validate-state" if real_run else ""),
                writes_files=False,
                network_access=False,
            ),
        ],
        sources=[
            ExecutionSource(
                source_type="github_issue",
                reference=issue.url,
                verified=True,
                notes="Active executor source issue.",
            ),
            ExecutionSource(
                source_type="audit_report",
                reference=audit_comment_url,
                verified=verified,
                notes="Accepted Gemini audit report comment.",
            ),
        ],
        executor_allowed=real_run,
        file_writes_allowed=False,
        pr_creation_allowed=False,
        merge_allowed=False,
        deploy_allowed=False,
        canon_write_allowed=False,
        next_safe_step=(
            "Run whitelisted validation commands only."
            if real_run
            else "Plan-only active execution packet created."
        ),
    )


def validate_active_packet(packet: ExecutionPacket) -> list[str]:
    reasons: list[str] = []

    if not packet.audit_verified:
        reasons.append("missing_verified_accept_audit_comment")
    if packet.audit_status not in ACCEPT_STATUSES:
        reasons.append("audit_status_not_accepted")

    if packet.real_run and not packet.executor_allowed:
        reasons.append("real_run_requires_executor_allowed")

    if packet.file_writes_allowed:
        reasons.append("file_writes_not_allowed_in_sprint_7_phase_1")
    if packet.pr_creation_allowed:
        reasons.append("pr_creation_not_allowed_in_sprint_7_phase_1")
    if packet.merge_allowed:
        reasons.append("merge_not_allowed")
    if packet.deploy_allowed:
        reasons.append("deploy_not_allowed")
    if packet.canon_write_allowed:
        reasons.append("canon_write_not_allowed")

    for action in packet.planned_actions:
        if action.writes_files:
            reasons.append(f"action_{action.action_id}_writes_files")
        if action.action_type not in {
            ExecutionActionType.NOOP,
            ExecutionActionType.COMMENT_ONLY,
            ExecutionActionType.LABEL_TRANSITION_ONLY,
        }:
            reasons.append(f"action_{action.action_id}_unsupported_action_type")
        if action.command:
            allowed, reason = command_is_allowed(
                action.command,
                packet.allowed_commands,
            )
            if not allowed:
                reasons.append(f"action_{action.action_id}_{reason}")

    return sorted(set(reasons))


def run_command(command: str, *, cwd: Path) -> CommandResult:
    parts = parse_command(command)
    completed = subprocess.run(
        parts,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    return CommandResult(
        command=command,
        returncode=completed.returncode,
        stdout_tail=completed.stdout[-2000:],
        stderr_tail=completed.stderr[-2000:],
    )


def _post_comment(repo: str, issue_number: int, body: str) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix=f"active-executor-{issue_number}-comment-",
        delete=False,
        encoding="utf-8",
    ) as handle:
        payload_path = Path(handle.name)
        handle.write(json.dumps({"body": body}, ensure_ascii=False))

    try:
        completed = _run(
            [
                "gh",
                "api",
                "--method",
                "POST",
                f"repos/{repo}/issues/{issue_number}/comments",
                "--input",
                str(payload_path),
                "--jq",
                ".html_url",
            ]
        )
        return completed.stdout.strip()
    finally:
        with suppress(FileNotFoundError):
            payload_path.unlink()


def _edit_labels(
    repo: str,
    issue_number: int,
    *,
    add: list[str] | None = None,
    remove: list[str] | None = None,
) -> None:
    args = ["gh", "issue", "edit", str(issue_number), "--repo", repo]
    if add:
        args.extend(["--add-label", ",".join(add)])
    if remove:
        args.extend(["--remove-label", ",".join(remove)])
    _run(args)


def _comment_body(result: ActiveExecutionResult) -> str:
    payload = json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2)
    return (
        "Active Executor Report\n\n"
        f"Issue: #{result.issue_number}\n"
        f"Mode: `{result.mode}`\n"
        f"Decision: `{result.decision}`\n"
        f"Status: `{result.status}`\n"
        f"Blocked reasons: `{result.blocked_reasons}`\n\n"
        "Safety:\n"
        "- no file writes allowed\n"
        "- no PR creation allowed\n"
        "- no merge allowed\n"
        "- no deploy allowed\n"
        "- no canon write allowed\n\n"
        "```json\n"
        f"{payload[-6000:]}\n"
        "```\n"
    )


def execute_packet(
    packet: ExecutionPacket,
    *,
    repo_root: Path | None = None,
) -> tuple[ExecutionDecision, list[CommandResult], list[str]]:
    """Execute a packet if and only if it passes all active-executor gates."""
    root = repo_root or Path.cwd()
    blocked = validate_active_packet(packet)
    if blocked:
        return ExecutionDecision.BLOCKED, [], blocked

    if not packet.real_run:
        return ExecutionDecision.WOULD_EXECUTE, [], []

    results: list[CommandResult] = []
    for action in packet.planned_actions:
        if not action.command:
            continue

        append_to_skeleton_diary(
            f"[REAL_EXECUTION] Module active_executor starting command for "
            f"Issue #{packet.issue_number}: {action.command}"
        )

        result = run_command(action.command, cwd=root)
        results.append(result)

        append_to_skeleton_diary(
            f"[REAL_EXECUTION] Module active_executor completed command for "
            f"Issue #{packet.issue_number}: {action.command}; returncode={result.returncode}"
        )

        if result.returncode != 0:
            create_system_snapshot(last_processed_issue_id=packet.issue_number)
            return (
                ExecutionDecision.FAILED,
                results,
                [f"command_failed:{action.action_id}:{result.returncode}"],
            )

    create_system_snapshot(last_processed_issue_id=packet.issue_number)
    return ExecutionDecision.WOULD_EXECUTE, results, []


def process_issue(
    repo: str,
    issue: GitHubIssueExport,
    *,
    mode: ExecutorMode,
    repo_root: Path | None = None,
) -> ActiveExecutionResult:
    real_run = mode == "real"
    packet = build_active_execution_packet(issue, real_run=real_run)
    decision, command_results, blocked_reasons = execute_packet(packet, repo_root=repo_root)

    if blocked_reasons:
        status: Literal["planned", "real_complete", "blocked", "failed"] = (
            "failed" if decision == ExecutionDecision.FAILED else "blocked"
        )
        labels_added = ["agent:execution-failed"]
        labels_removed = ["agent:executing"]
    else:
        status = "real_complete" if real_run else "planned"
        labels_added = ["agent:executed"]
        labels_removed = ["agent:audited", "agent:executing"]

    result = ActiveExecutionResult(
        issue_number=issue.number,
        issue_url=issue.url,
        mode=mode,
        decision=decision,
        status=status,
        packet=packet,
        command_results=command_results,
        blocked_reasons=blocked_reasons,
        labels_added=labels_added,
        labels_removed=labels_removed,
        next_safe_step=(
            "Stop and alert Oleksii."
            if blocked_reasons
            else "Active executor phase complete. Await human review."
        ),
    )

    comment_url = _post_comment(repo, issue.number, _comment_body(result))
    _edit_labels(repo, issue.number, add=labels_added, remove=labels_removed)
    result.posted_comment_url = comment_url

    if real_run:
        append_to_skeleton_diary(
            f"[REAL_EXECUTION] Module active_executor processed "
            f"Issue #{issue.number} with status={status}; "
            f"decision={decision}; comment_url={comment_url}"
        )
        create_system_snapshot(last_processed_issue_id=issue.number)

    return result


def process_queue(
    repo: str,
    *,
    limit: int,
    mode: ExecutorMode,
    repo_root: Path | None = None,
) -> list[ActiveExecutionResult]:
    issues = fetch_execution_candidates(repo, limit=limit)
    return [process_issue(repo, issue, mode=mode, repo_root=repo_root) for issue in issues]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Skeleton active executor.")
    parser.add_argument("--repo", default="alanua/jeeves")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--mode", choices=["plan", "real"], default="plan")
    args = parser.parse_args(argv)

    results = process_queue(args.repo, limit=args.limit, mode=args.mode)

    print(
        json.dumps(
            {
                "schema_version": "active_executor.result.v1",
                "repo": args.repo,
                "mode": args.mode,
                "processed": len(results),
                "results": [result.model_dump(mode="json") for result in results],
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )

    if any(result.status in {"blocked", "failed"} for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
