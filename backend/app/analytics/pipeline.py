from typing import Dict, Any, List, Optional
from collections import defaultdict

from app.application.snapshot import BusinessDataSnapshot
from app.analytics.models import AnalyticsResult
from app.domain.models import DealStage, DealStatus

class PipelineAnalytics:
    def __init__(self, snapshot: BusinessDataSnapshot):
        self.deals = snapshot.dataset.deals
        self.data_quality = snapshot.data_quality_report

    def get_overview(self) -> AnalyticsResult:
        total_value = 0.0
        deal_count = 0
        deals_by_stage: Dict[str, int] = defaultdict(int)
        value_by_stage: Dict[str, float] = defaultdict(float)
        warnings: List[str] = []
        
        missing_value_count = 0

        for deal in self.deals:
            # We only count active pipeline (not dead/won/on hold typically, but for this basic logic we'll consider OPEN deals)
            if deal.status != DealStatus.OPEN:
                continue
                
            deal_count += 1
            deals_by_stage[deal.stage.value] += 1
            
            if deal.value and deal.value.amount is not None:
                total_value += deal.value.amount
                value_by_stage[deal.stage.value] += deal.value.amount
            else:
                missing_value_count += 1

        if missing_value_count > 0:
            warnings.append(f"{missing_value_count} open deals have no assigned monetary value. Pipeline value may be underrepresented.")

        return AnalyticsResult(
            metric_name="Pipeline Overview",
            value=total_value,
            dimensions={
                "deal_count": deal_count,
                "deals_by_stage": dict(deals_by_stage),
                "value_by_stage": dict(value_by_stage),
            },
            data_quality_warnings=warnings,
            source_scope="Monday.com Deals Board (Status: Open)"
        )
