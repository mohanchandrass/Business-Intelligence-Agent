from typing import Dict, Any, List
from app.application.snapshot import BusinessDataSnapshot
from app.analytics.models import AnalyticsResult

class CrossBoardAnalytics:
    def __init__(self, snapshot: BusinessDataSnapshot):
        self.dataset = snapshot.dataset
        self.data_quality = snapshot.data_quality_report

    def get_cross_board_metrics(self) -> AnalyticsResult:
        deals_with_wos = len(self.dataset.deals) - len(self.dataset.deals_without_work_orders)
        
        deals_pipeline_val = sum((d.value.amount for d in self.dataset.deals if d.value and d.value.amount), 0.0)
        
        execution_val = sum(
            (wo.value_excl_gst.amount for wo in self.dataset.work_orders if wo.value_excl_gst and wo.value_excl_gst.amount),
            0.0
        )
        
        warnings = []
        if self.dataset.orphan_work_orders:
            warnings.append(f"{len(self.dataset.orphan_work_orders)} work orders could not be matched to any deal.")
            
        return AnalyticsResult(
            kpis=[
                {"type": "kpi", "title": "Matched Deals", "value": str(deals_with_wos)},
                {"type": "kpi", "title": "Deals w/o WOs", "value": str(len(self.dataset.deals_without_work_orders))},
                {"type": "kpi", "title": "Pipeline Value", "value": f"₹{deals_pipeline_val:,.2f}"},
                {"type": "kpi", "title": "Execution Value", "value": f"₹{execution_val:,.2f}"}
            ],
            tables=[
                {
                    "type": "table",
                    "title": "Cross-Board Relationship",
                    "columns": ["Metric", "Count"],
                    "data": [
                        {"Metric": "Deals with Work Orders", "Count": deals_with_wos},
                        {"Metric": "Deals without Work Orders", "Count": len(self.dataset.deals_without_work_orders)},
                        {"Metric": "Orphan Work Orders", "Count": len(self.dataset.orphan_work_orders)}
                    ]
                }
            ],
            warnings=warnings,
            metadata={"scope": "Joined Deals & Work Orders"}
        )
