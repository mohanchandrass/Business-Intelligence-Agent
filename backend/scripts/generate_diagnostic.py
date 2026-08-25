import asyncio
import json
import os
import sys
from datetime import datetime

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import get_settings
from app.infrastructure.monday.client import MondayClient
from app.infrastructure.monday.board_catalog import BoardCatalog
from app.infrastructure.monday.repositories import MondayDealRepository, MondayWorkOrderRepository
from app.normalization.normalizer import NormalizationService
from app.application.snapshot import CrossBoardDataset

async def main():
    settings = get_settings()
    client = MondayClient()
    catalog = BoardCatalog(client)
    
    print("Refreshing Board Catalog...")
    await catalog.refresh()
    
    deals_descriptor = await catalog.get_deals_board()
    wos_descriptor = await catalog.get_work_orders_board()
    
    deal_repo = MondayDealRepository(client, deals_descriptor)
    wo_repo = MondayWorkOrderRepository(client, wos_descriptor)
    
    print("Fetching items...")
    raw_deals_items = await deal_repo._fetch_all_items()
    raw_wos_items = await wo_repo._fetch_all_items()
    
    parsed_deals = await deal_repo.get_all_deals()
    parsed_wos = await wo_repo.get_all_work_orders()
    
    normalized_deals = []
    deal_issues = []
    for pd in parsed_deals:
        res = NormalizationService.normalize_deal(pd)
        if res.record:
            normalized_deals.append(res.record)
        deal_issues.extend(res.report.issues)
        
    normalized_wos = []
    wo_issues = []
    for pw in parsed_wos:
        res = NormalizationService.normalize_work_order(pw)
        if res.record:
            normalized_wos.append(res.record)
        wo_issues.extend(res.report.issues)
        
    dataset = CrossBoardDataset()
    dataset.deals = normalized_deals
    
    for deal in normalized_deals:
        dataset.deals_by_id[deal.name] = deal
        dataset.work_orders_by_deal[deal.name] = []
        
    for wo in normalized_wos:
        if wo.deal_reference in dataset.deals_by_id:
            dataset.work_orders_by_deal[wo.deal_reference].append(wo)
        else:
            dataset.orphan_work_orders.append(wo)
            
    for deal in normalized_deals:
        if not dataset.work_orders_by_deal.get(deal.name):
            dataset.deals_without_work_orders.append(deal)

    def extract_important_fields(record, is_deal=True):
        if is_deal:
            return {
                "identifier/name": getattr(record, "name", None),
                "deal value": getattr(record, "value", None),
                "stage": getattr(record, "stage", None),
                "sector": getattr(record, "sector", None),
                "client code": getattr(record, "client_id", getattr(record, "client_code", None)),
                "date": getattr(record, "close_date", None)
            }
        else:
            return {
                "serial number": getattr(record, "serial_number", None),
                "deal reference": getattr(record, "deal_reference", None),
                "amount": getattr(record, "amount_incl_gst", getattr(record, "amount", None)),
                "execution status": getattr(record, "execution_status", getattr(record, "status", None)),
                "sector": getattr(record, "sector", None),
                "customer": getattr(record, "customer_code", None)
            }

    diag = {
        "timestamp": datetime.utcnow().isoformat(),
        "boards": [
            {"id": deals_descriptor.board_id, "name": deals_descriptor.board_name, "type": "DEALS"},
            {"id": wos_descriptor.board_id, "name": wos_descriptor.board_name, "type": "WORK_ORDERS"}
        ],
        "schemas": [
            {"board": "DEALS", "columns": [c.model_dump() for c in deals_descriptor.columns]},
            {"board": "WORK_ORDERS", "columns": [c.model_dump() for c in wos_descriptor.columns]}
        ],
        "semantic_mappings": [
            {"board": "DEALS", "mapping": deals_descriptor.semantic_mapping.model_dump() if deals_descriptor.semantic_mapping else {}},
            {"board": "WORK_ORDERS", "mapping": wos_descriptor.semantic_mapping.model_dump() if wos_descriptor.semantic_mapping else {}}
        ],
        "raw_samples": [
            {"board": "DEALS", "sample": raw_deals_items[0].model_dump() if raw_deals_items else None},
            {"board": "WORK_ORDERS", "sample": raw_wos_items[0].model_dump() if raw_wos_items else None}
        ],
        "parsed_samples": [
            {"board": "DEALS", "sample": parsed_deals[0].model_dump() if parsed_deals else None},
            {"board": "WORK_ORDERS", "sample": parsed_wos[0].model_dump() if parsed_wos else None}
        ],
        "normalized_samples": [
            {"board": "DEALS", "sample": normalized_deals[0].model_dump() if normalized_deals else None, "important_fields": extract_important_fields(normalized_deals[0], True) if normalized_deals else {}},
            {"board": "WORK_ORDERS", "sample": normalized_wos[0].model_dump() if normalized_wos else None, "important_fields": extract_important_fields(normalized_wos[0], False) if normalized_wos else {}}
        ],
        "field_statistics": {
            "deals": {
                "raw_count": len(raw_deals_items),
                "parsed_count": len(parsed_deals),
                "normalized_count": len(normalized_deals),
                "missing_values": len([d for d in parsed_deals if d.value is None])
            },
            "work_orders": {
                "raw_count": len(raw_wos_items),
                "parsed_count": len(parsed_wos),
                "normalized_count": len(normalized_wos),
                "missing_amounts": len([w for w in parsed_wos if getattr(w, 'amount_excl_gst', None) is None])
            }
        },
        "normalization_issues": {
            "deals_issues_sample": [i.model_dump() for i in deal_issues[:5]],
            "wos_issues_sample": [i.model_dump() for i in wo_issues[:5]]
        },
        "relationship_statistics": {
            "matched_wos": len(normalized_wos) - len(dataset.orphan_work_orders),
            "orphan_wos": len(dataset.orphan_work_orders),
            "deals_without_wos": len(dataset.deals_without_work_orders)
        }
    }
    
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'diagnostics', 'latest-parsed-data.json'))
    with open(out_path, "w") as f:
        json.dump(diag, f, indent=2, default=str)
        
    print(f"Diagnostic artifact generated at {out_path}")

if __name__ == "__main__":
    asyncio.run(main())
