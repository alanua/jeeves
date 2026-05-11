"""Active bounded executor.

Sprint 8 Atomic Actions:
- fail-closed
- real mode allows only:
  1. python -m tools.skeleton_core.cli validate-state
  2. python -m tools.skeleton_core.cli create-report
- atomic writes are restricted to Green Zone:
  knowledge_base/active_tasks/
  knowledge_base/reports/
- src/, tests/, canon/ are immutable
- every real write is logged with [REAL_WRITE]
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

from tools.skeleton_core.atomic_writer import AtomicWritePanic
from tools.skeleton_core.atomic_writer import safe_write as atomic_safe_write
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
    utc_now_iso,
)

ExecutorMode = Literal["plan", "real"]

VALIDATE_STATE_COMMAND = "python -m tools.skeleton_core.cli validate-state"
CREATE_REPORT_COMMAND = "python -m tools.skeleton_core.cli create-report"

ALLOWED_WRITE_PATHS = [
    "knowledge_base/active_tasks/",
    "knowledge_base/reports/",
]

SAFE_COMMAND_PREFIXES = (
    ("python", "-m", "pytest"),
    ("python", "-m", "ruff", "check"),
    ("python", "-m", "black", "--check"),
    ("python", "-m", "tools.skeleton_core.cli", "validate-state"),
    ("python", "-m", "tools.skeleton_core.cli", "create-report"),
    ("git", "status", "--short"),
    ("git", "diff", "--stat"),
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


class ActiveTaskPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    type: Literal["integrity_check"]
    command: str
    safety_level: Literal["green"]


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

    allowed_exact = set(allowed_commands or [])
    if stripped in allowed_exact:
        return True, ""

    for prefix in SAFE_COMMAND_PREFIXES:
        if tuple(parts[: len(prefix)]) == prefix:
            return True, ""

    return False, "command_not_whitelisted"


def active_task_path(issue_number: int, repo_root: Path | None = None) -> Path:
    root = repo_root or Path.cwd()
    return root / "knowledge_base" / "active_tasks" / f"task_{issue_number}.json"


def load_active_task_payload(
    issue_number: int,
    *,
    repo_root: Path | None = None,
) -> tuple[ActiveTaskPayload | None, list[str]]:
    path = active_task_path(issue_number, repo_root=repo_root)

    if not path.exists():
        return None, [f"missing_active_task_payload:{path}"]

    try:
        payload = ActiveTaskPayload.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as err:
        return None, [f"invalid_active_task_payload:{err}"]

    if payload.id != issue_number:
        return None, [f"task_payload_id_mismatch:{payload.id}!={issue_number}"]

    if payload.command not in {VALIDATE_STATE_COMMAND, CREATE_REPORT_COMMAND}:
        return None, [f"task_payload_command_not_allowed:{payload.command}"]

    return payload, []


def safe_write(target_path: str | Path, content: str, *, repo_root: Path | None = None) -> Path:
    written = atomic_safe_write(target_path, content, repo_root=repo_root)
    append_to_skeleton_diary(
        f"[REAL_WRITE] Module active_executor atomically wrote {written}.",
        repo_root=repo_root,
    )
    return written


def report_target_path(issue_number: int) -> str:
    return f"knowledge_base/reports/self_integrity_report_{issue_number}.json"


def build_self_integrity_report(issue: GitHubIssueExport, packet: ExecutionPacket) -> str:
    return (
        json.dumps(
            {
                "schema_version": "skeleton_self_integrity_report.v1",
                "issue_number": issue.number,
                "issue_url": issue.url,
                "title": issue.title,
                "generated_at_utc": utc_now_iso(),
                "mode": "real",
                "action": "atomic_green_zone_write",
                "target": report_target_path(issue.number),
                "audit_verified": packet.audit_verified,
                "audit_status": packet.audit_status,
                "allowed_write_paths": ALLOWED_WRITE_PATHS,
                "immutability": {
                    "src": "read_only",
                    "tests": "read_only",
                    "canon": "read_only",
                },
                "git_mutation": False,
                "merge_allowed": False,
                "deploy_allowed": False,
                "canon_write_allowed": False,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )


def fetch_issue(repo: str, issue_number: int) -> GitHubIssueExport:
    raw = _gh_json(
        [
            "issue",
            "view",
            str(issue_number),
            "--repo",
            repo,
            "--json",
            "number,title,body,labels,comments,url,state",
        ]
    )
    return GitHubIssueExport.model_validate(raw)


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
        issue = fetch_issue(repo, int(item["number"]))
        labels = {label.name for label in issue.labels}
        if "agent:audited" in labels and "agent:executed" not in labels:
            issues.append(issue)

    return issues


def build_active_execution_packet(
    issue: GitHubIssueExport,
    *,
    real_run: bool,
    task_payload: ActiveTaskPayload | None = None,
) -> ExecutionPacket:
    verified, audit_status, audit_comment_url, audit_body = find_verified_audit_comment(issue)
    labels = sorted(label.name for label in issue.labels)

    command = task_payload.command if task_payload else VALIDATE_STATE_COMMAND

    writes_files = command == CREATE_REPORT_COMMAND
    action_id = (
        "atomic-write-self-integrity-report" if writes_files else "first-breath-validate-state"
    )

    planned_command = command if real_run else ""

    return ExecutionPacket(
        issue_number=issue.number,
        issue_url=issue.url,
        title=issue.title,
        mode=ExecutionMode.REAL if real_run else ExecutionMode.DRY_RUN,
        real_run=real_run,
        allowed_commands=[VALIDATE_STATE_COMMAND, CREATE_REPORT_COMMAND],
        target_branch=f"skeleton-exec-issue-{issue.number}",
        trigger_labels=labels,
        audit_verified=verified,
        audit_status=audit_status,
        audit_comment_url=audit_comment_url,
        audit_summary=audit_body[:1000],
        objective=issue.body[:2000],
        planned_actions=[
            ExecutionAction(
                action_id=action_id,
                action_type=ExecutionActionType.NOOP,
                description=(
                    "Sprint 8 atomic Green Zone report write."
                    if writes_files
                    else "Read-only Skeleton integrity check."
                ),
                dry_run_only=not real_run,
                command=planned_command,
                writes_files=writes_files,
                network_access=False,
            )
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
        file_writes_allowed=writes_files,
        pr_creation_allowed=False,
        merge_allowed=False,
        deploy_allowed=False,
        canon_write_allowed=False,
        next_safe_step=(
            "Run atomic Green Zone report write."
            if writes_files
            else "Run read-only validate-state command."
        ),
    )


def validate_active_packet(packet: ExecutionPacket) -> list[str]:
    reasons: list[str] = []

    labels = set(packet.trigger_labels)
    if "agent:task" not in labels:
        reasons.append("missing_label_agent_task")
    if "agent:audited" not in labels:
        reasons.append("missing_label_agent_audited")
    if not ({"runner:hetzner", "runner:any"} & labels):
        reasons.append("missing_runner_label")

    if not packet.audit_verified:
        reasons.append("missing_verified_accept_audit_comment")
    if packet.audit_status not in ACCEPT_STATUSES:
        reasons.append("audit_status_not_accepted")

    if packet.real_run and not packet.executor_allowed:
        reasons.append("real_run_requires_executor_allowed")

    if packet.pr_creation_allowed:
        reasons.append("pr_creation_not_allowed")
    if packet.merge_allowed:
        reasons.append("merge_not_allowed")
    if packet.deploy_allowed:
        reasons.append("deploy_not_allowed")
    if packet.canon_write_allowed:
        reasons.append("canon_write_not_allowed")

    for action in packet.planned_actions:
        if action.command:
            allowed, reason = command_is_allowed(action.command, packet.allowed_commands)
            if not allowed:
                reasons.append(f"action_{action.action_id}_{reason}")

        if action.writes_files and action.command != CREATE_REPORT_COMMAND:
            reasons.append(f"action_{action.action_id}_write_requires_create_report_command")

    return sorted(set(reasons))


def run_shell_command(command: str, *, cwd: Path) -> CommandResult:
    completed = subprocess.run(
        parse_command(command),
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


def run_create_report_command(
    *,
    issue: GitHubIssueExport,
    packet: ExecutionPacket,
    repo_root: Path,
) -> CommandResult:
    target = report_target_path(issue.number)
    content = build_self_integrity_report(issue, packet)

    try:
        written = safe_write(target, content, repo_root=repo_root)
    except AtomicWritePanic as err:
        return CommandResult(
            command=CREATE_REPORT_COMMAND,
            returncode=50,
            stdout_tail="",
            stderr_tail=str(err),
        )

    return CommandResult(
        command=CREATE_REPORT_COMMAND,
        returncode=0,
        stdout_tail=f"atomic_write_ok:{written}\n",
        stderr_tail="",
    )


def _update_current_state_execution_block(
    *,
    issue_number: int,
    state: str,
    blocked_reasons: list[str],
    command_results: list[CommandResult],
    repo_root: Path,
) -> None:
    snapshot_path = create_system_snapshot(
        last_processed_issue_id=issue_number,
        repo_root=repo_root,
    )

    data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    data["active_executor_state"] = {
        "issue_number": issue_number,
        "state": state,
        "updated_at_utc": utc_now_iso(),
        "blocked_reasons": blocked_reasons,
        "command_results": [result.model_dump(mode="json") for result in command_results],
    }
    snapshot_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def execute_packet(
    issue_or_packet: GitHubIssueExport | ExecutionPacket,
    packet: ExecutionPacket | None = None,
    *,
    repo_root: Path | None = None,
) -> tuple[ExecutionDecision, list[CommandResult], list[str]]:
    root = repo_root or Path.cwd()

    if packet is None:
        issue: GitHubIssueExport | None = None
        packet = issue_or_packet  # type: ignore[assignment]
    else:
        issue = issue_or_packet  # type: ignore[assignment]

    blocked = validate_active_packet(packet)

    if blocked:
        _update_current_state_execution_block(
            issue_number=packet.issue_number,
            state="blocked",
            blocked_reasons=blocked,
            command_results=[],
            repo_root=root,
        )
        return ExecutionDecision.BLOCKED, [], blocked

    if not packet.real_run:
        return ExecutionDecision.WOULD_EXECUTE, [], []

    results: list[CommandResult] = []

    for action in packet.planned_actions:
        if not action.command:
            continue

        append_to_skeleton_diary(
            f"[REAL_EXECUTION] Module active_executor starting action for "
            f"Issue #{packet.issue_number}: {action.command}",
            repo_root=root,
        )

        if action.command == CREATE_REPORT_COMMAND:
            if issue is None:
                result = CommandResult(
                    command=CREATE_REPORT_COMMAND,
                    returncode=51,
                    stdout_tail="",
                    stderr_tail="missing_issue_for_create_report",
                )
            else:
                result = run_create_report_command(
                    issue=issue,
                    packet=packet,
                    repo_root=root,
                )
        else:
            result = run_shell_command(action.command, cwd=root)

        results.append(result)

        append_to_skeleton_diary(
            f"[REAL_EXECUTION] Module active_executor completed action for "
            f"Issue #{packet.issue_number}: {action.command}; returncode={result.returncode}",
            repo_root=root,
        )

        if result.returncode != 0:
            reasons = [f"command_failed:{action.action_id}:{result.returncode}"]
            _update_current_state_execution_block(
                issue_number=packet.issue_number,
                state="failed",
                blocked_reasons=reasons,
                command_results=results,
                repo_root=root,
            )
            return ExecutionDecision.FAILED, results, reasons

    _update_current_state_execution_block(
        issue_number=packet.issue_number,
        state="real_complete",
        blocked_reasons=[],
        command_results=results,
        repo_root=root,
    )
    return ExecutionDecision.WOULD_EXECUTE, results, []


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
        "- Atomic Green Zone writes only\n"
        "- allowed write paths: knowledge_base/active_tasks/, knowledge_base/reports/\n"
        "- src/, tests/, canon/ immutable\n"
        "- no PR creation allowed\n"
        "- no merge allowed\n"
        "- no deploy allowed\n"
        "- no git commit or git push performed by executor\n\n"
        "```json\n"
        f"{payload[-6000:]}\n"
        "```\n"
    )


def process_issue(
    repo: str,
    issue: GitHubIssueExport,
    *,
    mode: ExecutorMode,
    repo_root: Path | None = None,
) -> ActiveExecutionResult:
    root = repo_root or Path.cwd()
    real_run = mode == "real"

    task_payload: ActiveTaskPayload | None = None
    pre_blocked: list[str] = []

    if real_run:
        task_payload, pre_blocked = load_active_task_payload(issue.number, repo_root=root)

    packet = build_active_execution_packet(
        issue,
        real_run=real_run,
        task_payload=task_payload,
    )

    if pre_blocked:
        decision = ExecutionDecision.BLOCKED
        command_results: list[CommandResult] = []
        blocked_reasons = pre_blocked
        _update_current_state_execution_block(
            issue_number=issue.number,
            state="blocked",
            blocked_reasons=blocked_reasons,
            command_results=command_results,
            repo_root=root,
        )
    else:
        if real_run:
            _edit_labels(repo, issue.number, add=["agent:executing"])
        decision, command_results, blocked_reasons = execute_packet(
            issue,
            packet,
            repo_root=root,
        )

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
            f"decision={decision}; comment_url={comment_url}",
            repo_root=root,
        )
        # Do not call create_system_snapshot() here:
        # execute_packet() already writes active_executor_state, and a plain snapshot
        # would overwrite that execution block.

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
    parser.add_argument("--issue", type=int, default=None)
    args = parser.parse_args(argv)

    if args.issue is not None:
        issue = fetch_issue(args.repo, args.issue)
        results = [process_issue(args.repo, issue, mode=args.mode)]
    else:
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
