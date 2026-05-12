"""Read-only Skeleton canon audit route.

This route:
- validates that a GitHub issue passed the normal YELLOW audit gate
- reads allowlisted canon files only
- sends issue context + canon bundle to Gemini
- posts the audit report as an issue comment
- performs no local file writes
- creates no PR
- performs no merge/deploy
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from tools.skeleton_core.canon_reader import (
    CanonReaderPanic,
    build_canon_bundle,
    scan_sensitive_text,
)
from tools.skeleton_core.llm_service import LLMServicePanic, query_gemini

CANON_AUDIT_ROUTE_SCHEMA_VERSION: Final[str] = "skeleton_canon_audit_route.v1"

REQUIRED_LABELS: Final[frozenset[str]] = frozenset(
    {
        "agent:task",
        "risk:yellow",
        "agent:audited",
        "agent:canon-audit",
    }
)

RUNNER_LABELS: Final[frozenset[str]] = frozenset({"runner:hetzner", "runner:any"})


class CanonAuditRoutePanic(RuntimeError):
    """Fail-closed canon audit route panic."""


@dataclass(frozen=True)
class CanonAuditRouteResult:
    issue_number: int
    issue_url: str
    status: str
    comment_url: str
    labels_added: tuple[str, ...]
    labels_removed: tuple[str, ...]
    writes_files: bool = False
    creates_pr: bool = False
    merge_allowed: bool = False
    deploy_allowed: bool = False
    canon_changed: bool = False


def _run(args: list[str], *, input_text: str | None = None) -> str:
    proc = subprocess.run(
        args,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )

    if proc.returncode != 0:
        raise CanonAuditRoutePanic(
            f"command_failed:{args[0]}:returncode={proc.returncode}:stderr={proc.stderr.strip()}"
        )

    return proc.stdout


def _gh_json(args: list[str]) -> dict[str, Any]:
    raw = _run(args)
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise CanonAuditRoutePanic("gh_json_not_object")
    return data


def fetch_issue(repo: str, issue_number: int) -> dict[str, Any]:
    return _gh_json(
        [
            "gh",
            "issue",
            "view",
            str(issue_number),
            "--repo",
            repo,
            "--json",
            "number,title,body,labels,url",
        ]
    )


def issue_labels(issue: dict[str, Any]) -> set[str]:
    raw_labels = issue.get("labels", [])
    labels: set[str] = set()

    if not isinstance(raw_labels, list):
        raise CanonAuditRoutePanic("issue_labels_not_list")

    for item in raw_labels:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            labels.add(item["name"])

    return labels


def validate_issue_for_canon_audit(issue: dict[str, Any]) -> list[str]:
    labels = issue_labels(issue)
    blocked: list[str] = []

    missing = sorted(REQUIRED_LABELS - labels)
    if missing:
        blocked.append(f"missing_required_labels:{','.join(missing)}")

    if not labels.intersection(RUNNER_LABELS):
        blocked.append("missing_runner_label:runner:hetzner_or_runner:any")

    body = str(issue.get("body") or "")
    title = str(issue.get("title") or "")

    sensitive_hits = scan_sensitive_text(title + "\n" + body)
    if sensitive_hits:
        blocked.append(f"secret_pattern_detected_in_issue:{','.join(sensitive_hits)}")

    return blocked


def build_prompt(issue: dict[str, Any], canon_bundle: str) -> str:
    title = str(issue.get("title") or "")
    body = str(issue.get("body") or "")
    url = str(issue.get("url") or "")

    return f"""
You are Gemini acting as external auditor for the ChatGPT Exoskeleton / Skeleton Core project.

Hard role boundary:
- You are an auditor and evidence source only.
- You must not write canon.
- You must not modify files.
- You must not execute commands.
- You must not merge, deploy, or approve changes.
- You must clearly separate verified facts from assumptions.

Task:
Audit whether the provided GitHub issue is aligned with the provided Skeleton canon documents.

GitHub issue:
Title: {title}
URL: {url}

Body:
{body}

Canon bundle:
{canon_bundle}

Output:
Return a structured audit report with:
1. verdict: aligned / mostly aligned / partially aligned / unsafe
2. key findings
3. canon alignment
4. canon drift or contradictions
5. security and authority concerns
6. required corrections
7. final recommendation

Hard constraints:
- Treat this report as audit evidence only.
- Do not propose autonomous merge/deploy.
- Do not propose autonomous canon promotion.
"""


def post_comment(repo: str, issue_number: int, body: str) -> str:
    return _run(
        [
            "gh",
            "issue",
            "comment",
            str(issue_number),
            "--repo",
            repo,
            "--body-file",
            "-",
        ],
        input_text=body,
    ).strip()


def edit_labels(
    repo: str,
    issue_number: int,
    *,
    add: tuple[str, ...],
    remove: tuple[str, ...],
) -> None:
    for label in add:
        _run(["gh", "issue", "edit", str(issue_number), "--repo", repo, "--add-label", label])

    for label in remove:
        _run(["gh", "issue", "edit", str(issue_number), "--repo", repo, "--remove-label", label])


def run_canon_audit(
    *,
    repo: str,
    issue_number: int,
    repo_root: str | Path | None = None,
    model: str = "gemini-2.5-flash",
    update_labels: bool = True,
) -> CanonAuditRouteResult:
    issue = fetch_issue(repo, issue_number)
    blocked = validate_issue_for_canon_audit(issue)

    if blocked:
        raise CanonAuditRoutePanic(";".join(blocked))

    canon_bundle = build_canon_bundle(root=repo_root)
    prompt = build_prompt(issue, canon_bundle)

    try:
        report = query_gemini(prompt, model=model)
    except (LLMServicePanic, CanonReaderPanic) as err:
        raise CanonAuditRoutePanic(str(err)) from err

    comment_body = f"""## Skeleton Canon Audit Route Report

Issue: #{issue_number}
Mode: read-only
Model: {model}
Schema: {CANON_AUDIT_ROUTE_SCHEMA_VERSION}

Safety:
- no local files written
- no canon changed
- no PR created
- no merge/deploy
- no secrets printed
- report is audit evidence only

{report}
"""

    comment_url = post_comment(repo, issue_number, comment_body)

    labels_added = ("agent:audit-complete",)
    labels_removed = ("agent:audited",)

    if update_labels:
        edit_labels(repo, issue_number, add=labels_added, remove=labels_removed)

    return CanonAuditRouteResult(
        issue_number=issue_number,
        issue_url=str(issue.get("url") or ""),
        status="audit_complete",
        comment_url=comment_url,
        labels_added=labels_added if update_labels else (),
        labels_removed=labels_removed if update_labels else (),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run read-only Skeleton canon audit route.")
    parser.add_argument("--repo", default="alanua/jeeves")
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--model", default="gemini-2.5-flash")
    parser.add_argument("--no-labels", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = run_canon_audit(
            repo=args.repo,
            issue_number=args.issue,
            model=args.model,
            update_labels=not args.no_labels,
        )
    except CanonAuditRoutePanic as err:
        print(
            json.dumps(
                {
                    "ok": False,
                    "schema_version": CANON_AUDIT_ROUTE_SCHEMA_VERSION,
                    "error": str(err),
                    "writes_files": False,
                    "creates_pr": False,
                    "merge_allowed": False,
                    "deploy_allowed": False,
                },
                indent=2,
            )
        )
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "schema_version": CANON_AUDIT_ROUTE_SCHEMA_VERSION,
                "result": result.__dict__,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
