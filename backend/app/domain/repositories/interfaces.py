from abc import ABC, abstractmethod
from typing import List, Protocol

from app.infrastructure.monday.dtos import RawDealRecord, RawWorkOrderRecord

class DealRepository(ABC):
    @abstractmethod
    async def get_all_deals(self) -> List[RawDealRecord]:
        """Fetch all deals from the Monday Deals board."""
        pass

class WorkOrderRepository(ABC):
    @abstractmethod
    async def get_all_work_orders(self) -> List[RawWorkOrderRecord]:
        """Fetch all work orders from the Monday Work Orders board."""
        pass
