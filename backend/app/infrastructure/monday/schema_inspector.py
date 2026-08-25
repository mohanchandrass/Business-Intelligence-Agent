from typing import List, Dict, Any, Tuple, Optional
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

    def _score_column(self, col: ColumnDescriptor, expected_types: List[str], aliases: List[str]) -> Tuple[float, List[str]]:
        score = 0.0
        evidence = []
        
        lower_title = col.title.lower()
        
        if expected_types and col.type not in expected_types:
            return 0.0, []
            
        for alias in aliases:
            if alias.lower() == lower_title:
                score += 1.0
                evidence.append(f"Exact match on alias '{alias}'")
            elif alias.lower() in lower_title:
                score += 0.5
                evidence.append(f"Partial match on alias '{alias}'")
                
        if expected_types:
            evidence.append(f"Matches expected type {col.type}")
            
        return score, evidence

    def _find_best_column(self, descriptor: BoardDescriptor, expected_types: List[str], aliases: List[str]) -> Tuple[Optional[ColumnDescriptor], float, List[str]]:
        best_col = None
        best_score = 0.0
        best_evidence = []
        
        for col in descriptor.columns:
            score, evidence = self._score_column(col, expected_types, aliases)
            if score > best_score:
                best_col = col
                best_score = score
                best_evidence = evidence
                
        return best_col, best_score, best_evidence

    def _evaluate_as_deals_board(self, descriptor: BoardDescriptor) -> Tuple[float, List[str], Dict[str, str]]:
        board_score = 0.0
        board_evidence = []
        mapping = {}
        
        if "deal" in descriptor.board_name.lower() or "funnel" in descriptor.board_name.lower() or "pipeline" in descriptor.board_name.lower():
            board_score += 0.3
            board_evidence.append(f"Board name '{descriptor.board_name}' suggests deals/pipeline.")
            
        # Define semantic fields and their aliases
        semantic_fields = {
            "client_code": (["dropdown", "text", "name"], ["client code", "customer", "client"]),
            "deal_value": (["numeric", "numbers", "number"], ["deal value", "value", "amount"]),
            "deal_stage": (["status", "dropdown", "color"], ["deal stage", "stage", "pipeline stage"]),
            "deal_status": (["status", "dropdown", "color"], ["deal status", "status"]),
            "owner_code": (["status", "dropdown", "text", "people", "name", "color"], ["owner", "assignee", "kam"]),
            "sector": (["status", "dropdown", "text", "color"], ["sector", "industry", "service"]),
            "close_date": (["date"], ["close date", "closure date", "date"])
        }
        
        for field, (expected_types, aliases) in semantic_fields.items():
            best_col, score, evidence = self._find_best_column(descriptor, expected_types, aliases)
            if best_col and score > 0:
                mapping[field] = best_col.id
                board_score += 0.1
                board_evidence.append(f"Found {field} -> {best_col.id} (Score {score}: {evidence})")
                
        return board_score, board_evidence, mapping

    def _evaluate_as_work_orders_board(self, descriptor: BoardDescriptor) -> Tuple[float, List[str], Dict[str, str]]:
        board_score = 0.0
        board_evidence = []
        mapping = {}
        
        if "work order" in descriptor.board_name.lower() or "execution" in descriptor.board_name.lower() or "tracker" in descriptor.board_name.lower():
            board_score += 0.3
            board_evidence.append(f"Board name '{descriptor.board_name}' suggests work orders.")
            
        semantic_fields = {
            "serial_number": (["text", "name", "dropdown"], ["serial", "serial #", "work order #"]),
            "customer_code": (["dropdown", "text", "status", "color"], ["customer name code", "customer", "client"]),
            "execution_status": (["status", "dropdown", "color"], ["execution status", "status", "state"]),
            "amount_excl_gst": (["numeric", "numbers"], ["amount in rupees (excl", "amount (excl", "excl gst", "amount excl", "billed value"]),
            "amount_incl_gst": (["numeric", "numbers"], ["amount in rupees (incl", "amount (incl", "incl gst", "amount incl"]),
            "amount_receivable": (["numeric", "numbers"], ["amount receivable", "receivable", "amount to be received"]),
            "po_date": (["date"], ["date of po/loi", "po date", "date of po", "loi date"]),
            "document_type": (["status", "dropdown", "text", "color"], ["document type", "doc type"]),
            "sector": (["status", "dropdown", "text", "color"], ["sector", "industry"])
        }
        
        for field, (expected_types, aliases) in semantic_fields.items():
            best_col, score, evidence = self._find_best_column(descriptor, expected_types, aliases)
            if best_col and score > 0:
                mapping[field] = best_col.id
                board_score += 0.1
                board_evidence.append(f"Found {field} -> {best_col.id} (Score {score}: {evidence})")
                
        return board_score, board_evidence, mapping
