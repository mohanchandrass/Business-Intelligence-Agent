import asyncio
import json
import logging
from typing import Dict, Any

from app.config import get_settings
from app.infrastructure.monday.client import MondayClient
from app.infrastructure.monday.board_catalog import BoardCatalog
from app.application.snapshot import BusinessDataService

# Minimal config override for local testing if needed
# get_settings().monday.api_token = "..."

logging.basicConfig(level=logging.INFO)

async def generate():
    client = MondayClient()
    catalog = BoardCatalog(client)
    service = BusinessDataService(catalog)
    
    snapshot = await service.get_snapshot("DIAG")
    dataset = snapshot.dataset
    
    # 5 representative Deals
    sample_deals = []
    for d in dataset.deals[:5]:
        sample_deals.append({
            "id": d.id,
            "name": d.name,
            "client_id": d.client_id,
            "value": d.value.amount if d.value else None,
            "close_date": d.close_date.isoformat() if d.close_date else None,
            "stage": d.stage.value,
            "status": d.status.value,
            "sector": d.sector.value if d.sector else None
        })
        
    # 5 representative Work Orders
    sample_wos = []
    for w in dataset.work_orders[:5]:
        sample_wos.append({
            "id": w.id,
            "name": w.name,
            "deal_reference": w.deal_reference,
            "client_id": w.client_id,
            "execution_status": w.execution_status.value,
            "value_excl_gst": w.value_excl_gst.amount if w.value_excl_gst else None,
            "po_date": w.po_date.isoformat() if w.po_date else None,
            "sector": w.sector.value if w.sector else None
        })
        
    # Extracted data
    diag = {
        "deals_board": {
            "id": (await catalog.get_deals_board()).board_id,
            "name": (await catalog.get_deals_board()).board_name,
            "classification_confidence": (await catalog.get_deals_board()).confidence,
            "evidence": (await catalog.get_deals_board()).evidence,
            "semantic_mapping": (await catalog.get_deals_board()).semantic_mapping.mappings
        },
        "work_orders_board": {
            "id": (await catalog.get_work_orders_board()).board_id,
            "name": (await catalog.get_work_orders_board()).board_name,
            "classification_confidence": (await catalog.get_work_orders_board()).confidence,
            "evidence": (await catalog.get_work_orders_board()).evidence,
            "semantic_mapping": (await catalog.get_work_orders_board()).semantic_mapping.mappings
        },
        "statistics": {
            "total_deals": len(dataset.deals),
            "total_work_orders": len(dataset.work_orders),
            "deals_without_work_orders": len(dataset.deals_without_work_orders),
            "orphan_work_orders": len(dataset.orphan_work_orders),
            "total_matched_deals": len(dataset.deals) - len(dataset.deals_without_work_orders),
            "normalization_issues": len(snapshot.data_quality_report.issues)
        },
        "representative_deals": sample_deals,
        "representative_work_orders": sample_wos,
        "normalization_issues_sample": [
            {
                "record_type": i.record_type,
                "field": i.field,
                "issue_type": i.issue_type,
                "message": i.message
            }
            for i in snapshot.data_quality_report.issues[:5]
        ]
    }
    
    with open("../docs/diagnostics/verified-parsed-data.json", "w") as f:
        json.dump(diag, f, indent=2)
        
if __name__ == "__main__":
    asyncio.run(generate())
