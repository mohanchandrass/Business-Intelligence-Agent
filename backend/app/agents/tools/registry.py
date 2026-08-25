from typing import Callable, Dict, Any, Type, Awaitable
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: Any = None
    warnings: list[str] = Field(default_factory=list)
    error: str = None

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters_schema: Type[BaseModel]
    handler: Callable[..., Awaitable[ToolResult]]

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolDefinition:
        return self._tools.get(name)

    def get_all_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())
