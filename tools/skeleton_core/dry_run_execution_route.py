"""Dry-run execution handoff route.

Sprint 5 phase 1:
- consumes audited issues
- verifies audit evidence
- builds ExecutionPacket
- posts mock execution report
- transitions labels
- executes zero real commands
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.bounded_execution_packet import (
    ExecutionAction,
    ExecutionActionType,
    ExecutionDecision,
    ExecutionPacket,
    ExecutionReportPacket,
    ExecutionSource,
)

RouteOutcome = Literal["executed", "blocked", "failed"]

REQUIRED_LABELS = {"agent:task", "agent:audited"}
RUNNER_LABELS = {"runner:hetzner", "runner:any"}
SKIP_LABELS = {
    "agent:executing",
    "agent:executed",
    "agent:execution-failed",
    "agent:queued",
    "agent:blocked",
    "agent:audit-error",
    "agent:needs-revision",
}

ACCEPT_STATUSES = {
    "live_accept",
    "mock_accept",
}


class GitHubIssueLabel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str


class GitHubIssueComment(BaseModel):
    model_config = ConfigDict(extra="ignore")

    body: str = ""
    url: str = ""


class GitHubIssueExport(BaseModel):
    model_config = ConfigDict(extra="ignore")

    number: int
    title: str
    body: str = ""
    url: str = ""
    state: str = ""
    labels: list[GitHubIssueLabel] = Field(default_factory=list)
    comments: list[GitHubIssueComment] = Field(default_factory=list)


def _run(
    args: list[str],
    *,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=input_text,
        text=True,
        capture_output=True,
        check=check,
    )


def _gh_json(args: list[str]) -> Any:
    completed = _run(["gh", *args])
    return json.loads(completed.stdout)


def _label_names(issue: GitHubIssueExport) -> set[str]:
    return {label.name for label in issue.labels}


def has_execution_trigger_labels(issue: GitHubIssueExport) -> bool:
    labels = _label_names(issue)
    return (
        REQUIRED_LABELS.issubset(labels)
        and bool(labels.intersection(RUNNER_LABELS))
        and not labels.intersection(SKIP_LABELS)
    )


def fetch_candidate_issues(repo: str, *, limit: int) -> list[GitHubIssueExport]:
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
        if has_execution_trigger_labels(issue):
            issues.append(issue)

    return issues


def _extract_adapter_status(comment_body: str) -> str:
    marker = "Adapter status: `"
    if marker in comment_body:
        after = comment_body.split(marker, 1)[1]
        return after.split("`", 1)[0].strip()

    try:
        start = comment_body.find("{")
        end = comment_body.rfind("}")
        if start >= 0 and end > start:
            data = json.loads(comment_body[start : end + 1])
            status = data.get("status")
            if isinstance(status, str):
                return status
    except json.JSONDecodeError:
        return ""

    return ""


def find_verified_audit_comment(issue: GitHubIssueExport) -> tuple[bool, str, str, str]:
    """Return audit verification tuple.

    Returns:
        verified, status, comment_url, comment_body
    """
    for comment in reversed(issue.comments):
        body = comment.body or ""
        if "Autonomous YELLOW Gemini audit route report" not in body:
            continue

        status = _extract_adapter_status(body)
        if status in ACCEPT_STATUSES:
            return True, status, comment.url, body

    return False, "", "", ""


def build_execution_packet(issue: GitHubIssueExport) -> ExecutionPacket:
    verified, audit_status, audit_comment_url, audit_body = find_verified_audit_comment(issue)

    labels = sorted(_label_names(issue))

    planned_actions = [
        ExecutionAction(
            action_id="dry-run-noop-001",
            action_type=ExecutionActionType.NOOP,
            description=("Dry-run only. No command execution is allowed in Sprint 5 phase 1."),
            dry_run_only=True,
            command="",
            writes_files=False,
            network_access=False,
        ),
        ExecutionAction(
            action_id="github-comment-001",
            action_type=ExecutionActionType.COMMENT_ONLY,
            description="Post bounded dry-run execution report to GitHub issue.",
            dry_run_only=True,
            command="",
            writes_files=False,
            network_access=True,
        ),
        ExecutionAction(
            action_id="label-transition-001",
            action_type=ExecutionActionType.LABEL_TRANSITION_ONLY,
            description="Transition labels from audited/executing to executed.",
            dry_run_only=True,
            command="",
            writes_files=False,
            network_access=True,
        ),
    ]

    return ExecutionPacket(
        issue_number=issue.number,
        issue_url=issue.url,
        title=issue.title,
        trigger_labels=labels,
        audit_verified=verified,
        audit_status=audit_status,
        audit_comment_url=audit_comment_url,
        audit_summary=audit_body[:1000],
        objective=issue.body[:2000],
        planned_actions=planned_actions,
        sources=[
            ExecutionSource(
                source_type="github_issue",
                reference=issue.url or f"issue:{issue.number}",
                verified=True,
                notes="Execution handoff source issue.",
            ),
            ExecutionSource(
                source_type="audit_report",
                reference=audit_comment_url,
                verified=verified,
                notes="Accepted Gemini audit report comment.",
            ),
        ],
        executor_allowed=False,
        file_writes_allowed=False,
        pr_creation_allowed=False,
        merge_allowed=False,
        deploy_allowed=False,
        canon_write_allowed=False,
    )


def validate_execution_packet(packet: ExecutionPacket) -> list[str]:
    reasons: list[str] = []

    if not packet.audit_verified:
        reasons.append("missing_verified_accept_audit_comment")
    if packet.audit_status not in ACCEPT_STATUSES:
        reasons.append("audit_status_not_accepted")
    if packet.executor_allowed:
        reasons.append("executor_allowed_must_be_false_in_phase_1")
    if packet.file_writes_allowed:
        reasons.append("file_writes_must_be_false_in_phase_1")
    if packet.pr_creation_allowed:
        reasons.append("pr_creation_must_be_false_in_phase_1")
    if packet.merge_allowed:
        reasons.append("merge_must_be_false")
    if packet.deploy_allowed:
        reasons.append("deploy_must_be_false")
    if packet.canon_write_allowed:
        reasons.append("canon_write_must_be_false")
    for action in packet.planned_actions:
        if action.command:
            reasons.append(f"action_{action.action_id}_contains_command")
        if action.writes_files:
            reasons.append(f"action_{action.action_id}_writes_files")
        if not action.dry_run_only:
            reasons.append(f"action_{action.action_id}_not_dry_run_only")

    return sorted(set(reasons))


def ensure_execution_labels(repo: str) -> None:
    _run(
        [
            "gh",
            "label",
            "create",
            "agent:executing",
            "--repo",
            repo,
            "--color",
            "C5DEF5",
            "--description",
            "Dry-run execution is processing",
        ],
        check=False,
    )
    _run(
        [
            "gh",
            "label",
            "create",
            "agent:executed",
            "--repo",
            repo,
            "--color",
            "0E8A16",
            "--description",
            "Dry-run execution completed",
        ],
        check=False,
    )
    _run(
        [
            "gh",
            "label",
            "create",
            "agent:execution-failed",
            "--repo",
            repo,
            "--color",
            "B60205",
            "--description",
            "Dry-run execution failed or blocked",
        ],
        check=False,
    )


def _edit_labels(
    repo: str,
    issue_number: int,
    *,
    add: list[str] | None = None,
    remove: list[str] | None = None,
    no_write: bool,
) -> None:
    if no_write:
        return

    args = ["gh", "issue", "edit", str(issue_number), "--repo", repo]
    if add:
        args.extend(["--add-label", ",".join(add)])
    if remove:
        args.extend(["--remove-label", ",".join(remove)])
    _run(args)


def _post_comment(
    repo: str,
    issue_number: int,
    body: str,
    *,
    no_write: bool,
) -> str:
    if no_write:
        return ""

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix=f"execution-{issue_number}-comment-",
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


def _comment_body(report: ExecutionReportPacket) -> str:
    text = json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2)
    return (
        "Bounded Execution Handoff — DRY RUN report\n\n"
        f"Issue: #{report.issue_number}\n"
        f"Decision: `{report.decision}`\n"
        f"Execution status: `{report.execution_status}`\n"
        f"Blocked reasons: `{report.blocked_reasons}`\n\n"
        "No shell commands were executed.\n"
        "No files were changed.\n"
        "No PR was created.\n"
        "No merge/deploy/canon write was performed.\n\n"
        "```json\n"
        f"{text[-6000:]}\n"
        "```\n"
    )


def process_issue(
    repo: str,
    issue: GitHubIssueExport,
    *,
    no_write: bool = False,
) -> ExecutionReportPacket:
    _edit_labels(repo, issue.number, add=["agent:executing"], no_write=no_write)

    packet = build_execution_packet(issue)
    blocked_reasons = validate_execution_packet(packet)

    if blocked_reasons:
        report = ExecutionReportPacket(
            issue_number=issue.number,
            issue_url=issue.url,
            decision=ExecutionDecision.BLOCKED,
            execution_status="blocked",
            packet=packet,
            blocked_reasons=blocked_reasons,
            labels_added=["agent:executing", "agent:execution-failed"],
            labels_removed=["agent:audited", "agent:executing"],
            commands_executed=[],
            files_changed=[],
            next_safe_step="Human review required before any execution handoff.",
        )
        comment_url = _post_comment(
            repo,
            issue.number,
            _comment_body(report),
            no_write=no_write,
        )
        _edit_labels(
            repo,
            issue.number,
            add=["agent:execution-failed"],
            remove=["agent:audited", "agent:executing"],
            no_write=no_write,
        )
        report.posted_comment_url = comment_url
        return report

    report = ExecutionReportPacket(
        issue_number=issue.number,
        issue_url=issue.url,
        decision=ExecutionDecision.WOULD_EXECUTE,
        execution_status="dry_run_complete",
        packet=packet,
        blocked_reasons=[],
        labels_added=["agent:executing", "agent:executed"],
        labels_removed=["agent:audited", "agent:executing"],
        commands_executed=[],
        files_changed=[],
        next_safe_step="Dry-run execution handoff complete. Await human approval for real executor design.",
    )

    comment_url = _post_comment(repo, issue.number, _comment_body(report), no_write=no_write)
    _edit_labels(
        repo,
        issue.number,
        add=["agent:executed"],
        remove=["agent:audited", "agent:executing"],
        no_write=no_write,
    )
    report.posted_comment_url = comment_url
    return report


def process_queue(
    repo: str,
    *,
    limit: int,
    no_write: bool,
) -> list[ExecutionReportPacket]:
    if not no_write:
        ensure_execution_labels(repo)

    issues = fetch_candidate_issues(repo, limit=limit)
    return [process_issue(repo, issue, no_write=no_write) for issue in issues]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded dry-run execution handoff.")
    parser.add_argument("--repo", default="alanua/jeeves")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)

    reports = process_queue(args.repo, limit=args.limit, no_write=args.no_write)

    print(
        json.dumps(
            {
                "schema_version": "dry_run_execution_route.result.v1",
                "repo": args.repo,
                "processed": len(reports),
                "no_write": args.no_write,
                "results": [report.model_dump(mode="json") for report in reports],
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )

    if any(report.decision != ExecutionDecision.WOULD_EXECUTE for report in reports):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
