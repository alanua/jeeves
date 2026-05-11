"""Skeleton Core technical memory service.

Writes only to knowledge_base/.
This is Skeleton technical memory, not Jeeves personality memory.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_LOCK_FILE = Path("/home/agent/agent-dev/runner-state/yellow_runnerd.lock")

VERIFIED_MODULE_PATHS = {
    "gemini_auditor_adapter": "tools/skeleton_core/gemini_auditor_adapter.py",
    "dual_brain_task_packet": "tools/skeleton_core/dual_brain_task_packet.py",
    "issue_to_gemini_audit": "tools/skeleton_core/issue_to_gemini_audit.py",
    "yellow_gemini_audit_route": "tools/skeleton_core/yellow_gemini_audit_route.py",
    "yellow_runnerd": "tools/skeleton_core/yellow_runnerd.py",
    "bounded_execution_packet": "tools/skeleton_core/bounded_execution_packet.py",
    "dry_run_execution_route": "tools/skeleton_core/dry_run_execution_route.py",
    "active_executor": "tools/skeleton_core/active_executor.py",
}


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _repo_root(repo_root: str | Path | None = None) -> Path:
    return Path(repo_root).resolve() if repo_root else Path.cwd().resolve()


def _knowledge_base_dir(repo_root: str | Path | None = None) -> Path:
    kb_dir = _repo_root(repo_root) / "knowledge_base"
    kb_dir.mkdir(parents=True, exist_ok=True)
    return kb_dir


def _git_head_hash(repo_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=True,
        )
        return completed.stdout.strip()
    except Exception:
        return ""


def _pid_is_running(pid: int) -> bool:
    return pid > 0 and Path(f"/proc/{pid}").exists()


def _daemon_status(lock_file: Path = DEFAULT_LOCK_FILE) -> dict[str, Any]:
    lock_exists = lock_file.exists()
    pid: int | None = None

    if lock_exists:
        raw = lock_file.read_text(encoding="utf-8", errors="replace").strip()
        if raw.isdigit():
            pid = int(raw)

    return {
        "lock_file": str(lock_file),
        "lock_exists": lock_exists,
        "pid": pid,
        "process_running": _pid_is_running(pid) if pid is not None else False,
    }


def _verified_modules(repo_root: Path) -> dict[str, bool]:
    return {
        name: (repo_root / relative_path).exists()
        for name, relative_path in VERIFIED_MODULE_PATHS.items()
    }


def _read_previous_snapshot(snapshot_path: Path) -> dict[str, Any]:
    if not snapshot_path.exists():
        return {}
    try:
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def append_to_skeleton_diary(entry: str, *, repo_root: str | Path | None = None) -> Path:
    kb_dir = _knowledge_base_dir(repo_root)
    diary_path = kb_dir / "skeleton_diary.md"

    if not diary_path.exists():
        diary_path.write_text(
            "# Skeleton Technical Diary\n\n"
            "Append-only technical memory for Skeleton Core operations.\n\n",
            encoding="utf-8",
        )

    with diary_path.open("a", encoding="utf-8") as handle:
        handle.write(f"## {utc_now_iso()}\n\n")
        handle.write("- source: skeleton_core\n")
        handle.write("- memory_layer: L2_skeleton_diary\n")
        handle.write(f"- entry: {entry.strip()}\n\n")

    return diary_path


def create_system_snapshot(
    *,
    last_processed_issue_id: int | None = None,
    repo_root: str | Path | None = None,
    lock_file: str | Path = DEFAULT_LOCK_FILE,
) -> Path:
    root = _repo_root(repo_root)
    kb_dir = _knowledge_base_dir(root)
    snapshot_path = kb_dir / "current_state.json"

    previous = _read_previous_snapshot(snapshot_path)
    effective_last_issue = (
        last_processed_issue_id
        if last_processed_issue_id is not None
        else previous.get("last_processed_issue_id")
    )

    snapshot = {
        "schema_version": "skeleton_current_state.v1",
        "generated_at_utc": utc_now_iso(),
        "memory_layer": "L1_system_snapshot",
        "last_processed_issue_id": effective_last_issue,
        "active_daemon_status": _daemon_status(Path(lock_file)),
        "git_head_hash": _git_head_hash(root),
        "verified_modules": _verified_modules(root),
    }

    snapshot_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return snapshot_path
