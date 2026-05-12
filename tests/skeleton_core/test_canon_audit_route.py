from __future__ import annotations

from pathlib import Path

import pytest

from tools.skeleton_core import canon_audit_route
from tools.skeleton_core.canon_audit_route import CanonAuditRoutePanic


def _issue(labels: list[str] | None = None) -> dict[str, object]:
    return {
        "number": 141,
        "title": "Audit this issue",
        "body": "Check against canon.",
        "url": "https://github.com/alanua/jeeves/issues/141",
        "labels": [{"name": label} for label in (labels or [])],
    }


def test_validate_issue_requires_core_labels() -> None:
    blocked = canon_audit_route.validate_issue_for_canon_audit(_issue(labels=[]))

    assert any(reason.startswith("missing_required_labels") for reason in blocked)
    assert "missing_runner_label:runner:hetzner_or_runner:any" in blocked


def test_validate_issue_accepts_required_labels() -> None:
    blocked = canon_audit_route.validate_issue_for_canon_audit(
        _issue(
            labels=[
                "agent:task",
                "risk:yellow",
                "agent:audited",
                "agent:canon-audit",
                "runner:hetzner",
            ]
        )
    )

    assert blocked == []


def test_validate_issue_blocks_secret_in_body() -> None:
    issue = _issue(
        labels=[
            "agent:task",
            "risk:yellow",
            "agent:audited",
            "agent:canon-audit",
            "runner:hetzner",
        ]
    )
    issue["body"] = "OPENAI_API_KEY=value"

    blocked = canon_audit_route.validate_issue_for_canon_audit(issue)

    assert any(reason.startswith("secret_pattern_detected_in_issue") for reason in blocked)


def test_run_canon_audit_posts_comment_without_local_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for rel in ["BOOTLOADER.md", "knowledge_base/MEMORY_POLICY.md"]:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("canon text\n", encoding="utf-8")

    monkeypatch.setattr(
        canon_audit_route,
        "fetch_issue",
        lambda repo, issue_number: _issue(
            labels=[
                "agent:task",
                "risk:yellow",
                "agent:audited",
                "agent:canon-audit",
                "runner:hetzner",
            ]
        ),
    )
    monkeypatch.setattr(
        canon_audit_route,
        "build_canon_bundle",
        lambda root=None: "--- FILE: BOOTLOADER.md ---\ncanon text",
    )
    monkeypatch.setattr(
        canon_audit_route,
        "query_gemini",
        lambda prompt, model="gemini-2.5-flash": "verdict: aligned",
    )
    monkeypatch.setattr(
        canon_audit_route,
        "post_comment",
        lambda repo, issue_number, body: "https://github.com/alanua/jeeves/issues/141#comment",
    )

    label_edits: list[tuple[tuple[str, ...], tuple[str, ...]]] = []

    def fake_edit_labels(
        repo: str,
        issue_number: int,
        *,
        add: tuple[str, ...],
        remove: tuple[str, ...],
    ) -> None:
        label_edits.append((add, remove))

    monkeypatch.setattr(canon_audit_route, "edit_labels", fake_edit_labels)

    result = canon_audit_route.run_canon_audit(
        repo="alanua/jeeves",
        issue_number=141,
        repo_root=tmp_path,
    )

    assert result.status == "audit_complete"
    assert result.writes_files is False
    assert result.creates_pr is False
    assert result.merge_allowed is False
    assert label_edits == [(("agent:audit-complete",), ("agent:audited",))]


def test_run_canon_audit_blocks_unapproved_issue(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        canon_audit_route,
        "fetch_issue",
        lambda repo, issue_number: _issue(labels=["agent:task"]),
    )

    with pytest.raises(CanonAuditRoutePanic):
        canon_audit_route.run_canon_audit(repo="alanua/jeeves", issue_number=141)
