import asyncio
import os
import sys

# Add the backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.monday.client import MondayClient
from app.infrastructure.monday.board_catalog import BoardCatalog
from app.infrastructure.monday.repositories import MondayDealRepository, MondayWorkOrderRepository
from app.normalization.normalizer import NormalizationService
from app.infrastructure.monday.dtos import RawDealRecord, RawWorkOrderRecord

async def main():
    client = MondayClient()
    catalog = BoardCatalog(client)
    
    print("MONDAY DATA AUDIT")
    print("-" * 20)
    
    # 1. Fetch Deals
    deals_descriptor = await catalog.get_deals_board()
    deal_repo = MondayDealRepository(client, deals_descriptor)
    
    # We will override _fetch_all_items to also count pages and raw records
    # But since it's already implemented, we can just call the public method
    # Wait, let's fetch raw items manually to count pages
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
    
    deals_pages = 0
    deals_fetched = 0
    cursor = None
    deals_raw_items = []
    
    while True:
        variables = {"board_id": [deals_descriptor.board_id]}
        if cursor:
            variables["cursor"] = cursor
        response = await client.execute(query, variables)
        boards = response.get("data", {}).get("boards", [])
        if not boards: break
        items_page = boards[0].get("items_page", {})
        items = items_page.get("items", [])
        
        deals_pages += 1
        deals_fetched += len(items)
        deals_raw_items.extend(items)
        
        cursor = items_page.get("cursor")
        if not cursor: break

    from app.infrastructure.monday.dtos import MondayItem
    deal_records = [RawDealRecord.from_item(MondayItem.model_validate(item), deals_descriptor.semantic_mapping) for item in deals_raw_items]
    
    deals_normalized = 0
    deals_discarded = 0
    deal_discard_reasons = {}
    
    for raw in deal_records:
        norm = NormalizationService.normalize_deal(raw)
        if norm.record is not None:
            deals_normalized += 1
        else:
            deals_discarded += 1
            reason = norm.report.issues[0].message if norm.report.issues else "Unknown"
            deal_discard_reasons[reason] = deal_discard_reasons.get(reason, 0) + 1

    print("Deals:")
    print(f"  fetched: {deals_fetched}")
    print(f"  normalized: {deals_normalized}")
    print(f"  discarded: {deals_discarded}")
    if deals_discarded > 0:
        print(f"  discard reasons: {deal_discard_reasons}")
        
    print()
    
    # 2. Fetch Work Orders
    wo_descriptor = await catalog.get_work_orders_board()
    
    wo_pages = 0
    wo_fetched = 0
    cursor = None
    wo_raw_items = []
    
    while True:
        variables = {"board_id": [wo_descriptor.board_id]}
        if cursor:
            variables["cursor"] = cursor
        response = await client.execute(query, variables)
        boards = response.get("data", {}).get("boards", [])
        if not boards: break
        items_page = boards[0].get("items_page", {})
        items = items_page.get("items", [])
        
        wo_pages += 1
        wo_fetched += len(items)
        wo_raw_items.extend(items)
        
        cursor = items_page.get("cursor")
        if not cursor: break
        
    wo_records = [RawWorkOrderRecord.from_item(MondayItem.model_validate(item), wo_descriptor.semantic_mapping) for item in wo_raw_items]
    
    wo_normalized = 0
    wo_discarded = 0
    wo_discard_reasons = {}
    
    for raw in wo_records:
        norm = NormalizationService.normalize_work_order(raw)
        if norm.record is not None:
            wo_normalized += 1
        else:
            wo_discarded += 1
            reason = norm.report.issues[0].message if norm.report.issues else "Unknown"
            wo_discard_reasons[reason] = wo_discard_reasons.get(reason, 0) + 1
            
    print("Work Orders:")
    print(f"  fetched: {wo_fetched}")
    print(f"  normalized: {wo_normalized}")
    print(f"  discarded: {wo_discarded}")
    if wo_discarded > 0:
        print(f"  discard reasons: {wo_discard_reasons}")
        
    print()
    print("Pagination:")
    print(f"  deals pages: {deals_pages}")
    print(f"  work order pages: {wo_pages}")
    
    print("\nSample Deal Raw Record (first one):")
    if deal_records:
        r = deal_records[0]
        print(f"  name (project name): {r.name}")
        print(f"  value: {r.value}")
        print(f"  client_code: {r.client_code}")
        print(f"  status: {r.status}")
        print(f"  sector: {r.sector}")
        
    print("\nSample Work Order Raw Record (first one):")
    if wo_records:
        r = wo_records[0]
        print(f"  name: {r.name}")
        print(f"  serial (deal ref): {r.serial_number}")
        print(f"  customer: {r.customer_code}")
        print(f"  amount (incl gst): {r.amount_incl_gst}")
        print(f"  status: {r.execution_status}")

if __name__ == "__main__":
    asyncio.run(main())
