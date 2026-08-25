import asyncio
import json
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import get_settings
from app.infrastructure.monday.client import MondayClient
from app.infrastructure.monday.board_catalog import BoardCatalog
from app.infrastructure.monday.repositories import MondayDealRepository, MondayWorkOrderRepository
from app.normalization.normalizer import NormalizationService

async def main():
    settings = get_settings()
    client = MondayClient()
    catalog = BoardCatalog(client)
    
    print("Loading Board Catalog...")
    await catalog.refresh()
    
    deals_descriptor = await catalog.get_deals_board()
    wos_descriptor = await catalog.get_work_orders_board()
    
    deal_repo = MondayDealRepository(client, deals_descriptor)
    wo_repo = MondayWorkOrderRepository(client, wos_descriptor)
    
    print("Fetching raw items...")
    raw_deals_items = await deal_repo._fetch_all_items()
    raw_wos_items = await wo_repo._fetch_all_items()
    
    print(f"Fetched {len(raw_deals_items)} deals and {len(raw_wos_items)} work orders.")
    
    # 1. Raw dumps (DTO items)
    with open("debug/monday_raw_deals.json", "w") as f:
        json.dump([item.model_dump() for item in raw_deals_items], f, indent=2)
        
    with open("debug/monday_raw_work_orders.json", "w") as f:
        json.dump([item.model_dump() for item in raw_wos_items], f, indent=2)
        
    # 2. Parsed dumps (RawDealRecord, RawWorkOrderRecord)
    print("Parsing deals...")
    parsed_deals = await deal_repo.get_all_deals()
    with open("debug/monday_parsed_deals.json", "w") as f:
        json.dump([d.model_dump() for d in parsed_deals], f, indent=2)
        
    print("Parsing work orders...")
    parsed_wos = await wo_repo.get_all_work_orders()
    with open("debug/monday_parsed_work_orders.json", "w") as f:
        json.dump([wo.model_dump() for wo in parsed_wos], f, indent=2)
        
    # 3. Normalized dumps (Deal, WorkOrder)
    print("Normalizing deals...")
    normalized_deals = []
    for pd in parsed_deals:
        res = NormalizationService.normalize_deal(pd)
        normalized_deals.append({
            "parsed": pd.model_dump(),
            "normalized": res.record.model_dump() if res.record else None,
            "issues": [i.model_dump() for i in res.report.issues]
        })
        
    with open("debug/monday_normalized_deals.json", "w") as f:
        json.dump(normalized_deals, f, indent=2, default=str)
        
    print("Normalizing work orders...")
    normalized_wos = []
    for pw in parsed_wos:
        res = NormalizationService.normalize_work_order(pw)
        normalized_wos.append({
            "parsed": pw.model_dump(),
            "normalized": res.record.model_dump() if res.record else None,
            "issues": [i.model_dump() for i in res.report.issues]
        })
        
    with open("debug/monday_normalized_work_orders.json", "w") as f:
        json.dump(normalized_wos, f, indent=2, default=str)
        
    print("Export complete. Check backend/debug directory.")

if __name__ == "__main__":
    asyncio.run(main())
