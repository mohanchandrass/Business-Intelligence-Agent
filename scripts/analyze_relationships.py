import json
from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path("data/processed")
RAW_DIR = Path("data/raw")

def main():
    print("========================================")
    print("SKYLARK BI AGENT - RELATIONSHIP ANALYSIS")
    print("========================================\n")
    
    excel_files = list(RAW_DIR.glob("*.xlsx")) + list(RAW_DIR.glob("*.csv")) + list(RAW_DIR.glob("*.xls"))
    deals_file = next((f for f in excel_files if "deal" in f.name.lower()), None)
    wo_file = next((f for f in excel_files if "work" in f.name.lower() or "order" in f.name.lower()), None)
    
    if not deals_file or not wo_file:
        print("[FAIL] Both Deals and Work Orders datasets are required for relationship analysis.")
        return
        
    try:
        deals_df = pd.read_excel(deals_file) if deals_file.suffix.lower() != '.csv' else pd.read_csv(deals_file)
        wo_df = pd.read_excel(wo_file) if wo_file.suffix.lower() != '.csv' else pd.read_csv(wo_file)
    except Exception as e:
        print(f"[FAIL] Failed to read datasets: {e}")
        return
        
    # Heuristic: look for 'client', 'customer', 'company', 'project', 'deal', 'work order'
    candidates = ['client', 'customer', 'company', 'project', 'name']
    
    deals_cols = [c for c in deals_df.columns if any(cand in str(c).lower() for cand in candidates)]
    wo_cols = [c for c in wo_df.columns if any(cand in str(c).lower() for cand in candidates)]
    
    relationships = []
    
    for dc in deals_cols:
        for wc in wo_cols:
            d_vals = set(deals_df[dc].dropna().astype(str).str.strip().str.lower())
            w_vals = set(wo_df[wc].dropna().astype(str).str.strip().str.lower())
            
            if not d_vals or not w_vals:
                continue
                
            intersection = d_vals.intersection(w_vals)
            match_rate = len(intersection) / max(len(d_vals), len(w_vals))
            
            if match_rate > 0.1:  # At least 10% overlap
                relationships.append({
                    "deals_column": dc,
                    "work_orders_column": wc,
                    "deals_unique_count": len(d_vals),
                    "work_orders_unique_count": len(w_vals),
                    "overlapping_values": len(intersection),
                    "match_rate": round(match_rate * 100, 2)
                })
                
    if relationships:
        print(f"[OK] Found {len(relationships)} candidate relationships.")
        with open(PROCESSED_DIR / "relationship_profile.json", "w") as f:
            json.dump(relationships, f, indent=2)
    else:
        print("[FAIL] No obvious candidate relationships found with >10% match rate.")
        
    print("\nRelationship analysis completed. Check data/processed/relationship_profile.json")

if __name__ == "__main__":
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    main()
