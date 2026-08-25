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
    w = await cat.get_work_orders_board()
    print([(c.id, c.title) for c in w.columns])

if __name__ == "__main__":
    asyncio.run(main())
