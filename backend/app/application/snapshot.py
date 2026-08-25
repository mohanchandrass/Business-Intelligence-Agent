from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.domain.models import Deal, WorkOrder, DataQualityReport
from app.normalization.normalizer import NormalizationService
from app.infrastructure.monday.board_catalog import BoardCatalog
from app.infrastructure.monday.repositories import MondayDealRepository, MondayWorkOrderRepository

class CrossBoardDataset(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    deals: List[Deal] = Field(default_factory=list)
    work_orders: List[WorkOrder] = Field(default_factory=list)
    
    # Relationships
    work_orders_by_deal: Dict[str, List[WorkOrder]] = Field(default_factory=dict)
    deals_by_id: Dict[str, Deal] = Field(default_factory=dict)
    
    # Metadata
    orphan_work_orders: List[WorkOrder] = Field(default_factory=list)
    deals_without_work_orders: List[Deal] = Field(default_factory=list)

class BusinessDataSnapshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    dataset: CrossBoardDataset
    data_quality_report: DataQualityReport
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)

import logging
logger = logging.getLogger(__name__)

class BusinessDataService:
    def __init__(self, catalog: BoardCatalog):
        self.catalog = catalog

    async def get_snapshot(self, req_id: str = "REQ unknown") -> BusinessDataSnapshot:
        logger.info(f"[{req_id}] BOARD DISCOVERY started")
        # 1. Retrieve Raw DTOs using dynamic discovery
        deals_descriptor = await self.catalog.get_deals_board()
        wo_descriptor = await self.catalog.get_work_orders_board()
        
        deal_repo = MondayDealRepository(self.catalog.client, deals_descriptor)
        wo_repo = MondayWorkOrderRepository(self.catalog.client, wo_descriptor)
        
        logger.info(f"[{req_id}] MONDAY API raw data retrieval")
        raw_deals = await deal_repo.get_all_deals()
        raw_wos = await wo_repo.get_all_work_orders()
        
        logger.info(f"[{req_id}] RAW DATA retrieved: {len(raw_deals)} deals, {len(raw_wos)} work orders")
        
        # 2. Normalize and build Data Quality Report
        logger.info(f"[{req_id}] NORMALIZATION starting")
        global_report = DataQualityReport()
        global_report.total_records_inspected = len(raw_deals) + len(raw_wos)
        
        valid_deals: List[Deal] = []
        for raw_deal in raw_deals:
            result = NormalizationService.normalize_deal(raw_deal)
            for issue in result.report.issues:
                global_report.add_issue(issue)
            if result.record:
                valid_deals.append(result.record)
                global_report.usable_records += 1

        valid_wos: List[WorkOrder] = []
        for raw_wo in raw_wos:
            result = NormalizationService.normalize_work_order(raw_wo)
            for issue in result.report.issues:
                global_report.add_issue(issue)
            if result.record:
                valid_wos.append(result.record)
                global_report.usable_records += 1

        logger.info(f"[{req_id}] NORMALIZATION complete: Valid Deals: {len(valid_deals)}/{len(raw_deals)}, Valid WOs: {len(valid_wos)}/{len(raw_wos)}, Issues: {len(global_report.issues)}")
        
        # 3. Cross-Board Relationship Engine
        dataset = CrossBoardDataset()
        dataset.deals = valid_deals
        dataset.work_orders = valid_wos
        
        for deal in valid_deals:
            dataset.deals_by_id[deal.name] = deal
            dataset.work_orders_by_deal[deal.name] = []
            
        # Instrument mapping (First 5 Work Orders)
        logger.info(f"[{req_id}] --- DATA MAPPING SAMPLE ---")
        sample_deals = list(dataset.deals_by_id.keys())[:5]
        logger.info(f"[{req_id}] Sample Deal Identifiers (Deal Names): {sample_deals}")
        
        match_samples = []
        for wo in valid_wos[:5]:
            matched = wo.deal_reference in dataset.deals_by_id
            match_samples.append(f"WO RAW Ref (Unknown yet) -> Normalized Ref: '{wo.deal_reference}' -> MATCH: {matched}")
        for sample in match_samples:
            logger.info(f"[{req_id}] {sample}")
        logger.info(f"[{req_id}] -----------------------------")

        for wo in valid_wos:
            if wo.deal_reference in dataset.deals_by_id:
                dataset.work_orders_by_deal[wo.deal_reference].append(wo)
            else:
                dataset.orphan_work_orders.append(wo)
                
        for deal in valid_deals:
            if not dataset.work_orders_by_deal.get(deal.name):
                dataset.deals_without_work_orders.append(deal)

        logger.info(f"[{req_id}] SNAPSHOT constructed: Matched WOs: {len(valid_wos)-len(dataset.orphan_work_orders)}, Orphan WOs: {len(dataset.orphan_work_orders)}, Unmatched Deals: {len(dataset.deals_without_work_orders)}")

        return BusinessDataSnapshot(
            dataset=dataset,
            data_quality_report=global_report
        )
