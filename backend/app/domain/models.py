from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel, Field, ConfigDict

# --- Support Enums ---

class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class Currency(str, Enum):
    INR = "INR"

class DealStatus(str, Enum):
    WON = "Won"
    DEAD = "Dead"
    OPEN = "Open"
    ON_HOLD = "On Hold"
    UNKNOWN = "Unknown"

class DealStage(str, Enum):
    LEAD_GENERATED = "A. Lead Generated"
    SALES_QUALIFIED = "B. Sales Qualified Leads"
    DEMO_DONE = "C. Demo Done"
    FEASIBILITY = "D. Feasibility"
    PROPOSAL_SENT = "E. Proposal/Commercials Sent"
    NEGOTIATIONS = "F. Negotiations"
    PROJECT_WON = "G. Project Won"
    WORK_ORDER_RECEIVED = "H. Work Order Received"
    POC = "I. POC"
    INVOICE_SENT = "J. Invoice sent"
    AMOUNT_ACCRUED = "K. Amount Accrued"
    PROJECT_LOST = "L. Project Lost"
    PROJECTS_ON_HOLD = "M. Projects On Hold"
    NOT_RELEVANT_MOMENT = "N. Not relevant at the moment"
    NOT_RELEVANT_ALL = "O. Not Relevant at all"
    PROJECT_COMPLETED = "Project Completed"
    UNKNOWN = "Unknown"

class WorkOrderExecutionStatus(str, Enum):
    NOT_STARTED = "Not Started"
    ONGOING = "Ongoing"
    PARTIAL_COMPLETED = "Partial Completed"
    COMPLETED = "Completed"
    EXECUTED_UNTIL_CURRENT = "Executed until current month"
    DETAILS_PENDING = "Details pending from Client"
    PAUSED_STUCK = "Pause / struck"
    UNKNOWN = "Unknown"

class Sector(str, Enum):
    POWERLINE = "Powerline"
    MINING = "Mining"
    TENDER = "Tender"
    RENEWABLES = "Renewables"
    RAILWAYS = "Railways"
    CONSTRUCTION = "Construction"
    DSP = "DSP"
    SECURITY_SURVEILLANCE = "Security and Surveillance"
    AVIATION = "Aviation"
    MANUFACTURING = "Manufacturing"
    OTHERS = "Others"
    UNKNOWN = "Unknown"


# --- Data Quality Models ---

class DataQualityIssue(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    record_id: str
    record_type: str
    field: str
    issue_type: str
    severity: Severity
    message: str
    excluded: bool
    original_value: Optional[Any] = None

class DataQualityReport(BaseModel):
    total_records_inspected: int = 0
    usable_records: int = 0
    excluded_records: int = 0
    issues: List[DataQualityIssue] = Field(default_factory=list)
    
    def add_issue(self, issue: DataQualityIssue):
        self.issues.append(issue)
        if issue.excluded:
            self.excluded_records += 1
            
    def get_summary(self) -> Dict[str, Any]:
        warnings = len([i for i in self.issues if i.severity == Severity.WARNING])
        errors = len([i for i in self.issues if i.severity == Severity.ERROR])
        return {
            "inspected": self.total_records_inspected,
            "usable": self.usable_records,
            "excluded": self.excluded_records,
            "warnings": warnings,
            "errors": errors
        }


# --- Canonical Domain Models ---

class Money(BaseModel):
    model_config = ConfigDict(frozen=True)
    amount: float
    currency: Currency = Currency.INR

class Deal(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: str
    name: str  # e.g., SDPLDEAL-075
    client_id: str  # Canonicalized COMPANYxxx
    owner_id: Optional[str] = None
    
    status: DealStatus
    stage: DealStage
    sector: Sector
    
    value: Optional[Money] = None
    
    close_date: Optional[date] = None
    tentative_close_date: Optional[date] = None
    created_date: Optional[date] = None

class WorkOrder(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: str
    name: str
    deal_reference: str  # Strict FK to Deal.name (e.g., SDPLDEAL-075)
    client_id: str  # Canonicalized COMPANYxxx
    
    execution_status: WorkOrderExecutionStatus
    sector: Sector
    document_type: Optional[str] = None
    
    po_date: Optional[date] = None
    probable_start_date: Optional[date] = None
    probable_end_date: Optional[date] = None
    
    value_excl_gst: Optional[Money] = None
    billed_value_incl_gst: Optional[Money] = None
    receivable_amount: Optional[Money] = None
