import os
import json
import pandas as pd
from pathlib import Path

# The user has not provided Excel files yet. 
# We'll make this script fail gracefully if they don't exist.

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

def discover_files():
    """Identify Deals and Work Orders datasets based on filenames/content."""
    if not RAW_DIR.exists():
        print(f"[FAIL] Directory {RAW_DIR} not found.")
        return None, None
        
    excel_files = list(RAW_DIR.glob("*.xlsx")) + list(RAW_DIR.glob("*.csv")) + list(RAW_DIR.glob("*.xls"))
    
    deals_file = None
    wo_file = None
    
    for f in excel_files:
        name_lower = f.name.lower()
        if "deal" in name_lower:
            deals_file = f
        elif "work" in name_lower or "order" in name_lower:
            wo_file = f
            
    return deals_file, wo_file

def profile_dataset(file_path: Path) -> dict:
    print(f"Profiling {file_path.name}...")
    try:
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Failed to read {file_path.name}: {e}")
        return {"error": str(e)}
        
    profile = {
        "filename": file_path.name,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": {}
    }
    
    for col in df.columns:
        col_data = df[col]
        null_count = int(col_data.isnull().sum())
        profile["columns"][col] = {
            "dtype": str(col_data.dtype),
            "null_count": null_count,
            "null_percentage": round(null_count / len(df) * 100, 2) if len(df) > 0 else 0,
            "unique_count": int(col_data.nunique()),
            "sample_values": col_data.dropna().head(3).tolist()
        }
    return profile

def main():
    print("========================================")
    print("SKYLARK BI AGENT - DATA PROFILING")
    print("========================================\n")
    
    deals_file, wo_file = discover_files()
    
    if not deals_file and not wo_file:
        print("[FAIL] No datasets found in data/raw/")
        return
        
    if deals_file:
        print(f"[OK] Deals dataset found: {deals_file.name}")
        deals_profile = profile_dataset(deals_file)
        with open(PROCESSED_DIR / "deals_profile.json", "w") as f:
            json.dump(deals_profile, f, indent=2, default=str)
    else:
        print("[FAIL] Deals dataset NOT found.")
        
    if wo_file:
        print(f"[OK] Work Orders dataset found: {wo_file.name}")
        wo_profile = profile_dataset(wo_file)
        with open(PROCESSED_DIR / "work_orders_profile.json", "w") as f:
            json.dump(wo_profile, f, indent=2, default=str)
    else:
        print("[FAIL] Work Orders dataset NOT found.")
        
    print("\nProfiling completed. Check data/processed/ for JSON outputs.")

if __name__ == "__main__":
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    main()
