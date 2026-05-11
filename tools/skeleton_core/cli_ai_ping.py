"""Read-only AI connectivity ping for Skeleton Core."""

from __future__ import annotations

import argparse
import json

from tools.skeleton_core.llm_service import (
    LLMServicePanic,
    query_gemini,
    query_openai,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only AI API connectivity ping.")
    parser.add_argument("--openai-model", default="gpt-4o")
    parser.add_argument("--gemini-model", default="gemini-2.5-pro")
    args = parser.parse_args(argv)

    try:
        openai_text = query_openai(
            "Respond with exactly: Ping OpenAI OK",
            model=args.openai_model,
        )
        gemini_text = query_gemini(
            "Respond with exactly: Ping Gemini OK",
            model=args.gemini_model,
        )
    except LLMServicePanic as err:
        print(
            json.dumps(
                {
                    "ok": False,
                    "schema_version": "skeleton_ai_ping.v1",
                    "error": str(err),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1
    except Exception as err:
        print(
            json.dumps(
                {
                    "ok": False,
                    "schema_version": "skeleton_ai_ping.v1",
                    "error": f"ai_ping_failed:{type(err).__name__}:{err}",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    result = {
        "ok": True,
        "schema_version": "skeleton_ai_ping.v1",
        "mode": "read_only_connectivity_check",
        "openai": {
            "model": args.openai_model,
            "response": openai_text,
            "matched_expected": openai_text.strip() == "Ping OpenAI OK",
        },
        "gemini": {
            "model": args.gemini_model,
            "response": gemini_text,
            "matched_expected": gemini_text.strip() == "Ping Gemini OK",
        },
        "writes_files": False,
        "creates_pr": False,
        "executes_commands": False,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["openai"]["matched_expected"] and result["gemini"]["matched_expected"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
