from typing import List, Optional
from app.domain.repositories.interfaces import DealRepository, WorkOrderRepository
from app.infrastructure.monday.client import MondayClient
from app.infrastructure.monday.dtos import RawDealRecord, RawWorkOrderRecord, MondayItem
from app.infrastructure.monday.discovery_models import BoardDescriptor

class MondayBaseRepository:
    def __init__(self, client: MondayClient, board_id: str):
        self.client = client
        self.board_id = board_id

    async def _fetch_all_items(self) -> List[MondayItem]:
        query = """
        query ($board_id: [ID!], $cursor: String) {
            boards(ids: $board_id) {
                items_page(limit: 500, cursor: $cursor) {
                    cursor
                    items {
                        id
                        name
                        column_values {
                            id
                            text
                            value
                            type
                        }
                    }
                }
            }
        }
        """
        all_items: List[MondayItem] = []
        cursor: Optional[str] = None
        
        while True:
            variables = {"board_id": [self.board_id]}
            if cursor:
                variables["cursor"] = cursor
                
            response = await self.client.execute(query, variables)
            data = response.get("data", {})
            boards = data.get("boards", [])
            
            if not boards:
                break
                
            board = boards[0]
            items_page = board.get("items_page", {})
            items_raw = items_page.get("items", [])
            
            for item_raw in items_raw:
                # Map dict to Pydantic model
                all_items.append(MondayItem.model_validate(item_raw))
                
            cursor = items_page.get("cursor")
            if not cursor:
                break
                
        return all_items


class MondayDealRepository(MondayBaseRepository, DealRepository):
    def __init__(self, client: MondayClient, descriptor: BoardDescriptor):
        super().__init__(client, descriptor.board_id)
        self.descriptor = descriptor

    async def get_all_deals(self) -> List[RawDealRecord]:
        items = await self._fetch_all_items()
        return [RawDealRecord.from_item(item, self.descriptor.semantic_mapping) for item in items]


class MondayWorkOrderRepository(MondayBaseRepository, WorkOrderRepository):
    def __init__(self, client: MondayClient, descriptor: BoardDescriptor):
        super().__init__(client, descriptor.board_id)
        self.descriptor = descriptor

    async def get_all_work_orders(self) -> List[RawWorkOrderRecord]:
        items = await self._fetch_all_items()
        return [RawWorkOrderRecord.from_item(item, self.descriptor.semantic_mapping) for item in items]
