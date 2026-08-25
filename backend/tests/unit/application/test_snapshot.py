import pytest
from unittest.mock import AsyncMock
from app.application.snapshot import BusinessDataService
from app.infrastructure.monday.dtos import RawDealRecord, RawWorkOrderRecord

@pytest.mark.asyncio
async def test_business_data_snapshot():
    mock_deal_repo = AsyncMock()
    mock_wo_repo = AsyncMock()
    
    # 2 deals, 1 valid work order matching Deal 1, 1 orphan work order
    mock_deal_repo.get_all_deals.return_value = [
        RawDealRecord(id="1", name="DEAL-1", value="1000"),
        RawDealRecord(id="2", name="DEAL-2", value="2000")
    ]
    
    mock_wo_repo.get_all_work_orders.return_value = [
        RawWorkOrderRecord(id="10", name="WO-1", serial_number="DEAL-1", amount_excl_gst="900"),
        RawWorkOrderRecord(id="11", name="WO-ORPHAN", serial_number="DEAL-999", amount_excl_gst="500")
    ]
    
    service = BusinessDataService(deal_repo=mock_deal_repo, wo_repo=mock_wo_repo)
    snapshot = await service.get_snapshot()
    
    dataset = snapshot.dataset
    
    assert len(dataset.deals) == 2
    assert len(dataset.work_orders) == 2
    
    # Check relationships
    assert len(dataset.work_orders_by_deal["DEAL-1"]) == 1
    assert dataset.work_orders_by_deal["DEAL-1"][0].id == "10"
    
    assert len(dataset.work_orders_by_deal["DEAL-2"]) == 0
    
    # Check metadata
    assert len(dataset.orphan_work_orders) == 1
    assert dataset.orphan_work_orders[0].id == "11"
    
    assert len(dataset.deals_without_work_orders) == 1
    assert dataset.deals_without_work_orders[0].id == "2"
    
    # Check data quality aggregation
    assert snapshot.data_quality_report.total_records_inspected == 4
    assert snapshot.data_quality_report.usable_records == 4
