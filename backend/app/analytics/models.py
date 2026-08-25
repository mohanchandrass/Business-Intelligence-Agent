from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class AnalyticsResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    metric_name: str
    value: Any
    dimensions: Optional[Dict[str, Any]] = None
    data_quality_warnings: List[str] = Field(default_factory=list)
    source_scope: str = "Deals and Work Orders"
    metadata: Dict[str, Any] = Field(default_factory=dict)
