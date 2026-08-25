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

        table_data = []
        for status, count in status_distribution.items():
            table_data.append({
                "Status": status,
                "Deals": count
            })

        return AnalyticsResult(
            kpis=[
                {"type": "kpi", "title": "Total Deals", "value": str(deal_count)},
                {"type": "kpi", "title": "Avg Deal Value", "value": f"₹{avg_value:,.2f}"},
                {"type": "kpi", "title": "Won Deals", "value": str(status_distribution.get(DealStatus.WON.value, 0))}
            ],
            tables=[
                {
                    "type": "table",
                    "title": "Deal Status Distribution",
                    "columns": ["Status", "Deals"],
                    "data": table_data
                }
            ],
            warnings=warnings,
            metadata={"scope": "Monday.com Deals Board (All deals)"}
        )
