import asyncio
from typing import Dict, Any
from app.infrastructure.monday.client import MondayClient, MondayClientError
from app.config import get_settings

class MondayDiagnostics:
    def __init__(self):
        self.client = MondayClient()
        self.settings = get_settings().monday

    async def test_authentication(self) -> Dict[str, Any]:
        """Test authentication by querying the current user."""
        query = """
        query {
            me {
                id
                name
                email
            }
        }
        """
        try:
            result = await self.client.execute(query)
            return {"status": "success", "data": result.get("data", {}).get("me")}
        except MondayClientError as e:
            return {"status": "error", "message": str(e)}

    async def get_board_metadata(self, board_id: str) -> Dict[str, Any]:
        """Get board schema and metadata."""
        query = """
        query ($boardId: [ID!]) {
            boards(ids: $boardId) {
                id
                name
                state
                board_folder_id
                board_kind
                description
                columns {
                    id
                    title
                    type
                    settings_str
                }
            }
        }
        """
        try:
            result = await self.client.execute(query, variables={"boardId": [board_id]})
            boards = result.get("data", {}).get("boards", [])
            if not boards:
                return {"status": "error", "message": "Board not found"}
            return {"status": "success", "data": boards[0]}
        except MondayClientError as e:
            return {"status": "error", "message": str(e)}
            
    async def get_sample_items(self, board_id: str, limit: int = 5) -> Dict[str, Any]:
        """Get sample items from a board to profile actual values."""
        query = """
        query ($boardId: [ID!], $limit: Int!) {
            boards(ids: $boardId) {
                items_page(limit: $limit) {
                    cursor
                    items {
                        id
                        name
                        column_values {
                            id
                            type
                            text
                            value
                        }
                    }
                }
            }
        }
        """
        try:
            result = await self.client.execute(query, variables={"boardId": [board_id], "limit": limit})
            boards = result.get("data", {}).get("boards", [])
            if not boards:
                return {"status": "error", "message": "Board not found"}
            
            items = boards[0].get("items_page", {}).get("items", [])
            return {"status": "success", "data": items}
        except MondayClientError as e:
            return {"status": "error", "message": str(e)}
