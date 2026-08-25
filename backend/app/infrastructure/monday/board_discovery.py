from typing import List, Dict, Any, Optional
from app.infrastructure.monday.client import MondayClient, MondayClientError
from .discovery_models import BoardDescriptor, ColumnDescriptor
from .schema_inspector import SchemaInspector

class BoardDiscoverer:
    def __init__(self, client: MondayClient):
        self.client = client
        self.inspector = SchemaInspector()

    async def get_accessible_boards(self) -> List[BoardDescriptor]:
        """Fetch all accessible boards and classify them deterministically."""
        query = """
        query {
            boards(limit: 50) {
                id
                name
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
            result = await self.client.execute(query)
            raw_boards = result.get("data", {}).get("boards", [])
            
            descriptors = []
            for rb in raw_boards:
                board_id = rb.get("id")
                board_name = rb.get("name")
                description = rb.get("description") or ""
                raw_columns = rb.get("columns", [])
                
                # Inspect and classify
                descriptor = self.inspector.inspect(board_id, board_name, description, raw_columns)
                descriptors.append(descriptor)
                
            return descriptors
        except MondayClientError as e:
            # Propagate or log based on application requirements
            raise e
