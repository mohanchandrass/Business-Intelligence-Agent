from typing import List, Optional, Dict
from app.infrastructure.monday.client import MondayClient
from app.config import get_settings
from .board_discovery import BoardDiscoverer
from .discovery_models import BoardDescriptor, BoardClassification

class BoardCatalogError(Exception):
    pass

class BoardCatalog:
    def __init__(self, client: MondayClient):
        self.client = client
        self.discoverer = BoardDiscoverer(client)
        self.settings = get_settings().monday
        self._descriptors: List[BoardDescriptor] = []
        self._is_loaded = False
        
    async def refresh(self) -> None:
        """Forces a re-discovery of boards."""
        self._descriptors = await self.discoverer.get_accessible_boards()
        self._is_loaded = True
        
    async def _ensure_loaded(self) -> None:
        if not self._is_loaded:
            await self.refresh()
            
    async def get_deals_board(self) -> BoardDescriptor:
        await self._ensure_loaded()
        
        # 1. Dev override via explicitly configured ID
        if self.settings.deals_board_id:
            for d in self._descriptors:
                if d.board_id == self.settings.deals_board_id:
                    return d
            raise BoardCatalogError(f"Configured Deals board {self.settings.deals_board_id} not found in accessible boards.")
            
        # 2. Heuristic Discovery
        best_match = None
        highest_confidence = 0.0
        
        for d in self._descriptors:
            if d.classification == BoardClassification.DEALS and d.confidence > highest_confidence:
                best_match = d
                highest_confidence = d.confidence
                
        if best_match:
            return best_match
            
        raise BoardCatalogError("Could not deterministically find a Deals board.")
        
    async def get_work_orders_board(self) -> BoardDescriptor:
        await self._ensure_loaded()
        
        # 1. Dev override
        if self.settings.work_orders_board_id:
            for d in self._descriptors:
                if d.board_id == self.settings.work_orders_board_id:
                    return d
            raise BoardCatalogError(f"Configured Work Orders board {self.settings.work_orders_board_id} not found.")
            
        # 2. Heuristic Discovery
        best_match = None
        highest_confidence = 0.0
        
        for d in self._descriptors:
            if d.classification == BoardClassification.WORK_ORDERS and d.confidence > highest_confidence:
                best_match = d
                highest_confidence = d.confidence
                
        if best_match:
            return best_match
            
        raise BoardCatalogError("Could not deterministically find a Work Orders board.")
        
    def get_all_descriptors(self) -> List[BoardDescriptor]:
        return self._descriptors
