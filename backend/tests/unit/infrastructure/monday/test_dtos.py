from app.infrastructure.monday.dtos import (
    MondayItem, ColumnValue, RawDealRecord, RawWorkOrderRecord
)
from app.infrastructure.monday.discovery_models import SemanticMapping

def test_raw_deal_record_mapping():
    item = MondayItem(
        id="111",
        name="SDPLDEAL-100",
        column_values=[
            ColumnValue(id="numeric_mm6jty17", text="500000"),
            ColumnValue(id="dropdown_mm6jv7st", text="COMPANY001"),
            ColumnValue(id="color_mm6jqc55", text="H. Work Order Received")
        ]
    )
    
    mapping = SemanticMapping(mappings={
        "deal_value": "numeric_mm6jty17",
        "client_code": "dropdown_mm6jv7st",
        "deal_stage": "color_mm6jqc55"
    })
    
    deal_dto = RawDealRecord.from_item(item, mapping)
    assert deal_dto.id == "111"
    assert deal_dto.name == "SDPLDEAL-100"
    assert deal_dto.value == "500000"
    assert deal_dto.client_code == "COMPANY001"
    assert deal_dto.stage == "H. Work Order Received"

def test_raw_work_order_record_mapping():
    item = MondayItem(
        id="222",
        name="WO-100",
        column_values=[
            ColumnValue(id="dropdown_mm6j6em5", text="SDPLDEAL-100"),
            ColumnValue(id="dropdown_mm6jg7k1", text="WOCOMPANY_001"),
            ColumnValue(id="numeric_mm6jcs5f", text="450000")
        ]
    )
    
    mapping = SemanticMapping(mappings={
        "serial_number": "dropdown_mm6j6em5",
        "customer_code": "dropdown_mm6jg7k1",
        "amount_excl_gst": "numeric_mm6jcs5f"
    })
    
    wo_dto = RawWorkOrderRecord.from_item(item, mapping)
    assert wo_dto.id == "222"
    assert wo_dto.name == "WO-100"
    assert wo_dto.serial_number == "SDPLDEAL-100"
    assert wo_dto.customer_code == "WOCOMPANY_001"
    assert wo_dto.amount_excl_gst == "450000"

