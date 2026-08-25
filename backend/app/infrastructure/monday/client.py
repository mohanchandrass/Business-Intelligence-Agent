import httpx
import logging
from typing import Any, Dict, Optional
from app.config import get_settings

logger = logging.getLogger(__name__)

class MondayClientError(Exception):
    pass

class MondayClient:
    def __init__(self):
        self.settings = get_settings().monday
        self.headers = {
            "Authorization": self.settings.api_token,
            "API-Version": self.settings.api_version,
            "Content-Type": "application/json",
        }
        
    async def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a generic GraphQL query against Monday.com"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
            
        async with httpx.AsyncClient(timeout=self.settings.timeout_seconds) as client:
            try:
                response = await client.post(
                    self.settings.api_url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Check for GraphQL errors
                if "errors" in data:
                    error_msgs = [err.get("message", "Unknown error") for err in data["errors"]]
                    raise MondayClientError(f"GraphQL Errors: {'; '.join(error_msgs)}")
                    
                if "error_message" in data:
                    raise MondayClientError(f"Monday API Error: {data['error_message']}")
                    
                return data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Status Error: {e.response.status_code} - {e.response.text}")
                raise MondayClientError(f"HTTP Error: {e.response.status_code}") from e
            except httpx.RequestError as e:
                logger.error(f"Request Error: {str(e)}")
                raise MondayClientError(f"Request failed: {str(e)}") from e
