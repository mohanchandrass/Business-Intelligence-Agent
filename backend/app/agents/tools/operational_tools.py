from typing import Any
from pydantic import BaseModel, Field
from typing import Optional

from app.application.snapshot import BusinessDataSnapshot
from app.analytics.sectors import SectorAnalytics
from app.analytics.cross_board import CrossBoardAnalytics
from app.analytics.work_orders import WorkOrderAnalytics
from app.agents.tools.registry import ToolDefinition, ToolResult

class EmptyArgs(BaseModel):
    pass

class SectorArgs(BaseModel):
    sector_name: Optional[str] = Field(None, description="The specific sector to query. Omit to get data for all sectors.")

async def get_sector_performance(snapshot: BusinessDataSnapshot, args: SectorArgs) -> ToolResult:
    analytics = SectorAnalytics(snapshot)
    result = analytics.get_sector_performance(args.sector_name)
    
    return ToolResult(
        tool_name="get_sector_performance",
        success=True,
        data={
            "kpis": result.kpis,
            "tables": result.tables
        },
        warnings=result.warnings
    )

async def get_cross_board_metrics(snapshot: BusinessDataSnapshot, args: EmptyArgs) -> ToolResult:
    analytics = CrossBoardAnalytics(snapshot)
    result = analytics.get_cross_board_metrics()
    
    return ToolResult(
        tool_name="get_cross_board_metrics",
        success=True,
        data={
            "kpis": result.kpis,
            "tables": result.tables
        },
        warnings=result.warnings
    )

async def get_work_order_metrics(snapshot: BusinessDataSnapshot, args: EmptyArgs) -> ToolResult:
    analytics = WorkOrderAnalytics(snapshot)
    result = analytics.get_operational_metrics()
    
    return ToolResult(
        tool_name="get_work_order_metrics",
        success=True,
        data={
            "kpis": result.kpis,
            "tables": result.tables
        },
        warnings=result.warnings
    )

sector_performance_tool = ToolDefinition(
    name="get_sector_performance",
    description="Get pipeline and execution metrics broken down by sector. Use this to compare sectors or get metrics for a specific sector.",
    parameters_schema=SectorArgs,
    handler=get_sector_performance
)

cross_board_metrics_tool = ToolDefinition(
    name="get_cross_board_metrics",
    description="Get insights that join Deals and Work Orders together. Use this for questions about deals without work orders, or pipeline vs execution value.",
    parameters_schema=EmptyArgs,
    handler=get_cross_board_metrics
)

work_order_metrics_tool = ToolDefinition(
    name="get_work_order_metrics",
    description="Get operational metrics about work orders, including status distribution and delayed/paused counts. Use this to answer questions about operations.",
    parameters_schema=EmptyArgs,
    handler=get_work_order_metrics
)
