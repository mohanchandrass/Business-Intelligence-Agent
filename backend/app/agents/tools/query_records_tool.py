from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.application.snapshot import BusinessDataSnapshot
from app.agents.tools.registry import ToolDefinition, ToolResult

class QueryRecordsArgs(BaseModel):
    domain: str = Field(description="'deals' or 'work_orders'")
    limit: Optional[int] = Field(default=10, description="Max number of records to return. Default 10. Max 100.")
    status_filter: Optional[str] = Field(default=None, description="Optional status to filter by (e.g. 'Open', 'Won', 'Completed', 'Pause / struck')")
    search_query: Optional[str] = Field(default=None, description="Optional text to search in project name or client id")

async def query_business_records(snapshot: BusinessDataSnapshot, args: QueryRecordsArgs) -> ToolResult:
    domain = args.domain.lower()
    limit = min(args.limit or 10, 100)
    status_filter = args.status_filter.lower() if args.status_filter else None
    search_query = args.search_query.lower() if args.search_query else None
    
    records = []
    
    if domain == "deals":
        dataset = snapshot.dataset.deals
        columns = ["Project Name", "Client ID", "Status", "Stage", "Value", "Sector"]
        
        for deal in dataset:
            if status_filter and deal.status.value.lower() != status_filter:
                continue
                
            if search_query:
                name_match = search_query in deal.name.lower()
                client_match = search_query in deal.client_id.lower()
                if not (name_match or client_match):
                    continue
                    
            value = deal.value.amount if deal.value else 0.0
            records.append({
                "Project Name": deal.name,
                "Client ID": deal.client_id,
                "Status": deal.status.value,
                "Stage": deal.stage.value,
                "Value": f"₹{value:,.2f}",
                "Sector": deal.sector.value if deal.sector else "Unknown"
            })
    
    elif domain in ["work_orders", "work orders", "work_order"]:
        dataset = snapshot.dataset.work_orders
        columns = ["Project Name", "Client ID", "Execution Status", "Sector", "Value Excl GST", "Billed Value"]
        
        for wo in dataset:
            if status_filter and wo.execution_status.value.lower() != status_filter:
                continue
                
            if search_query:
                name_match = search_query in wo.name.lower()
                client_match = search_query in wo.client_id.lower()
                if not (name_match or client_match):
                    continue
                    
            value_excl = wo.value_excl_gst.amount if wo.value_excl_gst else 0.0
            billed = wo.billed_value_incl_gst.amount if wo.billed_value_incl_gst else 0.0
            records.append({
                "Project Name": wo.name,
                "Client ID": wo.client_id,
                "Execution Status": wo.execution_status.value,
                "Sector": wo.sector.value if wo.sector else "Unknown",
                "Value Excl GST": f"₹{value_excl:,.2f}",
                "Billed Value": f"₹{billed:,.2f}"
            })
    else:
        return ToolResult(
            tool_name="query_business_records",
            success=False,
            error=f"Unknown domain: {domain}. Use 'deals' or 'work_orders'."
        )
        
    total_matches = len(records)
    records = records[:limit]
    
    table_data = {
        "type": "table",
        "title": f"Queried Records: {domain.title()}",
        "columns": columns,
        "data": records
    }
    
    return ToolResult(
        tool_name="query_business_records",
        success=True,
        data={
            "tables": [table_data],
            "records": records,
            "total_matches": total_matches
        }
    )

query_records_tool = ToolDefinition(
    name="query_business_records",
    description="Query actual individual records (like project names) from Deals or Work Orders. Use this for record-level listing, searching, or when asked 'What are the project names?' or 'Show me the paused projects'. Do not use for aggregation/math.",
    parameters_schema=QueryRecordsArgs,
    handler=query_business_records
)
