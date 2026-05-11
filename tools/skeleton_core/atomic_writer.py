"""Atomic Green Zone writer for Skeleton Core.

Allowed write paths:
- knowledge_base/active_tasks/
- knowledge_base/reports/

Forbidden immutable zones:
- src/
- tests/
- canon/
"""

from __future__ import annotations

import os
import tempfile
from contextlib import suppress
from pathlib import Path

ALLOWED_WRITE_PATHS = [
    "knowledge_base/active_tasks/",
    "knowledge_base/reports/",
]

IMMUTABLE_PATHS = [
    "src/",
    "tests/",
    "canon/",
]


class AtomicWritePanic(RuntimeError):
    """Fail-closed write panic."""


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_write_path(target_path: str | Path, *, repo_root: str | Path | None = None) -> Path:
    root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    target = (
        (root / target_path).resolve()
        if not Path(target_path).is_absolute()
        else Path(target_path).resolve()
    )

    for raw in IMMUTABLE_PATHS:
        immutable = (root / raw).resolve()
        if _inside(target, immutable):
            raise AtomicWritePanic(f"panic_write_to_immutable_path:{target}")

    for raw in ALLOWED_WRITE_PATHS:
        allowed = (root / raw).resolve()
        if _inside(target, allowed):
            return target

    raise AtomicWritePanic(f"panic_write_outside_green_zone:{target}")


def safe_write(
    target_path: str | Path, content: str, *, repo_root: str | Path | None = None
) -> Path:
    target = validate_write_path(target_path, repo_root=repo_root)
    target.parent.mkdir(parents=True, exist_ok=True)

    tmp_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            tmp_name = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(tmp_name, target)
        return target
    except Exception:
        if tmp_name:
            with suppress(Exception):
                Path(tmp_name).unlink(missing_ok=True)
        raise
