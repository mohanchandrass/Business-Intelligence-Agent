from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field

class BoardClassification(str, Enum):
    DEALS = "DEALS"
    WORK_ORDERS = "WORK_ORDERS"
    UNKNOWN = "UNKNOWN"

class SemanticMapping(BaseModel):
    """Maps semantic concepts to raw Monday column IDs for a specific board."""
    model_config = ConfigDict(frozen=True)
    
    # Mappings from generic concept (e.g. "deal_value") to raw column ID (e.g. "numeric_mm6jty17")
    mappings: Dict[str, str] = Field(default_factory=dict)
    
    def get_column_id(self, semantic_key: str) -> Optional[str]:
        return self.mappings.get(semantic_key)

class ColumnDescriptor(BaseModel):
    id: str
    title: str
    type: str
    settings_str: Optional[str] = None

class BoardDescriptor(BaseModel):
    board_id: str
    board_name: str
    description: Optional[str] = None
    columns: List[ColumnDescriptor] = Field(default_factory=list)
    
    classification: BoardClassification = BoardClassification.UNKNOWN
    confidence: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    
    semantic_mapping: SemanticMapping = Field(default_factory=SemanticMapping)
    
    def get_column_by_title(self, title_substring: str) -> Optional[ColumnDescriptor]:
        """Find a column matching a title substring (case-insensitive)."""
        lower_target = title_substring.lower()
        for col in self.columns:
            if lower_target in col.title.lower():
                return col
        return None
