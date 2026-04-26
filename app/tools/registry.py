from app.tools.base import BaseTool, ToolResult


class ShellScaffoldTool(BaseTool):
    name = "shell"
    description = "Extremely dangerous shell execution. Mocked as a disabled scaffold."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            success=False, output=None, error="Shell execution is disabled by default policies."
        )


class ToolRegistry:
    def __init__(self):
        self._tools = {"shell": ShellScaffoldTool()}

    def get_tool(self, name: str) -> BaseTool:
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found.")
        return tool
