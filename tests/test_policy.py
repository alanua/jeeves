from __future__ import annotations

import pytest

from app.core.exceptions import PolicyViolationError
from app.policy.engine import PolicyEngine


@pytest.fixture
def policy():
    return PolicyEngine()


# --- Tool access ---

def test_tool_denied_when_allow_tools_false(policy):
    decision = policy.check_tool_access("shell", allow_tools=False)
    assert not decision.allowed
    assert "allow_tools is false" in decision.reason


def test_tool_denied_when_disabled_in_config(policy):
    # shell is disabled by default in config
    decision = policy.check_tool_access("shell", allow_tools=True)
    assert not decision.allowed
    assert "disabled in configuration" in decision.reason


def test_unknown_tool_denied(policy):
    decision = policy.check_tool_access("unknown_tool", allow_tools=True)
    assert not decision.allowed


def test_enforce_tool_raises_violation(policy):
    with pytest.raises(PolicyViolationError):
        policy.enforce_tool_access("shell", allow_tools=False)


# --- Provider access ---

def test_openrouter_denied_when_cloud_fallback_disabled(policy):
    import app.core.config as cfg
    original = cfg.settings.enable_cloud_fallback
    try:
        cfg.settings.enable_cloud_fallback = False  # type: ignore[misc]
        decision = policy.check_provider_access("openrouter")
        assert not decision.allowed
    finally:
        cfg.settings.enable_cloud_fallback = original


def test_ollama_always_allowed(policy):
    decision = policy.check_provider_access("ollama")
    assert decision.allowed


# --- Self-modification ---

def test_self_modification_blocked_by_default(policy):
    decision = policy.check_self_modification("Please modify your own code to be smarter")
    assert not decision.allowed


def test_normal_message_passes_self_modification_check(policy):
    decision = policy.check_self_modification("What is the weather like today?")
    assert decision.allowed


def test_enforce_self_modification_raises(policy):
    with pytest.raises(PolicyViolationError):
        policy.enforce_self_modification("Edit your source and update yourself")
