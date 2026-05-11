"""CLI helper for atomic report creation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.skeleton_core.atomic_writer import safe_write
from tools.skeleton_core.memory_service import append_to_skeleton_diary, utc_now_iso


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a Skeleton report atomically.")
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--input-json", default="")
    parser.add_argument("--content", default="")
    args = parser.parse_args(argv)

    if args.input_json:
        content = Path(args.input_json).read_text(encoding="utf-8")
    elif args.content:
        content = args.content
    else:
        content = (
            json.dumps(
                {
                    "schema_version": "skeleton_self_integrity_report.v1",
                    "issue_number": args.issue,
                    "generated_at_utc": utc_now_iso(),
                    "status": "created_by_cli_create_report",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )

    written = safe_write(args.target, content)

    append_to_skeleton_diary(
        f"[REAL_WRITE] Module cli_create_report wrote {written} for Issue #{args.issue}."
    )

    print(
        json.dumps(
            {
                "ok": True,
                "issue": args.issue,
                "target": str(written),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
