from typing import Any
from pydantic import BaseModel

from app.application.snapshot import BusinessDataSnapshot
from app.analytics.pipeline import PipelineAnalytics
from app.analytics.deals import DealAnalytics
from app.agents.tools.registry import ToolDefinition, ToolResult

class EmptyArgs(BaseModel):
    pass

async def get_pipeline_overview(snapshot: BusinessDataSnapshot, args: EmptyArgs) -> ToolResult:
    analytics = PipelineAnalytics(snapshot)
    result = analytics.get_overview()
    
    return ToolResult(
        tool_name="get_pipeline_overview",
        success=True,
        data={
            "kpis": result.kpis,
            "tables": result.tables
        },
        warnings=result.warnings
    )

async def get_deal_metrics(snapshot: BusinessDataSnapshot, args: EmptyArgs) -> ToolResult:
    analytics = DealAnalytics(snapshot)
    result = analytics.get_metrics()
    
    return ToolResult(
        tool_name="get_deal_metrics",
        success=True,
        data={
            "kpis": result.kpis,
            "tables": result.tables
        },
        warnings=result.warnings
    )

pipeline_overview_tool = ToolDefinition(
    name="get_pipeline_overview",
    description="Get the total active pipeline value and distribution by stage. Use this to answer general questions about the pipeline.",
    parameters_schema=EmptyArgs,
    handler=get_pipeline_overview
)

deal_metrics_tool = ToolDefinition(
    name="get_deal_metrics",
    description="Get aggregated deal metrics including average value, median value, and win counts. Use this to answer questions about deal performance.",
    parameters_schema=EmptyArgs,
    handler=get_deal_metrics
)
