import pytest
import json
from app.infrastructure.monday.discovery_models import BoardDescriptor, ColumnDescriptor
from app.infrastructure.monday.schema_inspector import SchemaInspector
from app.normalization.normalizer import NormalizationService
from app.infrastructure.monday.dtos import RawDealRecord, RawWorkOrderRecord
from app.analytics.pipeline import PipelineAnalytics
from app.application.snapshot import BusinessDataSnapshot, CrossBoardDataset
from app.domain.models import DataQualityReport

def test_semantic_mapping():
    inspector = SchemaInspector()
    descriptor = inspector.inspect("123", "Deals Board", "", [
        {"id": "name", "title": "Name", "type": "name"},
        {"id": "deal_val", "title": "Masked Deal value", "type": "numeric"},
        {"id": "stage", "title": "Deal Stage", "type": "status"},
        {"id": "owner", "title": "Owner", "type": "people"}
    ])
    assert descriptor.classification.value == "DEALS"
    mappings = descriptor.semantic_mapping.mappings
    assert mappings.get("deal_value") == "deal_val"
    assert mappings.get("deal_stage") == "stage"

def test_deal_value_extraction():
    raw = RawDealRecord(id="1", name="Naruto", client_code="C1", value="10,000.50", close_date="", stage="", status="", sector="", owner_code="")
    record = NormalizationService.normalize_deal(raw)
    assert record.record.value.amount == 10000.50

def test_missing_value_handling():
    raw = RawDealRecord(id="1", name="Naruto", client_code="C1", value="", close_date="", stage="", status="", sector="", owner_code="")
    record = NormalizationService.normalize_deal(raw)
    assert record.record.value is None
    assert any(i.field == "value" for i in record.report.issues)

def test_work_order_amount_extraction():
    raw = RawWorkOrderRecord(id="1", name="WO", customer_code="C1", serial_number="S1", execution_status="", amount_excl_gst=" 5000 ", amount_incl_gst="", amount_receivable="", po_date="", document_type="", sector="")
    record = NormalizationService.normalize_work_order(raw)
    assert record.record.value_excl_gst.amount == 5000.0

def test_po_date_extraction():
    raw = RawWorkOrderRecord(id="1", name="WO", customer_code="C1", serial_number="S1", execution_status="", amount_excl_gst="", amount_incl_gst="", amount_receivable="", po_date="2026-08-25", document_type="", sector="")
    record = NormalizationService.normalize_work_order(raw)
    assert record.record.po_date.isoformat() == "2026-08-25"

def test_deal_reference_extraction():
    raw = RawWorkOrderRecord(id="1", name="WO", customer_code="C1", serial_number="SDPLDEAL-101", execution_status="", amount_excl_gst="", amount_incl_gst="", amount_receivable="", po_date="", document_type="", sector="")
    record = NormalizationService.normalize_work_order(raw)
    assert record.record.deal_reference == "SDPLDEAL-101"

def test_customer_extraction():
    raw = RawWorkOrderRecord(id="1", name="WO", customer_code="WOCOMPANY_002", serial_number="SDPLDEAL-101", execution_status="", amount_excl_gst="", amount_incl_gst="", amount_receivable="", po_date="", document_type="", sector="")
    record = NormalizationService.normalize_work_order(raw)
    assert record.record.client_id == "COMPANY_002"

def test_analytics_reconciliation():
    raw = RawDealRecord(id="1", name="Naruto", client_code="C1", value="10000", close_date="", stage="B. SQL", status="Open", sector="", owner_code="")
    record = NormalizationService.normalize_deal(raw)
    
    dataset = CrossBoardDataset(deals=[record.record], work_orders=[])
    snapshot = BusinessDataSnapshot(dataset=dataset, data_quality_report=DataQualityReport())
    
    analytics = PipelineAnalytics(snapshot)
    res = analytics.get_overview()
    
    # Check KPIs
    assert len(res.kpis) == 2
    assert res.kpis[0]["title"] == "Active Deals"
    assert res.kpis[0]["value"] == "1"
    assert res.kpis[1]["title"] == "Pipeline Value"
    assert res.kpis[1]["value"] == "₹10,000.00"
    
    # Check Tables
    assert len(res.tables) == 1
    assert res.tables[0]["data"][0]["Deals"] == 1
    assert res.tables[0]["data"][0]["Value"] == 10000.0
