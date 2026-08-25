from typing import Dict, Any, List
from collections import defaultdict

from app.application.snapshot import BusinessDataSnapshot
from app.analytics.models import AnalyticsResult
from app.domain.models import DealStatus

class SectorAnalytics:
    def __init__(self, snapshot: BusinessDataSnapshot):
        self.deals = snapshot.dataset.deals
        self.work_orders = snapshot.dataset.work_orders
        self.data_quality = snapshot.data_quality_report

    def get_sector_performance(self, target_sector: str = None) -> AnalyticsResult:
        """
        If target_sector is provided, returns metrics for just that sector.
        Otherwise, returns distribution for all sectors.
        """
        pipeline_value_by_sector: Dict[str, float] = defaultdict(float)
        deal_count_by_sector: Dict[str, int] = defaultdict(int)
        wo_value_by_sector: Dict[str, float] = defaultdict(float)
        wo_count_by_sector: Dict[str, int] = defaultdict(int)
        
        warnings = []
        missing_sector = 0

        # Calculate Pipeline (Deals)
        for deal in self.deals:
            sector_name = deal.sector.value if deal.sector else "Unknown"
            if target_sector and target_sector.lower() != sector_name.lower():
                continue
                
            if sector_name == "Unknown":
                missing_sector += 1
                
            if deal.status == DealStatus.OPEN:
                deal_count_by_sector[sector_name] += 1
                if deal.value and deal.value.amount is not None:
                    pipeline_value_by_sector[sector_name] += deal.value.amount

        # Calculate Execution (Work Orders)
        for wo in self.work_orders:
            sector_name = wo.sector.value if wo.sector else "Unknown"
            if target_sector and target_sector.lower() != sector_name.lower():
                continue
                
            wo_count_by_sector[sector_name] += 1
            if wo.value_excl_gst and wo.value_excl_gst.amount is not None:
                wo_value_by_sector[sector_name] += wo.value_excl_gst.amount
            elif wo.billed_value_incl_gst and wo.billed_value_incl_gst.amount is not None:
                wo_value_by_sector[sector_name] += wo.billed_value_incl_gst.amount

        if missing_sector > 0 and not target_sector:
            warnings.append(f"{missing_sector} deals have an unknown sector and could not be properly categorized.")

        all_sectors = set(pipeline_value_by_sector.keys()) | set(wo_value_by_sector.keys())
        table_data = []
        for sector in sorted(all_sectors):
            table_data.append({
                "Sector": sector,
                "Pipeline Value": pipeline_value_by_sector[sector],
                "Execution Value": wo_value_by_sector[sector]
            })

        total_pipe = sum(pipeline_value_by_sector.values())
        total_exec = sum(wo_value_by_sector.values())

        return AnalyticsResult(
            kpis=[
                {"type": "kpi", "title": "Total Pipeline Value", "value": f"₹{total_pipe:,.2f}"},
                {"type": "kpi", "title": "Total Execution Value", "value": f"₹{total_exec:,.2f}"}
            ],
            tables=[
                {
                    "type": "table",
                    "title": f"Sector Performance: {target_sector or 'All Sectors'}",
                    "columns": ["Sector", "Pipeline Value", "Execution Value"],
                    "data": table_data
                }
            ],
            warnings=warnings,
            metadata={"scope": "Deals and Work Orders"}
        )
