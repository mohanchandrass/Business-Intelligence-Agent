import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.infrastructure.monday.client import MondayClient
from app.infrastructure.monday.board_catalog import BoardCatalog

async def main():
    c = MondayClient()
    cat = BoardCatalog(c)
    await cat.refresh()
    d = await cat.get_deals_board()
    print("DEALS MAPPING:", d.semantic_mapping.model_dump())
    
    w = await cat.get_work_orders_board()
    print("WORK ORDERS MAPPING:", w.semantic_mapping.model_dump())

if __name__ == "__main__":
    asyncio.run(main())
