from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from app.infrastructure.monday.discovery_models import SemanticMapping

class ColumnValue(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    text: Optional[str] = None
    value: Optional[str] = None
    type: Optional[str] = None

class MondayItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    column_values: List[ColumnValue] = Field(default_factory=list)
    
    def get_column_text(self, column_id: str) -> Optional[str]:
        for cv in self.column_values:
            if cv.id == column_id:
                return cv.text
        return None

    def get_column_value(self, column_id: str) -> Optional[str]:
        for cv in self.column_values:
            if cv.id == column_id:
                return cv.value
        return None

class Board(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    items_page: Optional[Dict[str, Any]] = None

class MondayResponseData(BaseModel):
    boards: List[Board] = Field(default_factory=list)

class MondayGraphQLResponse(BaseModel):
    data: Optional[MondayResponseData] = None
    errors: Optional[List[Dict[str, Any]]] = None
    account_id: Optional[int] = None

# --- Raw Deal Record ---
class RawDealRecord(BaseModel):
    id: str
    name: str  # Deal identifier
    client_code: Optional[str] = None
    owner_code: Optional[str] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    close_date: Optional[str] = None
    value: Optional[str] = None
    sector: Optional[str] = None

    @classmethod
    def from_item(cls, item: MondayItem, mapping: SemanticMapping) -> "RawDealRecord":
        return cls(
            id=item.id,
            name=item.name,
            owner_code=item.get_column_text(mapping.get_column_id("owner_code") or ""),
            client_code=item.get_column_text(mapping.get_column_id("client_code") or ""),
            status=item.get_column_text(mapping.get_column_id("deal_status") or ""),
            close_date=item.get_column_text(mapping.get_column_id("close_date") or ""),
            value=item.get_column_text(mapping.get_column_id("deal_value") or ""),
            stage=item.get_column_text(mapping.get_column_id("deal_stage") or ""),
            sector=item.get_column_text(mapping.get_column_id("sector") or "")
        )

# --- Raw Work Order Record ---
class RawWorkOrderRecord(BaseModel):
    id: str
    name: str  # Work order name
    customer_code: Optional[str] = None
    serial_number: Optional[str] = None
    execution_status: Optional[str] = None
    po_date: Optional[str] = None
    document_type: Optional[str] = None
    sector: Optional[str] = None
    amount_excl_gst: Optional[str] = None
    amount_incl_gst: Optional[str] = None
    amount_receivable: Optional[str] = None

    @classmethod
    def from_item(cls, item: MondayItem, mapping: SemanticMapping) -> "RawWorkOrderRecord":
        return cls(
            id=item.id,
            name=item.name,
            customer_code=item.get_column_text(mapping.get_column_id("customer_code") or ""),
            serial_number=item.get_column_text(mapping.get_column_id("serial_number") or ""),
            execution_status=item.get_column_text(mapping.get_column_id("execution_status") or ""),
            po_date=item.get_column_text(mapping.get_column_id("po_date") or ""),
            document_type=item.get_column_text(mapping.get_column_id("document_type") or ""),
            sector=item.get_column_text(mapping.get_column_id("sector") or ""),
            amount_excl_gst=item.get_column_text(mapping.get_column_id("amount_excl_gst") or ""),
            amount_incl_gst=item.get_column_text(mapping.get_column_id("amount_incl_gst") or ""),
            amount_receivable=item.get_column_text(mapping.get_column_id("amount_receivable") or "")
        )
