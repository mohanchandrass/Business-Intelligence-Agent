from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class AnalyticsResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    kpis: List[Dict[str, Any]] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
