"""Bounded GitHub PR creator for Skeleton Core.

Sprint 9: Git Autonomy.

This module is intentionally narrow:
- no git add . / git add -A
- no force push
- no src/, tests/, or canon/ mutation
- target files must be explicit
- target files must be inside Green Zone or explicitly allowed
- tracked dirty files outside target files cause fail-closed panic
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from tools.skeleton_core.atomic_writer import ALLOWED_WRITE_PATHS, AtomicWritePanic
from tools.skeleton_core.memory_service import append_to_skeleton_diary, utc_now_iso

EXPLICIT_ALLOWED_FILES = {
    "knowledge_base/skeleton_diary.md",
}

IMMUTABLE_PREFIXES = (
    "src/",
    "tests/",
    "canon/",
)


class CreatePrPanic(RuntimeError):
    """Fail-closed PR creation panic."""


def _run(args: list[str], *, cwd: Path) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise CreatePrPanic(
            "git_or_gh_command_failed:"
            + json.dumps(
                {
                    "args": args,
                    "returncode": completed.returncode,
                    "stdout_tail": completed.stdout[-1000:],
                    "stderr_tail": completed.stderr[-1000:],
                },
                ensure_ascii=False,
            )
        )
    return completed.stdout.strip()


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is not None:
        return Path(repo_root).resolve()
    return Path.cwd().resolve()


def parse_target_files(raw: str) -> list[str]:
    files = [item.strip() for item in raw.split(",") if item.strip()]
    if not files:
        raise CreatePrPanic("no_target_files")

    if "." in files or "./" in files or "-A" in files:
        raise CreatePrPanic("forbidden_target_file_shortcut")

    if len(files) != len(set(files)):
        raise CreatePrPanic("duplicate_target_files")

    return files


def _to_repo_relative(path: str | Path, *, repo_root: Path) -> str:
    candidate = Path(path)

    resolved = candidate.resolve() if candidate.is_absolute() else (repo_root / candidate).resolve()

    try:
        rel = resolved.relative_to(repo_root)
    except ValueError as err:
        raise CreatePrPanic(f"target_file_outside_repo:{path}") from err

    rel_str = rel.as_posix()

    if rel_str in {"", "."}:
        raise CreatePrPanic("target_file_is_repo_root")

    return rel_str


def validate_target_file(path: str | Path, *, repo_root: str | Path | None = None) -> str:
    root = _repo_root(repo_root)
    rel = _to_repo_relative(path, repo_root=root)

    for prefix in IMMUTABLE_PREFIXES:
        if rel == prefix.rstrip("/") or rel.startswith(prefix):
            raise CreatePrPanic(f"target_file_in_immutable_zone:{rel}")

    target = root / rel
    if not target.exists():
        raise CreatePrPanic(f"target_file_missing:{rel}")
    if not target.is_file():
        raise CreatePrPanic(f"target_file_not_regular_file:{rel}")

    if rel in EXPLICIT_ALLOWED_FILES:
        return rel

    for allowed_raw in ALLOWED_WRITE_PATHS:
        allowed_prefix = allowed_raw.rstrip("/") + "/"
        if rel.startswith(allowed_prefix):
            return rel

    raise AtomicWritePanic(f"target_file_outside_green_zone:{rel}")


def validate_target_files(
    target_files: list[str],
    *,
    repo_root: str | Path | None = None,
) -> list[str]:
    return [validate_target_file(path, repo_root=repo_root) for path in target_files]


def _dirty_tracked_files(*, repo_root: Path) -> set[str]:
    unstaged = _run(["git", "diff", "--name-only"], cwd=repo_root)
    staged = _run(["git", "diff", "--cached", "--name-only"], cwd=repo_root)

    dirty: set[str] = set()
    for blob in (unstaged, staged):
        for line in blob.splitlines():
            item = line.strip()
            if item:
                dirty.add(item)
    return dirty


def ensure_tracked_dirty_files_are_explicit_targets(
    target_files: list[str],
    *,
    repo_root: Path,
) -> None:
    dirty = _dirty_tracked_files(repo_root=repo_root)
    allowed = set(target_files)
    unexpected = sorted(dirty - allowed)

    if unexpected:
        raise CreatePrPanic(
            "tracked_worktree_dirty_outside_target_files:"
            + json.dumps(unexpected, ensure_ascii=False)
        )


def ensure_start_branch_safe(*, repo_root: Path) -> None:
    branch = _run(["git", "branch", "--show-current"], cwd=repo_root)
    if branch != "main":
        raise CreatePrPanic(f"must_start_from_main_current_branch_is:{branch}")


def branch_exists(branch: str, *, repo_root: Path) -> bool:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", branch],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode == 0


def create_pull_request(
    *,
    issue: int,
    target_files: list[str],
    title: str,
    body: str,
    repo: str,
    repo_root: str | Path | None = None,
) -> dict[str, object]:
    root = _repo_root(repo_root)
    validated_files = validate_target_files(target_files, repo_root=root)

    ensure_start_branch_safe(repo_root=root)
    ensure_tracked_dirty_files_are_explicit_targets(validated_files, repo_root=root)

    branch = f"agent-auto-pr-issue-{issue}"

    if branch_exists(branch, repo_root=root):
        raise CreatePrPanic(f"branch_already_exists:{branch}")

    _run(["git", "switch", "-c", branch], cwd=root)

    for rel in validated_files:
        if rel in {".", "-A"}:
            raise CreatePrPanic(f"forbidden_git_add_target:{rel}")
        _run(["git", "add", "--force", "--", rel], cwd=root)

    staged = _run(["git", "diff", "--cached", "--name-only"], cwd=root)
    staged_files = [line.strip() for line in staged.splitlines() if line.strip()]

    if sorted(staged_files) != sorted(validated_files):
        raise CreatePrPanic(
            "staged_files_mismatch:"
            + json.dumps(
                {
                    "expected": sorted(validated_files),
                    "actual": sorted(staged_files),
                },
                ensure_ascii=False,
            )
        )

    _run(["git", "commit", "-m", f"Auto-generated PR for Issue #{issue}"], cwd=root)
    _run(["git", "push", "-u", "origin", branch], cwd=root)

    pr_url = _run(
        [
            "gh",
            "pr",
            "create",
            "--repo",
            repo,
            "--base",
            "main",
            "--head",
            branch,
            "--title",
            title,
            "--body",
            body,
        ],
        cwd=root,
    )

    append_to_skeleton_diary(
        f"[REAL_EXECUTION] Module cli_create_pr created PR for Issue #{issue}: {pr_url}"
    )

    return {
        "ok": True,
        "schema_version": "skeleton_create_pr_result.v1",
        "issue": issue,
        "branch": branch,
        "target_files": validated_files,
        "pr_url": pr_url,
        "created_at_utc": utc_now_iso(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a bounded Skeleton PR.")
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--target-files", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--repo", default="alanua/jeeves")
    args = parser.parse_args(argv)

    try:
        result = create_pull_request(
            issue=args.issue,
            target_files=parse_target_files(args.target_files),
            title=args.title,
            body=args.body,
            repo=args.repo,
        )
    except Exception as err:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": str(err),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
