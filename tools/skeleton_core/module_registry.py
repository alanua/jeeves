"""Static Skeleton module registry.

This registry is an explicit, deterministic self-inventory of known Skeleton
modules. It is intentionally static for v0.

It must not:
- scan files;
- dynamically import modules;
- execute registered commands;
- call network/GitHub APIs;
- mutate labels/issues/files;
- grant merge/deploy authority.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ModuleStatus = Literal["stable", "experimental", "deprecated"]
RiskLevelName = Literal["GREEN", "YELLOW", "ORANGE", "RED"]


class ModuleParameter(BaseModel):
    """Public-safe CLI parameter metadata."""

    model_config = ConfigDict(extra="forbid")

    name: str
    required: bool = False
    description: str = ""


class ModuleRegistryEntry(BaseModel):
    """Public-safe module passport."""

    model_config = ConfigDict(extra="forbid")

    name: str
    purpose: str
    status: ModuleStatus
    cli_command: str
    parameters: list[ModuleParameter] = Field(default_factory=list)
    input_schema: str
    output_schema: str
    risk_level: RiskLevelName
    side_effects: bool
    allowed_actions: list[str]
    forbidden_actions: list[str]
    execution_authority: bool = False
    related_tests: list[str] = Field(default_factory=list)
    related_issues: list[int] = Field(default_factory=list)
    related_prs: list[int] = Field(default_factory=list)
    canon_source: str = ""
    example_invocations: list[str] = Field(default_factory=list)


REQUIRED_FORBIDDEN_ACTIONS = [
    "execute registered commands",
    "read .env",
    "print secrets",
    "merge",
    "deploy",
]


MODULE_REGISTRY: tuple[ModuleRegistryEntry, ...] = (
    ModuleRegistryEntry(
        name="runner-status-check",
        purpose="Build a public-safe runner/task status packet from offline evidence or fail closed without live collection.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli runner-status-check",
        parameters=[
            ModuleParameter(name="--input", description="Public-safe runner status fixture JSON"),
            ModuleParameter(name="--repo", description="Repository for fail-closed placeholder"),
            ModuleParameter(name="--issue", description="Issue number for fail-closed placeholder"),
        ],
        input_schema="RunnerStatusCheckInput JSON or repo/issue placeholder",
        output_schema="RunnerStatusCheckPacket JSON",
        risk_level="YELLOW",
        side_effects=False,
        allowed_actions=[
            "classify supplied public-safe status evidence",
            "return fail-closed needs_manual_review",
        ],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS
        + ["inspect live logs", "kill processes", "restart services"],
        related_tests=[
            "tests/skeleton_core/test_runner_status_check.py",
            "tests/skeleton_core/test_runner_status_cli.py",
        ],
        related_issues=[146, 153],
        related_prs=[151, 154],
        canon_source="#151, #154",
        example_invocations=[
            "python -m tools.skeleton_core.cli runner-status-check --input tests/fixtures/runner_status_check_running.json",
            "python -m tools.skeleton_core.cli runner-status-check --repo alanua/bauclock --issue 48",
        ],
    ),
    ModuleRegistryEntry(
        name="runner-env-check",
        purpose="Check runner environment readiness from an offline fixture or explicitly bounded live preflight arguments.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli runner-env-check",
        parameters=[
            ModuleParameter(name="--input", description="Offline environment fixture JSON"),
            ModuleParameter(
                name="--repo-url", description="Repository URL for bounded live preflight"
            ),
            ModuleParameter(
                name="--workdir", description="Disposable workdir for bounded live preflight"
            ),
            ModuleParameter(
                name="--allow-network-check", description="Explicitly allow network checks"
            ),
            ModuleParameter(name="--skip-clone-check", description="Skip clone check"),
        ],
        input_schema="RunnerEnvCheckInput JSON or bounded repo/workdir arguments",
        output_schema="RunnerEnvCheckPacket JSON",
        risk_level="YELLOW",
        side_effects=True,
        allowed_actions=[
            "validate explicit environment evidence",
            "perform bounded preflight when explicitly requested",
        ],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["mutate issues", "restart runner services"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/runner_env_check.py",
        example_invocations=[
            "python -m tools.skeleton_core.cli runner-env-check --input tests/fixtures/runner_env_check_ready.json"
        ],
    ),
    ModuleRegistryEntry(
        name="canon-audit",
        purpose="Run the specialized Skeleton canon-audit route for an already prepared audit issue.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli canon-audit",
        parameters=[
            ModuleParameter(
                name="--repo", required=True, description="Repository in owner/name form"
            ),
            ModuleParameter(name="--issue", required=True, description="Audit issue number"),
            ModuleParameter(name="--model", description="Gemini model name"),
            ModuleParameter(
                name="--no-labels", description="Disable label mutation when supported"
            ),
        ],
        input_schema="GitHub repo/issue arguments",
        output_schema="skeleton_canon_audit_route.v1 JSON plus GitHub audit comment",
        risk_level="YELLOW",
        side_effects=True,
        allowed_actions=[
            "read public-safe issue context",
            "post public-safe audit evidence",
            "update audit labels",
        ],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS
        + ["write canon", "create implementation PR", "approve merge"],
        related_issues=[147, 152, 155],
        canon_source="docs/canon_audit_request_standard.md",
        example_invocations=[
            "python -m tools.skeleton_core.cli canon-audit --repo alanua/jeeves --issue 155 --model gemini-2.5-flash-lite"
        ],
    ),
    ModuleRegistryEntry(
        name="workflow-gate",
        purpose="Evaluate whether a workflow action has required prerequisites before proceeding.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli workflow-gate",
        parameters=[
            ModuleParameter(
                name="--input", required=True, description="Public-safe workflow gate JSON"
            )
        ],
        input_schema="WorkflowGateInput JSON",
        output_schema="WorkflowGate result JSON",
        risk_level="YELLOW",
        side_effects=False,
        allowed_actions=["evaluate prerequisites", "return proceed/block recommendation"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["perform workflow action"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/workflow_gate.py",
    ),
    ModuleRegistryEntry(
        name="queue-state",
        purpose="Determine next runnable item from a public-safe queue state fixture.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli queue-state",
        parameters=[
            ModuleParameter(
                name="--input", required=True, description="Public-safe queue state JSON"
            ),
            ModuleParameter(name="--project", description="Optional project label"),
        ],
        input_schema="QueueStateInput JSON",
        output_schema="QueueState result JSON",
        risk_level="YELLOW",
        side_effects=False,
        allowed_actions=["rank queue items", "return next runnable recommendation"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["claim issues", "change labels"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/queue_state.py",
    ),
    ModuleRegistryEntry(
        name="pr-status",
        purpose="Build a deterministic PR status packet from public-safe PR JSON.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli pr-status",
        parameters=[
            ModuleParameter(name="--input", required=True, description="Public-safe PR status JSON")
        ],
        input_schema="PRStatusInput JSON",
        output_schema="PR status packet JSON",
        risk_level="YELLOW",
        side_effects=False,
        allowed_actions=["summarize PR state", "flag review/merge readiness"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["merge PR", "approve PR"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/pr_status.py",
    ),
    ModuleRegistryEntry(
        name="pr-review-gate",
        purpose="Decide whether a public-safe PR export is ready for ChatGPT review.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli pr-review-gate",
        parameters=[
            ModuleParameter(
                name="--input", required=True, description="Public-safe PR review gate JSON"
            )
        ],
        input_schema="PRReviewGateInput JSON",
        output_schema="PR review gate result JSON",
        risk_level="YELLOW",
        side_effects=False,
        allowed_actions=["evaluate review readiness", "return blockers"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["merge PR", "request deployment"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/pr_review_gate.py",
    ),
    ModuleRegistryEntry(
        name="issue-runner-bridge",
        purpose="Build a GREEN/YELLOW runner packet from public-safe issue JSON.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli issue-runner-bridge",
        parameters=[
            ModuleParameter(
                name="--input", required=True, description="Public-safe GitHub issue JSON"
            )
        ],
        input_schema="IssueRunnerInput JSON",
        output_schema="Issue runner packet JSON",
        risk_level="YELLOW",
        side_effects=False,
        allowed_actions=["normalize issue into runner packet"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["run the packet", "claim the issue"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/issue_runner_bridge.py",
    ),
    ModuleRegistryEntry(
        name="issue-dispatch",
        purpose="Normalize a public-safe issue export for runner bridge, optionally passing it through local bridge logic.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli issue-dispatch",
        parameters=[
            ModuleParameter(
                name="--input", required=True, description="Public-safe GitHub issue JSON"
            ),
            ModuleParameter(
                name="--run-bridge", description="Run normalized packet through bridge locally"
            ),
            ModuleParameter(
                name="--parent-queue", description="Optional parent queue issue number"
            ),
            ModuleParameter(
                name="--depends-on", description="Optional comma-separated dependency issue numbers"
            ),
        ],
        input_schema="IssueDispatchInput JSON",
        output_schema="Issue dispatch packet JSON",
        risk_level="YELLOW",
        side_effects=False,
        allowed_actions=["normalize public-safe issue data", "build local dispatch packet"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["mutate GitHub issue", "start daemon work"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/issue_dispatch.py",
    ),
    ModuleRegistryEntry(
        name="runner-command-pack",
        purpose="Build a compact runner command from public-safe JSON without executing it.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli runner-command-pack",
        parameters=[
            ModuleParameter(
                name="--input", required=True, description="Public-safe runner command JSON"
            )
        ],
        input_schema="RunnerCommandInput JSON",
        output_schema="Runner command pack JSON",
        risk_level="YELLOW",
        side_effects=False,
        allowed_actions=["render command recommendation"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["execute rendered command"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/runner_command_pack.py",
    ),
    ModuleRegistryEntry(
        name="runner-report-ingest",
        purpose="Normalize public-safe runner report text into status JSON.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli runner-report-ingest",
        parameters=[
            ModuleParameter(
                name="--input", required=True, description="Public-safe runner report text"
            )
        ],
        input_schema="Public-safe runner report text",
        output_schema="Runner report ingest JSON",
        risk_level="GREEN",
        side_effects=False,
        allowed_actions=["parse supplied report text", "return status summary"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["modify issue labels"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/runner_report_ingest.py",
    ),
    ModuleRegistryEntry(
        name="runner-report-from-trace",
        purpose="Render a short runner report from a public-safe TracePacket JSON file.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli runner-report-from-trace",
        parameters=[
            ModuleParameter(
                name="--input", required=True, description="Public-safe TracePacket JSON"
            )
        ],
        input_schema="TracePacket JSON",
        output_schema="Markdown/text runner report",
        risk_level="GREEN",
        side_effects=False,
        allowed_actions=["render report from trace"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["post report"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/report.py",
    ),
    ModuleRegistryEntry(
        name="format-preflight",
        purpose="Check formatting readiness before CI using offline fixture or explicit paths.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli format-preflight",
        parameters=[
            ModuleParameter(name="--input", description="Offline format fixture JSON"),
            ModuleParameter(name="--paths", description="Explicit paths for live check-only mode"),
            ModuleParameter(
                name="--check-only", description="Compatibility flag; live mode is check-only"
            ),
        ],
        input_schema="FormatPreflightInput JSON or explicit paths",
        output_schema="Format preflight result JSON",
        risk_level="YELLOW",
        side_effects=False,
        allowed_actions=["check formatting status"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["auto-format files"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/format_preflight.py",
    ),
    ModuleRegistryEntry(
        name="validate-state",
        purpose="Validate Skeleton boot and current-state files in a repository root.",
        status="stable",
        cli_command="python -m tools.skeleton_core.cli validate-state",
        parameters=[ModuleParameter(name="--root", description="Repository root to validate")],
        input_schema="Repository root path",
        output_schema="State validation JSON/text result",
        risk_level="GREEN",
        side_effects=False,
        allowed_actions=["read expected state files", "report validation findings"],
        forbidden_actions=REQUIRED_FORBIDDEN_ACTIONS + ["modify state files"],
        related_tests=["tests/skeleton_core"],
        canon_source="tools/skeleton_core/state_validator.py",
    ),
)


def list_module_entries() -> list[ModuleRegistryEntry]:
    """Return all static module registry entries."""
    return list(MODULE_REGISTRY)


def get_module_entry(name: str) -> ModuleRegistryEntry | None:
    """Return one registry entry by module name."""
    normalized = name.strip().casefold()
    for entry in MODULE_REGISTRY:
        if entry.name.casefold() == normalized:
            return entry
    return None


def module_registry_payload(*, command: str | None = None) -> list[dict] | dict | None:
    """Return JSON-serializable registry data."""
    if command:
        entry = get_module_entry(command)
        if entry is None:
            return None
        return entry.model_dump(mode="json")
    return [entry.model_dump(mode="json") for entry in MODULE_REGISTRY]


def render_module_registry_markdown(entries: list[ModuleRegistryEntry]) -> str:
    """Render registry entries as compact Markdown."""
    lines = [
        "| Module | Status | Risk | Side effects | Purpose |",
        "|---|---:|---:|---:|---|",
    ]
    for entry in entries:
        side_effects = "yes" if entry.side_effects else "no"
        lines.append(
            f"| `{entry.name}` | {entry.status} | {entry.risk_level} | {side_effects} | {entry.purpose} |"
        )
    return "\n".join(lines)
