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
            metric_name="Cross-Board Overview",
            value=deals_with_wos,
            dimensions={
                "deals_with_work_orders": deals_with_wos,
                "deals_without_work_orders": len(self.dataset.deals_without_work_orders),
                "orphan_work_orders": len(self.dataset.orphan_work_orders),
                "pipeline_value": deals_pipeline_val,
                "execution_value": execution_val,
            },
            data_quality_warnings=warnings,
            source_scope="Joined Deals & Work Orders"
        )
