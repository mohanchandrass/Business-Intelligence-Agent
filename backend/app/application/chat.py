import logging
from typing import Dict, Any

from app.application.snapshot import BusinessDataService, BusinessDataSnapshot
from app.agents.orchestrator import AgentOrchestrator
from app.agents.tools import get_default_registry
from app.infrastructure.llm.gemini import GeminiProvider

logger = logging.getLogger(__name__)

class ChatApplicationService:
    def __init__(self, data_service: BusinessDataService):
        self.data_service = data_service
        self.llm_provider = GeminiProvider()
        self.tool_registry = get_default_registry()
        self.orchestrator = AgentOrchestrator(
            llm_provider=self.llm_provider,
            tool_registry=self.tool_registry
        )

    async def process_query(self, query: str, req_id: str = "REQ unknown") -> Dict[str, Any]:
        try:
            logger.info(f"[{req_id}] CHAT SERVICE processing query")
            # 1. Fetch fresh snapshot for the request
            logger.info(f"[{req_id}] Requesting BusinessDataSnapshot")
            snapshot: BusinessDataSnapshot = await self.data_service.get_snapshot(req_id)
            logger.info(f"[{req_id}] SNAPSHOT constructed")
            
            # 2. Run orchestrator
            logger.info(f"[{req_id}] Handing off to AgentOrchestrator")
            answer = await self.orchestrator.execute(query, snapshot, req_id)

            
            # 3. Assemble response mapping to the frontend contract
            warnings = []
            if snapshot.data_quality_report.excluded_records > 0:
                warnings.append(
                    f"Data Quality Note: {snapshot.data_quality_report.excluded_records} records "
                    f"were excluded from analysis due to normalization errors."
                )

            # In a full implementation, we could parse the LLM's response to extract 
            # structured metrics/insights to populate the UI charts/KPIs.
            # For this MVP, we return the text response and high-level warnings.
            return {
                "answer": answer,
                "insights": [],
                "metrics": {},
                "warnings": warnings,
                "metadata": {
                    "records_inspected": snapshot.data_quality_report.total_records_inspected
                }
            }
            
        except Exception as e:
            # Log the full error internally, return safe message
            return {
                "answer": "I encountered an error while processing your request. Please try again.",
                "insights": [],
                "metrics": {},
                "warnings": [f"Internal error: {str(e)}"],
                "metadata": {}
            }
