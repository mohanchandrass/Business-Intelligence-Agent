from typing import Dict, Any, List
from collections import defaultdict
import statistics

from app.application.snapshot import BusinessDataSnapshot
from app.analytics.models import AnalyticsResult
from app.domain.models import DealStatus

class DealAnalytics:
    def __init__(self, snapshot: BusinessDataSnapshot):
        self.deals = snapshot.dataset.deals
        self.data_quality = snapshot.data_quality_report

    def get_metrics(self) -> AnalyticsResult:
        total_value = 0.0
        deal_count = len(self.deals)
        values = []
        
        status_distribution: Dict[str, int] = defaultdict(int)
        sector_distribution: Dict[str, int] = defaultdict(int)
        
        missing_value_count = 0
        missing_sector_count = 0

        for deal in self.deals:
            status_distribution[deal.status.value] += 1
            
            if deal.sector and deal.sector.value != "Unknown":
                sector_distribution[deal.sector.value] += 1
            else:
                missing_sector_count += 1
                
            if deal.value and deal.value.amount is not None:
                total_value += deal.value.amount
                values.append(deal.value.amount)
            else:
                missing_value_count += 1

        avg_value = total_value / len(values) if values else 0.0
        median_value = statistics.median(values) if values else 0.0
        
        warnings = []
        if missing_value_count > 0:
            warnings.append(f"{missing_value_count} deals lack monetary value.")
        if missing_sector_count > 0:
            warnings.append(f"{missing_sector_count} deals have an unknown sector.")

        return AnalyticsResult(
            metric_name="Deal Metrics",
            value=total_value,
            dimensions={
                "deal_count": deal_count,
                "average_deal_value": avg_value,
                "median_deal_value": median_value,
                "status_distribution": dict(status_distribution),
                "sector_distribution": dict(sector_distribution),
                "won_deals": status_distribution.get(DealStatus.WON.value, 0)
            },
            data_quality_warnings=warnings,
            source_scope="Monday.com Deals Board (All deals)"
        )
