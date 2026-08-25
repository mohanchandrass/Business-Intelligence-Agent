from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict

class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass

class ToolCallRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    tool_name: str
    arguments: Dict[str, Any]
    raw_part: Optional[Any] = None

class LLMResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    text: Optional[str] = None
    tool_calls: List[ToolCallRequest] = []
    raw_content: Optional[Any] = None

class LLMProvider(ABC):
    """Abstract interface for LLM capabilities."""
    
    @abstractmethod
    async def verify_authentication(self) -> Dict[str, Any]:
        """Test authentication to the provider."""
        pass
        
    @abstractmethod
    async def list_available_models(self) -> List[str]:
        """List models available to the current authenticated identity."""
        pass
        
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt (diagnostic only for now)."""
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, Any]], system_instruction: Optional[str] = None, tools: Optional[List[Any]] = None) -> LLMResponse:
        """Execute a chat turn, optionally providing tools.
        messages format: [{"role": "user"|"model"|"tool", "parts": [...]}]
        """
        pass
