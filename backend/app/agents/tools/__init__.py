from .registry import ToolRegistry, ToolDefinition, ToolResult
from .pipeline_tools import pipeline_overview_tool, deal_metrics_tool
from .operational_tools import sector_performance_tool, cross_board_metrics_tool, work_order_metrics_tool

def get_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(pipeline_overview_tool)
    registry.register(deal_metrics_tool)
    registry.register(sector_performance_tool)
    registry.register(cross_board_metrics_tool)
    registry.register(work_order_metrics_tool)
    return registry

__all__ = [
    "ToolRegistry",
    "ToolDefinition",
    "ToolResult",
    "get_default_registry"
]
