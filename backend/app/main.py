import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

# Configure structured runtime trace logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app.app_name,
    version="1.0.0",
)

cors_origins_list = [origin.strip() for origin in settings.app.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    return JSONResponse(content={"status": "ok", "message": "Backend is running"})

@app.get("/api/v1/status")
async def status_endpoint():
    from app.infrastructure.monday.diagnostics import MondayDiagnostics
    import os
    
    # Check whether the required API token exists and is not a default mock/fake placeholder
    api_token = settings.monday.api_token
    configured = bool(api_token and api_token.strip() and api_token != "fake_token")
    
    # Try to verify token connection status
    connected = False
    if configured:
        try:
            diag = MondayDiagnostics()
            auth_res = await diag.test_authentication()
            if auth_res.get("status") == "success":
                connected = True
        except Exception as e:
            logger.error(f"Monday connection check failed: {e}")
            
    # Derive mode from frontend config if available, otherwise default to "api"
    mode = "mock" if os.getenv("NEXT_PUBLIC_USE_MOCK_API") == "true" else "api"
    
    return JSONResponse(content={
        "backend": {
            "status": "ok"
        },
        "monday": {
            "configured": configured,
            "connected": connected
        },
        "environment": {
            "mode": mode
        }
    })


from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.infrastructure.monday.client import MondayClient
from app.infrastructure.monday.board_catalog import BoardCatalog
from app.application.snapshot import BusinessDataService
from app.application.chat import ChatApplicationService

# Initialize Singletons
monday_client = MondayClient()
board_catalog = BoardCatalog(client=monday_client)
data_service = BusinessDataService(catalog=board_catalog)
chat_service = ChatApplicationService(data_service=data_service)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    req_id = f"REQ {uuid.uuid4().hex[:6]}"
    logger.info(f"[{req_id}] User query received: '{request.message}'")
    
    # Pass req_id down via context or inject it. Since we can't easily change all signatures,
    # let's set a global or thread-local for simplicity in a hackathon, or just pass it in context.
    # For this trace, we'll pass req_id to process_query.
    result = await chat_service.process_query(request.message, req_id)
    
    logger.info(f"[{req_id}] FRONTEND RESPONSE generated")
    
    return JSONResponse(content={
        "conversation_id": request.conversation_id or "new_conv_123",
        "answer": result.get("answer", "No answer provided."),
        "insights": result.get("insights", []),
        "data": result.get("data", []),
        "data_quality": [{"severity": "warning", "message": w} for w in result.get("warnings", [])],
        "metadata": result.get("metadata", {})
    })
