import re
from typing import Optional, Generic, TypeVar, Tuple
from datetime import date, datetime
from pydantic import BaseModel
from app.domain.models import (
    Deal, WorkOrder, Money, DealStatus, DealStage,
    Sector, WorkOrderExecutionStatus, Currency,
    DataQualityIssue, DataQualityReport, Severity
)
from app.infrastructure.monday.dtos import RawDealRecord, RawWorkOrderRecord

T = TypeVar('T')

class NormalizedRecord(BaseModel, Generic[T]):
    record: Optional[T] = None
    report: DataQualityReport

class NormalizationService:
    @staticmethod
    def normalize_string(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None
        
    @staticmethod
    def normalize_money(value_str: Optional[str], record_id: str, field_name: str, report: DataQualityReport) -> Optional[Money]:
        cleaned = NormalizationService.normalize_string(value_str)
        if not cleaned:
            report.add_issue(DataQualityIssue(
                record_id=record_id, record_type="Unknown", field=field_name,
                issue_type="MISSING_VALUE", severity=Severity.WARNING,
                message=f"{field_name} is missing", excluded=False, original_value=value_str
            ))
            return None
            
        try:
            # Remove any commas or currency symbols (very basic normalization)
            num_str = re.sub(r'[^\d.-]', '', cleaned)
            amount = float(num_str)
            return Money(amount=amount, currency=Currency.INR)
        except ValueError:
            report.add_issue(DataQualityIssue(
                record_id=record_id, record_type="Unknown", field=field_name,
                issue_type="MALFORMED_NUMBER", severity=Severity.ERROR,
                message=f"Could not parse monetary value: {cleaned}", excluded=False, original_value=value_str
            ))
            return None

    @staticmethod
    def normalize_date(value_str: Optional[str], record_id: str, field_name: str, report: DataQualityReport) -> Optional[date]:
        cleaned = NormalizationService.normalize_string(value_str)
        if not cleaned:
            return None
        try:
            # Monday dates are usually YYYY-MM-DD
            return datetime.strptime(cleaned, "%Y-%m-%d").date()
        except ValueError:
            report.add_issue(DataQualityIssue(
                record_id=record_id, record_type="Unknown", field=field_name,
                issue_type="MALFORMED_DATE", severity=Severity.ERROR,
                message=f"Could not parse date: {cleaned}", excluded=False, original_value=value_str
            ))
            return None

    @staticmethod
    def normalize_client_code(code: Optional[str]) -> Optional[str]:
        # Rule: Strip "WO" prefix so "WOCOMPANY_002" -> "COMPANY_002"
        # and standardise underscore: "COMPANY089" -> "COMPANY_089"
        cleaned = NormalizationService.normalize_string(code)
        if not cleaned:
            return None
            
        if cleaned.startswith("WOCOMPANY"):
            cleaned = cleaned.replace("WOCOMPANY", "COMPANY")
            
        if cleaned.startswith("COMPANY") and "_" not in cleaned:
            num = cleaned.replace("COMPANY", "")
            cleaned = f"COMPANY_{num}"
            
        return cleaned

    @staticmethod
    def normalize_deal(raw: RawDealRecord) -> NormalizedRecord[Deal]:
        report = DataQualityReport()
        report.total_records_inspected = 1
        
        name = NormalizationService.normalize_string(raw.name)
        if not name:
            report.add_issue(DataQualityIssue(
                record_id=raw.id, record_type="Deal", field="name",
                issue_type="MISSING_IDENTIFIER", severity=Severity.ERROR,
                message="Deal name is missing, cannot identify record", excluded=True
            ))
            return NormalizedRecord(record=None, report=report)
            
        client_code = NormalizationService.normalize_client_code(raw.client_code)
        if not client_code:
            client_code = "UNKNOWN"
            report.add_issue(DataQualityIssue(
                record_id=raw.id, record_type="Deal", field="client_code",
                issue_type="MISSING_VALUE", severity=Severity.WARNING,
                message="Client code is missing", excluded=False
            ))
            
        value = NormalizationService.normalize_money(raw.value, raw.id, "value", report)
        close_date = NormalizationService.normalize_date(raw.close_date, raw.id, "close_date", report)
        
        try:
            status = DealStatus(NormalizationService.normalize_string(raw.status))
        except ValueError:
            status = DealStatus.UNKNOWN
            
        try:
            stage = DealStage(NormalizationService.normalize_string(raw.stage))
        except ValueError:
            stage = DealStage.UNKNOWN

        try:
            sector = Sector(NormalizationService.normalize_string(raw.sector))
        except ValueError:
            sector = Sector.UNKNOWN
            
        deal = Deal(
            id=raw.id,
            name=name,
            client_id=client_code,
            owner_id=NormalizationService.normalize_string(raw.owner_code),
            status=status,
            stage=stage,
            sector=sector,
            value=value,
            close_date=close_date
        )
        
        report.usable_records = 1
        return NormalizedRecord(record=deal, report=report)

    @staticmethod
    def normalize_work_order(raw: RawWorkOrderRecord) -> NormalizedRecord[WorkOrder]:
        report = DataQualityReport()
        report.total_records_inspected = 1
        
        name = NormalizationService.normalize_string(raw.name)
        serial_number = NormalizationService.normalize_string(raw.serial_number)
        
        if not name or not serial_number:
            report.add_issue(DataQualityIssue(
                record_id=raw.id, record_type="WorkOrder", field="name/serial_number",
                issue_type="MISSING_IDENTIFIER", severity=Severity.ERROR,
                message="Missing critical identifying fields", excluded=True
            ))
            return NormalizedRecord(record=None, report=report)
            
        client_code = NormalizationService.normalize_client_code(raw.customer_code)
        if not client_code:
            client_code = "UNKNOWN"
            
        value_excl_gst = NormalizationService.normalize_money(raw.amount_excl_gst, raw.id, "amount_excl_gst", report)
        billed_value = NormalizationService.normalize_money(raw.amount_incl_gst, raw.id, "amount_incl_gst", report)
        receivable = NormalizationService.normalize_money(raw.amount_receivable, raw.id, "amount_receivable", report)
        
        po_date = NormalizationService.normalize_date(raw.po_date, raw.id, "po_date", report)
        
        try:
            exec_status = WorkOrderExecutionStatus(NormalizationService.normalize_string(raw.execution_status))
        except ValueError:
            exec_status = WorkOrderExecutionStatus.UNKNOWN
            
        try:
            sector = Sector(NormalizationService.normalize_string(raw.sector))
        except ValueError:
            sector = Sector.UNKNOWN
            
        wo = WorkOrder(
            id=raw.id,
            name=name,
            deal_reference=serial_number,
            client_id=client_code,
            execution_status=exec_status,
            sector=sector,
            document_type=NormalizationService.normalize_string(raw.document_type),
            po_date=po_date,
            value_excl_gst=value_excl_gst,
            billed_value_incl_gst=billed_value,
            receivable_amount=receivable
        )
        
        report.usable_records = 1
        return NormalizedRecord(record=wo, report=report)
