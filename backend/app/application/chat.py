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
            
            async def snapshot_factory():
                logger.info(f"[{req_id}] Requesting BusinessDataSnapshot (Lazy)")
                return await self.data_service.get_snapshot(req_id)
            
            # 2. Run orchestrator
            logger.info(f"[{req_id}] Handing off to AgentOrchestrator")
            answer = await self.orchestrator.execute(query, snapshot_factory, req_id)

            
            # 3. Assemble response mapping to the frontend contract
            # Since the snapshot is fetched lazily, we don't have it here to check global warnings.
            # But the user requested: "Only show warnings relevant to the requested analysis."
            # The warnings will be part of the structured tool result!
            warnings = []
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
