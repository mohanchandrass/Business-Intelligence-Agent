import asyncio
import logging
from app.application.chat import ChatApplicationService
from app.application.snapshot import BusinessDataService
from app.infrastructure.monday.board_catalog import BoardCatalog

# Add basic stream handler to capture the logs in standard output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

from app.infrastructure.monday.client import MondayClient
from app.infrastructure.monday.board_catalog import BoardCatalog
from app.infrastructure.monday.repositories import MondayDealRepository, MondayWorkOrderRepository

async def main():
    print("Initializing services...")
    client = MondayClient()
    catalog = BoardCatalog(client)
    
    deals_board = await catalog.get_deals_board()
    deal_repo = MondayDealRepository(client, deals_board)
    raw_deals = await deal_repo._fetch_all_items()  # Bypass DTO parsing to see raw item
    
    print("\n--- FIRST DEAL RAW DATA ---")
    if raw_deals:
        print(f"Name: {raw_deals[0].name}")
        print(f"ID: {raw_deals[0].id}")
        for cv in raw_deals[0].column_values:
            print(f"Col {cv.id}: text='{cv.text}' value='{cv.value}' type='{cv.type}'")
    else:
        print("No deals found")

    wo_board = await catalog.get_work_orders_board()
    wo_repo = MondayWorkOrderRepository(client, wo_board)
    raw_wos = await wo_repo._fetch_all_items()
    
    print("\n--- FIRST WORK ORDER RAW DATA ---")
    if raw_wos:
        print(f"Name: {raw_wos[0].name}")
        print(f"ID: {raw_wos[0].id}")
        for cv in raw_wos[0].column_values:
            print(f"Col {cv.id}: text='{cv.text}' value='{cv.value}' type='{cv.type}'")
    else:
        print("No work orders found")
        
    print("\n--- NOW RUNNING CHAT QUERY ---")
    data_service = BusinessDataService(catalog)
    chat_service = ChatApplicationService(data_service)
    
    print("Running query: 'tell me about our pipeline'")
    result = await chat_service.process_query("tell me about our pipeline", "REQ TRACE0")
    
    print("=== FINAL RESULT ===")
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("Answer:")
    print(result.get("answer"))
    print("\nWarnings:")
    print(result.get("warnings"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
