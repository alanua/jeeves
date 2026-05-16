"""CLI wiring for the public-safe deep-diff audit packet builder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from tools.skeleton_core.deep_diff_audit_pack import (
    build_deep_diff_audit_pack_from_json,
    packet_to_json_dict,
)


def _print_error(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr, flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a public-safe deep-diff evidence packet from JSON."
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to public-safe deep-diff evidence packet JSON",
    )
    args = parser.parse_args(argv)

    try:
        raw_json = args.input.read_text(encoding="utf-8")
    except OSError as err:
        _print_error(
            {
                "ok": False,
                "error": "input_read_failed",
                "input": str(args.input),
                "detail": str(err),
            }
        )
        return 1

    try:
        packet = build_deep_diff_audit_pack_from_json(raw_json)
    except ValidationError as err:
        _print_error(
            {
                "ok": False,
                "error": "input_validation_failed",
                "input": str(args.input),
                "detail": err.errors(include_url=False),
            }
        )
        return 2

    print(json.dumps(packet_to_json_dict(packet), ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
