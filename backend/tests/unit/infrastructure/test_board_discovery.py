import pytest
from app.infrastructure.monday.schema_inspector import SchemaInspector
from app.infrastructure.monday.discovery_models import BoardClassification

@pytest.fixture
def inspector():
    return SchemaInspector()

def test_deals_board_classification(inspector):
    raw_columns = [
        {"id": "col1", "title": "Client Code", "type": "dropdown"},
        {"id": "col2", "title": "Deal Value", "type": "numeric"},
        {"id": "col3", "title": "Deal Stage", "type": "color"}
    ]
    
    descriptor = inspector.inspect("123", "Sales Funnel", "", raw_columns)
    
    assert descriptor.classification == BoardClassification.DEALS
    assert descriptor.semantic_mapping.get_column_id("client_code") == "col1"
    assert descriptor.semantic_mapping.get_column_id("deal_value") == "col2"
    assert descriptor.semantic_mapping.get_column_id("deal_stage") == "col3"
    assert descriptor.confidence > 0.5

def test_work_orders_board_classification(inspector):
    raw_columns = [
        {"id": "col_a", "title": "Serial #", "type": "text"},
        {"id": "col_b", "title": "Execution Status", "type": "color"},
        {"id": "col_c", "title": "Amount (excl GST)", "type": "numeric"}
    ]
    
    descriptor = inspector.inspect("456", "Work Order Tracker", "", raw_columns)
    
    assert descriptor.classification == BoardClassification.WORK_ORDERS
    assert descriptor.semantic_mapping.get_column_id("serial_number") == "col_a"
    assert descriptor.semantic_mapping.get_column_id("execution_status") == "col_b"
    assert descriptor.confidence > 0.5

def test_unknown_board_classification(inspector):
    raw_columns = [
        {"id": "c1", "title": "Name", "type": "text"},
        {"id": "c2", "title": "Date", "type": "date"}
    ]
    
    descriptor = inspector.inspect("789", "Random Board", "", raw_columns)
    
    assert descriptor.classification == BoardClassification.UNKNOWN
    assert descriptor.confidence < 0.5
