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
            result = await self.orchestrator.execute(query, snapshot_factory, req_id)

            return {
                "answer": result.get("answer", ""),
                "insights": [],
                "data": result.get("data", []),
                "warnings": result.get("warnings", []),
                "metadata": {}
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
