from typing import Dict, Any, List
from collections import defaultdict

from app.application.snapshot import BusinessDataSnapshot
from app.analytics.models import AnalyticsResult
from app.domain.models import WorkOrderExecutionStatus

class WorkOrderAnalytics:
    def __init__(self, snapshot: BusinessDataSnapshot):
        self.work_orders = snapshot.dataset.work_orders
        self.data_quality = snapshot.data_quality_report

    def get_operational_metrics(self) -> AnalyticsResult:
        total_wos = len(self.work_orders)
        total_value = 0.0
        execution_status_dist: Dict[str, int] = defaultdict(int)
        
        missing_value_count = 0

        for wo in self.work_orders:
            execution_status_dist[wo.execution_status.value] += 1
            
            if wo.value_excl_gst and wo.value_excl_gst.amount is not None:
                total_value += wo.value_excl_gst.amount
            else:
                missing_value_count += 1

        warnings = []
        if missing_value_count > 0:
            warnings.append(f"{missing_value_count} work orders have no explicit value_excl_gst. Value metrics may be incomplete.")

        return AnalyticsResult(
            metric_name="Operational Metrics",
            value=total_wos,
            dimensions={
                "total_work_orders": total_wos,
                "total_value": total_value,
                "execution_status_distribution": dict(execution_status_dist),
                "delayed_count": execution_status_dist.get(WorkOrderExecutionStatus.PAUSED_STUCK.value, 0)
            },
            data_quality_warnings=warnings,
            source_scope="Monday.com Work Orders Board"
        )
