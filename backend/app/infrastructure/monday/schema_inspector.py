from typing import List, Dict, Any, Tuple
from .discovery_models import BoardDescriptor, ColumnDescriptor, BoardClassification, SemanticMapping

class SchemaInspector:
    
    def inspect(self, board_id: str, board_name: str, description: str, raw_columns: List[Dict[str, Any]]) -> BoardDescriptor:
        """Inspect board metadata and columns to deterministically classify it and generate mappings."""
        
        columns = []
        for c in raw_columns:
            columns.append(ColumnDescriptor(
                id=c.get("id", ""),
                title=c.get("title", ""),
                type=c.get("type", ""),
                settings_str=c.get("settings_str")
            ))
            
        descriptor = BoardDescriptor(
            board_id=board_id,
            board_name=board_name,
            description=description,
            columns=columns
        )
        
        # 1. Check for Deals Board
        deals_score, deals_evidence, deals_mapping = self._evaluate_as_deals_board(descriptor)
        
        # 2. Check for Work Orders Board
        wo_score, wo_evidence, wo_mapping = self._evaluate_as_work_orders_board(descriptor)
        
        # Classification Decision (Deterministic)
        if deals_score > 0.5 and deals_score > wo_score:
            descriptor.classification = BoardClassification.DEALS
            descriptor.confidence = deals_score
            descriptor.evidence = deals_evidence
            descriptor.semantic_mapping = SemanticMapping(mappings=deals_mapping)
        elif wo_score > 0.5 and wo_score > deals_score:
            descriptor.classification = BoardClassification.WORK_ORDERS
            descriptor.confidence = wo_score
            descriptor.evidence = wo_evidence
            descriptor.semantic_mapping = SemanticMapping(mappings=wo_mapping)
        else:
            descriptor.classification = BoardClassification.UNKNOWN
            descriptor.confidence = max(deals_score, wo_score)
            descriptor.evidence = ["Could not definitively classify board based on columns."]
            
        return descriptor

    def _evaluate_as_deals_board(self, descriptor: BoardDescriptor) -> Tuple[float, List[str], Dict[str, str]]:
        score = 0.0
        evidence = []
        mapping = {}
        
        # Name check
        if "deal" in descriptor.board_name.lower() or "funnel" in descriptor.board_name.lower() or "pipeline" in descriptor.board_name.lower():
            score += 0.3
            evidence.append(f"Board name '{descriptor.board_name}' suggests deals/pipeline.")
            
        # Semantic Column Checks
        client_col = descriptor.get_column_by_title("client code")
        if client_col:
            score += 0.2
            evidence.append(f"Found Client Code column ({client_col.id})")
            mapping["client_code"] = client_col.id
            
        value_col = descriptor.get_column_by_title("deal value") or descriptor.get_column_by_title("value")
        if value_col and value_col.type == "numeric":
            score += 0.2
            evidence.append(f"Found Deal Value column ({value_col.id})")
            mapping["deal_value"] = value_col.id
            
        stage_col = descriptor.get_column_by_title("deal stage") or descriptor.get_column_by_title("stage")
        if stage_col:
            score += 0.2
            evidence.append(f"Found Deal Stage column ({stage_col.id})")
            mapping["deal_stage"] = stage_col.id
            
        status_col = descriptor.get_column_by_title("deal status") or descriptor.get_column_by_title("status")
        if status_col:
            mapping["deal_status"] = status_col.id
            
        owner_col = descriptor.get_column_by_title("owner")
        if owner_col:
            mapping["owner_code"] = owner_col.id
            
        sector_col = descriptor.get_column_by_title("sector")
        if sector_col:
            mapping["sector"] = sector_col.id
            
        close_date_col = descriptor.get_column_by_title("close date")
        if close_date_col:
            mapping["close_date"] = close_date_col.id
            
        return score, evidence, mapping

    def _evaluate_as_work_orders_board(self, descriptor: BoardDescriptor) -> Tuple[float, List[str], Dict[str, str]]:
        score = 0.0
        evidence = []
        mapping = {}
        
        # Name check
        if "work order" in descriptor.board_name.lower() or "execution" in descriptor.board_name.lower() or "tracker" in descriptor.board_name.lower():
            score += 0.3
            evidence.append(f"Board name '{descriptor.board_name}' suggests work orders.")
            
        # Semantic Column Checks
        serial_col = descriptor.get_column_by_title("serial")
        if serial_col:
            score += 0.3
            evidence.append(f"Found Serial # column ({serial_col.id})")
            mapping["serial_number"] = serial_col.id
            
        customer_col = descriptor.get_column_by_title("customer")
        if customer_col:
            score += 0.1
            mapping["customer_code"] = customer_col.id
            
        status_col = descriptor.get_column_by_title("execution status")
        if status_col:
            score += 0.2
            evidence.append(f"Found Execution Status column ({status_col.id})")
            mapping["execution_status"] = status_col.id
            
        excl_gst_col = descriptor.get_column_by_title("amount (excl")
        if excl_gst_col:
            mapping["amount_excl_gst"] = excl_gst_col.id
            
        incl_gst_col = descriptor.get_column_by_title("amount (incl")
        if incl_gst_col:
            mapping["amount_incl_gst"] = incl_gst_col.id
            
        receivable_col = descriptor.get_column_by_title("amount to be received")
        if receivable_col:
            mapping["amount_receivable"] = receivable_col.id
            
        po_date_col = descriptor.get_column_by_title("po date")
        if po_date_col:
            mapping["po_date"] = po_date_col.id
            
        doc_type_col = descriptor.get_column_by_title("document type")
        if doc_type_col:
            mapping["document_type"] = doc_type_col.id
            
        sector_col = descriptor.get_column_by_title("sector")
        if sector_col:
            mapping["sector"] = sector_col.id

        return score, evidence, mapping
