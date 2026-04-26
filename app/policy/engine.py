from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from app.core.exceptions import PolicyViolationError


@dataclass
class PolicyContext:
    """All information needed for a policy decision."""

    request_tool: str | None = None  # tool name being requested
    provider_name: str | None = None  # provider being selected
    allow_tools: bool = False  # did user opt in to tools?
    task_message: str = ""  # raw user message
    is_code_execution: bool = False  # is this a shell/code-exec request?


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str


class PolicyEngine:
    """
    Evaluates policy rules before tools, providers, and code execution are invoked.

    Design: deny by default. Permissions must be explicitly enabled via config.
    No exceptions to the self-modification rule regardless of config (unless flag is set).
    """

    def check_tool_access(self, tool_name: str, allow_tools: bool) -> PolicyDecision:
        """
        Deny tool execution unless:
        1. The request includes allow_tools=True
        2. The specific tool is enabled in config
        """
        if not allow_tools:
            return PolicyDecision(
                allowed=False,
                reason=f"Tool '{tool_name}' denied: allow_tools is false for this request",
            )

        tool_gates: dict[str, bool] = {
            "shell": settings.tool_shell_enabled,
            "filesystem": settings.tool_filesystem_enabled,
            "http_fetch": settings.tool_http_enabled,
        }

        enabled = tool_gates.get(tool_name, False)
        if not enabled:
            return PolicyDecision(
                allowed=False,
                reason=f"Tool '{tool_name}' denied: disabled in configuration",
            )

        return PolicyDecision(allowed=True, reason="allowed")

    def check_provider_access(self, provider_name: str) -> PolicyDecision:
        """Verify the provider is permitted. All known providers are allowed unless cloud is off."""
        if provider_name == "openrouter" and not settings.enable_cloud_fallback:
            return PolicyDecision(
                allowed=False,
                reason="OpenRouter denied: cloud fallback is disabled",
            )
        return PolicyDecision(allowed=True, reason="allowed")

    def check_self_modification(self, message: str) -> PolicyDecision:
        """
        Block any attempt to modify system code through the runtime path.
        Only bypassed if SELF_MODIFICATION_ENABLED is explicitly True.
        """
        if settings.self_modification_enabled:
            return PolicyDecision(allowed=True, reason="self-modification explicitly enabled")

        _self_mod_signals = [
            "modify your own code",
            "edit your source",
            "update yourself",
            "rewrite your code",
            "change your instructions",
            "patch yourself",
        ]
        lower = message.lower()
        for signal in _self_mod_signals:
            if signal in lower:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Self-modification denied: message contains prohibited signal '{signal}'",
                )
        return PolicyDecision(allowed=True, reason="no self-modification signal detected")

    def enforce_tool_access(self, tool_name: str, allow_tools: bool) -> None:
        """Raise PolicyViolationError if tool access is denied."""
        decision = self.check_tool_access(tool_name, allow_tools)
        if not decision.allowed:
            raise PolicyViolationError(decision.reason)

    def enforce_provider_access(self, provider_name: str) -> None:
        """Raise PolicyViolationError if provider access is denied."""
        decision = self.check_provider_access(provider_name)
        if not decision.allowed:
            raise PolicyViolationError(decision.reason)

    def enforce_self_modification(self, message: str) -> None:
        """Raise PolicyViolationError if self-modification is detected."""
        decision = self.check_self_modification(message)
        if not decision.allowed:
            raise PolicyViolationError(decision.reason)
