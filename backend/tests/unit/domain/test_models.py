import pytest
from datetime import date
from pydantic import ValidationError
from app.domain.models import (
    Deal, WorkOrder, Money, DealStatus, DealStage, 
    Sector, WorkOrderExecutionStatus, Currency,
    DataQualityIssue, DataQualityReport, Severity
)

def test_money_default_currency():
    money = Money(amount=100.50)
    assert money.currency == Currency.INR
    assert money.amount == 100.50

def test_deal_instantiation():
    deal = Deal(
        id="123",
        name="SDPLDEAL-001",
        client_id="COMPANY001",
        status=DealStatus.WON,
        stage=DealStage.PROJECT_WON,
        sector=Sector.POWERLINE,
        value=Money(amount=5000)
    )
    assert deal.id == "123"
    assert deal.name == "SDPLDEAL-001"
    assert deal.value.amount == 5000.0

def test_work_order_instantiation():
    wo = WorkOrder(
        id="456",
        name="WO-001",
        deal_reference="SDPLDEAL-001",
        client_id="COMPANY001",
        execution_status=WorkOrderExecutionStatus.COMPLETED,
        sector=Sector.POWERLINE,
        value_excl_gst=Money(amount=4500)
    )
    assert wo.deal_reference == "SDPLDEAL-001"
    assert wo.sector == Sector.POWERLINE
    
def test_data_quality_report():
    report = DataQualityReport(total_records_inspected=10)
    
    issue1 = DataQualityIssue(
        record_id="123",
        record_type="Deal",
        field="value",
        issue_type="MISSING_VALUE",
        severity=Severity.WARNING,
        message="Value is missing",
        excluded=False
    )
    
    issue2 = DataQualityIssue(
        record_id="456",
        record_type="WorkOrder",
        field="po_date",
        issue_type="INVALID_DATE",
        severity=Severity.ERROR,
        message="Date is unparseable",
        excluded=True
    )
    
    report.add_issue(issue1)
    report.add_issue(issue2)
    
    assert report.total_records_inspected == 10
    assert report.excluded_records == 1
    
    summary = report.get_summary()
    assert summary["warnings"] == 1
    assert summary["errors"] == 1
    assert summary["excluded"] == 1

def test_domain_models_are_frozen():
    deal = Deal(
        id="123", name="Deal1", client_id="C1",
        status=DealStatus.OPEN, stage=DealStage.POC, sector=Sector.POWERLINE
    )
    with pytest.raises(ValidationError):
        deal.status = DealStatus.WON  # Should fail because model is frozen
