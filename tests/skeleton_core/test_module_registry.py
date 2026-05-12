from __future__ import annotations

from tools.skeleton_core.module_registry import (
    get_module_entry,
    list_module_entries,
    module_registry_payload,
    render_module_registry_markdown,
)

REQUIRED_MODULES = {
    "runner-status-check",
    "runner-env-check",
    "canon-audit",
    "workflow-gate",
    "queue-state",
    "pr-status",
    "pr-review-gate",
    "issue-runner-bridge",
    "issue-dispatch",
    "runner-command-pack",
    "runner-report-ingest",
    "runner-report-from-trace",
    "format-preflight",
    "validate-state",
}


def test_registry_contains_required_entries() -> None:
    names = {entry.name for entry in list_module_entries()}

    assert names >= REQUIRED_MODULES


def test_registry_module_names_are_unique() -> None:
    names = [entry.name for entry in list_module_entries()]

    assert len(names) == len(set(names))


def test_registry_entries_have_required_fields() -> None:
    for entry in list_module_entries():
        assert entry.name
        assert entry.purpose
        assert entry.status in {"stable", "experimental", "deprecated"}
        assert entry.cli_command.startswith("python -m tools.skeleton_core.cli ")
        assert entry.input_schema
        assert entry.output_schema
        assert entry.risk_level in {"GREEN", "YELLOW", "ORANGE", "RED"}
        assert isinstance(entry.side_effects, bool)
        assert entry.allowed_actions
        assert entry.forbidden_actions
        assert entry.execution_authority is False


def test_registry_lookup_by_name_works_for_runner_status_check() -> None:
    entry = get_module_entry("runner-status-check")

    assert entry is not None
    assert entry.name == "runner-status-check"
    assert entry.side_effects is False
    assert entry.execution_authority is False


def test_unknown_registry_lookup_returns_none() -> None:
    assert get_module_entry("missing-module") is None


def test_registry_payload_can_return_all_or_one() -> None:
    all_payload = module_registry_payload()
    one_payload = module_registry_payload(command="runner-status-check")

    assert isinstance(all_payload, list)
    assert isinstance(one_payload, dict)
    assert one_payload["name"] == "runner-status-check"
    assert one_payload["execution_authority"] is False


def test_markdown_renderer_outputs_static_table() -> None:
    markdown = render_module_registry_markdown(list_module_entries())

    assert "| Module | Status | Risk | Side effects | Purpose |" in markdown
    assert "`runner-status-check`" in markdown
