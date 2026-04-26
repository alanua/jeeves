from app.policy.engine import PolicyEngine
from app.tools.registry import ToolRegistry


class ToolHandler:
    """Service to handle explicit tool requests before passing control to the LLM agent."""

    def __init__(self, policy: PolicyEngine, tool_registry: ToolRegistry):
        self._policy = policy
        self._tool_registry = tool_registry

    async def handle_tool_intent(
        self, message: str, allow_tools: bool
    ) -> tuple[list[dict], str | None]:
        """
        Parses explicit tool intent from the message and attempts tool execution
        or returns a structured denial based on policy.

        Returns:
            (tool_calls, warning_message)
        """
        tool_calls = []
        warning = None

        if allow_tools and message.startswith("tool:shell "):
            decision = self._policy.check_tool_access("shell", allow_tools=allow_tools)
            if not decision.allowed:
                tool_calls.append(
                    {
                        "tool": "shell",
                        "status": "denied",
                        "reason": decision.reason,
                        "arguments": message[len("tool:shell ") :].strip(),
                    }
                )
                warning = decision.reason
            else:
                # Execution attempt (fallback, though shell is disabled by default)
                tool = self._tool_registry.get_tool("shell")
                res = await tool.execute()
                if not res.success:
                    tool_calls.append(
                        {
                            "tool": "shell",
                            "status": "denied",
                            "reason": str(res.error),
                            "arguments": message[len("tool:shell ") :].strip(),
                        }
                    )
                    warning = str(res.error)

        return tool_calls, warning
