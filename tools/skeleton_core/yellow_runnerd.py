"""Continuous Hetzner YELLOW runner daemon.

Polls GitHub for queued YELLOW issues and routes them through the Gemini
audit gate before any later execution stage.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import signal
import sys
import time
from pathlib import Path

from tools.skeleton_core.yellow_gemini_audit_route import (
    ensure_route_labels,
    fetch_candidate_issues,
    process_issue,
)

STOP_REQUESTED = False


def _signal_handler(signum: int, frame: object | None) -> None:
    del frame
    global STOP_REQUESTED
    STOP_REQUESTED = True
    _log("shutdown_requested", signal=signum)


def _log(event: str, **payload: object) -> None:
    record = {
        "event": event,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **payload,
    }
    print(json.dumps(record, ensure_ascii=False, sort_keys=True), flush=True)


def _sleep_interruptible(seconds: float) -> None:
    deadline = time.monotonic() + seconds
    while not STOP_REQUESTED and time.monotonic() < deadline:
        time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))


def _check_live_env(mode: str) -> None:
    if mode != "live":
        return

    os.environ.setdefault("GEMINI_API_LIVE_MODE", "true")

    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        raise RuntimeError("missing_gemini_api_key_env_for_yellow_runnerd")


def _acquire_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("w", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        _log("lock_busy", lock_path=str(lock_path))
        handle.close()
        raise SystemExit(0)

    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()))
    handle.flush()
    return handle


def poll_once(
    *,
    repo: str,
    limit: int,
    mode: str,
    model: str,
    dry_run: bool,
) -> int:
    issues = fetch_candidate_issues(repo, limit=limit)
    if not issues:
        _log("no_candidates", repo=repo)
        return 0

    processed = 0
    for issue in issues:
        if STOP_REQUESTED:
            break

        _log(
            "processing_issue",
            repo=repo,
            issue_number=issue.number,
            issue_url=issue.url,
            mode=mode,
            dry_run=dry_run,
        )

        result = process_issue(
            repo,
            issue,
            mode=mode,
            model=model,
            dry_run=dry_run,
        )
        processed += 1

        _log(
            "processed_issue",
            repo=repo,
            issue_number=result.issue_number,
            outcome=result.outcome,
            adapter_status=result.adapter_status,
            comment_url=result.posted_comment_url,
            labels_added=result.labels_added,
            labels_removed=result.labels_removed,
            blocked_reasons=result.blocked_reasons,
            security_flags=result.security_flags,
            dry_run=result.dry_run,
        )

    return processed


def run_daemon(args: argparse.Namespace) -> int:
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    lock_handle = _acquire_lock(Path(args.lock_file))
    del lock_handle

    _log(
        "yellow_runnerd_started",
        repo=args.repo,
        mode=args.mode,
        model=args.model,
        poll_interval=args.poll_interval,
        limit=args.limit,
        dry_run=args.dry_run,
        once=args.once,
    )

    if not args.dry_run and not args.no_ensure_labels:
        ensure_route_labels(args.repo)

    failures = 0

    while not STOP_REQUESTED:
        try:
            _check_live_env(args.mode)
            processed = poll_once(
                repo=args.repo,
                limit=args.limit,
                mode=args.mode,
                model=args.model,
                dry_run=args.dry_run,
            )
            failures = 0

            if args.once:
                _log("yellow_runnerd_once_complete", processed=processed)
                return 0

            _sleep_interruptible(args.poll_interval)

        except Exception as exc:
            failures += 1
            backoff = min(
                args.error_backoff_max,
                args.error_backoff_initial * (2 ** max(0, failures - 1)),
            )
            _log(
                "yellow_runnerd_error",
                error_type=type(exc).__name__,
                error=str(exc),
                failures=failures,
                backoff_seconds=backoff,
            )

            if args.once:
                return 1

            _sleep_interruptible(backoff)

    _log("yellow_runnerd_stopped")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Skeleton YELLOW Gemini audit daemon.")
    parser.add_argument("--repo", default="alanua/jeeves")
    parser.add_argument("--mode", choices=["mock", "live"], default="live")
    parser.add_argument("--model", default="gemini-2.5-flash")
    parser.add_argument("--poll-interval", type=float, default=60.0)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--error-backoff-initial", type=float, default=30.0)
    parser.add_argument("--error-backoff-max", type=float, default=300.0)
    parser.add_argument(
        "--lock-file", default="/home/agent/agent-dev/runner-state/yellow_runnerd.lock"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--no-ensure-labels", action="store_true")
    args = parser.parse_args(argv)

    return run_daemon(args)


if __name__ == "__main__":
    raise SystemExit(main())
