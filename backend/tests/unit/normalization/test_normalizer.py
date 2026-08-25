import pytest
from app.normalization.normalizer import NormalizationService
from app.infrastructure.monday.dtos import RawDealRecord, RawWorkOrderRecord
from app.domain.models import DataQualityReport, DealStatus, DealStage, Sector, WorkOrderExecutionStatus

def test_normalize_client_code():
    assert NormalizationService.normalize_client_code("WOCOMPANY_002") == "COMPANY_002"
    assert NormalizationService.normalize_client_code("COMPANY089") == "COMPANY_089"
    assert NormalizationService.normalize_client_code("COMPANY_123") == "COMPANY_123"
    assert NormalizationService.normalize_client_code("") is None

def test_normalize_money():
    report = DataQualityReport()
    money = NormalizationService.normalize_money("₹ 50,000.50", "1", "val", report)
    assert money is not None
    assert money.amount == 50000.50
    
    money = NormalizationService.normalize_money("", "1", "val", report)
    assert money is None
    assert len(report.issues) == 1
    assert report.issues[0].issue_type == "MISSING_VALUE"
    
    money = NormalizationService.normalize_money("abc", "1", "val", report)
    assert money is None
    assert len(report.issues) == 2
    assert report.issues[1].issue_type == "MALFORMED_NUMBER"

def test_normalize_date():
    report = DataQualityReport()
    d = NormalizationService.normalize_date("2023-12-31", "1", "date", report)
    assert d is not None
    assert d.year == 2023
    assert d.month == 12
    assert d.day == 31

def test_normalize_deal():
    raw = RawDealRecord(
        id="1",
        name="SDPLDEAL-1",
        client_code="COMPANY001",
        status="Won",
        stage="G. Project Won",
        sector="Powerline",
        value="5000"
    )
    result = NormalizationService.normalize_deal(raw)
    assert result.record is not None
    assert result.record.name == "SDPLDEAL-1"
    assert result.record.client_id == "COMPANY_001"
    assert result.record.status == DealStatus.WON
    assert result.record.stage == DealStage.PROJECT_WON
    assert result.record.sector == Sector.POWERLINE
    assert result.record.value.amount == 5000
    assert len(result.report.issues) == 0

def test_normalize_deal_missing_id():
    raw = RawDealRecord(id="1", name="")
    result = NormalizationService.normalize_deal(raw)
    assert result.record is None
    assert len(result.report.issues) == 1
    assert result.report.issues[0].issue_type == "MISSING_IDENTIFIER"
    assert result.report.excluded_records == 1

def test_normalize_work_order():
    raw = RawWorkOrderRecord(
        id="2",
        name="WO-1",
        serial_number="SDPLDEAL-1",
        customer_code="WOCOMPANY_001",
        execution_status="Completed",
        sector="Mining",
        amount_excl_gst="4500"
    )
    result = NormalizationService.normalize_work_order(raw)
    assert result.record is not None
    assert result.record.name == "WO-1"
    assert result.record.deal_reference == "SDPLDEAL-1"
    assert result.record.client_id == "COMPANY_001"
    assert result.record.execution_status == WorkOrderExecutionStatus.COMPLETED
    assert result.record.value_excl_gst.amount == 4500
