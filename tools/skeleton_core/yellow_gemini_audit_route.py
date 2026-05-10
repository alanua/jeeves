"""Autonomous YELLOW issue -> Gemini audit route.

This module processes queued GitHub issues through the already-validated
Skeleton dual-brain path:

GitHub Issue JSON
-> DualBrainTaskPacket
-> GeminiAuditorInput
-> gemini_auditor_adapter
-> GitHub issue comment + label transition

It does not merge, deploy, execute issue payloads, or write canon.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from tools.skeleton_core.gemini_auditor_adapter import scan_sensitive_text

AuditOutcome = Literal["accepted", "revise", "blocked", "error", "skipped"]

SECRET_OR_PII_FLAGS = {
    "gemini_api_key",
    "generic_api_key",
    "private_key",
    "email_address",
}

DEFAULT_REQUIRED_LABELS = {
    "agent:task",
    "agent:queued",
    "risk:yellow",
}

DEFAULT_RUNNER_LABELS = {
    "runner:hetzner",
    "runner:any",
}

SKIP_LABELS = {
    "agent:auditing",
    "agent:audited",
    "agent:blocked",
    "agent:audit-error",
    "agent:needs-revision",
}


class GitHubIssueLabel(BaseModel):
    """Minimal label object returned by gh."""

    model_config = ConfigDict(extra="ignore")

    name: str


class GitHubIssueExport(BaseModel):
    """Minimal GitHub issue JSON accepted by this route."""

    model_config = ConfigDict(extra="ignore")

    number: int
    title: str
    body: str = ""
    url: str = ""
    state: str = ""
    labels: list[GitHubIssueLabel] = Field(default_factory=list)


class RouteResult(BaseModel):
    """Public-safe route result."""

    model_config = ConfigDict(extra="forbid")

    issue_number: int
    issue_url: str = ""
    outcome: AuditOutcome
    adapter_status: str = ""
    posted_comment_url: str = ""
    labels_added: list[str] = Field(default_factory=list)
    labels_removed: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
    security_flags: list[str] = Field(default_factory=list)
    dry_run: bool = False
    next_safe_step: str = ""


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


def _label_names(issue: GitHubIssueExport) -> set[str]:
    return {label.name for label in issue.labels}


def _has_required_route_labels(issue: GitHubIssueExport) -> bool:
    labels = _label_names(issue)
    return DEFAULT_REQUIRED_LABELS.issubset(labels) and bool(
        labels.intersection(DEFAULT_RUNNER_LABELS)
    )


def _should_skip(issue: GitHubIssueExport) -> bool:
    return bool(_label_names(issue).intersection(SKIP_LABELS))


def _gh_json(args: list[str]) -> Any:
    completed = _run(["gh", *args])
    return json.loads(completed.stdout)


def fetch_candidate_issues(repo: str, *, limit: int) -> list[GitHubIssueExport]:
    """Fetch queued YELLOW issue candidates from GitHub."""
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
            "agent:queued",
            "--label",
            "risk:yellow",
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
                "number,title,body,labels,url,state",
            ]
        )
        issue = GitHubIssueExport.model_validate(full)
        if _has_required_route_labels(issue) and not _should_skip(issue):
            issues.append(issue)
    return issues


def _blocking_flags(flags: list[str]) -> list[str]:
    return sorted(set(flags).intersection(SECRET_OR_PII_FLAGS))


def sanitize_issue_for_gemini(issue: GitHubIssueExport) -> tuple[GitHubIssueExport, list[str]]:
    """Return issue JSON safe enough for Gemini routing.

    Secret/PII flags block before Gemini.
    Poison/control-injection flags sanitize the body before Gemini.
    """
    flags = scan_sensitive_text(issue.body or "")
    blocking = _blocking_flags(flags)
    if blocking:
        raise ValueError("local_secret_or_pii_block:" + ",".join(blocking))

    if flags:
        sanitized_body = (
            "Public-safe sanitized issue body.\n\n"
            "The original issue body contained local control-text patterns and was not "
            "sent raw to Gemini. Title, labels, URL, and task envelope are preserved.\n\n"
            "Audit goal:\n"
            "Decide whether this GitHub issue is safe to route as a bounded runner task. "
            "Gemini must remain auditor/evidence source only. No commands, no merge, "
            "no deploy, no canon writes, no secrets."
        )
        return issue.model_copy(update={"body": sanitized_body}), flags

    return issue, []


def _write_temp_issue_json(issue: GitHubIssueExport) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix=f"issue-{issue.number}-safe-",
        delete=False,
        encoding="utf-8",
    ) as handle:
        handle.write(json.dumps(issue.model_dump(mode="json"), ensure_ascii=False, indent=2))
        return Path(handle.name)


def run_gemini_audit(
    issue: GitHubIssueExport,
    *,
    mode: str,
    model: str,
) -> tuple[dict[str, Any], int]:
    """Run issue_to_gemini_audit.py as the canonical bridge."""
    issue_json = _write_temp_issue_json(issue)
    try:
        completed = _run(
            [
                sys.executable,
                "-m",
                "tools.skeleton_core.issue_to_gemini_audit",
                "--issue-json",
                str(issue_json),
                "--mode",
                mode,
                "--model",
                model,
                "--run-adapter",
            ],
            check=False,
        )
    finally:
        with suppress(FileNotFoundError):
            issue_json.unlink()

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()

    if not stdout:
        return (
            {
                "status": "route_error_no_stdout",
                "blocked_reasons": [stderr[:2000] if stderr else "no stdout"],
                "security_flags": [],
            },
            completed.returncode,
        )

    try:
        return json.loads(stdout), completed.returncode
    except json.JSONDecodeError:
        return (
            {
                "status": "route_error_invalid_json",
                "blocked_reasons": [stdout[-2000:], stderr[-2000:] if stderr else ""],
                "security_flags": [],
            },
            completed.returncode,
        )


def _outcome_from_adapter_status(status: str, returncode: int) -> AuditOutcome:
    if status == "live_accept" or status == "mock_accept":
        return "accepted"
    if status == "live_revise" or status == "mock_revise":
        return "revise"
    if status.startswith("blocked_") or status in {"live_block", "mock_block"}:
        return "blocked"
    if returncode != 0:
        return "error"
    return "error"


def _ensure_label(repo: str, name: str, color: str, description: str) -> None:
    _run(
        [
            "gh",
            "label",
            "create",
            name,
            "--repo",
            repo,
            "--color",
            color,
            "--description",
            description,
        ],
        check=False,
    )


def ensure_route_labels(repo: str) -> None:
    """Create transition labels if they do not already exist."""
    _ensure_label(repo, "agent:auditing", "C5DEF5", "Gemini audit is running")
    _ensure_label(repo, "agent:audited", "0E8A16", "Gemini audit accepted")
    _ensure_label(repo, "agent:blocked", "B60205", "Gemini audit blocked")
    _ensure_label(repo, "agent:audit-error", "D93F0B", "Gemini audit route error")
    _ensure_label(repo, "agent:needs-revision", "FBCA04", "Gemini audit requested revision")


def _edit_labels(
    repo: str,
    issue_number: int,
    *,
    add: list[str] | None = None,
    remove: list[str] | None = None,
    dry_run: bool,
) -> None:
    add = add or []
    remove = remove or []
    if dry_run:
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
    dry_run: bool,
) -> str:
    if dry_run:
        return ""

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix=f"issue-{issue_number}-comment-",
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


def _safe_json_tail(data: dict[str, Any], *, limit: int = 6000) -> str:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    return text[-limit:]


def _comment_body(
    issue: GitHubIssueExport,
    *,
    adapter_result: dict[str, Any],
    outcome: AuditOutcome,
    sanitized_flags: list[str],
) -> str:
    status = str(adapter_result.get("status", "unknown"))
    blocked_reasons = adapter_result.get("blocked_reasons") or []
    security_flags = adapter_result.get("security_flags") or []

    return (
        "Autonomous YELLOW Gemini audit route report\n\n"
        f"Issue: #{issue.number}\n"
        f"Outcome: `{outcome}`\n"
        f"Adapter status: `{status}`\n"
        f"Sanitized issue body: `{bool(sanitized_flags)}`\n"
        f"Blocked reasons: `{blocked_reasons}`\n"
        f"Security flags: `{security_flags}`\n\n"
        "```json\n"
        f"{_safe_json_tail(adapter_result)}\n"
        "```\n\n"
        "Private/environment values printed: no known unredacted values in this report.\n"
        "Merge allowed: false\n"
        "Deploy allowed: false\n"
        "Gemini role: auditor/evidence source only\n"
    )


def process_issue(
    repo: str,
    issue: GitHubIssueExport,
    *,
    mode: str,
    model: str,
    dry_run: bool,
) -> RouteResult:
    """Process one issue through Gemini audit and GitHub state transition."""
    _edit_labels(repo, issue.number, add=["agent:auditing"], dry_run=dry_run)

    try:
        safe_issue, sanitized_flags = sanitize_issue_for_gemini(issue)
    except ValueError as exc:
        body = (
            "Autonomous YELLOW Gemini audit route report\n\n"
            f"Issue: #{issue.number}\n"
            "Outcome: `blocked`\n"
            "Adapter status: `local_secret_or_pii_block`\n"
            f"Blocked reasons: `{str(exc)}`\n\n"
            "Issue was not sent to Gemini.\n"
            "Private/environment values printed: no known unredacted values in this report.\n"
            "Merge allowed: false\n"
            "Deploy allowed: false\n"
        )
        url = _post_comment(repo, issue.number, body, dry_run=dry_run)
        _edit_labels(
            repo,
            issue.number,
            add=["agent:blocked"],
            remove=["agent:queued", "agent:auditing"],
            dry_run=dry_run,
        )
        return RouteResult(
            issue_number=issue.number,
            issue_url=issue.url,
            outcome="blocked",
            adapter_status="local_secret_or_pii_block",
            posted_comment_url=url,
            labels_added=["agent:auditing", "agent:blocked"],
            labels_removed=["agent:queued", "agent:auditing"],
            blocked_reasons=[str(exc)],
            dry_run=dry_run,
            next_safe_step="Issue removed from active queue.",
        )

    adapter_result, returncode = run_gemini_audit(safe_issue, mode=mode, model=model)
    status = str(adapter_result.get("status", "unknown"))
    outcome = _outcome_from_adapter_status(status, returncode)

    comment_url = _post_comment(
        repo,
        issue.number,
        _comment_body(
            issue,
            adapter_result=adapter_result,
            outcome=outcome,
            sanitized_flags=sanitized_flags,
        ),
        dry_run=dry_run,
    )

    if outcome == "accepted":
        add_labels = ["agent:audited"]
    elif outcome == "revise":
        add_labels = ["agent:needs-revision"]
    elif outcome == "blocked":
        add_labels = ["agent:blocked"]
    else:
        add_labels = ["agent:audit-error"]

    remove_labels = ["agent:queued", "agent:auditing"]

    _edit_labels(
        repo,
        issue.number,
        add=add_labels,
        remove=remove_labels,
        dry_run=dry_run,
    )

    return RouteResult(
        issue_number=issue.number,
        issue_url=issue.url,
        outcome=outcome,
        adapter_status=status,
        posted_comment_url=comment_url,
        labels_added=["agent:auditing", *add_labels],
        labels_removed=remove_labels,
        blocked_reasons=list(adapter_result.get("blocked_reasons") or []),
        security_flags=list(adapter_result.get("security_flags") or []),
        dry_run=dry_run,
        next_safe_step=(
            "Issue audited and removed from active queue."
            if outcome == "accepted"
            else "Issue removed from active queue for review."
        ),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run autonomous YELLOW Gemini audit route.")
    parser.add_argument("--repo", default="alanua/jeeves")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--mode", choices=["mock", "live"], default="live")
    parser.add_argument("--model", default="gemini-2.5-flash")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-ensure-labels", action="store_true")
    args = parser.parse_args(argv)

    if args.mode == "live":
        os.environ.setdefault("GEMINI_API_LIVE_MODE", "true")

    if not args.dry_run and not args.no_ensure_labels:
        ensure_route_labels(args.repo)

    issues = fetch_candidate_issues(args.repo, limit=args.limit)
    results = [
        process_issue(
            args.repo,
            issue,
            mode=args.mode,
            model=args.model,
            dry_run=args.dry_run,
        )
        for issue in issues
    ]

    print(
        json.dumps(
            {
                "schema_version": "yellow_gemini_audit_route.result.v1",
                "repo": args.repo,
                "mode": args.mode,
                "model": args.model,
                "dry_run": args.dry_run,
                "processed": len(results),
                "results": [result.model_dump(mode="json") for result in results],
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )

    if any(result.outcome == "error" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
