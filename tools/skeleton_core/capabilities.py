"""Public-safe Skeleton capability registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkeletonCapability:
    """Static metadata for a safe Skeleton CLI capability."""

    name: str
    description: str
    read_only: bool = True
    merge_allowed: bool = False
    deploy_allowed: bool = False


CAPABILITIES: dict[str, SkeletonCapability] = {
    "branch-recovery": SkeletonCapability(
        name="branch-recovery",
        description="Recover interrupted branch state from a public-safe export.",
    ),
    "checkpoint": SkeletonCapability(
        name="checkpoint",
        description="Render a compact checkpoint packet from a trace.",
    ),
    "handoff-pack": SkeletonCapability(
        name="handoff-pack",
        description="Render a compact public-safe Skeleton handoff.",
    ),
    "issue-dispatch": SkeletonCapability(
        name="issue-dispatch",
        description="Normalize a public-safe issue export into a runner-ready packet.",
    ),
    "issue-runner-bridge": SkeletonCapability(
        name="issue-runner-bridge",
        description="Build a GREEN/YELLOW runner packet from a public-safe issue export.",
    ),
    "job-log-summary": SkeletonCapability(
        name="job-log-summary",
        description="Summarize a public-safe CI/job log excerpt.",
    ),
    "pr-review-gate": SkeletonCapability(
        name="pr-review-gate",
        description="Decide whether a PR export is ready for ChatGPT/Oleksii review.",
    ),
    "queue-state": SkeletonCapability(
        name="queue-state",
        description="Select next safe runnable item from a public-safe queue export.",
    ),
    "runner-command-pack": SkeletonCapability(
        name="runner-command-pack",
        description="Build a compact runner instruction from a safe task packet.",
    ),
    "runner-report-ingest": SkeletonCapability(
        name="runner-report-ingest",
        description="Normalize a public-safe runner report into status JSON.",
    ),
    "task-lifecycle": SkeletonCapability(
        name="task-lifecycle",
        description="Build a compact lifecycle packet from a public-safe issue export.",
    ),
    "validate-state": SkeletonCapability(
        name="validate-state",
        description="Validate Skeleton boot and current-state files.",
    ),
}

APPLICATION_FLOW = [
    "issue-dispatch",
    "runner-command-pack",
    "runner-report-ingest",
    "pr-review-gate",
    "branch-recovery",
]
SKELETON_CORE_FLOW = [
    "issue-dispatch",
    "runner-command-pack",
    "runner-report-ingest",
    "pr-review-gate",
    "branch-recovery",
    "queue-state",
    "validate-state",
    "handoff-pack",
]

DANGEROUS_DEFAULT_MARKERS = {
    "auto merge allowed",
    "auto merge without approval",
    "auto-merge allowed",
    "auto-merge without approval",
    "automerge allowed",
    "automerge without approval",
    "deploy allowed",
    "deploy without approval",
    "merge allowed",
    "merge without approval",
    "production db write",
    "read .env",
    "secrets access",
    "server ssh allowed",
}

SAFE_FORBIDDEN_MARKERS = {
    ".env",
    "automerge",
    "deploy",
    "external credentials",
    "merge",
    "production db",
    "secrets",
    "server ssh",
}


def known_capability_names() -> set[str]:
    """Return known safe Skeleton capability names."""
    return set(CAPABILITIES)


def capability_flow(project_type: str, allowed_capabilities: list[str]) -> list[str]:
    """Return deterministic flow filtered by allowed capabilities."""
    allowed = set(allowed_capabilities)
    canonical_flow = SKELETON_CORE_FLOW if project_type == "skeleton-core" else APPLICATION_FLOW
    return [capability for capability in canonical_flow if capability in allowed]
