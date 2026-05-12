"""Allowlist-only read service for Skeleton canon audit routes.

Sprint 11 boundary:
- read only predefined files
- fail closed on non-allowlisted paths
- fail closed on secret patterns
- no file writes
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

CANON_READER_SCHEMA_VERSION: Final[str] = "skeleton_canon_reader.v1"

ALLOWED_CANON_PATHS: Final[tuple[str, ...]] = (
    "BOOTLOADER.md",
    "knowledge_base/START_HERE_FOR_CHATGPT.md",
    "knowledge_base/MEMORY_POLICY.md",
    "knowledge_base/WORKING_PROTOCOL.md",
    "knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md",
    "knowledge_base/assistant_diary.md",
    "knowledge_base/CHATGPT_EXOSKELETON.md",
    "knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md",
    "knowledge_base/chatgpt_exoskeleton/START_HERE.md",
    "knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md",
    "docs/dual_brain_state.md",
)

SECRET_PATTERNS: Final[tuple[str, ...]] = (
    r"sk-[A-Za-z0-9_\-]{20,}",
    r"AIza[0-9A-Za-z_\-]{20,}",
    r"ghp_[A-Za-z0-9_]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"OPENAI_API_KEY\s*=",
    r"GEMINI_API_KEY\s*=",
    r"GOOGLE_API_KEY\s*=",
)


class CanonReaderPanic(RuntimeError):
    """Fail-closed canon reader panic."""


def repo_root(path: str | Path | None = None) -> Path:
    if path is not None:
        return Path(path).resolve()

    return Path.cwd().resolve()


def _relative_posix(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as err:
        raise CanonReaderPanic(f"path_outside_repo:{path}") from err


def validate_canon_path(path: str | Path, *, root: str | Path | None = None) -> Path:
    base = repo_root(root)
    candidate = Path(path)

    resolved = candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()
    rel = _relative_posix(resolved, base)

    if rel not in ALLOWED_CANON_PATHS:
        raise CanonReaderPanic(f"canon_path_not_allowlisted:{rel}")

    if not resolved.exists():
        raise CanonReaderPanic(f"canon_path_missing:{rel}")

    if not resolved.is_file():
        raise CanonReaderPanic(f"canon_path_not_file:{rel}")

    return resolved


def scan_sensitive_text(text: str) -> list[str]:
    hits: list[str] = []

    for pattern in SECRET_PATTERNS:
        if re.search(pattern, text):
            hits.append(pattern)

    return hits


def read_canon_file(path: str | Path, *, root: str | Path | None = None) -> tuple[str, str]:
    base = repo_root(root)
    resolved = validate_canon_path(path, root=base)
    rel = _relative_posix(resolved, base)
    text = resolved.read_text(encoding="utf-8", errors="replace")

    hits = scan_sensitive_text(text)
    if hits:
        raise CanonReaderPanic(f"secret_pattern_detected:{rel}:{','.join(hits)}")

    return rel, text


def build_canon_bundle(
    paths: tuple[str, ...] | list[str] | None = None,
    *,
    root: str | Path | None = None,
) -> str:
    selected = tuple(paths) if paths is not None else ALLOWED_CANON_PATHS

    parts: list[str] = []

    for path in selected:
        rel, text = read_canon_file(path, root=root)
        parts.append(f"\n\n--- FILE: {rel} ---\n{text}\n")

    return "".join(parts)
