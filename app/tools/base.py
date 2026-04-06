from typing import Any

from pydantic import BaseModel


class ToolResult(BaseModel):
    success: bool
    output: Any
    error: str | None = None

class BaseTool:
    name: str
    description: str

    async def execute(self, **kwargs) -> ToolResult:
        raise NotImplementedError
