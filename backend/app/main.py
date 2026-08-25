import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware

# Configure structured runtime trace logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Skylark BI Agent API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://10.17.7.218:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    return JSONResponse(content={"status": "ok", "message": "Backend is running"})

from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.infrastructure.monday.client import MondayClient
from app.infrastructure.monday.board_catalog import BoardCatalog
from app.application.snapshot import BusinessDataService
from app.application.chat import ChatApplicationService
from app.config import get_settings

# Initialize Singletons
settings = get_settings()
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
        "data": [],
        "data_quality": [{"severity": "warning", "message": w} for w in result.get("warnings", [])],
        "metadata": result.get("metadata", {})
    })
